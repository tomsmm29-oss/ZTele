import asyncio
from telethon import functions
from zlzl import zedub
from zlzl.core.managers import edit_delete
from zlzl.sql_helper import pmpermit_sql
from zlzl.sql_helper.globals import addgvar, delgvar, gvarstatus

# ----------------------------------------------------------------
# رابط القناة ليظهر الاسم باللون الأزرق
# يمكنك تغيير الرابط https://t.me/ZThon إلى رابط قناتك أو حسابك
ZED_LINK = "https://t.me/ZThon"
# المتغير الذي يحمل الاسم المزخرف والرابط المخفي
Z_LOGO = f"[𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁]({ZED_LINK})"
# ----------------------------------------------------------------

@zedub.zed_cmd(pattern="قفل الخاص$")
async def strict_lock(event):
    """
    تفعيل وضع الحماية الصارم (الحظر الفوري).
    """
    if gvarstatus("strict_pm_lock"):
        return await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔒 الدروع تعمل بالفعل .. الخاص مغلق.**")
    
    addgvar("strict_pm_lock", "active")
    
    # رسالة التفعيل المطلوبة
    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔒 تم تشغيل الدروع .. الخاص مغلق.**")


@zedub.zed_cmd(pattern="فتح الخاص$")
async def strict_unlock(event):
    """
    تعطيل وضع الحماية الصارم.
    """
    if not gvarstatus("strict_pm_lock"):
        return await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔓 الدروع متوقفة بالفعل .. الخاص مفتوح.**")
    
    delgvar("strict_pm_lock")
    
    # رسالة الإيقاف المطلوبة
    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔓 تم إيقاف الدروع .. الخاص مفتوح.**")


@zedub.zed_handler(incoming=True, func=lambda e: e.is_private)
async def strict_block_action(event):
    """
    مراقب الرسائل: يحظر فوراً إذا كان الوضع مفعلاً والشخص غير مصرح له.
    """
    # 1. إذا لم يكن وضع القفل الصارم مفعلاً، لا تفعل شيئاً
    if gvarstatus("strict_pm_lock") is None:
        return

    sender = await event.get_sender()
    chat_id = event.chat_id

    # 2. استثناءات (لا تحظر نفسك، البوتات، أو الأشخاص المسموح لهم سابقاً)
    if sender.is_self or sender.bot or sender.verified:
        return
    
    if pmpermit_sql.is_approved(chat_id):
        return

    # 3. رسالة الحظر الفخمة والجدية
    block_msg = (
        f"**🖥┊نظام الحماية {Z_LOGO}**\n\n"
        "**🔒 الخاص مقفل (Restricted Area)**\n"
        "**🚫 عذراً.. تم حظرك تلقائياً، لا تقم بالمراسلة.**\n"
        "**⚠️ 𝗕𝗹𝗼𝗰𝗸𝗲𝗱.**"
    )

    try:
        # إرسال التحذير
        await event.reply(block_msg, link_preview=False)
        
        # انتظار لحظة صغيرة جداً لضمان ظهور الرسالة قبل الحظر
        await asyncio.sleep(0.5)
        
        # تنفيذ الحظر
        await event.client(functions.contacts.BlockRequest(chat_id))
    except Exception as e:
        print(f"Error in Strict Block: {e}")
