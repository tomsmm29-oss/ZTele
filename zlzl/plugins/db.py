import asyncio
import os

from zlzl import zedub
from zlzl.utils import admin_cmd

# متغير لحفظ وقت آخر تعديل على قاعدة البيانات
LAST_BACKUP_TIME = 0


async def update_backup_message(manual=False):
    global LAST_BACKUP_TIME
    db_path = "ztele.db"

    # التحقق من وجود الملف
    if not os.path.exists(db_path):
        return False, "❌ **لم يتم العثور على ملف قاعدة البيانات!**"

    # قراءة وقت آخر تعديل لملف قاعدة البيانات
    current_time = os.path.getmtime(db_path)

    # المستشعر الذكي: إذا مافي تغيير، كنسل الرفع التلقائي
    if not manual and current_time <= LAST_BACKUP_TIME:
        return False, "No changes"

    if manual:
        caption = "#ZTELE_DB_BACKUP\n\n✅ تم تحديث قاعدة البيانات يدوياً.\n(يرجى عدم حذف الملف)"
    else:
        caption = "#ZTELE_DB_BACKUP\n\nتم الرفع بواسطة نظام التحديث التلقائي.\n(يرجى عدم حذف الملف)"

    target_msg = None
    # 🔒 حماية 100%: نبحث فقط عن الرسالة اللي فيها الهاشتاج الخاص فينا!
    async for msg in zedub.iter_messages("me", search="#ZTELE_DB_BACKUP", limit=1):
        if msg.document and msg.text and "#ZTELE_DB_BACKUP" in msg.text:
            target_msg = msg
            break

    try:
        if target_msg:
            # إذا لقينا رسالة القاعدة، نعدلها هي فقط
            await zedub.edit_message(
                entity="me",
                message=target_msg.id,
                file=db_path,
                text=caption,
                force_document=True,
            )
        else:
            # إذا ما لقيناها (أول مرة)، نرسل رسالة جديدة تماماً في الأسفل!
            await zedub.send_file("me", db_path, caption=caption, force_document=True)

        # حفظ وقت الرفع الجديد
        LAST_BACKUP_TIME = current_time
        return True, "⌭ **تـم تحديـث قـاعدة البيانـات فـي المحفـوظـات بنجـاح .. ✓**"
    except Exception as e:
        print(f"⚠️ خطأ في رفع قاعدة البيانات: {e}")
        return False, f"⚠️ خطأ: {str(e)}"


# أمر يدوي
@zedub.on(admin_cmd(pattern="رفع_القاعدة"))
async def backup_db_cmd(event):
    await event.edit("⌭ **جـارِ تحديـث قاعـدة البيانـات بصمـت .. 𓄂**")
    success, text = await update_backup_message(manual=True)
    await event.edit(text)


# مهمة الرفع التلقائي
async def auto_backup():
    # محاولة رفع عند التشغيل بعد 15 ثانية
    await asyncio.sleep(15)
    await update_backup_message(manual=False)

    while True:
        await asyncio.sleep(3600)  # كل ساعة
        await update_backup_message(manual=False)


# تشغيل المهمة التلقائية
zedub.loop.create_task(auto_backup())
