import asyncio
from datetime import datetime
from telethon.tl import functions, types

# استيراد من السورس الحالي
from . import zedub
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.tools import media_type
from ..helpers.utils import _format

# تجاوز مشكلة السجل إذا لم يكن معرفاً
try:
    BOTLOG_CHATID = Config.PM_LOGGER_GROUP_ID
except:
    BOTLOG_CHATID = None
BOTLOG = True

plugin_category = "البوت"
LOGS = logging.getLogger(__name__)

class AFK:
    def __init__(self):
        self.USERAFK_ON = {}
        self.afk_time = None
        self.last_afk_message = {}
        # خليناهم None عشان نتفادى خطأ الطرح من قاموس فارغ
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
    
    # حساب الوقت بطريقة آمنة 100%
    endtime = "لحظات"
    if AFK_.afk_star:
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

    current_message = event.message.message
    if (("afk" not in current_message) or ("#afk" not in current_message)) and (
        "on" in AFK_.USERAFK_ON
    ):
        shite = await event.client.send_message(
            event.chat_id,
            "**الان اعمل بشكل طبيعي\nلقد كان امر السليب مفعل منذ: **" + endtime,
        )
        AFK_.USERAFK_ON = {}
        AFK_.afk_time = None
        await asyncio.sleep(5)
        await shite.delete()
        AFK_.afk_on = False
        if BOTLOG and BOTLOG_CHATID:
            try:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "⪼  انتهاء امر السليب \n"
                    + "`⪼  تم تعطيله والرجوع للوضع الطبيعي كان مفعل لـ "
                    + endtime
                    + "`",
                )
            except:
                pass

@zedub.zed_cmd(
    incoming=True, func=lambda e: bool(e.mentioned or e.is_private), edited=False
)
async def on_afk(event):
    if AFK_.afk_on is False:
        return
    
    back_alivee = datetime.now()
    AFK_.afk_end = back_alivee.replace(microsecond=0)
    
    endtime = "وقت غير معروف"
    if AFK_.afk_star:
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

    current_message_text = event.message.message.lower()
    if "afk" in current_message_text or "#afk" in current_message_text:
        return False
    if not await event.get_sender():
        return
    if AFK_.USERAFK_ON and not (await event.get_sender()).bot:
        # تجهيز الرسالة
        message_to_reply = f"**⚠️ | عـذراً انـا فـي وضـع عـدم التواجـد**\n**⏰ | منـذ :** `{endtime}`"
        if AFK_.reason:
            message_to_reply += f"\n**📝 | السبـب :** `{AFK_.reason}`"

        msg = None
        if AFK_.afk_type == "media" and AFK_.media_afk:
            try:
                msg = await event.reply(message_to_reply, file=AFK_.media_afk.media)
            except:
                msg = await event.reply(message_to_reply)
        else:
            msg = await event.reply(message_to_reply)

        if event.chat_id in AFK_.last_afk_message:
            try:
                await AFK_.last_afk_message[event.chat_id].delete()
            except:
                pass
        AFK_.last_afk_message[event.chat_id] = msg

@zedub.zed_cmd(pattern="سليب(?:\s|$)([\s\S]*)")
async def _(event):
    AFK_.USERAFK_ON = {}
    AFK_.afk_time = None
    AFK_.last_afk_message = {}
    AFK_.afk_end = None
    AFK_.afk_type = "text"
    AFK_.afk_on = True
    AFK_.afk_star = datetime.now().replace(microsecond=0)
    
    input_str = event.pattern_match.group(1)
    if ";" in input_str:
        msg, mlink = input_str.split(";", 1)
        AFK_.reason = f"[{msg.strip()}]({mlink.strip()})"
        AFK_.msg_link = True
    else:
        AFK_.reason = input_str if input_str else None
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
        await edit_delete(event, f"**⚠️ | تم تفعيـل وضـع عـدم التواجـد**\n**السبب:** `{AFK_.reason}`", 5)
    else:
        await edit_delete(event, "**⚠️ | تم تفعيـل وضـع عـدم التواجـد**", 5)
    
    if BOTLOG and BOTLOG_CHATID:
        try:
            if AFK_.reason:
                await event.client.send_message(BOTLOG_CHATID, f"⪼ تم تفعيل السليب: {AFK_.reason}")
            else:
                await event.client.send_message(BOTLOG_CHATID, "⪼ تم تفعيل السليب")
        except:
            pass

@zedub.zed_cmd(pattern="سليب_ميديا(?:\s|$)([\s\S]*)")
async def _(event):
    reply = await event.get_reply_message()
    media_t = media_type(reply)
    if media_t == "Sticker" or not media_t:
        return await edit_or_reply(event, "⪼ امر السليب : المرجو قم بالرد على الصورة بالامر ")
    
    AFK_.USERAFK_ON = {}
    AFK_.afk_time = None
    AFK_.last_afk_message = {}
    AFK_.afk_end = None
    AFK_.media_afk = None
    AFK_.afk_type = "media"
    AFK_.afk_on = True
    AFK_.afk_star = datetime.now().replace(microsecond=0)
    
    input_str = event.pattern_match.group(1)
    AFK_.reason = input_str if input_str else None
    
    try:
        last_seen_status = await event.client(
            functions.account.GetPrivacyRequest(types.InputPrivacyKeyStatusTimestamp())
        )
        if isinstance(last_seen_status.rules, types.PrivacyValueAllowAll):
            AFK_.afk_time = datetime.now()
    except:
        pass

    AFK_.USERAFK_ON = f"on: {AFK_.reason}"
    try:
        AFK_.media_afk = await reply.forward_to(BOTLOG_CHATID)
    except:
        AFK_.media_afk = None

    if AFK_.reason:
        await edit_delete(event, f"**⚠️ | تم تفعيـل وضـع عـدم التواجـد (ميديا)**\n**السبب:** `{AFK_.reason}`", 5)
    else:
        await edit_delete(event, "**⚠️ | تم تفعيـل وضـع عـدم التواجـد (ميديا)**", 5)
        
    if BOTLOG and BOTLOG_CHATID:
        try:
            await event.client.send_message(BOTLOG_CHATID, "⪼ تم تفعيل السليب (ميديا)")
        except:
            pass
