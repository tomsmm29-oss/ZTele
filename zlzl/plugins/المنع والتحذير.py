import re
import html
import json

from telethon.utils import get_display_name
from telethon.tl.types import (
    MessageMediaDocument,
    MessageMediaPhoto,
    DocumentAttributeSticker,
)

from . import zedub, BOTLOG_CHATID
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper import blacklist_sql as spl
from ..sql_helper import warns_sql as sql
from ..utils import is_admin

logger = logging.getLogger(__name__)

# ================================================================================= #
# ====================== دالة استخراج جبارة متوافقة مع 2026 ======================= #
# ================================================================================= #

def get_media_id(msg):
    """
    ترجع:
    - media_id
    - set_id (حزمة الملصقات)
    """

    if not msg:
        return None, None

    media_id = None
    set_id = None

    # ========================================================================== #
    # الطريقة 1 : document/photo المباشر
    # ========================================================================== #
    try:
        if getattr(msg, "document", None):
            media_id = str(msg.document.id)

        if getattr(msg, "photo", None):
            media_id = str(msg.photo.id)
    except:
        pass

    # ========================================================================== #
    # الطريقة 2 : media الحديثة 2026
    # ========================================================================== #
    try:
        media = getattr(msg, "media", None)

        if isinstance(media, MessageMediaDocument):
            if getattr(media, "document", None):
                media_id = str(media.document.id)

        if isinstance(media, MessageMediaPhoto):
            if getattr(media, "photo", None):
                media_id = str(media.photo.id)
    except:
        pass

    # ========================================================================== #
    # الطريقة 3 : file object
    # ========================================================================== #
    try:
        file_obj = getattr(msg, "file", None)

        if file_obj and getattr(file_obj, "id", None):
            media_id = str(file_obj.id)
    except:
        pass

    # ========================================================================== #
    # الطريقة 4 : sticker object
    # ========================================================================== #
    try:
        sticker = getattr(msg, "sticker", None)

        if sticker and getattr(sticker, "id", None):
            media_id = str(sticker.id)
    except:
        pass

    # ========================================================================== #
    # الطريقة 5 : attributes extraction
    # ========================================================================== #
    try:
        document = getattr(msg, "document", None)

        if document:
            attrs = getattr(document, "attributes", [])

            for attr in attrs:
                if isinstance(attr, DocumentAttributeSticker):
                    media_id = str(document.id)

                    # ===== استخراج الحزمة =====
                    if getattr(attr, "stickerset", None):

                        try:
                            if getattr(attr.stickerset, "id", None):
                                set_id = f"set_{attr.stickerset.id}"
                        except:
                            pass
    except:
        pass

    # ========================================================================== #
    # الطريقة 6 : to_dict()
    # ========================================================================== #
    try:
        data = msg.to_dict()

        media = data.get("media")

        if media:

            # document
            if media.get("document"):
                media_id = str(media["document"]["id"])

                attrs = media["document"].get("attributes", [])

                for attr in attrs:
                    if attr.get("_") == "DocumentAttributeSticker":

                        sticker_set = attr.get("stickerset")

                        if sticker_set and sticker_set.get("id"):
                            set_id = f"set_{sticker_set['id']}"

            # photo
            if media.get("photo"):
                media_id = str(media["photo"]["id"])

    except:
        pass

    # ========================================================================== #
    # الطريقة 7 : JSON الخام
    # ========================================================================== #
    try:
        raw = json.loads(msg.to_json())

        media = raw.get("media")

        if media:

            if media.get("document"):
                media_id = str(media["document"]["id"])

                attrs = media["document"].get("attributes", [])

                for attr in attrs:

                    if attr.get("_") == "DocumentAttributeSticker":

                        sticker_set = attr.get("stickerset")

                        if sticker_set:

                            # الطريقة الأولى للحزمة
                            if sticker_set.get("id"):
                                set_id = f"set_{sticker_set['id']}"

                            # الطريقة الثانية للحزمة
                            elif sticker_set.get("short_name"):
                                set_id = f"setname_{sticker_set['short_name']}"

                            # الطريقة الثالثة للحزمة
                            elif sticker_set.get("access_hash"):
                                set_id = f"sethash_{sticker_set['access_hash']}"

            if media.get("photo"):
                media_id = str(media["photo"]["id"])

    except:
        pass

    return media_id, set_id


@zedub.zed_cmd(incoming=True)
async def on_new_message(event):
    snips = spl.get_chat_blacklist(event.chat_id)

    if not snips:
        return

    # التحقق من أن المستخدم مشرف فقط إذا كانت الدردشة ليست خاصة
    if not event.is_private:
        zthonadmin = await is_admin(
            event.client,
            event.chat_id,
            event.client.uid
        )

        if not zthonadmin:
            return

    # استخراج المعرفات
    media_id, set_id = get_media_id(event.message)

    name = event.raw_text

    for snip in snips:

        # ===================================================== #
        # منع الميديا المباشرة
        # ===================================================== #
        if media_id and snip == media_id:
            try:
                await event.delete()
                break
            except:
                pass

        # ===================================================== #
        # منع حزمة الملصقات بالكامل
        # ===================================================== #
        if set_id and snip == set_id:
            try:
                await event.delete()
                break
            except:
                pass

        # ===================================================== #
        # منع النصوص
        # ===================================================== #
        if (
            name
            and not snip.isdigit()
            and not snip.startswith("set_")
            and not snip.startswith("setname_")
            and not snip.startswith("sethash_")
        ):

            pattern = f"( |^|[^\\w]){re.escape(snip)}( |$|[^\\w])"

            if re.search(pattern, name, flags=re.IGNORECASE):

                try:
                    await event.delete()

                except Exception:

                    if not event.is_private:
                        await event.client.send_message(
                            BOTLOG_CHATID,
                            f"**⎉╎عـذراً عـزيـزي مـالك البـوت\n⎉╎ليست لدي صلاحية الحذف في** {get_display_name(await event.get_chat())}.\n**⎉╎لذا لن يتم إزالة الكلمات الممنوعـه في تلك الدردشـه ؟!**",
                        )

                        for word in snips:
                            spl.rm_from_blacklist(
                                event.chat_id,
                                word.lower()
                            )

                break


@zedub.zed_cmd(pattern="منع(?:\s|$)([\s\S]*)")
async def _(event):

    # إعفاء الخاص من شرط الإشراف
    if not event.is_private:

        zthonadmin = await is_admin(
            event.client,
            event.chat_id,
            event.client.uid
        )

        if not zthonadmin:
            return await edit_or_reply(
                event,
                "**⎉╎عذراً، يجب أن أمتلك صلاحية مشرف هنا لمنع الأشياء!**"
            )

    reply_msg = await event.get_reply_message()

    text = event.pattern_match.group(1)

    to_blacklist = []

    # استخراج الميديا أو الحزمة
    if reply_msg:

        m_id, set_id = get_media_id(reply_msg)

        if m_id:
            to_blacklist.append(m_id)

        elif set_id:
            to_blacklist.append(set_id)

        elif reply_msg.raw_text:
            to_blacklist.append(reply_msg.raw_text.strip())

    if text:
        to_blacklist.extend(
            [
                trigger.strip()
                for trigger in text.split("\n")
                if trigger.strip()
            ]
        )

    if not to_blacklist:
        return await edit_or_reply(
            event,
            "**⎉╎يجب الرد على (صورة/ملصق/نص) أو كتابة الكلمة لمنعها !**"
        )

    for trigger in to_blacklist:

        if trigger:
            spl.add_to_blacklist(
                event.chat_id,
                trigger.lower()
            )

    await edit_or_reply(
        event,
        f"**⎉╎تم اضافة (** {len(to_blacklist)} **)**\n**⎉╎الى قائمة الممنوعـات هنـا .. بنجـاح ✓**",
    )


@zedub.zed_cmd(pattern="الغاء منع(?:\s|$)([\s\S]*)")
async def _(event):

    if not event.is_private:

        zthonadmin = await is_admin(
            event.client,
            event.chat_id,
            event.client.uid
        )

        if not zthonadmin:
            return await edit_or_reply(
                event,
                "**⎉╎عذراً، يجب أن أمتلك صلاحية مشرف هنا!**"
            )

    reply_msg = await event.get_reply_message()

    text = event.pattern_match.group(1)

    to_unblacklist = []

    if reply_msg:

        m_id, set_id = get_media_id(reply_msg)

        if m_id:
            to_unblacklist.append(m_id)

        elif set_id:
            to_unblacklist.append(set_id)

        elif reply_msg.raw_text:
            to_unblacklist.append(reply_msg.raw_text.strip())

    if text:
        to_unblacklist.extend(
            [
                trigger.strip()
                for trigger in text.split("\n")
                if trigger.strip()
            ]
        )

    if not to_unblacklist:
        return await edit_or_reply(
            event,
            "**⎉╎يجب الرد على الميديا الممنوعة أو كتابة الكلمة لالغاء منعها !**"
        )

    successful = sum(
        bool(
            spl.rm_from_blacklist(
                event.chat_id,
                trigger.lower()
            )
        )
        for trigger in to_unblacklist
    )

    await edit_or_reply(
        event,
        f"**⎉╎تم حذف (** {successful} / {len(to_unblacklist)} **)**\n**⎉╎من قائمة الممنوعـات هنـا .. بنجـاح ✓**"
    )


@zedub.zed_cmd(pattern="قائمة المنع$")
async def _(event):

    all_blacklisted = spl.get_chat_blacklist(event.chat_id)

    OUT_STR = "**⎉╎قائمة الممنوعـات هنـا هـي :\n**"

    if len(all_blacklisted) > 0:

        for trigger in all_blacklisted:

            if trigger.isdigit():
                OUT_STR += f"- (ميديا/ملصق) : `{trigger}` \n"

            elif (
                trigger.startswith("set_")
                or trigger.startswith("setname_")
                or trigger.startswith("sethash_")
            ):
                OUT_STR += f"- (حزمة ملصقات) : `{trigger}` \n"

            else:
                OUT_STR += f"- {trigger} \n"

    else:
        OUT_STR = "**⎉╎لم يتم اضافة ممنوعـات هنـا بعـد ؟!**"

    await edit_or_reply(event, OUT_STR)


@zedub.zed_cmd(pattern="قائمه المنع$")
async def _(event):

    all_blacklisted = spl.get_chat_blacklist(event.chat_id)

    OUT_STR = "**⎉╎قائمة الممنوعـات هنـا هـي :\n**"

    if len(all_blacklisted) > 0:

        for trigger in all_blacklisted:

            if trigger.isdigit():
                OUT_STR += f"- (ميديا/ملصق) : `{trigger}` \n"

            elif (
                trigger.startswith("set_")
                or trigger.startswith("setname_")
                or trigger.startswith("sethash_")
            ):
                OUT_STR += f"- (حزمة ملصقات) : `{trigger}` \n"

            else:
                OUT_STR += f"- {trigger} \n"

    else:
        OUT_STR = "**⎉╎لم يتم اضافة ممنوعـات هنـا بعـد ؟!**"

    await edit_or_reply(event, OUT_STR)


# ================================================================================================ #
# =========================================التحذيرات================================================= #
# ================================================================================================ #

@zedub.zed_cmd(pattern="تحذير(?:\s|$)([\s\S]*)")
async def _(event):

    warn_reason = event.pattern_match.group(1)

    if not warn_reason:
        warn_reason = "**⪼ لايوجـد سبب 🗒**"

    reply_message = await event.get_reply_message()

    if not reply_message:
        return await edit_delete(
            event,
            "**⎉╎بالـرد ع المستخـدم لـ تحذيـره ☻**"
        )

    limit, soft_warn = sql.get_warn_setting(event.chat_id)

    num_warns, reasons = sql.warn_user(
        reply_message.sender_id,
        event.chat_id,
        warn_reason
    )

    if num_warns >= limit:

        sql.reset_warns(
            reply_message.sender_id,
            event.chat_id
        )

        if soft_warn:

            logger.info("TODO: طرد المستخدم")

            reply = (
                "**⎉╎بسبب تخطي التحذيـرات الـ {} ،**\n"
                "**⎉╎يجب طـرد المستخـدم! ⛔️**"
            ).format(limit, reply_message.sender_id)

        else:

            logger.info("TODO: حظر المستخدم")

            reply = (
                "**⎉╎بسبب تخطي التحذيـرات الـ {} ،**\n"
                "**⎉╎يجب حظـر المستخـدم! ⛔️**"
            ).format(limit, reply_message.sender_id)

    else:

        reply = (
            "**⎉╎[ المستخدم 👤](tg://user?id={}) **\n"
            "**⎉╎لديـه {}/{} تحذيـرات .. احـذر!**"
        ).format(
            reply_message.sender_id,
            num_warns,
            limit
        )

        if warn_reason:
            reply += "\n**⎉╎سبب التحذير الأخير **\n{}".format(
                html.escape(warn_reason)
            )

    await edit_or_reply(event, reply)


@zedub.zed_cmd(pattern="التحذيرات")
async def _(event):

    reply_message = await event.get_reply_message()

    if not reply_message:
        return await edit_delete(
            event,
            "**⎉╎بالـرد ع المستخـدم للحصول ع تحذيراتـه ☻**"
        )

    result = sql.get_warns(
        reply_message.sender_id,
        event.chat_id
    )

    if not result or result[0] == 0:
        return await edit_or_reply(
            event,
            "**⎉╎هـذا المستخـدم ليس لديه أي تحذيـرات! ツ**"
        )

    num_warns, reasons = result

    limit, soft_warn = sql.get_warn_setting(event.chat_id)

    if not reasons:
        return await edit_or_reply(
            event,
            "**⎉╎[ المستخدم 👤](tg://user?id={}) **\n"
            "**⎉╎لديـه {}/{} تحذيـرات ، **\n"
            "**⎉╎لكـن لا توجـد اسباب ؟!**".format(
                num_warns,
                limit
            ),
        )

    text = (
        "**⎉╎المستخـدم لديه {}/{} تحذيـرات ، **\n"
        "**⎉╎للأسباب : ↶**"
    ).format(num_warns, limit)

    text += "\r\n"
    text += reasons

    await event.edit(text)


@zedub.zed_cmd(pattern="حذف التحذيرات(?: |$)(.*)")
async def _(event):

    reply_message = await event.get_reply_message()

    sql.reset_warns(
        reply_message.sender_id,
        event.chat_id
    )

    await edit_or_reply(
        event,
        "**⎉╎تم إعـادة ضبط التحذيـرات! .. بنجـاح**"
    )