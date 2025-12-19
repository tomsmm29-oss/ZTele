# 🚬 ZThon Handler - Stealth Mode (Hidden from Source Loader)
# المسار: zlzl/plugins/الاوامر.py

import os
import asyncio
from telethon import events, Button, TelegramClient
from telethon.errors import MessageNotModifiedError
from zlzl import zedub

# =========================
# 1. إعداد العميل المستقل (بدون تشغيل فوري)
# =========================
api_id = zedub.api_id
api_hash = zedub.api_hash
bot_token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("BOT_TOKEN")

# اسم الجلسة مختلف ومميز
worker = TelegramClient("zthon_stealth_worker", api_id, api_hash)

# =========================
# 2. استدعاء النصوص
# =========================
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS

# =========================
# 3. هندسة الزراير
# =========================
def get_menu_buttons(page):
    all_buttons = [
        "❶","❷","❸","❹","❺","❻",
        "❼","❽","❾","❿","⓫","⓬",
        "⓭","⓮","⓯","⓰","⓱","⓲",
        "⓳","⓴","❷❶","❷❷","❷❸","❷❹","❷❺"
    ]
    max_per_page = 12
    start = (page - 1) * max_per_page
    end = start + max_per_page
    rows, temp = [], []
    for i, icon in enumerate(all_buttons[start:end]):
        real_index = start + i + 1
        temp.append(Button.inline(f" {icon} ", data=f"m{real_index}"))
        if len(temp) == 3: rows.append(temp); temp = []
    if temp: rows.append(temp)
    
    nav = []
    nav.append(Button.inline("⪼ الســابق ⪻", data=f"page_{page-1}") if page > 1 else Button.inline("❨ الرئيسيــة ❩", data="dummy_start"))
    nav.append(Button.inline("❎ اغــلاق", data="close"))
    nav.append(Button.inline("⪼ التــالي ⪻", data=f"page_{page+1}") if end < len(all_buttons) else Button.inline("❨ النهايــة ❩", data="dummy_end"))
    rows.append(nav)
    return rows

# =========================
# 4. دالة التعديل الآمن
# =========================
async def safe_edit(event, text, buttons=None):
    try:
        if event.inline_message_id:
            await worker.edit_message(entity=None, message=event.inline_message_id, text=text, buttons=buttons)
        else:
            await event.edit(text, buttons=buttons)
    except:
        pass

# ====================================================================
# 5. الدوال "العريانة" (بدون أي علامة @)
# دي الدوال اللي هتشتغل بعيد عن عين السورس
# ====================================================================

async def ghost_inline_handler(event):
    """معالج البحث الانلاين"""
    # حماية يدوية: المالك فقط
    try:
        my_id = (await zedub.get_me()).id
        if event.sender_id != my_id:
            return
    except:
        pass 

    builder = event.builder
    if event.text == "zthon_menu":
        try:
            me = await zedub.get_me()
            name = me.first_name or "ZThon"
        except:
            name = "ZThon"
            
        result = builder.article(
            title="ZThon Menu",
            text=MAIN_MENU.format(name=name),
            buttons=get_menu_buttons(1),
            link_preview=False
        )
        await event.answer([result], switch_pm="ZThon", switch_pm_param="start")


async def ghost_callback_handler(event):
    """معالج الضغطات"""
    # حماية يدوية
    try:
        my_id = (await zedub.get_me()).id
        if event.sender_id != my_id:
            return
    except:
        pass

    data = event.data.decode('utf-8')
    try:
        me = await zedub.get_me()
        name = me.first_name or "ZThon"
    except:
        name = "ZThon"

    if data == "close":
        try:
            await event.delete()
        except:
            await safe_edit(event, "🔒", buttons=None)
        return

    if data in ("dummy_start", "dummy_end"):
        await event.answer("⚠️ لا توجد صفحات أخرى!", cache_time=1)
        return

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        new_text = MAIN_MENU.format(name=name)
        await safe_edit(event, new_text, buttons=get_menu_buttons(page))
        return

    if data == "main_menu":
        new_text = MAIN_MENU.format(name=name)
        await safe_edit(event, new_text, buttons=get_menu_buttons(1))
        return

    if data in SECTION_DETAILS:
        content = SECTION_DETAILS[data]
        back_btn = [[Button.inline("⪼ رجــوع للقائمــة ⪻", data="main_menu")]]
        await safe_edit(event, content, buttons=back_btn)
    else:
        await event.answer("⚠️ القسم قيد الصيانة", alert=True)


# ====================================================================
# 6. الحقن السري والتشغيل (The Injection Task)
# ====================================================================
async def start_stealth_bot():
    if not bot_token:
        print("🚬 Mikey: لم يتم العثور على توكن البوت، تم إلغاء تشغيل القائمة.")
        return

    try:
        # تشغيل البوت المستقل
        await worker.start(bot_token=bot_token)
        
        # 👇👇👇 هنا السحر كله 👇👇👇
        # بنضيف الدوال يدوياً للمكتبة، فالسورس ومشاكله مش بيحسوا بحاجة
        worker.add_event_handler(ghost_inline_handler, events.InlineQuery)
        worker.add_event_handler(ghost_callback_handler, events.CallbackQuery)
        
        print("🚬 Mikey: تم تفعيل البوت الشبح (Stealth Mode) بنجاح!")
    except Exception as e:
        print(f"🚬 Mikey Error: فشل تشغيل البوت: {e}")

# تشغيل المهمة في الخلفية
zedub.loop.create_task(start_stealth_bot())


# ====================================================================
# 7. أوامر المستخدم (دي عادية لانها شغالة على zedub)
# ====================================================================

@zedub.on(events.NewMessage(pattern=r"\.الاوامر"))
async def launch_menu(event):
    if not bot_token:
        await event.edit("⚠️ **خطأ:** لم يتم وضع `TG_BOT_TOKEN`!")
        return

    status = await event.edit("⌛️ **...**")
    
    # محاولة الاستدعاء عبر worker
    try:
        bot_user = (await worker.get_me()).username
        results = await zedub.inline_query(bot_user, "zthon_menu")
        if results:
            await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
            await status.delete()
    except Exception as e:
        # لو فشل الانلاين، يبعت مباشر
        try:
            me = await zedub.get_me()
            name = me.first_name or "ZThon"
            await worker.send_message(
                event.chat_id, 
                MAIN_MENU.format(name=name), 
                buttons=get_menu_buttons(1), 
                reply_to=event.id
            )
            await status.delete()
        except Exception:
            await status.edit("⚠️ **فشل العرض!**\nتأكد من تفعيل Inline Mode للبوت من @BotFather.")

@zedub.on(events.NewMessage(pattern=r"\.م(\d+)"))
async def direct_txt(event):
    num = event.pattern_match.group(1)
    key = f"m{num}"
    if key in SECTION_DETAILS:
        await event.edit(SECTION_DETAILS[key])

@zedub.on(events.NewMessage(pattern=r"\.اوامري"))
async def txt_menu(event):
    me = await event.client.get_me()
    await event.edit(MAIN_MENU.format(name=me.first_name or "ZThon"))