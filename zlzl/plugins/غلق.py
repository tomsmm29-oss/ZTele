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


@zedub.zed_cmd(pattern="^[.,]غلق (الفويس|الملفات|الوسائط|الملصقات)$")
async def lock_zed(event):
    lock_name = event.pattern_match.group(1)
    gvar_key = f"{event.chat_id}_{LOCK_TYPES[lock_name]}"

    if gvarstatus(gvar_key):
        return await edit_or_reply(
            event, f"**•❐• عـذراً .. {lock_name} مـغـلقـة بـالـفـعـل**"
        )

    addgvar(gvar_key, "true")
    await edit_or_reply(
        event, f"**•❐• تـم غـلـق {lock_name} بـنجـاح فـي هـذه الـدردشـة**"
    )


@zedub.zed_cmd(pattern="^[.,]الغاء قفل (الفويس|الملفات|الوسائط|الملصقات)$")
async def unlock_zed(event):
    lock_name = event.pattern_match.group(1)
    gvar_key = f"{event.chat_id}_{LOCK_TYPES[lock_name]}"

    if not gvarstatus(gvar_key):
        return await edit_or_reply(
            event, f"**•❐• عـذراً .. {lock_name} غـيـر مـقـفـولـة بـالـفـعـل**"
        )

    delgvar(gvar_key)
    await edit_or_reply(
        event, f"**•❐• تـم الـغـاء قـفـل {lock_name} بـنجـاح فـي هـذه الـدردشـة**"
    )


# --- المحرك الذكي للحذف التلقائي ---


@zedub.on(incoming=True)
async def watcher(event):
    if not event.chat_id:
        return

    # 1. فحص قفل الفويس (الرسائل الصوتية)
    if event.voice:
        if gvarstatus(f"{event.chat_id}_v_lock"):
            try:
                await event.delete()
            except:
                pass

    # 2. فحص قفل الملصقات
    elif event.sticker:
        if gvarstatus(f"{event.chat_id}_s_lock"):
            try:
                await event.delete()
            except:
                pass

    # 3. فحص قفل الوسائط (صور، فيديوهات)
    elif event.photo or event.video:
        if gvarstatus(f"{event.chat_id}_m_lock"):
            try:
                await event.delete()
            except:
                pass

    # 4. فحص قفل الملفات (المستندات)
    elif event.document and not (event.voice or event.sticker or event.video):
        if gvarstatus(f"{event.chat_id}_f_lock"):
            try:
                await event.delete()
            except:
                pass
