# 🚬 ZThon Handler - الكود ده مسؤول عن الربط والتشغيل
# By Mikey & Kalvari - The Stoner Devs 🍁
# حط الملف ده جوه مجلد plugins

from telethon import events, Button
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS

# 🚬 دالة هندسة الزراير (Pagination Logic)
def get_menu_buttons(page):
    # قائمة الأرقام الفخمة (25 زرار)
    all_buttons = [
        "❶", "❷", "❸", "❹", "❺", "❻", 
        "❼", "❽", "❾", "❿", "⓫", "⓬",
        "⓭", "⓮", "⓯", "⓰", "⓱", "⓲", 
        "⓳", "⓴", "㉑", "㉒", "㉓", "㉔", "㉕"
    ]

    # تقسيم الصفحات (12 زرار في الصفحة)
    max_per_page = 12
    start = (page - 1) * max_per_page
    end = start + max_per_page
    
    # قص الأزرار المطلوبة للصفحة الحالية
    current_page_icons = all_buttons[start:end]

    # بناء الصفوف (3 زراير في الصف)
    rows = []
    temp_row = []
    
    for i, icon in enumerate(current_page_icons):
        # حساب الرقم الحقيقي للقسم (m1, m2, etc.)
        real_index = start + i + 1
        callback_data = f"m{real_index}"
        
        # الزرار العريض
        temp_row.append(Button.inline(f" {icon} ", data=callback_data))
        
        # لو الصف كمل 3، ارفعه وابدأ صف جديد
        if len(temp_row) == 3:
            rows.append(temp_row)
            temp_row = []
    
    # لو فيه زراير لسه مكملتش صف (بواقي)، ضيفهم
    if temp_row:
        rows.append(temp_row)

    # 🚬 زراير التنقل (التالي - الإغلاق - السابق) بترتيب فخم
    nav_buttons = []
    
    # زرار السابق (يظهر لو إحنا مش في الصفحة الأولى)
    if page > 1:
        nav_buttons.append(Button.inline("⪼ الســابق ⪻", data=f"page_{page-1}"))
    else:
        # زرار "منظر" بس عشان يحفظ التوازن (اختياري، لو مش عايزه شيله)
        nav_buttons.append(Button.inline("❨ القائمــة ❩", data="dummy"))

    # زرار الإغلاق (في النص أو الترتيب حسب الزوق، هنا خليته في النص)
    nav_buttons.append(Button.inline("❎ اغــلاق", data="close"))

    # زرار التالي (يظهر لو لسه فيه أقسام)
    if end < len(all_buttons):
        nav_buttons.append(Button.inline("⪼ التــالي ⪻", data=f"page_{page+1}"))
    else:
        # زرار "منظر" للنهاية
        nav_buttons.append(Button.inline("❨ النهايــة ❩", data="dummy"))

    rows.append(nav_buttons)
    return rows

# 1️⃣ معالج الأمر النصي (.الاوامر) - بداية الليلة
@zthon.on(events.NewMessage(pattern=r"\.الاوامر"))
async def start_menu(event):
    # جلب اسم المستخدم للفخامة
    sender = await event.client.get_me()
    name = sender.first_name if sender.first_name else "ZThon"
    
    # سحب النص من الملف 2
    menu_text = MAIN_MENU.format(name=name)
    
    # عرض الصفحة الأولى
    await event.edit(menu_text, buttons=get_menu_buttons(1))


# 2️⃣ معالج الضغطات (Callback Query) - المخ المدبر
@zthon.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode('utf-8')
    
    # ❌ زرار الإغلاق
    if data == "close":
        await event.delete()
        return
    
    # 🤡 زرار المنظر (Dummy)
    if data == "dummy":
        await event.answer(" انت هنا بالفعل✔️", cache_time=1)
        return

    # 🔄 التنقل بين الصفحات
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        sender = await event.client.get_me()
        name = sender.first_name if sender.first_name else "ZThon"
        menu_text = MAIN_MENU.format(name=name)
        
        await event.edit(menu_text, buttons=get_menu_buttons(page))
        return

    # 🔙 الرجوع للقائمة الرئيسية (من داخل القسم)
    if data == "main_menu":
        sender = await event.client.get_me()
        name = sender.first_name if sender.first_name else "ZThon"
        menu_text = MAIN_MENU.format(name=name)
        await event.edit(menu_text, buttons=get_menu_buttons(1))
        return

    # 📄 فتح الأقسام (m1, m2... m25)
    if data in SECTION_DETAILS:
        # سحب النص من الملف 3
        content = SECTION_DETAILS[data]
        
        # زرار الرجوع الفخم أسفل النص
        back_btn = [[Button.inline("⪼ رجــوع للقائمــة ⪻", data="main_menu")]]
        
        await event.edit(content, buttons=back_btn)
    else:
        await event.answer("هذا القسم غير موجود✔️", alert=True)


# 3️⃣ معالج الأوامر النصية (.م1 .م2) - التحديث الصامت 🤫
@zthon.on(events.NewMessage(pattern=r"\.م(\d+)"))
async def text_section_handler(event):
    num_str = event.pattern_match.group(1)
    key = f"m{num_str}"
    
    # هنا الشرط القاتل: لو موجود هات، لو مش موجود اخرس.
    if key in SECTION_DETAILS:
        await event.edit(SECTION_DETAILS[key])
    else:
        # الصمت لغة العظماء.. ولا كأنه شاف حاجة
        return