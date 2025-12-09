import os
import datetime
from telethon import events

# --- تصحيح المسارات لـ ZThon ---
from . import zedub
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..core.managers import edit_delete, edit_or_reply

# قواميس الأيام
Aljoker_Asbo3 = {
    'Monday': 'الاثنين',
    'Tuesday': 'الثلاثاء',
    'Wednesday': 'الأربعاء',
    'Thursday': 'الخميس',
    'Friday': 'الجمعة',
    'Saturday': 'السبت',
    'Sunday': 'الأحد'
}

@zedub.zed_cmd(pattern="(جلب الصورة|جلب الصوره|ذاتيه|ذاتية)")
async def dato(event):
    if not event.is_reply:
        return await event.edit("..")
    lMl10l = await event.get_reply_message()
    pic = await lMl10l.download_media()
    await zedub.send_file(
        "me",
        pic,
        caption=f"""
- تـم حفظ الصـورة بنجـاح ✓
- غير مبري الذمه اذا استخدمت الامر للابتزاز
- CH: @ZThon
- Dev: @ZThon
  """,
    )
    await event.delete()

@zedub.zed_cmd(pattern="(الذاتية تشغيل|ذاتية تشغيل)")
async def reda(event):
    if gvarstatus ("savepicforme"):
        return await edit_delete(event, "**᯽︙حفظ الذاتيات مفعل وليس بحاجة للتفعيل مجدداً **")
    else:
        addgvar("savepicforme", "reda")
        await edit_delete(event, "**᯽︙تم تفعيل ميزة حفظ الذاتيات بنجاح ✓**")

@zedub.zed_cmd(pattern="(الذاتية تعطيل|ذاتية تعطيل)")
async def Reda_Is_Here(event):
    if gvarstatus ("savepicforme"):
        delgvar("savepicforme")
        return await edit_delete(event, "**᯽︙تم تعطيل حفظ الذاتيات بنجاح ✓**")
    else:
        await edit_delete(event, "**᯽︙انت لم تفعل حفظ الذاتيات لتعطيلها!**")

def joker_unread_media(message):
    return message.media_unread and (message.photo or message.video)

async def Hussein(event, caption):
    media = await event.download_media()
    sender = await event.get_sender()
    sender_id = event.sender_id
    lMl10l_date = event.date.strftime("%Y-%m-%d")
    lMl10l_day = Aljoker_Asbo3[event.date.strftime("%A")]
    await zedub.send_file(
        "me",
        media,
        caption=caption.format(sender.first_name, sender_id, lMl10l_date, lMl10l_day),
        parse_mode="markdown"
    )
    os.remove(media)

# المراقب السري (Watcher) - ZThon Style
@zedub.on(events.NewMessage(func=lambda e: e.is_private and joker_unread_media(e) and e.sender_id != zedub.uid))
async def Reda(event):
    if gvarstatus("savepicforme"):
        caption = """**
           ♡  غير مبري الذمة اذا استعملته للأبتزاز  ♡
♡ تم حفظ الذاتية بنجاح ✓
♡ تم الصنع : @ZThon
♡ أسم المرسل : [{0}](tg://user?id={1})
♡  تاريخ الذاتية : `{2}`
♡  أرسلت في يوم `{3}`
       ♡    ZThon    ♡
        **"""
        await Hussein(event, caption)