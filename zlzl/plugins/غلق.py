from telethon import events

from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import zedub

plugin_category = "الادمن"

# مصفوفة لتحويل الكلمات المفتاحية إلى مفاتيح في قاعدة البيانات
LOCK_TYPES = {
    "الفويس": "v_lock",
    "الملفات": "f_lock",
    "الوسائط": "m_lock",
    "الملصقات": "s_lock",
}


# استخدمنا r"..." و \s+ لمسافة إجبارية و $ للنهاية لمنع التداخل مع الأوامر الأخرى
@zedub.zed_cmd(pattern=r"^[.,]غلق\s+(الفويس|الملفات|الوسائط|الملصقات)$")
async def lock_zed(event):
    lock_name = event.pattern_match.group(1)
    gvar_key = f"{event.chat_id}_{LOCK_TYPES[lock_name]}"

    if gvarstatus(gvar_key):
        return await edit_or_reply(
            event, f"**•❐• عـذراً .. {lock_name} مـغـلقـة بـالـفـعـل هـنـا**"
        )

    addgvar(gvar_key, "true")
    await edit_or_reply(
        event, f"**•❐• تـم غـلـق {lock_name} بـنجـاح فـي هـذه الـدردشـة**"
    )


@zedub.zed_cmd(pattern=r"^[.,]الغاء قفل\s+(الفويس|الملفات|الوسائط|الملصقات)$")
async def unlock_zed(event):
    lock_name = event.pattern_match.group(1)
    gvar_key = f"{event.chat_id}_{LOCK_TYPES[lock_name]}"

    if not gvarstatus(gvar_key):
        return await edit_or_reply(
            event, f"**•❐• عـذراً .. {lock_name} غـيـر مـقـفـولـة بـالـفـعـل هـنـا**"
        )

    delgvar(gvar_key)
    await edit_or_reply(
        event, f"**•❐• تـم الـغـاء قـفـل {lock_name} بـنجـاح فـي هـذه الـدردشـة**"
    )


# --- المحرك الذكي للحذف التلقائي ---
# استخدمنا events.NewMessage لضمان عملها بشكل حقيقي مع كل رسالة جديدة
@zedub.on(events.NewMessage(incoming=True))
async def watcher(event):
    if not event.chat_id:
        return

    chat_id = event.chat_id

    # 1. فحص قفل الملصقات (يشمل الثابت والمتحرك TGS والفيديو WEBM)
    if event.sticker:
        if gvarstatus(f"{chat_id}_s_lock"):
            try:
                await event.delete()
                return  # إيقاف الفحص بعد الحذف
            except:
                pass

    # 2. فحص قفل الفويس (الرسائل الصوتية)
    elif event.voice:
        if gvarstatus(f"{chat_id}_v_lock"):
            try:
                await event.delete()
                return
            except:
                pass

    # 3. فحص قفل الوسائط (صور، فيديوهات، صور متحركة جيف GIF، فيديوهات دائرية)
    elif event.photo or event.video or event.gif or event.video_note:
        if gvarstatus(f"{chat_id}_m_lock"):
            try:
                await event.delete()
                return
            except:
                pass

    # 4. فحص قفل الملفات (المستندات، التطبيقات، الخ)
    # نضعها في النهاية لأن الملصقات والفويس تعتبر برمجياً "مستندات" أيضاً
    elif event.document:
        if gvarstatus(f"{chat_id}_f_lock"):
            try:
                await event.delete()
                return
            except:
                pass
