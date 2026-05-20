import re
import html
import json

from telethon.utils import get_display_name

from . import zedub, BOTLOG_CHATID
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper import blacklist_sql as spl
from ..sql_helper import warns_sql as sql
from ..utils import is_admin

logger = logging.getLogger(__name__)

# دالة الاستخراج الشاملة بـ 5 طرق جبارة لجلب آيدي الملصقات والصور غصب
def get_media_id(msg):
    if not msg:
        return None

    # الطريقة 1: عبر الكائنات المباشرة لتيليثون (الإصدارات الأحدث)
    try:
        if hasattr(msg, 'document') and msg.document:
            return str(msg.document.id)
        if hasattr(msg, 'photo') and msg.photo:
            return str(msg.photo.id)
    except Exception:
        pass

    # الطريقة 2: عبر كائن media الداخلي
    try:
        if getattr(msg, 'media', None):
            if hasattr(msg.media, 'document') and msg.media.document:
                return str(msg.media.document.id)
            if hasattr(msg.media, 'photo') and msg.media.photo:
                return str(msg.media.photo.id)
    except Exception:
        pass

    # الطريقة 3: عبر القاموس to_dict() (حسب إحداثيات السيرفر الأصلية)
    try:
        m_dict = msg.to_dict()
        if 'media' in m_dict and m_dict['media']:
            if 'document' in m_dict['media'] and 'id' in m_dict['media']['document']:
                return str(m_dict['media']['document']['id'])
            if 'photo' in m_dict['media'] and 'id' in m_dict['media']['photo']:
                return str(m_dict['media']['photo']['id'])
    except Exception:
        pass

    # الطريقة 4: عبر JSON الخام (هذي تفكك الإحداثيات اللي أنت أرسلتها لي وتجيب الـ ID غصب)
    try:
        msg_json = json.loads(msg.to_json())
        if 'media' in msg_json:
            if 'document' in msg_json['media']:
                return str(msg_json['media']['document']['id'])
            if 'photo' in msg_json['media']:
                return str(msg_json['media']['photo']['id'])
    except Exception:
        pass

    # الطريقة 5: التحقق من وجود ملف (file) أو ملصق (sticker) بشكل مباشر
    try:
        if getattr(msg, 'sticker', None) and getattr(msg.sticker, 'id', None):
            return str(msg.sticker.id)
        if getattr(msg, 'file', None) and getattr(msg.file, 'id', None):
            file_id = str(msg.file.id)
            if file_id.isdigit():
                return file_id
    except Exception:
        pass

    return None


@zedub.zed_cmd(incoming=True)
async def on_new_message(event):
    snips = spl.get_chat_blacklist(event.chat_id)
    if not snips:
        return

    # التحقق من أن المستخدم مشرف فقط إذا كانت الدردشة ليست خاصة
    if not event.is_private:
        zthonadmin = await is_admin(event.client, event.chat_id, event.client.uid)
        if not zthonadmin:
            return

    # جلب المعرف بـ 5 طرق
    media_id = get_media_id(event.message)
    name = event.raw_text

    for snip in snips:
        # فحص الملصق/الميديا
        if media_id and snip == media_id:
            try:
                await event.delete()
                break
            except Exception:
                pass 

        # فحص النص
        if name and not snip.isdigit(): 
            pattern = f"( |^|[^\\w]){re.escape(snip)}( |$|[^\\w])"
            if re.search(pattern, name, flags=re.IGNORECASE):
                try:
                    await event.delete()
                except Exception:
                    # التنبيه بعدم وجود صلاحية يرسل بالقروبات فقط وليس الخاص
                    if not event.is_private:
                        await event.client.send_message(
                            BOTLOG_CHATID,
                            f"**⎉╎عـذراً عـزيـزي مـالك البـوت\n⎉╎ليست لدي صلاحية الحذف في** {get_display_name(await event.get_chat())}.\n**⎉╎لذا لن يتم إزالة الكلمات الممنوعـه في تلك الدردشـه ؟!**",
                        )
                        for word in snips:
                            spl.rm_from_blacklist(event.chat_id, word.lower())
                break


@zedub.zed_cmd(pattern="منع(?:\s|$)([\s\S]*)")
async def _(event):
    # إعفاء الخاص من شرط الإشراف
    if not event.is_private:
        zthonadmin = await is_admin(event.client, event.chat_id, event.client.uid)
        if not zthonadmin:
            return await edit_or_reply(event, "**⎉╎عذراً، يجب أن أمتلك صلاحية مشرف هنا لمنع الأشياء!**")

    reply_msg = await event.get_reply_message()
    text = event.pattern_match.group(1)
    to_blacklist = []

    # استخدام الـ 5 طرق لجلب ID الملصق المردود عليه
    if reply_msg:
        m_id = get_media_id(reply_msg)
        if m_id:
            to_blacklist.append(m_id)
        elif reply_msg.text:
            to_blacklist.append(reply_msg.text.strip())

    if text:
        to_blacklist.extend(
            [trigger.strip() for trigger in text.split("\n") if trigger.strip()]
        )

    if not to_blacklist:
        return await edit_or_reply(event, "**⎉╎يجب الرد على (صورة/ملصق/نص) أو كتابة الكلمة لمنعها !**")

    for trigger in to_blacklist:
        if trigger:
            spl.add_to_blacklist(event.chat_id, trigger.lower())

    await edit_or_reply(
        event,
        f"**⎉╎تم اضافة (** {len(to_blacklist)} **)**\n**⎉╎الى قائمة الممنوعـات هنـا .. بنجـاح ✓**",
    )


@zedub.zed_cmd(pattern="الغاء منع(?:\s|$)([\s\S]*)")
async def _(event):
    if not event.is_private:
        zthonadmin = await is_admin(event.client, event.chat_id, event.client.uid)
        if not zthonadmin:
            return await edit_or_reply(event, "**⎉╎عذراً، يجب أن أمتلك صلاحية مشرف هنا!**")

    reply_msg = await event.get_reply_message()
    text = event.pattern_match.group(1)
    to_unblacklist = []

    if reply_msg:
        m_id = get_media_id(reply_msg)
        if m_id:
            to_unblacklist.append(m_id)
        elif reply_msg.text:
            to_unblacklist.append(reply_msg.text.strip())

    if text:
        to_unblacklist.extend(
            [trigger.strip() for trigger in text.split("\n") if trigger.strip()]
        )

    if not to_unblacklist:
         return await edit_or_reply(event, "**⎉╎يجب الرد على الميديا الممنوعة أو كتابة الكلمة لالغاء منعها !**")

    successful = sum(
        bool(spl.rm_from_blacklist(event.chat_id, trigger.lower()))
        for trigger in to_unblacklist
    )

    await edit_or_reply(
        event, f"**⎉╎تم حذف (** {successful} / {len(to_unblacklist)} **)**\n**⎉╎من قائمة الممنوعـات هنـا .. بنجـاح ✓**"
    )


@zedub.zed_cmd(pattern="قائمة المنع$")
async def _(event):
    all_blacklisted = spl.get_chat_blacklist(event.chat_id)
    OUT_STR = "**⎉╎قائمة الممنوعـات هنـا هـي :\n**"
    if len(all_blacklisted) > 0:
        for trigger in all_blacklisted:
            if trigger.isdigit():
                 OUT_STR += f"- (ميديا/ملصق) : `{trigger}` \n"
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
        return await edit_delete(event, "**⎉╎بالـرد ع المستخـدم لـ تحذيـره ☻**")
    limit, soft_warn = sql.get_warn_setting(event.chat_id)
    num_warns, reasons = sql.warn_user(
        reply_message.sender_id, event.chat_id, warn_reason
    )
    if num_warns >= limit:
        sql.reset_warns(reply_message.sender_id, event.chat_id)
        if soft_warn:
            logger.info("TODO: طرد المستخدم")
            reply = "**⎉╎بسبب تخطي التحذيـرات الـ {} ،**\n**⎉╎يجب طـرد المستخـدم! ⛔️**".format(
                limit, reply_message.sender_id
            )
        else:
            logger.info("TODO: حظر المستخدم")
            reply = "**⎉╎بسبب تخطي التحذيـرات الـ {} ،**\n**⎉╎يجب حظـر المستخـدم! ⛔️**".format(
                limit, reply_message.sender_id
            )
    else:
        reply = "**⎉╎[ المستخدم 👤](tg://user?id={}) **\n**⎉╎لديـه {}/{} تحذيـرات .. احـذر!**".format(
            reply_message.sender_id, num_warns, limit
        )
        if warn_reason:
            reply += "\n**⎉╎سبب التحذير الأخير **\n{}".format(html.escape(warn_reason))
    await edit_or_reply(event, reply)


@zedub.zed_cmd(pattern="التحذيرات")
async def _(event):
    reply_message = await event.get_reply_message()
    if not reply_message:
        return await edit_delete(event, "**⎉╎بالـرد ع المستخـدم للحصول ع تحذيراتـه ☻**")
    result = sql.get_warns(reply_message.sender_id, event.chat_id)
    if not result or result[0] == 0:
        return await edit_or_reply(event, "**⎉╎هـذا المستخـدم ليس لديه أي تحذيـرات! ツ**")
    num_warns, reasons = result
    limit, soft_warn = sql.get_warn_setting(event.chat_id)
    if not reasons:
        return await edit_or_reply(
            event,
            "**⎉╎[ المستخدم 👤](tg://user?id={}) **\n**⎉╎لديـه {}/{} تحذيـرات ، **\n**⎉╎لكـن لا توجـد اسباب ؟!**".format(
                num_warns, limit
            ),
        )

    text = "**⎉╎[ المستخـدم 👤](tg://user?id={}) **\n**⎉╎لديـه {}/{} تحذيـرات ، **\n**⎉╎للأسباب : ↶**".format(
        num_warns, limit
    )

    text = "**⎉╎المستخـدم لديه {}/{} تحذيـرات ، **\n**⎉╎للأسباب : ↶**".format(num_warns, limit)
    text += "\r\n"
    text += reasons
    await event.edit(text)


@zedub.zed_cmd(pattern="حذف التحذيرات(?: |$)(.*)")
async def _(event):
    reply_message = await event.get_reply_message()
    sql.reset_warns(reply_message.sender_id, event.chat_id)
    await edit_or_reply(event, "**⎉╎تم إعـادة ضبط التحذيـرات! .. بنجـاح**")