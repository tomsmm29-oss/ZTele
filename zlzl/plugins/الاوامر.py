# 🚬 ZThon Handler - Forced Connection Mode
# المسار: zlzl/plugins/الاوامر.py

import os
from telethon import events, Button, TelegramClient
from zlzl import zedub

# =========================
# ☢️ منطقة التعريف الإجباري (The Forced Injection)
# =========================
zthon = zedub
asst = None

# 1. بنحاول نشوف لو السورس معرفه بالأصول
if hasattr(zedub, 'tgbot') and zedub.tgbot:
    asst = zedub.tgbot
elif hasattr(zedub, 'bot') and zedub.bot:
    asst = zedub.bot

# 2. لو ملقيناهوش، بنعمل "كباري" ونسحبه من التوكن غصب
if not asst:
    try:
        # سحب التوكن من متغيرات النظام
        bot_token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("BOT_TOKEN")
        
        if bot_token:
            # إنشاء اتصال جديد خاص بالملف ده بس (Session منفصلة)
            # بنستخدم نفس الـ API ID و HASH بتوع السورس
            asst = TelegramClient(
                "zthon_menu_helper", # اسم جلسة مختلف عشان ميعملش قفلة
                zedub.api_id,
                zedub.api_hash
            ).start(bot_token=bot_token)
            
            print("🚬 Mikey: تم تفعيل البوت المساعد بوضع الاتصال الإجباري!")
    except Exception as e:
        print(f"🚬 Error forcing bot: {e}")

# =========================
# استدعاء النصوص
# =========================
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS

# =========================
# هندسة الزراير
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

# ====================================================================
# 🤖 1. برمجة البوت للرد على الاستعلام (The Listener)
# ====================================================================
if asst:
    @asst.on(events.InlineQuery)
    async def inline_handler(event):
        builder = event.builder
        # كلمة السر: zthon_menu
        if event.text == "zthon_menu":
            me = await zedub.get_me()
            name = me.first_name or "ZThon"
            
            result = builder.article(
                title="ZThon Menu",
                text=MAIN_MENU.format(name=name),
                buttons=get_menu_buttons(1),
                link_preview=False
            )
            await event.answer([result], switch_pm="ZThon Help", switch_pm_param="start")

# ====================================================================
# 👤 2. أمر المستخدم (.الاوامر) - الهجوم بـ 3 طرق
# ====================================================================
@zthon.on(events.NewMessage(pattern=r"\.الاوامر"))
async def ultimate_menu_handler(event):
    me = await event.client.get_me()
    name = me.first_name or "ZThon"
    text_content = MAIN_MENU.format(name=name)

    # فحص أخير
    if not asst:
        await event.edit(f"⚠️ **خطأ فادح في النظام!**\n\nلم يتم العثور على `TG_BOT_TOKEN`.\nتأكد من وضع توكن البوت في متغيرات (Vars).\n\n" + text_content)
        return

    status_msg = await event.edit("⌛️ **جاري فتح القائمة الفخمة...**")
    
    try:
        bot_username = (await asst.get_me()).username
    except:
        await status_msg.edit("⚠️ البوت المساعد لا يستجيب!")
        return

    # --- محاولة 1: الاستعلام الانلاين (The Pro Way) ---
    try:
        results = await zthon.inline_query(bot_username, "zthon_menu")
        if results:
            await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
            await status_msg.delete()
            return
    except Exception:
        pass # كمل يا وحش

    # --- محاولة 2: الإرسال المباشر ---
    try:
        await asst.send_message(event.chat_id, text_content, buttons=get_menu_buttons(1), reply_to=event.id)
        await status_msg.delete()
        return
    except Exception:
        pass

    # --- محاولة 3: خطة الهروب (Saved Messages) ---
    try:
        # ابعتها للمحفوظات وحولها
        msg = await asst.send_message("me", text_content, buttons=get_menu_buttons(1))
        await zthon.forward_messages(event.chat_id, msg)
        await status_msg.delete()
    except Exception:
        # --- الفشل التام ---
        error_msg = """
⚠️ **عذراً، حدث خطأ تقني في الانلاين.**

يبدو أن هناك مشكلة في صلاحيات البوت أو أن الـ Inline Mode غير مفعل.
يرجى التأكد من تفعيل Inline Mode من @BotFather.

**القائمة النصية:**
"""
        await status_msg.edit(error_msg + "\n" + text_content)


# ==========================================
# 3️⃣ معالج الضغطات (Bot Callback Handler)
# ==========================================
if asst:
    @asst.on(events.CallbackQuery)
    async def callback_handler(event):
        data = event.data.decode('utf-8')
        owner = await zedub.get_me()
        owner_name = owner.first_name or "ZThon"

        if data == "close":
            await event.delete()
            return

        if data in ("dummy_start", "dummy_end"):
            await event.answer("⚠️ لا توجد صفحات أخرى", cache_time=1)
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
            await event.answer("⚠️ القسم قيد الصيانة", alert=True)

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
@zthon.on(events.NewMessage(pattern=r"\.اوامري"))
async def text_only(event):
    me = await event.client.get_me()
    await event.edit(MAIN_MENU.format(name=me.first_name or "ZThon"))