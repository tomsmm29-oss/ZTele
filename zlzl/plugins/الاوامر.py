# 🚬 ZThon Handler - Secure & Auto-Detect
# المسار: zlzl/plugins/الاوامر.py

from telethon import events, Button
from zlzl import zedub

# =========================
# كشف البوت المساعد تلقائياً 🕵️‍♂️
# =========================
zthon = zedub

# بنحاول نمسك البوت المساعد بأي طريقة
asst = None
if hasattr(zedub, 'tgbot') and zedub.tgbot:
    asst = zedub.tgbot
elif hasattr(zedub, 'bot') and zedub.bot:
    asst = zedub.bot

# =========================
# استدعاء النصوص والمخزن
# =========================
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS

# =========================
# هندسة الزراير (Pagination)
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
    nav.append(Button.inline("⪼ الســابق ⪻", data=f"page_{page-1}") if page > 1 else Button.inline("❨ الرئيسيــة ❩", data="dummy_start"))
    nav.append(Button.inline("❎ اغــلاق", data="close"))
    nav.append(Button.inline("⪼ التــالي ⪻", data=f"page_{page+1}") if end < len(all_buttons) else Button.inline("❨ النهايــة ❩", data="dummy_end"))

    rows.append(nav)
    return rows


# ==========================================
# 1️⃣ .اوامري (نص فقط)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.اوامري"))
async def text_only_menu(event):
    me = await event.client.get_me()
    name = me.first_name or "ZThon"
    await event.edit(MAIN_MENU.format(name=name))


# ==========================================
# 2️⃣ .الاوامر (الانلاين - الفخامة)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.الاوامر"))
async def inline_menu_show(event):
    me = await event.client.get_me()
    name = me.first_name or "ZThon"
    text_content = MAIN_MENU.format(name=name)

    # تأكد إن البوت موجود
    if not asst:
        await event.edit(f"⚠️ **عذراً يا ريس!**\nالبوت المساعد مش شغال.\nاتأكد إنك حطيت `TG_BOT_TOKEN` في متغيرات ريندر.\n\n" + text_content)
        return

    await event.edit("⌛️ **جاري استدعاء القائمة...**")

    try:
        # إرسال عبر البوت المساعد
        results = await zthon.inline_query(asst.me.username, "menu")
        # دي طريقة تانية لاستدعاء الانلاين لو الطريقة المباشرة فشلت
        # بس حالياً هنجرب الإرسال المباشر أضمن
        await asst.send_message(
            event.chat_id,
            text_content,
            buttons=get_menu_buttons(1),
            reply_to=event.id
        )
        await event.delete()
        
    except Exception as e:
        # لو فشل، اعرض النص وخلاص
        await event.edit(text_content)


# ==========================================
# 3️⃣ معالج الضغطات (Bot Callback)
# ==========================================
if asst: # بنشغل الهاندلر بس لو البوت موجود
    @asst.on(events.CallbackQuery)
    async def callback_handler(event):
        data = event.data.decode('utf-8')
        owner = await zedub.get_me()
        owner_name = owner.first_name or "ZThon"

        if data == "close":
            await event.delete()
            return

        if data in ("dummy_start", "dummy_end"):
            await event.answer("⚠️ لا يوجد صفحات أخرى!", cache_time=1)
            return

        if data.startswith("page_"):
            page = int(data.split("_")[1])
            new_text = MAIN_MENU.format(name=owner_name)
            await event.edit(new_text, buttons=get_menu_buttons(page))
            return

        if data == "main_menu":
            new_text = MAIN_MENU.format(name=owner_name)
            await event.edit(new_text, buttons=get_menu_buttons(1))
            return

        if data in SECTION_DETAILS:
            content = SECTION_DETAILS[data]
            back_btn = [[Button.inline("⪼ رجــوع للقائمــة ⪻", data="main_menu")]]
            await event.edit(content, buttons=back_btn)
        else:
            await event.answer("⚠️ القسم ده لسه تحت الإنشاء!", alert=True)


# ==========================================
# 4️⃣ الأوامر النصية المباشرة (.م1)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.م(\d+)"))
async def direct_text_section(event):
    num = event.pattern_match.group(1)
    key = f"m{num}"
    if key in SECTION_DETAILS:
        await event.edit(SECTION_DETAILS[key])
    else:
        return