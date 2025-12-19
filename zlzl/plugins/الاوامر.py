# 🚬 ZThon Handler - Pyrogram Edition (The Hybrid)
# المسار: zlzl/plugins/الاوامر.py

import os
import asyncio
from telethon import events
from zlzl import zedub

# 👇 هنا بنستدعي المكتبة الجديدة (المستورد)
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    InlineQueryResultArticle, 
    InputTextMessageContent
)

# =========================
# 🏗 إعداد بوت بايروجرام (Pyrogram Bot)
# =========================
api_id = zedub.api_id
api_hash = zedub.api_hash
bot_token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("BOT_TOKEN")

# نستخدم Session String في الذاكرة عشان منعملش ملفات
# ومهم جداً: in_memory=True عشان السرعة
pyro_bot = Client(
    name="zthon_pyro_worker",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    in_memory=True
)

# =========================
# 📦 استدعاء النصوص
# =========================
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS

# =========================
# 🎮 هندسة الزراير (بستايل بايروجرام)
# =========================
def get_pyro_keyboard(page):
    all_buttons = [
        "❶","❷","❸","❹","❺","❻",
        "❼","❽","❾","❿","⓫","⓬",
        "⓭","⓮","⓯","⓰","⓱","⓲",
        "⓳","⓴","❷❶","❷❷","❷❸","❷❹","❷❺"
    ]
    max_per_page = 12
    start = (page - 1) * max_per_page
    end = start + max_per_page
    
    keyboard = []
    temp_row = []

    for i, icon in enumerate(all_buttons[start:end]):
        real_index = start + i + 1
        # بايروجرام بيستخدم InlineKeyboardButton
        temp_row.append(InlineKeyboardButton(f" {icon} ", callback_data=f"m{real_index}"))
        if len(temp_row) == 3:
            keyboard.append(temp_row)
            temp_row = []
    
    if temp_row:
        keyboard.append(temp_row)

    nav_row = []
    # زرار السابق
    if page > 1:
        nav_row.append(InlineKeyboardButton("⪼ الســابق ⪻", callback_data=f"page_{page-1}"))
    else:
        nav_row.append(InlineKeyboardButton("❨ الرئيسيــة ❩", callback_data="dummy_start"))

    # زرار الإغلاق
    nav_row.append(InlineKeyboardButton("❎ اغــلاق", callback_data="close"))

    # زرار التالي
    if end < len(all_buttons):
        nav_row.append(InlineKeyboardButton("⪼ التــالي ⪻", callback_data=f"page_{page+1}"))
    else:
        nav_row.append(InlineKeyboardButton("❨ النهايــة ❩", callback_data="dummy_end"))

    keyboard.append(nav_row)
    
    return InlineKeyboardMarkup(keyboard)

# ====================================================================
# 🔥 معالجات بايروجرام (منعزلة تماماً عن تليثون)
# ====================================================================

# 1. الرد على البحث (Inline Query)
@pyro_bot.on_inline_query(filters.regex("^zthon_menu$"))
async def pyro_inline_handler(client, inline_query):
    # التحقق من المالك (اختياري بس أمان)
    # هنجيب ايدي المالك من تليثون
    try:
        owner_id = (await zedub.get_me()).id
        if inline_query.from_user.id != owner_id:
            return
    except:
        pass

    try:
        # نجيب الاسم
        me = await zedub.get_me()
        name = me.first_name or "ZThon"
    except:
        name = "ZThon"

    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="ZThon Menu",
                input_message_content=InputTextMessageContent(
                    MAIN_MENU.format(name=name),
                    disable_web_page_preview=True
                ),
                reply_markup=get_pyro_keyboard(1)
            )
        ],
        cache_time=1
    )

# 2. الرد على الضغطات (Callback Query)
@pyro_bot.on_callback_query()
async def pyro_callback_handler(client, callback_query):
    # حماية المالك
    try:
        owner_id = (await zedub.get_me()).id
        if callback_query.from_user.id != owner_id:
            # تجاهل تام
            return 
    except:
        pass

    data = callback_query.data
    try:
        me = await zedub.get_me()
        name = me.first_name or "ZThon"
    except:
        name = "ZThon"

    # معالجة الزراير
    if data == "close":
        try:
            await callback_query.message.delete()
        except:
            # لو معرفش يحذف (انلاين) يعدلها لنص
            await callback_query.edit_message_text("🔒 تم الإغلاق")
        return

    if data in ("dummy_start", "dummy_end"):
        await callback_query.answer("⚠️ لا توجد صفحات أخرى!", show_alert=False)
        return

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await callback_query.edit_message_text(
            MAIN_MENU.format(name=name),
            reply_markup=get_pyro_keyboard(page),
            disable_web_page_preview=True
        )
        return

    if data == "main_menu":
        await callback_query.edit_message_text(
            MAIN_MENU.format(name=name),
            reply_markup=get_pyro_keyboard(1),
            disable_web_page_preview=True
        )
        return

    if data in SECTION_DETAILS:
        content = SECTION_DETAILS[data]
        back_btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("⪼ رجــوع للقائمــة ⪻", callback_data="main_menu")
        ]])
        await callback_query.edit_message_text(
            content,
            reply_markup=back_btn,
            disable_web_page_preview=True
        )
    else:
        await callback_query.answer("⚠️ القسم قيد الصيانة", show_alert=True)


# ====================================================================
# 🚀 تشغيل بايروجرام في الخلفية (The Engine)
# ====================================================================
async def start_pyro():
    if not bot_token:
        print("🚬 Mikey: لا يوجد توكن للبوت (Pyrogram)!")
        return
    try:
        await pyro_bot.start()
        print("🚬 Mikey: تم تشغيل بايروجرام (Pyrogram) بنجاح! وداعاً تليثون!")
    except Exception as e:
        print(f"🚬 Mikey Error (Pyrogram): {e}")

# نضيف التشغيل للـ Loop الحالي بتاع تليثون
zedub.loop.create_task(start_pyro())


# ====================================================================
# 👤 أوامر المستخدم (Telethon Trigger)
# هنا تليثون بيسلم الراية لبايروجرام
# ====================================================================

@zedub.on(events.NewMessage(pattern=r"\.الاوامر"))
async def launch_menu(event):
    if not bot_token:
        await event.edit("⚠️ **خطأ:** تأكد من `TG_BOT_TOKEN`")
        return

    status = await event.edit("⌛️ **جاري الفتح (Pyrogram Engine)...**")
    
    try:
        # بنجيب يوزر البوت من بايروجرام
        bot_user = pyro_bot.me.username
        
        # بنستخدم تليثون عشان نعمل البحث، وبايروجرام هو اللي هيرد
        results = await zedub.inline_query(bot_user, "zthon_menu")
        
        if results:
            await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
            await status.delete()
        else:
            await status.edit("⚠️ **لم يتم العثور على النتائج!**")
            
    except Exception as e:
        await status.edit(f"⚠️ **فشل:** {str(e)}")

# الأوامر النصية القديمة (لسه تليثون، بسيطة ومش بتعلق)
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