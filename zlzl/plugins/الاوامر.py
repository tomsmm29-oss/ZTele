import os
import re
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

# سحب الايدي من ريندر
try:
    RENDER_OWNER_ID = int(os.environ.get("OWNER_ID") or os.environ.get("SUDO_ID") or 0)
except:
    RENDER_OWNER_ID = 0

# ====================================================================
# 🛡 حل مشكلة تداخل الجلسات (Telethon Silencer)
# ====================================================================
# هذا الجزء وظيفته إسكات تليثون لكي لا يظهر رسالة "الخيار ليس لك"
@zedub.on(events.CallbackQuery(data=re.compile(b"^(m|page_|close_all|dummy)")))
async def telethon_silencer(event):
    # إذا كان المستخدم هو المالك، نجعل تليثون يجيب بصمت ويوقف الانتشار
    if RENDER_OWNER_ID != 0 and event.sender_id == RENDER_OWNER_ID:
        await event.answer() # رد صامت من تليثون
        raise events.StopPropagation # منع بقية ملفات السورس من استلام النقرة
    # إذا لم يكن المالك، نتركه للسورس الأساسي ليتعامل معه

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
     # تم إضافة "❷❻" إلى القائمة
     all_buttons = ["❶","❷","❸","❹","❺","❻","❼","❽","❾","❿","⓫","⓬","⓭","⓮","⓯","⓰","⓱","⓲","⓳","⓴","❷❶","❷❷","❷❸","❷❹","❷❺", "❷❻"] 
     
     max_per_page = 12 
     start = (page - 1) * max_per_page 
     end = start + max_per_page 
     keyboard = [] 
     temp_row = [] 
     
     # عرض الأزرار للصفحة الحالية
     for i, icon in enumerate(all_buttons[start:end]): 
         real_index = start + i + 1 
         temp_row.append(InlineKeyboardButton(f" {icon} ", callback_data=f"m{real_index}|{page}")) 
         if len(temp_row) == 3: 
             keyboard.append(temp_row) 
             temp_row = [] 
             
     if temp_row: 
         keyboard.append(temp_row) 
         
     # صف التنقل (السابق والتالي)
     nav_row = [] 
     if page > 1: 
         p_num = page - 1 
         nav_row.append(InlineKeyboardButton(f"⪻ ❨ {(p_num-1)*12+1} ⇄ {p_num*12} ❩", callback_data=f"page_{p_num}")) 
     else: 
         nav_row.append(InlineKeyboardButton("❨ الرئيسيــة ❩", callback_data="dummy")) 
         
     if end < len(all_buttons): 
         n_num = page + 1 
         # حساب نهاية المدى للصفحة التالية بشكل دقيق
         next_end = n_num * 12 if (n_num * 12) < len(all_buttons) else len(all_buttons)
         nav_row.append(InlineKeyboardButton(f"❨ {(n_num-1)*12+1} ⇄ {next_end} ❩ ⪼", callback_data=f"page_{n_num}")) 
     else: 
         nav_row.append(InlineKeyboardButton("❨ النهايــة ❩", callback_data="dummy")) 
         
     keyboard.append(nav_row) 
     keyboard.append([InlineKeyboardButton("❎ اغــلاق القائمــة", callback_data="close_all")]) 
     
     return InlineKeyboardMarkup(keyboard)





# ====================================================================
# 🔥 معالجات بايروجرام (Execution Handlers)
# ====================================================================

@pyro_bot.on_inline_query(filters.regex("^zthon_menu$"))
async def pyro_inline_handler(client, inline_query):
    if RENDER_OWNER_ID != 0 and inline_query.from_user.id != RENDER_OWNER_ID:
        return
    try:
        me = await zedub.get_me()
        name = me.first_name or "ZThon"
        await inline_query.answer(
            results=[InlineQueryResultArticle(
                title="ZThon Menu",
                input_message_content=InputTextMessageContent(generate_page_text(name, 1), disable_web_page_preview=True),
                reply_markup=get_pyro_keyboard(1)
            )], cache_time=1
        )
    except: pass

@pyro_bot.on_callback_query()
async def pyro_callback_handler(client, callback_query):
    # التحقق من المالك (بايروجرام)
    if RENDER_OWNER_ID != 0 and callback_query.from_user.id != RENDER_OWNER_ID:
        return await callback_query.answer("هذا الخيار ليس لك ⚠️!", show_alert=True)

    # رد صامت من بايروجرام
    try: await callback_query.answer()
    except: pass

    data = callback_query.data
    try:
        if data == "close_all":
            try: await callback_query.message.delete()
            except: await callback_query.edit_message_text("✅ تم إغلاق القائمة")
            return

        if data.startswith("page_"):
            page = int(data.split("_")[1])
            me = await zedub.get_me()
            await callback_query.edit_message_text(
                generate_page_text(me.first_name or "ZThon", page),
                reply_markup=get_pyro_keyboard(page),
                disable_web_page_preview=True
            )

        elif data.startswith("m"):
            section_key, origin_page = data.split("|")
            if section_key in SECTION_DETAILS:
                back_btn = InlineKeyboardMarkup([[InlineKeyboardButton("⪼ رجــوع للقائمــة ⪻", callback_data=f"page_{origin_page}")]])
                await callback_query.edit_message_text(SECTION_DETAILS[section_key], reply_markup=back_btn, disable_web_page_preview=True)
    except: pass

# =========================
# التشغيل
# =========================
async def start_pyro():
    if not bot_token: return
    try:
        await pyro_bot.start()
        print(f"✅ Started! ID: {RENDER_OWNER_ID}")
    except Exception as e:
        print(f"❌ Error: {e}")

zedub.loop.create_task(start_pyro())

# ====================================================================
# 👤 أوامر تليثون (Userbot Handlers)
# ====================================================================

@zedub.on(events.NewMessage(pattern=r"\.الاوامر", outgoing=True))
async def launch_menu(event):
    if not bot_token: return await event.edit("⚠️ خطأ في توكن البوت")
    await event.edit("⌛️")
    try:
        bot_info = await pyro_bot.get_me()
        results = await zedub.inline_query(bot_info.username, "zthon_menu")
        if results:
            await results[0].click(event.chat_id, hide_via=True)
            await event.delete()
        else: await event.edit("⚠️ فشل في جلب القائمة.")
    except Exception as e: await event.edit(f"⚠️ خطأ: {e}")

@zedub.on(events.NewMessage(pattern=r"\.م(\d+)", outgoing=True))
async def direct_txt(event):
    num = event.pattern_match.group(1)
    if f"m{num}" in SECTION_DETAILS: await event.edit(SECTION_DETAILS[f"m{num}"])

@zedub.on(events.NewMessage(pattern=r"\.اوامري", outgoing=True))
async def txt_menu(event):
    me = await event.client.get_me()
    await event.edit(get_full_menu(me.first_name or "ZThon"))
