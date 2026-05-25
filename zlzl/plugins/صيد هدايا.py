import asyncio
import time
from telethon import events
from telethon.errors.rpcerrorlist import FloodWaitError, MessageNotModifiedError

from . import zedub
from ..core.managers import edit_or_reply
from ..core.logger import logging

# محاولة استدعاء أحدث دوال الهدايا من نواة التليجرام
try:
    from telethon.tl.functions.payments import GetStarGiftsRequest, GetResaleStarGiftsRequest
    HAS_API = True
except ImportError:
    HAS_API = False

plugin_category = "البحث"
LOGS = logging.getLogger(__name__)

# المتغيرات العامة (State Variables)
HUNTER_ACTIVE = False
SHOW_COUNTER = True
SCANNED_COUNT = 0
FOUND_GIFTS = []

async def hunt_gifts_loop(event, client, currency, max_price, status_msg):
    """حلقة الفحص الأساسية التي تعمل في الخلفية"""
    global HUNTER_ACTIVE, SHOW_COUNTER, SCANNED_COUNT, FOUND_GIFTS
    
    chat_id = event.chat_id
    last_update_time = time.time()

    while HUNTER_ACTIVE:
        try:
            # 1. جلب كتالوج الهدايا الأساسي من سيرفر التليجرام
            catalog = await client(GetStarGiftsRequest(hash=0))
            gifts_list = getattr(catalog, 'gifts', [])
            
            # 2. فحص كل هدية ختمًا تلو الآخر
            for base_gift in gifts_list:
                if not HUNTER_ACTIVE:
                    break
                
                gift_id = getattr(base_gift, 'id', None)
                if not gift_id:
                    continue

                try:
                    # جلب النسخ المطورة المعروضة للبيع لهذه الهدية بالتحديد (الأرخص أولاً)
                    resale_items = await client(GetResaleStarGiftsRequest(
                        gift_id=gift_id,
                        sort_by_price=True,
                        offset="",
                        limit=10
                    ))
                    
                    items_list = getattr(resale_items, 'gifts', []) or getattr(resale_items, 'items', [])
                    
                    for item in items_list:
                        SCANNED_COUNT += 1 # زيادة عداد الفحص
                        
                        # تحديد نوع العملة والسعر من السيرفر
                        # في تحديثات التليجرام: يتم تحديد العملة إما بالنجوم أو الكريبتو (TON)
                        item_price = 0
                        is_ton = False
                        is_stars = False
                        
                        crypto_price = getattr(item, 'crypto_amount', None) or getattr(item, 'ton_value', None)
                        star_price = getattr(item, 'price', None) or getattr(item, 'stars', None)

                        if crypto_price:
                            item_price = float(crypto_price)
                            is_ton = True
                        elif star_price:
                            item_price = float(star_price)
                            is_stars = True

                        # فلترة حسب طلب المستخدم (تون أو نجوم)
                        matched = False
                        if currency == "تون" and is_ton and item_price <= max_price:
                            matched = True
                        elif currency == "نجوم" and is_stars and item_price <= max_price:
                            matched = True

                        # إذا طابقت الشروط ولم يتم إرسالها مسبقاً
                        item_slug = getattr(item, 'slug', None) or getattr(item, 'id', gift_id)
                        gift_link = f"https://t.me/nft/{item_slug}"

                        if matched and gift_link not in FOUND_GIFTS:
                            FOUND_GIFTS.append(gift_link)
                            
                            curr_icon = "💎" if currency == "تون" else "⭐️"
                            alert_msg = (
                                "**🛂┊صـائـد الـهـدايـا - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
                                f"**⎉╎تـم إصـطيـاد هـديـة مـطـورة 🎁**\n"
                                f"**⎉╎الـسـعـر ⩥** `{item_price}` {curr_icon}\n"
                                f"**⎉╎الـرابـط ⩥** {gift_link}\n\n"
                                "**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
                            )
                            await client.send_message(chat_id, alert_msg)
                            await asyncio.sleep(0.5)

                except FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except Exception:
                    pass

                # تحديث العداد كل 5 ثواني إذا كان العداد مفعلاً
                if SHOW_COUNTER and (time.time() - last_update_time >= 5):
                    try:
                        counter_text = (
                            "**🛂┊صـائـد الـهـدايـا - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
                            f"**⎉╎جـاري الـفـحـص عـن هـدايـا ( {currency} ) ..**\n"
                            f"**⎉╎أقـصـى سـعـر ⩥** `{max_price}`\n"
                            f"**⎉╎تـم فـحـص ⩥** `[ {SCANNED_COUNT} ]` **هـديـة حـتـى الآن 🔍**\n\n"
                            "**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
                        )
                        await status_msg.edit(counter_text)
                        last_update_time = time.time()
                    except MessageNotModifiedError:
                        pass
                    except Exception:
                        pass
                
                await asyncio.sleep(0.3) # فاصل زمني لتجنب كشف البوت

            # إعادة دورة الفحص من جديد
            await asyncio.sleep(1)

        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception:
            await asyncio.sleep(2)


@zedub.zed_cmd(pattern="^[.,]مطوره (تون|نجوم) ([0-9.]+)$")
async def start_hunter(event):
    global HUNTER_ACTIVE, SCANNED_COUNT, FOUND_GIFTS

    if not HAS_API:
        return await edit_or_reply(event, "**•❐• عـذراً .. مـكتبـة تـليـثون لـديـك قـديمـة ولا تـدعـم دوال الـهـدايـا الـجديـدة ⚠️**")

    if HUNTER_ACTIVE:
        return await edit_or_reply(event, "**•❐• صـائـد الـهـدايـا يـعمـل بـالـفعـل .. لإيـقـافـه أرسـل ⩥** `.ايقاف مطوره`")

    currency = event.pattern_match.group(1)
    max_price = float(event.pattern_match.group(2))

    HUNTER_ACTIVE = True
    SCANNED_COUNT = 0
    FOUND_GIFTS.clear()

    start_text = (
        "**🛂┊صـائـد الـهـدايـا - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**⎉╎تـم تـشـغيـل الـقـنـاص بـنـجـاح 🚀**\n"
        f"**⎉╎جـاري الـفـحـص عـن هـدايـا ( {currency} ) ..**\n"
        f"**⎉╎أقـصـى سـعـر ⩥** `{max_price}`\n"
        f"**⎉╎تـم فـحـص ⩥** `[ 0 ]` **هـديـة حـتـى الآن 🔍**\n\n"
        "**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )
    status_msg = await edit_or_reply(event, start_text)

    # تشغيل حلقة الفحص في الخلفية
    client = event.client
    event.client.loop.create_task(hunt_gifts_loop(event, client, currency, max_price, status_msg))


@zedub.zed_cmd(pattern="^[.,]ايقاف مطوره$")
async def stop_hunter(event):
    global HUNTER_ACTIVE
    if not HUNTER_ACTIVE:
        return await edit_or_reply(event, "**•❐• صـائـد الـهـدايـا مـتـوقـف بـالـفـعـل ⚠️**")
    
    HUNTER_ACTIVE = False
    await edit_or_reply(event, "**•❐• تـم إيـقـاف صـائـد الـهـدايـا بـنـجـاح ✓**")


@zedub.zed_cmd(pattern="^[.,]ايقاف العداد$")
async def stop_counter(event):
    global SHOW_COUNTER
    SHOW_COUNTER = False
    await edit_or_reply(event, "**•❐• تـم إيـقـاف الـعـداد الـحـي بـنـجـاح (لـتجـنـب الـفـلـود) ✓**")


@zedub.zed_cmd(pattern="^[.,]تشغيل العداد$")
async def start_counter(event):
    global SHOW_COUNTER
    SHOW_COUNTER = True
    await edit_or_reply(event, "**•❐• تـم تـشـغيـل الـعـداد الـحـي بـنـجـاح ✓**")