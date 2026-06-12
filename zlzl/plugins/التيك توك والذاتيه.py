from asyncio import sleep

from telethon import events

from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply  # ضفت دي عشان كانت ناقصة
from ..helpers.utils import _format
from ..sql_helper.autopost_sql import get_all_post
from ..sql_helper.globals import gvarstatus

# --- تصحيح المسارات والاستيرادات لـ ZThon ---
from . import zedub

plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)
zedself = True

POSC = gvarstatus("Z_POSC") or "(مم|ذاتية|ذاتيه|جلب الوقتيه)"

# --- تم تغيير الحقوق والنصوص لـ ZThon ---
ZelzalSelf_cmd = (
    "𓆩 [ᯓ 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - حفـظ الذاتيـه 🧧](t.me/ZThon) 𓆪\n\n"
    "**⪼** `.تفعيل الذاتيه`\n"
    "**لـ تفعيـل الحفظ التلقائي للذاتيـه**\n"
    "**سوف يقوم حسابك بحفظ الذاتيه تلقائياً في حافظة حسابك عندما يرسل لك اي شخص ميديـا ذاتيـه**\n\n"
    "**⪼** `.تعطيل الذاتيه`\n"
    "**لـ تعطيـل الحفظ التلقائي للذاتيـه**\n\n"
    "**⪼** `.ذاتيه`\n"
    "**بالـرد ؏ــلى صـوره ذاتيـه لحفظهـا في حال كان امر الحفظ التلقائي معطـل**\n\n\n"
    "**⪼** `.اعلان`\n"
    "**الامـر + الوقت بالدقائق + الرسـاله**\n"
    "**امـر مفيـد لجماعـة التمويـل لـ عمـل إعـلان مـؤقت بالقنـوات**\n\n"
    "\n 𓆩 [𝗭𝗧𝗵𝗼𝗻](t.me/ZThon) 𓆪"
)


@zedub.zed_cmd(pattern="الذاتيه")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalSelf_cmd)


@zedub.zed_cmd(pattern=f"{POSC}(?: |$)(.*)")
async def oho(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالـرد علـى صورة ذاتيـة التدميـر 𓆰...**")
    zzzzl1l = await event.get_reply_message()
    pic = await zzzzl1l.download_media()
    await zedub.send_file(
        "me", pic, caption=f"**⎉╎تم حفـظ الصـورة الذاتيـه .. بنجـاح ☑️𓆰**"
    )
    await event.delete()


@zedub.zed_cmd(pattern="(تفعيل الذاتيه|تفعيل الذاتية)")
async def start_datea(event):
    global zedself
    if zedself:
        return await edit_or_reply(
            event, "**⎉╎حفظ الذاتيـة التلقـائي .. مفعـله مسبقـاً ☑️**"
        )
    zedself = True
    await edit_or_reply(event, "**⎉╎تم تفعيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")


@zedub.zed_cmd(pattern="(تعطيل الذاتيه|تعطيل الذاتية)")
async def stop_datea(event):
    global zedself
    if zedself:
        zedself = False
        return await edit_or_reply(
            event, "**⎉╎تم تعطيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**"
        )
    await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. معطلـه مسبقـاً ☑️**")


@zedub.on(
    events.NewMessage(
        func=lambda e: e.is_private and (e.photo or e.video) and e.media_unread
    )
)
async def sddm(event):
    global zedself
    zelzal = event.sender_id
    malath = zedub.uid
    if zelzal == malath:
        return
    if zedself:
        sender = await event.get_sender()
        await event.get_chat()
        pic = await event.download_media()
        # --- كليشة الحفظ باسم ZThon ---
        await zedub.send_file(
            "me",
            pic,
            caption=f"[ᯓ 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - حفـظ الذاتيـه 🧧](t.me/ZThon) .\n\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n**⌔╎مࢪحبـاً عـزيـزي المـالك 🫂\n⌔╎ تـم حفـظ الذاتيـة تلقائيـاً .. بنجـاح ☑️** ❝\n**⌔╎المـرسـل** {_format.mentionuser(sender.first_name , sender.id)} .",
        )


# Code For T.me/ZThon
@zedub.zed_cmd(pattern="اعلان (\d*) ([\s\S]*)")
async def selfdestruct(destroy):
    zed = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
    message = zed[1]
    ttl = int(zed[0])
    zelzal = ttl * 60  # تعييـن الوقـت بالدقائـق بدلاً من الثـوانـي
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, message)
    await sleep(zelzal)
    await smsg.delete()


# Code For T.me/ZThon
@zedub.zed_cmd(pattern="إعلان (\d*) ([\s\S]*)")
async def selfdestruct(destroy):
    zed = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
    message = zed[1]
    ttl = int(zed[0])
    zelzal = ttl * 60  # تعييـن الوقـت بالدقائـق بدلاً من الثـوانـي
    text = (
        message + f"\n\n**- هذا الاعلان سيتم حذفه تلقـائيـاً بعـد {zelzal} دقائـق ⏳**"
    )
    await destroy.delete()
    smsg = await destroy.client.send_message(destroy.chat_id, text)
    await sleep(zelzal)
    await smsg.delete()


@zedub.on(events.NewMessage(incoming=True))
async def gpost(event):
    if event.is_private:
        return
    chat_id = str(event.chat_id).replace("-100", "")
    channels_set = get_all_post(chat_id)
    if channels_set == []:
        return
    for chat in channels_set:
        if event.media:
            await event.client.send_file(int(chat), event.media, caption=event.text)
        elif not event.media:
            await zedub.send_message(int(chat), event.message)
