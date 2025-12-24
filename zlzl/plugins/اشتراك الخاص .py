import asyncio
import logging
import requests

from telethon import events, Button
from telethon.errors.rpcerrorlist import UserNotParticipantError

from telethon.tl.functions.channels import (
    EditBannedRequest,
    GetParticipantRequest,
)

from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChatBannedRights


# --- تصحيح المسارات والحقن النسبي ---
from . import zedub
from ..core.managers import edit_delete, edit_or_reply

# محاولة استدعاء Config
try:
    from ..Config import Config
except ImportError:
    class Config:
        TG_BOT_TOKEN = None
        COMMAND_HAND_LER = "."

# محاولة استدعاء SQL
try:
    from ..sql_helper.globals import addgvar, delgvar, gvarstatus
except ImportError:
    def addgvar(x, y): pass
    def delgvar(x): pass
    def gvarstatus(x): return None

# محاولة استدعاء BOTLOG
try:
    from . import BOTLOG_CHATID
except ImportError:
    BOTLOG_CHATID = None

LOGS = logging.getLogger(__name__)
plugin_category = "الادمن"

# ================== صلاحيات الكتم ==================

MUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=True,
)

UNMUTE_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=False,
)

# ================== دالة تحقق قوية ==================

async def check_user_subscription(client, user_id, channel_id):
    try:
        await client(GetParticipantRequest(int(channel_id), user_id))
        return True
    except UserNotParticipantError:
        return False
    except Exception:
        return False

# ================== وضع اشتراك الخاص ==================

@zedub.zed_cmd(pattern="(ضع الاشتراك خاص|وضع الاشتراك خاص)(?:\s|$)([\s\S]*)")
async def set_pm_sub(event):
    input_str = event.pattern_match.group(2)

    if input_str:
        try:
            p = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_delete(event, f"{e}", 5)

        delgvar("Custom_Pm_Channel")
        addgvar("Custom_Pm_Channel", f"-100{p.id}")

        name = p.title if hasattr(p, "title") else p.first_name
        return await edit_or_reply(
            event,
            f"⎉╎تم إضافة قناة الاشتراك الاجباري للخاص .. بنجـاح ☑️\n\n"
            f"**⎉╎اسم القناة : ↶** {name}\n"
            f"**⎉╎ايدي القناة : ↶** {p.id}\n\n"
            f"**⎉╎ارسـل الان** .اشتراك خاص"
        )

    delgvar("Custom_Pm_Channel")
    addgvar("Custom_Pm_Channel", event.chat_id)
    await edit_or_reply(
        event,
        f"**⎉╎تم إضافة قناة الاشتراك الاجباري للخاص .. بنجـاح ☑️**\n\n"
        f"**⎉╎ايدي القناة : ↶** `{event.chat_id}`\n\n"
        f"**⎉╎ارسـل الان** `.اشتراك خاص`"
    )

# ================== وضع اشتراك الكروب ==================

@zedub.zed_cmd(pattern="(ضع الاشتراك كروب|وضع الاشتراك كروب)(?:\s|$)([\s\S]*)")
async def set_grp_sub(event):
    input_str = event.pattern_match.group(2)

    if input_str:
        try:
            p = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_delete(event, f"{e}", 5)

        delgvar("Custom_G_Channel")
        addgvar("Custom_G_Channel", f"-100{p.id}")

        name = p.title if hasattr(p, "title") else p.first_name
        return await edit_or_reply(
            event,
            f"⎉╎تم إضافة قناة الاشتراك الاجباري للكروب .. بنجـاح ☑️\n\n"
            f"**⎉╎اسم القناة : ↶** {name}\n"
            f"**⎉╎ايدي القناة : ↶** {p.id}\n\n"
            f"**⎉╎ارسـل الان** .اشتراك كروب"
        )

    delgvar("Custom_G_Channel")
    addgvar("Custom_G_Channel", event.chat_id)
    await edit_or_reply(
        event,
        f"**⎉╎تم إضافة قناة الاشتراك الاجباري للكروب .. بنجـاح ☑️**\n\n"
        f"**⎉╎ايدي القناة : ↶** `{event.chat_id}`\n\n"
        f"**⎉╎ارسـل الان** `.اشتراك كروب`"
    )

# ================== تفعيل الاشتراك ==================

@zedub.zed_cmd(pattern="اشتراك")
async def enable_sub(event):
    ty = event.text.replace(".اشتراك", "").replace(" ", "")

    if ty in ["كروب", "جروب", "قروب", "مجموعة", "مجموعه"]:
        if gvarstatus("sub_group"):
            return await edit_delete(event, "⎉╎الاشتـراك الاجبـاري مفعـل مسبقـاً")
        addgvar("sub_group", str(event.chat_id))
        return await edit_or_reply(event, "⎉╎تم تفعيل الاشتراك الاجباري لـ هذه المجموعة .. بنجـاح✓")

    if ty == "خاص":
        if gvarstatus("sub_private"):
            return await edit_delete(event, "⎉╎الاشتـراك الاجبـاري لـ الخـاص مفعـل مسبقـاً")
        addgvar("sub_private", True)
        return await edit_or_reply(event, "⎉╎تم تفعيل الاشتراك الاجباري لـ الخـاص .. بنجـاح✓")

    await edit_delete(event, "⎉╎اختـر نوع الاشتـراك الاجبـاري اولاً :\n\n.اشتراك كروب\n\n.اشتراك خاص")

# ================== تعطيل الاشتراك ==================

@zedub.zed_cmd(pattern="تعطيل")
async def disable_sub(event):
    ty = event.text.replace(".تعطيل", "").replace(" ", "")

    if ty in ["كروب", "جروب", "قروب", "مجموعة", "مجموعه"]:
        delgvar("sub_group")
        return await edit_delete(event, "⎉╎تم الغاء الاشتراك الاجباري للكروب .. بنجـاح ✓")

    if ty == "خاص":
        delgvar("sub_private")
        return await edit_delete(event, "⎉╎تم إلغاء الاشتراك الاجباري للخاص .. بنجـاح✓")

    await edit_delete(event, "⎉╎اختـر نوع الاشتـراك الاجبـاري اولاً لـ الالغـاء")

# ================== فحص الخاص ==================

@zedub.zed_cmd(incoming=True, func=lambda e: e.is_private)
async def pm_checker(event):
    if not gvarstatus("sub_private"):
        return

    ch = gvarstatus("Custom_Pm_Channel")
    if not ch:
        return

    user = await event.get_sender()
    if not user:
        return

    if await check_user_subscription(event.client, user.id, ch):
        return

    c = await event.client.get_entity(int(ch))
    link = f"https://t.me/{c.username}" if c.username else "#"

    await event.reply(
        f"**⎉╎يجب عليك الإشـتࢪاڪ بالقناة أولاً\n⎉╎قناة الاشتراك : {c.title}**",
        buttons=[[Button.url("اضغط لـ الإشـتࢪاڪ 🗳", link)]]
    )
    await event.delete()

# ================== فحص الكروب ==================

@zedub.zed_cmd(incoming=True, func=lambda e: e.is_group)
async def group_checker(event):
    if gvarstatus("sub_group") != str(event.chat_id):
        return

    ch = gvarstatus("Custom_G_Channel")
    if not ch:
        return

    user = await event.get_sender()
    if not user or user.bot:
        return

    if await check_user_subscription(event.client, user.id, ch):
        try:
            await event.client(EditBannedRequest(event.chat_id, user.id, UNMUTE_RIGHTS))
        except:
            pass
        return

    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
    except:
        pass

    c = await event.client.get_entity(int(ch))
    link = f"https://t.me/{c.username}" if c.username else "#"

    await event.reply(
        f"**⎉╎يجب عليك الإشـتࢪاڪ بالقناة أولاً\n⎉╎قناة الاشتراك : {c.title}**",
        buttons=[[Button.url("اضغط لـ الإشـتࢪاڪ 🗳", link)]]
    )