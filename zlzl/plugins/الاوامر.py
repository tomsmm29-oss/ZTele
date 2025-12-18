# 🚬 ZThon Ultimate Handler - الهجوم الشامل
# المسار: zlzl/plugins/الاوامر.py

from telethon import events, Button
from telethon.errors import BotResponseTimeoutError, ChatSendMediaForbiddenError
from zlzl import zedub

# =========================
# 🕵️‍♂️ كشف البوت المساعد (المخابرات)
# =========================
zthon = zedub
asst = None

if hasattr(zedub, 'tgbot') and zedub.tgbot:
    asst = zedub.tgbot
elif hasattr(zedub, 'bot') and zedub.bot:
    asst = zedub.bot

# =========================
# 📦 استدعاء البضاعة
# =========================
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS

# =========================
# 🎮 هندسة الزراير (تم تثبيت الفخامة)
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
# 🤖 1. برمجة البوت المساعد للرد على الاستعلام (The Hidden Listener)
# ده الجزء اللي كان ناقص! البوت لازم يعرف يرد لما يتنادى
# ====================================================================
if asst:
    @asst.on(events.InlineQuery)
    async def inline_handler(event):
        builder = event.builder
        # لو الاستعلام هو كلمة "menu"
        if event.text == "zthon_menu":
            me = await zedub.get_me()
            name = me.first_name or "ZThon"
            
            # تجهيز النتيجة (قائمة)
            result = builder.article(
                title="ZThon Menu",
                text=MAIN_MENU.format(name=name),
                buttons=get_menu_buttons(1),
                link_preview=False
            )
            await event.answer([result], switch_pm="طرح المشكلة", switch_pm_param="start")

# ====================================================================
# 👤 2. أمر المستخدم (.الاوامر) - تنفيذ الهجوم بـ 5 طرق
# ====================================================================
@zthon.on(events.NewMessage(pattern=r"\.الاوامر"))
async def ultimate_menu_handler(event):
    me = await event.client.get_me()
    name = me.first_name or "ZThon"
    text_content = MAIN_MENU.format(name=name)

    # 1. التحقق من وجود البوت
    if not asst:
        await event.edit(f"⚠️ **عذراً.. حدث خطأ تقني!**\n\nالبوت المساعد غير متصل بالنظام.\nيرجى التحقق من `TG_BOT_TOKEN` في إعدادات السورس.\n\n" + text_content)
        return

    # تعديل الرسالة ليعرف المستخدم أننا نحاول
    status_msg = await event.edit("⌛️ **جاري استدعاء القائمة...**")
    bot_username = asst.me.username

    # ==========================
    # 🧨 الطريقة الأولى: الاستعلام الانلاين (The Cleanest Way)
    # ==========================
    try:
        # بنبحث عن البوت بتاعنا ونقوله "zthon_menu"
        results = await zthon.inline_query(bot_username, "zthon_menu")
        
        # لو لقينا نتيجة، نبعتها
        if results:
            await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
            # نحذف رسالة الأمر (.الاوامر) ورسالة الانتظار
            await status_msg.delete()
            return # نجحت المهمة، اخلع
            
    except Exception as e:
        print(f"Method 1 Failed: {e}") 
        # نكمل للطريقة التانية

    # ==========================
    # 🔫 الطريقة الثانية: الإرسال المباشر (Direct Send)
    # ==========================
    try:
        await asst.send_message(
            event.chat_id,
            text_content,
            buttons=get_menu_buttons(1),
            reply_to=event.id
        )
        await status_msg.delete()
        return
    except Exception as e:
        print(f"Method 2 Failed: {e}")

    # ==========================
    # 🛠 الطريقة الثالثة: الإرسال للخاص والتحويل (Saved Messages)
    # ==========================
    try:
        # ابعتها لنفسك (Saved Messages)
        msg = await asst.send_message("me", text_content, buttons=get_menu_buttons(1))
        # حولها للشات اللي انت فيه
        await zthon.forward_messages(event.chat_id, msg)
        await status_msg.delete()
        return
    except Exception as e:
        print(f"Method 3 Failed: {e}")

    # ==========================
    # ❌ لو كل الطرق فشلت (The Fallback)
    # ==========================
    # عرض رسالة الخطأ الرسمية بالفصحى + القائمة النصية
    error_text = """
⚠️ **عذراً، حدث خطأ أثناء جلب القائمة التفاعلية.**

يبدو أن هناك مشكلة في الاتصال بالبوت المساعد، أو أن الانلاين (Inline Mode) غير مفعل في البوت.
يرجى الذهاب لـ @BotFather وتفعيل Inline Mode للبوت الخاص بك.

**إليك القائمة النصية مؤقتاً:**
"""
    await status_msg.edit(error_text + "\n" + text_content)


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
            await event.answer("⚠️ هذا القسم قيد التطوير حالياً", alert=True)

# ==========================================
# 4️⃣ .اوامري (النصية فقط)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.اوامري"))
async def direct_text_menu(event):
    me = await event.client.get_me()
    name = me.first_name or "ZThon"
    await event.edit(MAIN_MENU.format(name=name))

# ==========================================
# 5️⃣ الأوامر المباشرة (.م1)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.م(\d+)"))
async def direct_section(event):
    num = event.pattern_match.group(1)
    key = f"m{num}"
    if key in SECTION_DETAILS:
        await event.edit(SECTION_DETAILS[key])
    else:
        return