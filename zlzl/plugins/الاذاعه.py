import base64
import contextlib
from asyncio import sleep

from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.utils import get_display_name

# --- تصحيح المسارات والحقن النسبي ---
from . import zedub
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format, get_user_from_event

# محاولة استدعاء SQL، لو مش موجود نتخطاه عشان الكود ما يوقفش
try:
    from ..sql_helper import broadcast_sql as sql
except ImportError:
    sql = None

try:
    from . import BOTLOG, BOTLOG_CHATID
except ImportError:
    BOTLOG = False
    BOTLOG_CHATID = None

plugin_category = "البوت"
LOGS = logging.getLogger(__name__)

ZED_BLACKLIST = [
    -1001236815136,
    -1001614012587,
]

# تم زرع الآيدي الخاص بك مع المطورين
DEVZ = [
    1111565135,
    6114298715,
    8241311871, 
]

ZelzalPRO_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗭𝗘𝗗𝗧𝗵𝗼𝗻 𝗖𝗼𝗻𝗳𝗶𝗴 - اوامـر الاذا؏ـــة](t.me/ZEDthon) 𓆪\n\n"
    "**⎞𝟏⎝** `.للكروبات`  / `.للمجموعات`\n"
    "**بالــࢪد ؏ــلى ࢪســالة نصيــه او وسـائــط تحتهــا نــص**\n"
    "**- لـ اذاعـة رسـالة او ميديـا لكـل المجموعـات اللي انت موجود فيهـا . .**\n\n\n"
    "**⎞𝟐⎝** `.للخاص`\n"
    "**بالــࢪد ؏ــلى ࢪســالة نصيــه او وسـائــط تحتهــا نــص**\n"
    "**- لـ اذاعـة رسـالة او ميديـا لكـل الاشخـاص اللي موجـودين عنـدك خـاص . .**\n\n\n"
    "**⎞𝟑⎝** `.خاص`\n"
    "**الامـر + معرف الشخص + الرسـاله . .**\n"
    " **- ارسـال رسـاله الى الشخص المحدد بدون الدخول للخاص وقراءة الرسـائل . .**\n\n\n"
    "**⎞4⎝** `.للكل`\n"
    "**بالــࢪد ؏ــلى ࢪســالة نصيــه او وسـائــط تحتهــا نــص**\n"
    " **- ارسـال رسـاله اذاعـة الى جميـع اعضـاء مجموعـة محددة .. قم باستخـدام الامـر داخـل المجموعـة . .**\n\n"
    "**⎞5⎝** `.زاجل`\n"
    "**بالــࢪد ؏ــلى ࢪســالة نصيــه او وسـائــط تحتهــا نــص**\n"
    " **- ارسـال رسـاله اذاعـة الى اشخاص محددة 🕊. .**\n\n"
    "\n 𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿](t.me/ZedThon) 𓆪"
)


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="الاذاعه")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalPRO_cmd)


# تم دمج الأمرين (للكروبات وللمجموعات) في دالة واحدة لتوفير الكود
@zedub.zed_cmd(pattern="للكروبات(?: |$)(.*)|للمجموعات(?: |$)(.*)")
async def gcast_group(event):
    # استخراج النص من أي مجموعة (الأولى أو الثانية)
    zedthon = event.pattern_match.group(1) or event.pattern_match.group(2)

    if zedthon: 
        await edit_or_reply(event, "**⎉╎بالـࢪد ؏ــلى ࢪسـالة او وسائـط**")
        return
    elif event.is_reply:
        zelzal = await event.get_reply_message()
    else:
        await edit_or_reply(event, "**⎉╎بالـࢪد ؏ــلى ࢪسـالة او وسائـط**")
        return

    zzz = await edit_or_reply(event, "**⎉╎جـاري الاذاعـه في المجموعـات ...الرجـاء الانتظـار**")
    er = 0
    done = 0

    async for x in event.client.iter_dialogs():
        if x.is_group:
            chat = x.id
            try:
                # تم استبدال borg بـ event.client
                if zelzal.text and not zelzal.media:
                    await event.client.send_message(chat, zelzal.text, link_preview=False)
                    done += 1
                else:
                    # إرسال الميديا مع الكابشن
                    await event.client.send_file(
                        chat,
                        zelzal.media,
                        caption=zelzal.text or "",
                        link_preview=False,
                    )
                    done += 1
            except BaseException:
                er += 1

    await zzz.edit(
        f"**⎉╎تمت الاذاعـه بنجـاح الـى ** `{done}` **من المجموعـات** \n**⎉╎خطـأ في الارسـال الـى ** `{er}` **من المجموعـات**"
    )


@zedub.zed_cmd(pattern="للخاص(?: |$)(.*)")
async def gucast(event):
    zedthon = event.pattern_match.group(1)
    if zedthon: 
        await edit_or_reply(event, "**⎉╎بالـࢪد ؏ــلى ࢪسـالة او وسائـط**")
        return
    elif event.is_reply:
        zelzal = await event.get_reply_message()
    else:
        await edit_or_reply(event, "**⎉╎بالـࢪد ؏ــلى ࢪسـالة او وسائـط**")
        return

    zzz = await edit_or_reply(event, "**⎉╎جـاري الاذاعـه في الخـاص ...الرجـاء الانتظـار**")
    er = 0
    done = 0

    async for x in event.client.iter_dialogs():
        if x.is_user and not x.entity.bot:
            chat = x.id
            try:
                if zelzal.text and not zelzal.media:
                    await event.client.send_message(chat, zelzal.text, link_preview=False)
                    done += 1
                else:
                    await event.client.send_file(
                        chat,
                        zelzal.media,
                        caption=zelzal.text or "",
                        link_preview=False,
                    )
                    done += 1
            except BaseException:
                er += 1

    await zzz.edit(
        f"**⎉╎تمت الاذاعـه بنجـاح الـى ** `{done}` **من الخـاص**\n**⎉╎خطـأ في الارسـال الـى ** `{er}` **من الخـاص**"
    )


@zedub.zed_cmd(pattern="خاص ?(.*)")
async def pmto(event):
    r = event.pattern_match.group(1)
    if not r:
        return await edit_or_reply(event, "**⎉╎يجب وضع المعرف او الايدي مع الرسالة**")

    p = r.split(" ")
    chat_dest = p[0]

    # محاولة تحويل الايدي لرقم لو كان رقمي
    try:
        if chat_dest.isnumeric():
            chat_dest = int(chat_dest)
    except:
        pass

    zelzal = ""
    for i in p[1:]:
        zelzal += i + " "

    if zelzal == "":
        return await edit_or_reply(event, "**⎉╎اكتب الرسالة يا وحش!**")

    try:
        await zedub.send_message(chat_dest, zelzal)
        await event.edit("**⎉╎تـم ارسال الرسـالة بنجـاح ✓**\n**⎉╎بـدون الدخـول للخـاص**")
    except Exception as e:
        await event.edit(f"**⎉╎اووبس .. لقـد حدث خطـأ: {e}**")