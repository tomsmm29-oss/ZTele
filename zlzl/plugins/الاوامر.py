# update by mikey 👉🏿✔️🤏🏿
# 🚬 ZThon Handler - Final Luxury Version
# By Mikey & Kalvari 🍁
# المسار: zlzl/plugins/الاوامر.py

from telethon import events, Button
from zlzl import zedub

# تعريف الاختصار
zthon = zedub 

# استدعاء الملفات الخارجية
from zlzl.zthon_texts import MAIN_MENU
from zlzl.zthon_strings import SECTION_DETAILS

# 🚬 دالة هندسة الزراير (تم توحيد الفخامة السوداء)
def get_menu_buttons(page):
    # تم تعديل الأرقام بعد 20 لتكون سوداء وثقيلة دمجاً 
    all_buttons = [
        "❶", "❷", "❸", "❹", "❺", "❻", 
        "❼", "❽", "❾", "❿", "⓫", "⓬",
        "⓭", "⓮", "⓯", "⓰", "⓱", "⓲", 
        "⓳", "⓴", "❷❶", "❷❷", "❷❸", "❷❹", "❷❺"
    ]

    max_per_page = 12
    start = (page - 1) * max_per_page
    end = start + max_per_page
    current_page_icons = all_buttons[start:end]

    rows = []
    temp_row = []
    
    for i, icon in enumerate(current_page_icons):
        real_index = start + i + 1
        callback_data = f"m{real_index}"
        # مسافات حول الأيقونة لزيادة العرض والهيبة
        temp_row.append(Button.inline(f" {icon} ", data=callback_data))
        
        if len(temp_row) == 3:
            rows.append(temp_row)
            temp_row = []
    
    if temp_row:
        rows.append(temp_row)

    nav_buttons = []
    
    # زرار السابق
    if page > 1:
        nav_buttons.append(Button.inline("⪼ الســابق ⪻", data=f"page_{page-1}"))
    else:
        # زرار منظر (بداية القائمة)
        nav_buttons.append(Button.inline("❨ الرئيسيــة ❩", data="dummy_start"))

    # زرار الإغلاق
    nav_buttons.append(Button.inline("❎ اغــلاق", data="close"))

    # زرار التالي
    if end < len(all_buttons):
        nav_buttons.append(Button.inline("⪼ التــالي ⪻", data=f"page_{page+1}"))
    else:
        # زرار منظر (نهاية القائمة)
        nav_buttons.append(Button.inline("❨ النهايــة ❩", data="dummy_end"))

    rows.append(nav_buttons)
    return rows


# ==========================================
# 1️⃣ معالج الأمر النصي الصافي (.اوامري)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.اوامري"))
async def text_only_menu(event):
    sender = await event.client.get_me()
    name = sender.first_name if sender.first_name else "ZThon"
    
    menu_text = MAIN_MENU.format(name=name)
    await event.edit(menu_text)


# ==========================================
# 2️⃣ معالج الأمر المتطور (.الاوامر)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.الاوامر"))
async def inline_menu_handler(event):
    sender = await event.client.get_me()
    name = sender.first_name if sender.first_name else "ZThon"
    
    menu_text = MAIN_MENU.format(name=name)
    
    try:
        await event.edit(menu_text, buttons=get_menu_buttons(1))
    except Exception:
        await event.edit(menu_text)


# ==========================================
# 3️⃣ معالج الضغطات (Callback Query)
# ==========================================
@zthon.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode('utf-8')
    
    # ❌ إغلاق
    if data == "close":
        await event.delete()
        return
    
    # ⚠️ رسائل التنبيه الرسمية (بدل الهزار)
    if data == "dummy_start":
        await event.answer("⚠️ أنت في الصفحة الأولى بالفعل", cache_time=1)
        return
    
    if data == "dummy_end":
        await event.answer("⚠️ لا توجد صفحات أخرى", cache_time=1)
        return

    # 🔄 التنقل
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        sender = await event.client.get_me()
        name = sender.first_name if sender.first_name else "ZThon"
        menu_text = MAIN_MENU.format(name=name)
        
        await event.edit(menu_text, buttons=get_menu_buttons(page))
        return

    # 🔙 الرجوع
    if data == "main_menu":
        sender = await event.client.get_me()
        name = sender.first_name if sender.first_name else "ZThon"
        menu_text = MAIN_MENU.format(name=name)
        await event.edit(menu_text, buttons=get_menu_buttons(1))
        return

    # 📄 عرض الأقسام
    if data in SECTION_DETAILS:
        content = SECTION_DETAILS[data]
        back_btn = [[Button.inline("⪼ رجــوع للقائمــة ⪻", data="main_menu")]]
        
        await event.edit(content, buttons=back_btn)
    else:
        # رسالة خطأ رسمية
        await event.answer("⚠️ هذا القسم غير متاح حالياً", alert=True)


# ==========================================
# 4️⃣ معالج الأوامر النصية (.م1 .م2)
# ==========================================
@zthon.on(events.NewMessage(pattern=r"\.م(\d+)"))
async def direct_text_section(event):
    num_str = event.pattern_match.group(1)
    key = f"m{num_str}"
    
    if key in SECTION_DETAILS:
        await event.edit(SECTION_DETAILS[key])
    else:
        return