import os
import traceback
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

# متغير عالمي لحفظ معرف المالك لتقليل الطلبات
OWNER_ID = None

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
        callback_data = f"m{real_index}|{page}"
        temp_row.append(InlineKeyboardButton(f" {icon} ", callback_data=callback_data))

        if len(temp_row) == 3:
            keyboard.append(temp_row)
            temp_row = []

    if temp_row:
        keyboard.append(temp_row)

    nav_row = []

    if page > 1:
        prev_page_num = page - 1
        prev_range_start = (prev_page_num - 1) * max_per_page + 1
        prev_range_end = prev_page_num * max_per_page
        label = f"⪻ ❨ {prev_range_start} ⇄ {prev_range_end} ❩"
        nav_row.append(InlineKeyboardButton(label, callback_data=f"page_{prev_page_num}"))
    else:
        nav_row.append(InlineKeyboardButton("❨ الرئيسيــة ❩", callback_data="dummy_start"))

    if end < len(all_buttons):
        next_page_num = page + 1
        next_range_start = (next_page_num - 1) * max_per_page + 1
        next_range_end = next_page_num * max_per_page
        if next_range_start >= 25:
            label = f"❨ {next_range_start} ⇄ ∞ ❩ ⪼"
        else:
            label = f"❨ {next_range_start} ⇄ {next_range_end} ❩ ⪼"
        nav_row.append(InlineKeyboardButton(label, callback_data=f"page_{next_page_num}"))
    else:
        nav_row.append(InlineKeyboardButton("❨ النهايــة ❩", callback_data="dummy_end"))

    keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("❎ اغــلاق القائمــة", callback_data="close")])
    return InlineKeyboardMarkup(keyboard)

# ====================================================================
# 🔥 المعالجات (Bot Handlers)
# ====================================================================

@pyro_bot.on_inline_query(filters.regex("^zthon_menu$"))
async def pyro_inline_handler(client, inline_query):
    global OWNER_ID
    try:
        if OWNER_ID is None:
            OWNER_ID = (await zedub.get_me()).id
        
        if inline_query.from_user.id != OWNER_ID:
            return
    except:
        return

    try:
        me = await zedub.get_me()
        name = me.first_name or "ZThon"
    except:
        name = "ZThon"

    text_content = generate_page_text(name, 1)

    await inline_query.answer(
        results=[
            InlineQueryResultArticle(
                title="ZThon Menu",
                input_message_content=InputTextMessageContent(
                    text_content,
                    disable_web_page_preview=True
                ),
                reply_markup=get_pyro_keyboard(1)
            )
        ],
        cache_time=1
    )

@pyro_bot.on_callback_query()
async def pyro_callback_handler(client, callback_query):
    global OWNER_ID
    
    # 1. جلب معرف المالك إذا لم يكن موجوداً
    if OWNER_ID is None:
        try:
            OWNER_ID = (await zedub.get_me()).id
        except:
            pass

    # 2. التحقق من الهوية فوراً
    if callback_query.from_user.id != OWNER_ID:
        # إذا لم يكن المالك، نظهر الرسالة له هو فقط
        return await callback_query.answer("هذا الخيار ليس لك ⚠️!", show_alert=True)

    # 3. إذا كان المالك، نرسل إجابة صامتة فوراً لإخفاء علامة التحميل
    try:
        await callback_query.answer()
    except:
        pass

    data = callback_query.data or ""

    try:
        if data == "close":
            await callback_query.message.delete()
            return

        if data.startswith("dummy"):
            return

        if data.startswith("page_"):
            page = int(data.split("_")[1])
            me = await zedub.get_me()
            new_text = generate_page_text(me.first_name or "ZThon", page)
            await callback_query.edit_message_text(
                new_text,
                reply_markup=get_pyro_keyboard(page),
                disable_web_page_preview=True
            )
            return

        if data.startswith("m"):
            section_key, origin_page = data.split("|")
            if section_key in SECTION_DETAILS:
                content = SECTION_DETAILS[section_key]
                back_btn = InlineKeyboardMarkup([[
                    InlineKeyboardButton("⪼ رجــوع للقائمــة ⪻", callback_data=f"page_{origin_page}")
                ]])
                await callback_query.edit_message_text(
                    content,
                    reply_markup=back_btn,
                    disable_web_page_preview=True
                )
            return
    except Exception:
        traceback.print_exc()

# =========================
# التشغيل
# =========================
async def start_pyro():
    global OWNER_ID
    if not bot_token:
        print("🚬 Mikey: لا يوجد توكن!")
        return
    try:
        await pyro_bot.start()
        # جلب ID المالك عند بدء التشغيل لتسريع الاستجابة
        OWNER_ID = (await zedub.get_me()).id
        print(f"🚬 Mikey: Pyrogram Started (Owner ID: {OWNER_ID})")
    except Exception as e:
        print(f"🚬 Mikey Error: {e}")

zedub.loop.create_task(start_pyro())

# ====================================================================
# 👤 أوامر المستخدم (Userbot Handlers)
# ====================================================================

@zedub.on(events.NewMessage(pattern=r"\.الاوامر", outgoing=True))
async def launch_menu(event):
    if not bot_token:
        await event.edit("⚠️ **خطأ:** تأكد من `TG_BOT_TOKEN`")
        return

    status = await event.edit("⌛️ **يتم فتح قائمة الأوامر...**")
    try:
        bot_user = pyro_bot.me.username
        results = await zedub.inline_query(bot_user, "zthon_menu")
        if results:
            await results[0].click(
                event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=True
            )
            await status.delete()
        else:
            await status.edit("⚠️ **فشل:** تأكد أن البوت المساعد يعمل.")
    except Exception as e:
        await status.edit(f"⚠️ **حدث خطأ:** {str(e)}")

@zedub.on(events.NewMessage(pattern=r"\.م(\d+)", outgoing=True))
async def direct_txt(event):
    num = event.pattern_match.group(1)
    key = f"m{num}"
    if key in SECTION_DETAILS:
        await event.edit(SECTION_DETAILS[key])

@zedub.on(events.NewMessage(pattern=r"\.اوامري", outgoing=True))
async def txt_menu(event):
    me = await event.client.get_me()
    name = me.first_name or "ZThon"
    await event.edit(get_full_menu(name))