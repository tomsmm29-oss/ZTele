import asyncio
import time
import traceback
from telethon import events
from telethon.errors.rpcerrorlist import FloodWaitError, MessageNotModifiedError

from . import zedub
from ..core.managers import edit_or_reply
from ..core.logger import logging

# محاولة استدعاء دوال الهدايا من تليثون
try:
    from telethon.tl.functions.payments import GetStarGiftsRequest, GetResaleStarGiftsRequest
    HAS_API = True
except ImportError:
    HAS_API = False

plugin_category = "البحث"
LOGS = logging.getLogger(__name__)

# المتغيرات العامة
HUNTER_ACTIVE = False
SHOW_COUNTER = True
SCANNED_COUNT = 0
FOUND_GIFTS = []

async def hunt_gifts_loop(event, client, currency, max_price, status_msg):
    global HUNTER_ACTIVE, SHOW_COUNTER, SCANNED_COUNT, FOUND_GIFTS
    
    chat_id = event.chat_id
    last_update_time = time.time()

    LOGS.info(f"🟢 بدء تشغيل قناص الهدايا | العملة: {currency} | السعر الأقصى: {max_price}")

    while HUNTER_ACTIVE:
        try:
            # 1. جلب الكتالوج الأساسي
            catalog = await client(GetStarGiftsRequest(hash=0))
            gifts_list = getattr(catalog, 'gifts', [])
            
            if not gifts_list:
                LOGS.warning("⚠️ لم يتم العثور على أي هدايا في الكتالوج الأساسي (ربما مشكلة في اتصال الحساب).")
                await asyncio.sleep(5)
                continue

            # 2. فحص الهدايا المطورة هدية تلو الأخرى
            for base_gift in gifts_list:
                if not HUNTER_ACTIVE:
                    break
                
                gift_id = getattr(base_gift, 'id', None)
                if not gift_id:
                    continue

                try:
                    # جلب الهدايا المعروضة للبيع
                    resale_items = await client(GetResaleStarGiftsRequest(
                        gift_id=gift_id,
                        sort_by_price=True,
                        offset="",
                        limit=20
                    ))
                    
                    items_list = getattr(resale_items, 'gifts', []) or getattr(resale_items, 'items', [])
                    
                    # LOGS.info(f"🔎 جاري فحص الهدية رقم {gift_id} - تم العثور على {len(items_list)} نسخة مطورة للبيع.")
                    
                    for item in items_list:
                        SCANNED_COUNT += 1
                        
                        item_price = 0.0
                        is_ton = False
                        is_stars = False
                        
                        try:
                            # ---------------------------------------------------------
                            # التشريح الذكي للأسعار (التصحيح الشامل)
                            # ---------------------------------------------------------
                            crypto_obj = getattr(item, 'crypto_amount', None) or getattr(item, 'ton_value', None)
                            star_obj = getattr(item, 'price', None) or getattr(item, 'stars', None)

                            if crypto_obj is not None:
                                val = getattr(crypto_obj, 'amount', crypto_obj)
                                val_float = float(val)
                                # إذا كان الرقم ضخم جداً (بالنانو تون) نقسمه على مليار
                                item_price = val_float / 1e9 if val_float > 1e6 else val_float
                                is_ton = True
                                
                            elif star_obj is not None:
                                val = getattr(star_obj, 'amount', star_obj)
                                item_price = float(val)
                                is_stars = True
                                
                        except Exception as parse_err:
                            LOGS.error(f"❌ خطأ في تشريح سعر الهدية! \nالخطأ: {parse_err}\nالتفاصيل: {item}\n{traceback.format_exc()}")
                            continue # تخطي هذه الهدية إذا فشل التشريح

                        # فلترة الهدايا حسب طلب المستخدم
                        matched = False
                        if currency == "تون" and is_ton and 0 < item_price <= max_price:
                            matched = True
                        elif currency == "نجوم" and is_stars and 0 < item_price <= max_price:
                            matched = True

                        # إذا طابقت المواصفات
                        if matched:
                            item_slug = getattr(item, 'slug', None) or getattr(item, 'id', gift_id)
                            gift_link = f"https://t.me/nft/{item_slug}"
                            
                            if gift_link not in FOUND_GIFTS:
                                FOUND_GIFTS.append(gift_link)
                                
                                curr_icon = "💎" if currency == "تون" else "⭐️"
                                LOGS.info(f"🎉 تم اصطياد هدية! السعر: {item_price} {currency} | الرابط: {gift_link}")
                                
                                alert_msg = (
                                    "**🛂┊صـائـد الـهـدايـا - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
                                    f"**⎉╎تـم إصـطيـاد هـديـة مـطـورة 🎁**\n"
                                    f"**⎉╎الـسـعـر ⩥** `{item_price}` {curr_icon}\n"
                                    f"**⎉╎الـرابـط ⩥** {gift_link}\n\n"
                                    "**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
                                )
                                await client.send_message(chat_id, alert_msg)
                                await asyncio.sleep(1) # حماية إضافية من حظر الإرسال

                except FloodWaitError as e:
                    LOGS.warning(f"⏳ فلود ويت من تليجرام! تم إيقاف الفحص مؤقتاً لمدة {e.seconds} ثانية.")
                    await asyncio.sleep(e.seconds + 1)
                except Exception as req_err:
                    LOGS.error(f"❌ خطأ غير متوقع أثناء طلب تفاصيل الهدية: {req_err}\n{traceback.format_exc()}")

                # تحديث العداد الحي كل 5 ثواني
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
                    except Exception as cnt_err:
                        LOGS.error(f"⚠️ خطأ أثناء تحديث العداد: {cnt_err}")
                
                # فاصل زمني لتجنب غضب سيرفر تليجرام (FloodWait)
                await asyncio.sleep(1.5) 

            # استراحة بسيطة قبل إعادة الفحص من جديد
            LOGS.info("🔄 انتهت دورة الفحص لجميع الهدايا، جاري إعادة الفحص من جديد...")
            await asyncio.sleep(3)

        except FloodWaitError as e:
            LOGS.warning(f"⏳ فلود ويت عام! انتظار {e.seconds} ثانية.")
            await asyncio.sleep(e.seconds)
        except Exception as main_err:
            LOGS.error(f"❌ انهيار في الحلقة الرئيسية: {main_err}\n{traceback.format_exc()}")
            await asyncio.sleep(5)


@zedub.zed_cmd(pattern="^[.,]مطوره (تون|نجوم) ([0-9.]+)$")
async def start_hunter(event):
    global HUNTER_ACTIVE, SCANNED_COUNT, FOUND_GIFTS

    if not HAS_API:
        return await edit_or_reply(event, "**•❐• عـذراً .. مـكتبـة تـليـثون لـديـك قـديمـة ولا تـدعـم دوال الـهـدايـا الـجديـدة ⚠️**")

    if HUNTER_ACTIVE:
        return await edit_or_reply(event, "**•❐• صـائـد الـهـدايـا يـعمـل بـالـفعـل .. لإيـقـافـه أرسـل ⩥** `.ايقاف مطوره`")

    currency = event.pattern_match.group(1)
    try:
        max_price = float(event.pattern_match.group(2))
    except ValueError:
        return await edit_or_reply(event, "**•❐• عـذراً .. الـسـعـر الـذي أدخـلـته غـيـر صـالـح ⚠️**")

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

    # تشغيل حلقة الفحص كمهام في الخلفية
    client = event.client
    event.client.loop.create_task(hunt_gifts_loop(event, client, currency, max_price, status_msg))


@zedub.zed_cmd(pattern="^[.,]ايقاف مطوره$")
async def stop_hunter(event):
    global HUNTER_ACTIVE
    if not HUNTER_ACTIVE:
        return await edit_or_reply(event, "**•❐• صـائـد الـهـدايـا مـتـوقـف بـالـفـعـل ⚠️**")
    
    HUNTER_ACTIVE = False
    LOGS.info("🛑 تم إيقاف قناص الهدايا بواسطة المستخدم.")
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