import re
import html

from telethon.utils import get_display_name

from . import zedub, BOTLOG_CHATID
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper import blacklist_sql as spl
from ..sql_helper import warns_sql as sql
from ..utils import is_admin

logger = logging.getLogger(__name__)

@zedub.zed_cmd(incoming=True, groups_only=True)
async def on_new_message(event):
    # الحصول على معرف الميديا (صورة، ملصق، فيديو) اذا وجدت
    media_id = None
    if event.media:
        if hasattr(event.media, "document") and event.media.document:
            media_id = str(event.media.document.id)
        elif hasattr(event.media, "photo") and event.media.photo:
            media_id = str(event.media.photo.id)

    name = event.raw_text
    snips = spl.get_chat_blacklist(event.chat_id)
    if not snips:
        return
    zthonadmin = await is_admin(event.client, event.chat_id, event.client.uid)
    if not zthonadmin:
        return
    
    for snip in snips:
        # التحقق من الميديا (تطابق تام للمعرف)
        if media_id and snip == media_id:
            try:
                await event.delete()
                break # تم الحذف لا داعي لإكمال اللوب
            except Exception:
                pass # اذا فشل الحذف لا تفعل شيئاً

        # التحقق من النصوص (نظام Regex السابق)
        # نتجاوز هذا الفحص اذا كان الممنوع هو ايدي ميديا (أرقام طويلة) لتجنب الخطأ
        if not snip.isdigit(): 
            pattern = f"( |^|[^\\w]){re.escape(snip)}( |$|[^\\w])"
            if re.search(pattern, name, flags=re.IGNORECASE):
                try:
                    await event.delete()
                except Exception:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**⎉╎عـذراً عـزيـزي مـالك البـوت\n⎉╎ليست لدي صلاحية الحذف في** {get_display_name(await event.get_chat())}.\n**⎉╎لذا لن يتم إزالة الكلمات الممنوعـه في تلك الدردشـه ؟!**",
                    )
                    for word in snips:
                        spl.rm_from_blacklist(event.chat_id, word.lower())
                break


@zedub.zed_cmd(
    pattern="منع(?:\s|$)([\s\S]*)",
    require_admin=True,
)
async def _(event):
    reply_msg = await event.get_reply_message()
    text = event.pattern_match.group(1)
    to_blacklist = []

    # حالة الرد على رسالة (صورة، ملصق، نص، الخ)
    if reply_msg:
        # اذا كان الرد على ميديا (ملصق، صورة، فيديو، ملف)
        if reply_msg.media:
            if hasattr(reply_msg.media, "document") and reply_msg.media.document:
                to_blacklist.append(str(reply_msg.media.document.id))
            elif hasattr(reply_msg.media, "photo") and reply_msg.media.photo:
                to_blacklist.append(str(reply_msg.media.photo.id))
        # اذا كان الرد على نص
        elif reply_msg.text:
            to_blacklist.append(reply_msg.text.strip())
    
    # حالة كتابة الكلمات بجانب الأمر مباشرة (بدون رد أو مع رد لإضافة المزيد)
    if text:
        to_blacklist.extend(
            [trigger.strip() for trigger in text.split("\n") if trigger.strip()]
        )

    if not to_blacklist:
        return await edit_or_reply(event, "**⎉╎يجب الرد على (صورة/ملصق/نص) أو كتابة الكلمة لمنعها !**")

    for trigger in to_blacklist:
        spl.add_to_blacklist(event.chat_id, trigger.lower())
        
    await edit_or_reply(
        event,
        f"**⎉╎تم اضافة (** {len(to_blacklist)} **)**\n**⎉╎الى قائمة الممنوعـات هنـا .. بنجـاح ✓**",
    )


@zedub.zed_cmd(
    pattern="الغاء منع(?:\s|$)([\s\S]*)",
    require_admin=True,
)
async def _(event):
    reply_msg = await event.get_reply_message()
    text = event.pattern_match.group(1)
    to_unblacklist = []

    # حالة الرد لإلغاء المنع
    if reply_msg:
        if reply_msg.media:
            if hasattr(reply_msg.media, "document") and reply_msg.media.document:
                to_unblacklist.append(str(reply_msg.media.document.id))
            elif hasattr(reply_msg.media, "photo") and reply_msg.media.photo:
                to_unblacklist.append(str(reply_msg.media.photo.id))
        elif reply_msg.text:
            to_unblacklist.append(reply_msg.text.strip())

    if text:
        to_unblacklist.extend(
            [trigger.strip() for trigger in text.split("\n") if trigger.strip()]
        )

    successful = sum(
        bool(spl.rm_from_blacklist(event.chat_id, trigger.lower()))
        for trigger in to_unblacklist
    )
    
    if len(to_unblacklist) == 0:
         return await edit_or_reply(event, "**⎉╎يجب الرد على الميديا الممنوعة أو كتابة الكلمة لالغاء منعها !**")

    await edit_or_reply(
        event, f"**⎉╎تم حذف (** {successful} / {len(to_unblacklist)} **(**\n**⎉╎من قائمة الممنوعـات هنـا .. بنجـاح ✓**"
    )


@zedub.zed_cmd(
    pattern="قائمة المنع$",
    require_admin=True,
)
async def _(event):
    all_blacklisted = spl.get_chat_blacklist(event.chat_id)
    OUT_STR = "**⎉╎قائمة الممنوعـات هنـا هـي :\n**"
    if len(all_blacklisted) > 0:
        for trigger in all_blacklisted:
            # اذا كان الممنوع عبارة عن ايدي (ارقام) نكتب انه ميديا
            if trigger.isdigit():
                 OUT_STR += f"- (ميديا/ملصق) : `{trigger}` \n"
            else:
                 OUT_STR += f"- {trigger} \n"
    else:
        OUT_STR = "**⎉╎لم يتم اضافة ممنوعـات هنـا بعـد ؟!**"
    await edit_or_reply(event, OUT_STR)


@zedub.zed_cmd(
    pattern="قائمه المنع$",
    require_admin=True,
)
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
