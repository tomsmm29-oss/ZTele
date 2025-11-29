import asyncio
from datetime import datetime

from telethon.tl import functions, types

from . import zedub
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.tools import media_type
from ..helpers.utils import _format

# تصحيح الاستيرادات
BOTLOG = True 
BOTLOG_CHATID = Config.PM_LOGGER_GROUP_ID

plugin_category = "البوت"

LOGS = logging.getLogger(__name__)


class AFK:
    def __init__(self):
        self.USERAFK_ON = {}
        self.afk_time = None
        self.last_afk_message = {}
        self.afk_star = None
        self.afk_end = None
        self.reason = None
        self.msg_link = False
        self.afk_type = None
        self.media_afk = None
        self.afk_on = False


AFK_ = AFK()


@zedub.zed_cmd(outgoing=True, edited=False)
async def set_not_afk(event):
    if AFK_.afk_on is False:
        return
    back_alive = datetime.now()
    AFK_.afk_end = back_alive.replace(microsecond=0)
    
    if AFK_.afk_star is not None:
        total_afk_time = AFK_.afk_end - AFK_.afk_star
        time = int(total_afk_time.seconds)
        d = time // (24 * 3600)
        time %= 24 * 3600
        h = time // 3600
        time %= 3600
        m = time // 60
        time %= 60
        s = time
        endtime = ""
        if d > 0:
            endtime += f"{d} يوم {h} ساعة {m} دقيقة {s} ثانية"
        elif h > 0:
            endtime += f"{h} ساعة {m} دقيقة {s} ثانية"
        else:
            endtime += f"{m} دقيقة {s} ثانية" if m > 0 else f"{s} ثانية"
    else:
        endtime = "لحظات"

    current_message = event.message.message
    if (("afk" not in current_message) or ("#afk" not in current_message)) and (
        "on" in AFK_.USERAFK_ON
    ):
        shite = await event.client.send_message(
            event.chat_id,
            "**الان اعمل بشكل طبيعي\nلقد كان امر السليب مفعل منذ " + endtime + "`",
        )
        AFK_.USERAFK_ON = {}
        AFK_.afk_time = None
        await asyncio.sleep(5)
        await shite.delete()
        AFK_.afk_on = False
        if BOTLOG:
            try:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "⪼  انتهاء امر السليب \n"
                    + "`⪼  تم تعطيله والرجوع للوضع الطبيعي كان مفعل لـ"
                    + endtime
                    + "`",
                )
            except Exception:
                pass


@zedub.zed_cmd(
    incoming=True, func=lambda e: bool(e.mentioned or e.is_private), edited=False
)
async def on_afk(event):
    if AFK_.afk_on is False:
        return
    back_alivee = datetime.now()
    AFK_.afk_end = back_alivee.replace(microsecond=0)
    
    if AFK_.afk_star is not None:
        total_afk_time = AFK_.afk_end - AFK_.afk_star
        time = int(total_afk_time.seconds)
        d = time // (24 * 3600)
        time %= 24 * 3600
        h = time // 3600
        time %= 3600
        m = time // 60
        time %= 60
        s = time
        endtime = ""
        if d > 0:
            endtime += f"{d} يوم {h} ساعة {m} دقيقة {s} ثانية"
        elif h > 0:
            endtime += f"{h} ساعة {m} دقيقة {s} ثانية"
        else:
            endtime += f"{m} دقيقة {s} ثانية" if m > 0 else f"{s} ثانية"
    else:
        endtime = "وقت غير معروف"

    current_message_text = event.message.message.lower()
    if "afk" in current_message_text or "#afk" in current_message_text:
        return False
    if not await event.get_sender():
        return
    if AFK_.USERAFK_ON and not (await event.get_sender()).bot:
        msg = None
        if AFK_.afk_type == "media":
            if AFK_.reason:
                message_to_reply = f"انا الان في وضعيه عدم الاتصال منذ\n`{endtime}`\nالسبب : {AFK_.reason}"
            else:
                message_to_reply = f"انا الان في وضعيه عدم الاتصال منذ\n`{endtime}`"
            if event.chat_id:
                try:
                    msg = await event.reply(message_to_reply, file=AFK_.media_afk.media)
                except:
                     msg = await event.reply(message_to_reply)
        elif AFK_.afk_type == "text":
            if AFK_.msg_link and AFK_.reason:
                message_to_reply = f"انا الان في وضعيه عدم الاتصال منذ .\n\n{endtime}\nالسبب : {AFK_.reason}"
            elif AFK_.reason:
                message_to_reply = f"انا الان في وضعيه عدم الاتصال منذ .\n\n{endtime}\nالسبب : {AFK_.reason}"
            else:
                message_to_reply = f"انا الان في وضعيه عدم الاتصال منذ.\n\n{endtime}"
            if event.chat_id:
                msg = await event.reply(message_to_reply)
        if event.chat_id in AFK_.last_afk_message:
            try:
                await AFK_.last_afk_message[event.chat_id].delete()
            except:
                pass
        AFK_.last_afk_message[event.chat_id] = msg
        if event.is_private:
            return
        hmm = await event.get_chat()
        if Config.PM_LOGGER_GROUP_ID == -100:
            return
        full = None
        try:
            full = await event.client.get_entity(event.message.from_id)
        except Exception as e:
            LOGS.info(str(e))
        
        try:
            messaget = media_type(event)
        except:
            messaget = "Unknown"

        resalt = f" \n<b>المجموعة : </b><code>{hmm.title}</code>"
        if full is not None:
            resalt += f"\n<b>المرسل : </b> {_format.htmlmentionuser(full.first_name , full.id)}"
        if messaget is not None:
            resalt += f"\n<b>نوع الرسالة : </b><code>{messaget}</code>"
        else:
            resalt += f"\n<b>الرسالة : </b>{event.message.message}"
        resalt += f"\n<b>رابط الرسالة: </b><a href = 'https://t.me/c/{hmm.id}/{event.message.id}'> الرابط</a>"
        if not event.is_private:
            try:
                await event.client.send_message(
                    Config.PM_LOGGER_GROUP_ID,
                    resalt,
                    parse_mode="html",
                    link_preview=False,
                )
            except:
                pass


@zedub.zed_cmd(pattern="سليب(?:\s|$)([\s\S]*)")
async def _(event):
    AFK_.USERAFK_ON = {}
    AFK_.afk_time = None
    AFK_.last_afk_message = {}
    AFK_.afk_end = None
    AFK_.afk_type = "text"
    start_1 = datetime.now()
    AFK_.afk_on = True
    AFK_.afk_star = start_1.replace(microsecond=0)
    if not AFK_.USERAFK_ON:
        input_str = event.pattern_match.group(1)
        if ";" in input_str:
            msg, mlink = input_str.split(";", 1)
            AFK_.reason = f"[{msg.strip()}]({mlink.strip()})"
            AFK_.msg_link = True
        else:
            AFK_.reason = input_str
            AFK_.msg_link = False
        
        try:
            last_seen_status = await event.client(
                functions.account.GetPrivacyRequest(types.InputPrivacyKeyStatusTimestamp())
            )
            if isinstance(last_seen_status.rules, types.PrivacyValueAllowAll):
                AFK_.afk_time = datetime.now()
        except:
            pass

        AFK_.USERAFK_ON = f"on: {AFK_.reason}"
        if AFK_.reason:
            await edit_delete(
                event, f"انا الان في وضعيه عدم الاتصال بسبب ~ {AFK_.reason}", 5
            )
        else:
            await edit_delete(event, "انا الان في وضعيه عدم الاتصال", 5)
        if BOTLOG:
            try:
                if AFK_.reason:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"⪼ وضع السليب \nتم تشغيل وضع السليب، والسبب هو {AFK_.reason}",
                    )
                else:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "⪼ وضع السليب \nتم تشغيل وضع السليب، بدون ذكر اي سبب",
                    )
            except Exception: # هذا السطر اللي كان ناقص
                pass


@zedub.zed_cmd(pattern="سليب_ميديا(?:\s|$)([\s\S]*)")
async def _(event):
    reply = await event.get_reply_message()
    media_t = media_type(reply)
    if media_t == "Sticker" or not media_t:
        return await edit_or_reply(
            event, "⪼ امر السليب : المرجو قم بالرد على الصورة بالامر "
        )
    
    AFK_.USERAFK_ON = {}
    AFK_.afk_time = None
    AFK_.last_afk_message = {}
    AFK_.afk_end = None
    AFK_.media_afk = None
    AFK_.afk_type = "media"
    start_1 = datetime.now()
    AFK_.afk_on = True
    AFK_.afk_star = start_1.replace(microsecond=0)
    if not AFK_.USERAFK_ON:
        input_str = event.pattern_match.group(1)
        AFK_.reason = input_str
        
        try:
            last_seen_status = await event.client(
                functions.account.GetPrivacyRequest(types.InputPrivacyKeyStatusTimestamp())
            )
            if isinstance(last_seen_status.rules, types.PrivacyValueAllowAll):
                AFK_.afk_time = datetime.now()
        except:
            pass

        AFK_.USERAFK_ON = f"on: {AFK_.reason}"
        if AFK_.reason:
            await edit_delete(
                event, f"انا الان في وضعيه عدم الاتصال بسبب ~ {AFK_.reason}", 5
            )
        else:
            await edit_delete(event, "انا الان في وضعيه عدم الاتصال", 5)
        
        try:
            AFK_.media_afk = await reply.forward_to(BOTLOG_CHATID)
        except Exception as e:
            return await edit_or_reply(event, f"خطأ في حفظ الميديا: {e}")

        if AFK_.reason:
            try:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    f"⪼ وضع السليب \nتم تشغيل وضع السليب، والسبب هو {AFK_.reason}",
                )
            except Exception: # وهنا كمان كان ناقص
                pass
        else:
            try:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "⪼ وضع السليب \nتم تشغيل وضع السليب، بدون ذكر اي سبب",
                )
            except Exception: # وهنا
                pass