import asyncio
import os
from zlzl import zedub
from zlzl.utils import admin_cmd

async def delete_old_backups():
    """دالة تقوم بالبحث عن نسخ قاعدة البيانات القديمة في الرسائل المحفوظة وحذفها"""
    async for msg in zedub.iter_messages("me", search="#ZTELE_DB_BACKUP"):
        try:
            await msg.delete()
        except Exception:
            pass

# أمر يدوي: .رفع_القاعدة (أو حسب بادئة سورس زلزال/زدثون)
@zedub.on(admin_cmd(pattern="رفع_القاعدة"))
async def backup_db_cmd(event):
    await event.edit("🔄 **جاري تحديث قاعدة البيانات في الرسائل المحفوظة...**")
    if os.path.exists("ztele.db"):
        # 1. مسح النسخ القديمة
        await delete_old_backups()
        
        # 2. رفع النسخة الجديدة
        await zedub.send_file(
            "me", 
            "ztele.db", 
            caption="#ZTELE_DB_BACKUP\n\n✅ نسخة احتياطية (تم تحديثها يدوياً).\n**هذا هو الملف الوحيد الذي تحتاجه.**"
        )
        await event.edit("✅ **تم تحديث قاعدة البيانات بنجاح!** (تم حذف النسخة القديمة)")
    else:
        await event.edit("❌ **لم يتم العثور على ملف قاعدة البيانات!**")

# مهمة تعمل في الخلفية للرفع التلقائي كل ساعة
async def auto_backup():
    while True:
        await asyncio.sleep(3600)  # 3600 ثانية = ساعة كاملة (يمكنك تقليلها لو أردت)
        if os.path.exists("ztele.db"):
            try:
                # 1. مسح النسخ القديمة بصمت
                await delete_old_backups()
                
                # 2. رفع النسخة الجديدة بصمت
                await zedub.send_file(
                    "me", 
                    "ztele.db", 
                    caption="#ZTELE_DB_BACKUP\n\n🔄 نسخة احتياطية تلقائية.\n**تم الرفع بواسطة نظام التحديث التلقائي.**"
                )
            except Exception as e:
                print(f"فشل الرفع التلقائي للقاعدة: {e}")

# تشغيل المهمة التلقائية بمجرد اشتغال البوت
zedub.loop.create_task(auto_backup())