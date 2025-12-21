import os
import traceback
import asyncio
from telethon import events
from zlzl import zedub

# مكتبة الباشا (Pyrogram)
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent
)

# =========================
# 🏗 إعداد بوت بايروجرام
# =========================
api_id = zedub.api_id
api_hash = zedub.api_hash
bot_token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("BOT_TOKEN")

pyro_bot = Client(
    name="zthon_pyro_secure",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    in_memory=True
)

# متغيرات عالمية لتجنب استدعاء تليثون المتكرر
OWNER_ID = None
OWNER_NAME = "ZThon"

# =========================
# 📦 استدعاء النصوص
# =========================
from zlzl.zthon_texts import HEADER_TEXT, TITLES, FOOTER_TEXT, get_full_menu
from zlzl.zthon_strings import SECTION_DETAILS

# =========================
# 📝 دالة بناء النص
# =========================
def generate_page_text(name, page):
    max_per_page = 12
    start = (page - 1) * max_per_page + 1
    end = start + max_per_page - 1

    page_titles = []
    for i in range(start, end + 2):
        if i in TITLES:
            page_titles.append(TITLES[i])

    titles_str = "\n".join(page_titles)
    return f"{HEADER_TEXT.format(name=name)}\n{titles_str}\n{FOOTER_TEXT}"

# =========================
# 🎮 هندسة الزراير
# =========================
def get_pyro_keyboard(page):
    all_buttons = ["❶","❷","❸","❹","❺","❻","❼","❽","❾","❿","⓫","⓬","⓭","⓮","⓯","⓰","⓱","⓲","⓳","⓴","❷❶","❷❷","❷❸","❷❹","❷❺"]
    max_per_page = 12
    start = (page - 1) * max_per_page
    end = start + max_per_page

    keyboard = []
    temp_row = []

    for i, icon in enumerate(all_buttons[start:end]):
        real_index = start + i + 1
        temp_row.append(InlineKeyboardButton(f" {icon} ", callback_data=f"m{real_index}|{page}"))
        if len(temp_row) == 3:
            keyboard.append(temp_row)
            temp_row = []

    if temp_row:
        keyboard.append(temp_row)

    nav_row = []
    if page > 1:
        prev_p = page - 1
        nav_row.append(InlineKeyboardButton(f"⪻ ❨ {(prev_p-1)*12+1} ⇄ {prev_p*12} ❩", callback_data=f"page_{prev_p}"))
    else:
        nav_row.append(InlineKeyboardButton("❨ الرئيسيــة ❩", callback_data="dummy"))

    if end < len(all_buttons):
        next_p = page + 1
        nav_row.append(InlineKeyboardButton(f"❨ {(next_p-1)*12+1} ⇄ {next_p*12} ❩ ⪼", callback_data=f"page_{next_p}"))
    else:
        nav_row.append(InlineKeyboardButton("❨ النهايــة ❩", callback_data="dummy"))

    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("❎ اغــلاق القائمــة", callback_data="close_all")])
    return InlineKeyboardMarkup(keyboard)

# ====================================================================
# 🔥 المعالجات (Bot Handlers)
# ====================================================================

@pyro_bot.on_inline_query(filters.regex("^zthon_menu$"))
async def pyro_inline_handler(client, inline_query):
    if OWNER_ID and inline_query.from_user.id != OWNER_ID:
        return

    text_content = generate_page_text(OWNER_NAME, 1)
    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="ZThon Menu",
                input_message_content=InputTextMessageContent(text_content, disable_web_page_preview=True),
                reply_markup=get_pyro_keyboard(1)
            )
        ],
        cache_time=1
    )

@pyro_bot.on_callback_query()
async def pyro_callback_handler(client, callback_query):
    global OWNER_ID
    
    # 1. أهم خطوة: الرد الفوري لإيقاف التحميل ومنع تداخل السورس الأساسي
    try:
        await callback_query.answer() 
    except:
        pass

    # 2. التحقق من المالك باستخدام المتغير المحلي (سريع جداً)
    if OWNER_ID and callback_query.from_user.id != OWNER_ID:
        # إذا ضغط شخص آخر، نظهر له التنبيه وننهي التنفيذ
        try:
            return await callback_query.answer("هذا الخيار ليس لك ⚠️!", show_alert=True)
        except:
            return

    data = callback_query.data
    try:
        # إصلاح زر الإغلاق (في الإنلاين التعديل أفضل من الحذف لتجنب الأخطاء)
        if data == "close_all":
            await callback_query.edit_message_text("✅ تم إغلاق قائمة الأوامر.")
            return

        if data == "dummy":
            return

        if data.startswith("page_"):
            page = int(data.split("_")[1])
            await callback_query.edit_message_text(
                generate_page_text(OWNER_NAME, page),
                reply_markup=get_pyro_keyboard(page),
                disable_web_page_preview=True
            )
            return

        if data.startswith("m"):
            section, p = data.split("|")
            if section in SECTION_DETAILS:
                back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⪼ رجــوع للقائمــة ⪻", callback_data=f"page_{p}")]])
                await callback_query.edit_message_text(
                    SECTION_DETAILS[section],
                    reply_markup=back_btn,
                    disable_web_page_preview=True
                )
            return
    except Exception:
        pass

# =========================
# التشغيل
# =========================
async def start_pyro():
    global OWNER_ID, OWNER_NAME
    if not bot_token:
        return
    try:
        await pyro_bot.start()
        # جلب معلومات المالك مرة واحدة عند التشغيل فقط
        me = await zedub.get_me()
        OWNER_ID = me.id
        OWNER_NAME = me.first_name or "ZThon"
        print(f"✅ PyroBot Started - Owner: {OWNER_ID}")
    except Exception as e:
        print(f"❌ Error starting PyroBot: {e}")

# تشغيل بايروجرام في الخلفية
zedub.loop.create_task(start_pyro())

# ====================================================================
# 👤 أوامر المستخدم (Userbot Handlers)
# ====================================================================

@zedub.on(events.NewMessage(pattern=r"\.الاوامر", outgoing=True))
async def launch_menu(event):
    if not bot_token:
        return await event.edit("⚠️ تأكد من وضع توكن البوت في المتغيرات")

    await event.edit("⌛️")
    try:
        results = await zedub.inline_query(pyro_bot.me.username, "zthon_menu")
        if results:
            await results[0].click(event.chat_id, hide_via=True)
            await event.delete()
        else:
            await event.edit("⚠️ فشل في تشغيل الإنلاين")
    except Exception as e:
        await event.edit(f"⚠️ خطأ: {str(e)}")

@zedub.on(events.NewMessage(pattern=r"\.م(\d+)", outgoing=True))
async def direct_txt(event):
    num = event.pattern_match.group(1)
    key = f"m{num}"
    if key in SECTION_DETAILS:
        await event.edit(SECTION_DETAILS[key])

@zedub.on(events.NewMessage(pattern=r"\.اوامري", outgoing=True))
async def txt_menu(event):
    await event.edit(get_full_menu(OWNER_NAME))