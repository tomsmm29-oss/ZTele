import os
from telethon import events, Button, TelegramClient
from zlzl import zedub

# =========================
# الاختصارات
# =========================
zthon = zedub

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

# =========================
# إنشاء البوت المساعد
# =========================
assistant = TelegramClient(
    "assistant_bot",
    zedub.api_id,
    zedub.api_hash
).start(bot_token=TG_BOT_TOKEN)

# =========================
# استدعاء النصوص
# =========================
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS


# =========================
# هندسة الزراير (بدون لمس)
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
        if len(temp) == 3:
            rows.append(temp)
            temp = []

    if temp:
        rows.append(temp)

    nav = []
    nav.append(
        Button.inline("⪼ الســابق ⪻", data=f"page_{page-1}")
        if page > 1 else
        Button.inline("❨ الرئيسيــة ❩", data="dummy_start")
    )

    nav.append(Button.inline("❎ اغــلاق", data="close"))

    nav.append(
        Button.inline("⪼ التــالي ⪻", data=f"page_{page+1}")
        if end < len(all_buttons) else
        Button.inline("❨ النهايــة ❩", data="dummy_end")
    )

    rows.append(nav)
    return rows


# =========================
# 1️⃣ .اوامري (يوزر فقط)
# =========================
@zthon.on(events.NewMessage(pattern=r"\.اوامري"))
async def text_only_menu(event):
    me = await event.client.get_me()
    await event.edit(MAIN_MENU.format(name=me.first_name or "ZThon"))


# =========================
# 2️⃣ .الاوامر (يوزر → بوت)
# =========================
@zthon.on(events.NewMessage(pattern=r"\.الاوامر"))
async def inline_menu_handler(event):
    me = await event.client.get_me()
    text = MAIN_MENU.format(name=me.first_name or "ZThon")

    # تعديل رسالة اليوزر (إحساس الاستمرار)
    await event.edit("⌛️ جاري فتح القائمة...")

    # البوت يرسل القائمة الفعلية
    await assistant.send_message(
        event.chat_id,
        text,
        buttons=get_menu_buttons(1)
    )


# =========================
# 3️⃣ CallbackQuery (بوت فقط)
# =========================
@assistant.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode()

    if data == "close":
        return await event.delete()

    if data in ("dummy_start", "dummy_end"):
        return await event.answer("⚠️ لا يوجد تنقل", cache_time=1)

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        me = await assistant.get_me()
        return await event.edit(
            MAIN_MENU.format(name=me.first_name or "ZThon"),
            buttons=get_menu_buttons(page)
        )

    if data == "main_menu":
        me = await assistant.get_me()
        return await event.edit(
            MAIN_MENU.format(name=me.first_name or "ZThon"),
            buttons=get_menu_buttons(1)
        )

    if data in SECTION_DETAILS:
        return await event.edit(
            SECTION_DETAILS[data],
            buttons=[[Button.inline("⪼ رجــوع للقائمــة ⪻", data="main_menu")]]
        )

    await event.answer("⚠️ هذا القسم غير متاح", alert=True)


# =========================
# 4️⃣ .م1 .م2 (يوزر مباشر)
# =========================
@zthon.on(events.NewMessage(pattern=r"\.م(\d+)"))
async def direct_text_section(event):
    key = f"m{event.pattern_match.group(1)}"
    if key in SECTION_DETAILS:
        await event.edit(SECTION_DETAILS[key])