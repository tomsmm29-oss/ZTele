# 🚬 ZThon Handler - Private Security Edition 👮‍♂️
# المسار: zlzl/plugins/الاوامر.py

import os
from telethon import events, Button, TelegramClient
from telethon.errors import MessageNotModifiedError
from zlzl import zedub

# =========================
# ☢️ كشف وتعريف البوت المساعد (إجباري)
# =========================
zthon = zedub
asst = None

# محاولة 1: السحب من السورس
if hasattr(zedub, 'tgbot') and zedub.tgbot:
    asst = zedub.tgbot
elif hasattr(zedub, 'bot') and zedub.bot:
    asst = zedub.bot

# محاولة 2: السحب من التوكن (لو السورس نايم)
if not asst:
    try:
        bot_token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("BOT_TOKEN")
        if bot_token:
            asst = TelegramClient(
                "zthon_menu_helper_safe", 
                zedub.api_id, 
                zedub.api_hash
            ).start(bot_token=bot_token)
    except Exception as e:
        print(f"🚬 Mikey Error: {e}")

# =========================
# 📦 استدعاء النصوص
# =========================
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS

# =========================
# 🎮 هندسة الزراير
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
# 🛠 دالة التعديل الآمن (Safe Edit)
# ====================================================================
async def safe_edit(event, text, buttons=None):
    try:
        await event.edit(text, buttons=buttons)
    except Exception:
        try:
            if event.inline_message_id:
                await asst.edit_message(entity=None, message=event.inline_message_id, text=text, buttons=buttons)
            elif event.chat_id and event.message_id:
                await asst.edit_message(entity=event.chat_id, message=event.message_id, text=text, buttons=buttons)
        except MessageNotModifiedError:
            pass
        except Exception:
            pass

# ====================================================================
# 🤖 1. Listener (الانلاين المخفي)
# ====================================================================
if asst:
    @asst.on(events.InlineQuery)
    async def inline_handler(event):
        # ⛔️ تحقق أمني: تجاهل الغرباء في البحث
        # بنجيب ايدي المالك
        owner_id = await zedub.get_peer_id('me')
        if event.sender_id != owner_id:
            # لو مش المالك، منردش عليه أصلاً (تجاهل تام)
            return

        builder = event.builder
        if event.text == "zthon_menu":
            me = await zedub.get_me()
            name = me.first_name or "ZThon"
            result = builder.article(
                title="ZThon Menu",
                text=MAIN_MENU.format(name=name),
                buttons=get_menu_buttons(1),
                link_preview=False
            )
            await event.answer([result], switch_pm="ZThon", switch_pm_param="start")

# ====================================================================
# 👤 2. أمر المستخدم (.الاوامر)
# ====================================================================
@zthon.on(events.NewMessage(pattern=r"\.الاوامر"))
async def ultimate_menu_handler(event):
    # هنا مش محتاجين تحقق لان الامر بيجي من حسابك اصلا (.الاوامر)
    me = await event.client.get_me()
    name = me.first_name or "ZThon"
    text_content = MAIN_MENU.format(name=name)

    if not asst:
        await event.edit(f"⚠️ **عذراً.. البوت المساعد غير متصل!**\nتأكد من `TG_BOT_TOKEN`.\n\n" + text_content)
        return

    status_msg = await event.edit("⌛️ **...**")
    
    try:
        bot_username = (await asst.get_me()).username
        results = await zthon.inline_query(bot_username, "zthon_menu")
        if results:
            await results[0].click(event.chat_id, reply_to=event.reply_to_msg_id, hide_via=True)
            await status_msg.delete()
            return
    except Exception:
        pass

    try:
        await asst.send_message(event.chat_id, text_content, buttons=get_menu_buttons(1), reply_to=event.id)
        await status_msg.delete()
    except Exception:
        await status_msg.edit(f"⚠️ **فشل الانلاين.**\n\n{text_content}")


# ==========================================
# 3️⃣ معالج الضغطات (Bot Callback) - البودي جارد هنا 👮‍♂️
# ==========================================
if asst:
    @asst.on(events.CallbackQuery)
    async def callback_handler(event):
        # 👇👇👇👇 الحماية اليدوية (The Firewall) 👇👇👇👇
        
        # 1. هات ايدي المالك الحقيقي
        owner_id = await zedub.get_peer_id('me')
        
        # 2. هات ايدي الشخص اللي داس ع الزرار
        sender_id = event.sender_id
        
        # 3. قارن بينهم.. لو مش هو، اخرس خالص (Return)
        if sender_id != owner_id:
            # ممكن تفتح السطر الجاي لو عايز تغيظه، بس انت طلبت تجاهل
            # await event.answer("⚠️ هذا الأمر للمالك فقط!", cache_time=3600, alert=True)
            return 
            
        # 👆👆👆👆 انتهى التحقق 👇👇👇👇

        data = event.data.decode('utf-8')
        try:
            owner = await zedub.get_me()
            owner_name = owner.first_name or "ZThon"
        except:
            owner_name = "ZThon"

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
            new_text = MAIN_MENU.format(name=owner_name)
            await safe_edit(event, new_text, buttons=get_menu_buttons(page))
            return

        if data == "main_menu":
            new_text = MAIN_MENU.format(name=owner_name)
            await safe_edit(event, new_text, buttons=get_menu_buttons(1))
            return

        if data in SECTION_DETAILS:
            content = SECTION_DETAILS[data]
            back_btn = [[Button.inline("⪼ رجــوع للقائمــة ⪻", data="main_menu")]]
            await safe_edit(event, content, buttons=back_btn)
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