# 🚬 ZThon Handler - Fixed & Powered by Mikey
# المسار: zlzl/plugins/الاوامر.py

from telethon import events, Button
from zlzl import zedub

# =========================
# تعريف الاختصارات (مهم جداً)
# =========================
zthon = zedub
# هنا بنستخدم البوت المساعد الموجود بالفعل في السورس
# بدل ما نعمل واحد جديد ونعمل قفلة
asst = zthon.tgbot 

# =========================
# استدعاء النصوص والمخزن
# =========================
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS

# =========================
# هندسة الزراير (Pagination Logic)
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
        # m1, m2, etc.
        temp.append(Button.inline(f" {icon} ", data=f"m{real_index}"))
        if len(temp) == 3:
            rows.append(temp)
            temp = []

    if temp:
        rows.append(temp)

    nav = []
    # زرار السابق
    if page > 1:
        nav.append(Button.inline("⪼ الســابق ⪻", data=f"page_{page-1}"))
    else:
        nav.append(Button.inline("❨ الرئيسيــة ❩", data="dummy_start"))

    # زرار الإغلاق
    nav.append(Button.inline("❎ اغــلاق", data="close"))

    # زرار التالي
    if end < len(all_buttons):
        nav.append(Button.inline("⪼ التــالي ⪻", data=f"page_{page+1}"))
    else:
        nav.append(Button.inline("❨ النهايــة ❩", data="dummy_end"))

    rows.append(nav)
    return rows


# ==========================================
# 1️⃣ .اوامري (نص فقط - للمسطول الكلاسيكي)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.اوامري"))
async def text_only_menu(event):
    me = await event.client.get_me()
    name = me.first_name or "ZThon"
    await event.edit(MAIN_MENU.format(name=name))


# ==========================================
# 2️⃣ .الاوامر (الانلاين - شغل الفخامة)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.الاوامر"))
async def inline_menu_show(event):
    # 1. نجيب معلومات المستخدم عشان الاسم
    me = await event.client.get_me()
    name = me.first_name or "ZThon"
    text_content = MAIN_MENU.format(name=name)

    # 2. نعدل رسالة المستخدم عشان يعرف اننا شغالين
    await event.edit("⌛️ **جاري استدعاء القائمة ...**")

    # 3. نخلي البوت المساعد يرمي القائمة
    try:
        # هنا بنستخدم asst اللي هو zedub.tgbot
        # بنعمل reply على رسالة المستخدم
        await asst.send_message(
            event.chat_id,
            text_content,
            buttons=get_menu_buttons(1),
            reply_to=event.id
        )
        # نمسح رسالة "جاري الاستدعاء" عشان النظافة
        await event.delete()
        
    except Exception as e:
        # لو البوت مش ادمن او فيه مشكلة، نرجع للنص العادي
        await event.edit(f"⚠️ **حدث خطأ في الانلاين:**\n{str(e)}\n\n" + text_content)


# ==========================================
# 3️⃣ معالج الضغطات (Bot Callback Handler)
# ==========================================
# لاحظ هنا: asst.on مش assistant.on
@asst.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode('utf-8')
    
    # عشان نجيب اسم صاحب الحساب (zedub) مش البوت
    owner = await zedub.get_me()
    owner_name = owner.first_name or "ZThon"

    # ❎ إغلاق
    if data == "close":
        await event.delete()
        return

    # ⚠️ تنبيهات
    if data in ("dummy_start", "dummy_end"):
        await event.answer("⚠️ لا يوجد صفحات أخرى!", cache_time=1)
        return

    # 🔄 تقليب الصفحات
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        new_text = MAIN_MENU.format(name=owner_name)
        await event.edit(new_text, buttons=get_menu_buttons(page))
        return

    # 🔙 الرجوع للقائمة الرئيسية
    if data == "main_menu":
        new_text = MAIN_MENU.format(name=owner_name)
        await event.edit(new_text, buttons=get_menu_buttons(1))
        return

    # 📄 عرض تفاصيل الأقسام (m1, m2...)
    if data in SECTION_DETAILS:
        content = SECTION_DETAILS[data]
        # زرار رجوع فخم
        back_btn = [[Button.inline("⪼ رجــوع للقائمــة ⪻", data="main_menu")]]
        
        await event.edit(content, buttons=back_btn)
    else:
        await event.answer("⚠️ القسم ده لسه تحت الإنشاء!", alert=True)


# ==========================================
# 4️⃣ الأوامر النصية المباشرة (.م1 .م2)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.م(\d+)"))
async def direct_text_section(event):
    # نستخرج الرقم
    num = event.pattern_match.group(1)
    key = f"m{num}"
    
    if key in SECTION_DETAILS:
        # نعرض النص بس بدون زراير
        await event.edit(SECTION_DETAILS[key])
    else:
        # الصمت لغة العظماء (تجاهل لو الرقم غلط)
        return