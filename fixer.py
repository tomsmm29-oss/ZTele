import os
import random
import re

# مسار الملف الملعون
TARGET_FILE = "zlzl/plugins/الاوامر.py"


def main():
    if not os.path.exists(TARGET_FILE):
        print(f"❌ الملف {TARGET_FILE} غير موجود! تأكد أنك داخل المجلد الصحيح.")
        return

    print(f"🚬 جاري قراءة الملف العملاق {TARGET_FILE}...")

    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. إصلاح الكارثة: zedub.edit -> event.edit
    # هذا اللي يخلي الأزرار تكرش
    fixed_edits = content.count("await zedub.edit(")
    content = content.replace("await zedub.edit(", "await event.edit(")
    print(f"✅ تم تصحيح {fixed_edits} خطأ (zedub.edit).")

    # 2. إصلاح تكرار الدوال (العملية الجراحية الكبرى)
    # سنقوم بتغيير اسم الدالة بناءً على رقم تسلسلي لضمان عدم التكرار

    # عداد للدوال العادية
    cmd_counter = 0
    # عداد لدوال الكول باك (الأزرار)
    callback_counter = 0

    def replace_function_names(match):
        nonlocal cmd_counter, callback_counter

        declaration = match.group(1)  # @zedub.zed_cmd(...) أو @zedub.tgbot.on(...)
        async_def = match.group(2)  # async def
        func_name = match.group(3)  # zed أو zed_handler
        args = match.group(4)  # (event)

        # إذا كانت دالة أمر (zed_cmd)
        if "zed_cmd" in declaration:
            cmd_counter += 1
            new_name = f"zed_command_{cmd_counter}_{random.randint(100,999)}"
            return f"{declaration}\n{async_def} {new_name}{args}"

        # إذا كانت دالة زر (CallbackQuery)
        elif "CallbackQuery" in declaration or "tgbot.on" in declaration:
            callback_counter += 1
            new_name = f"callback_handler_{callback_counter}_{random.randint(100,999)}"
            return f"{declaration}\n{async_def} {new_name}{args}"

        # إذا لم تكن مكررة، اتركها
        return match.group(0)

    # نمط البحث المعقد (يصيد الديكوريتور + تعريف الدالة)
    # هذا النمط يبحث عن السطر اللي فيه @ ثم السطر اللي تحته async def
    pattern = (
        r"(@zedub\.(?:zed_cmd|tgbot\.on).*?)\n\s*(async\s+def)\s+(\w+)\s*(\(.*?\):)"
    )

    # تنفيذ الاستبدال
    content = re.sub(pattern, replace_function_names, content, flags=re.DOTALL)

    print(f"✅ تم تغيير أسماء {cmd_counter} دالة أمر (كانت مكررة).")
    print(f"✅ تم تغيير أسماء {callback_counter} دالة زر (كانت مكررة).")

    # 3. تنظيف إضافي (reply_id)
    if "from ..helpers.utils import reply_id" in content:
        content = content.replace(
            "from ..helpers.utils import reply_id",
            "# from ..helpers.utils import reply_id",
        )
        print("✅ تم تعطيل استيراد reply_id المسبب للمشاكل.")

    # الحفظ
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("-" * 40)
    print("🚀 تم الإصلاح! الملف الآن نظيف وجاهز.")
    print("🔥 نفذ الأمر التالي للرفع:")
    print(
        "git add . && git commit -m 'Ultimate Fix for Orders' && git push origin master"
    )


if __name__ == "__main__":
    main()
