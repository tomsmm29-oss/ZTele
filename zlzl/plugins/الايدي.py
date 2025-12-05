# Zed-Thon - ZelZal (Fetch Fixed for ZTele 2025 by Mikey)
# Fixed Imports + Safe file_id packing + Relative paths

from telethon.utils import pack_bot_file_id

# --- تصحيح المسارات ---
from . import zedub
from ..core.logger import logging
from ..helpers.utils import get_user_from_event
from ..core.managers import edit_delete, edit_or_reply

plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)


@zedub.zed_cmd(
    pattern="(الايدي|id)(?:\s|$)([\s\S]*)",
    command=("id", plugin_category),
    info={
        "header": "To get id of the group or user.",
        "description": "Shows ID of chat/user/channel.",
        "usage": "{tr}id <reply/username>",
    },
)
async def get_id_cmd(event):
    "To get id of the group or user."
    if input_str := event.pattern_match.group(2):
        try:
            p = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_delete(event, f"`{e}`", 5)
        try:
            if hasattr(p, 'first_name') and p.first_name:
                return await edit_or_reply(
                    event, f"**⎉╎ايـدي المستخـدم**  `{input_str}` **هـو** `{p.id}`"
                )
        except Exception:
            try:
                if hasattr(p, 'title') and p.title:
                    return await edit_or_reply(
                        event, f"**⎉╎ايـدي المستخـدم**  `{p.title}` **هـو** `{p.id}`"
                    )
            except Exception as e:
                LOGS.info(str(e))
        await edit_or_reply(event, "**⎉╎أدخل إما اسم مستخدم أو الرد على المستخدم**")
    elif event.reply_to_msg_id:
        r_msg = await event.get_reply_message()
        if r_msg.media:
            try:
                bot_api_file_id = pack_bot_file_id(r_msg.media)
            except:
                bot_api_file_id = "غير متاح"
            
            await edit_or_reply(
                event,
                f"**⎉╎ايـدي الدردشـه : **`{event.chat_id}`\n\n**⎉╎ايـدي المستخـدم : **`{r_msg.sender_id}`\n\n**⎉╎ايـدي الميديـا : **`{bot_api_file_id}`",
            )

        else:
            await edit_or_reply(
                event,
                f"**⎉╎ايـدي الدردشـه : **`{event.chat_id}`\n\n**⎉╎ايـدي المستخـدم : **`{r_msg.sender_id}`",
            )

    else:
        await edit_or_reply(event, f"**⎉╎ايـدي الدردشـه : **`{event.chat_id}`")


@zedub.zed_cmd(
    pattern="رابطه(?:\s|$)([\s\S]*)",
    command=("رابطه", plugin_category),
    info={
        "header": "لـ جـلب اسـم الشخـص بشكـل ماركـدون",
        "الاسـتخـدام": "{tr}رابطه <username/userid/reply>",
    },
)
async def permalink_cmd(event):
    """Generates a link to the user's PM with a custom text."""
    user, custom = await get_user_from_event(event)
    if not user:
        return
    if custom:
        return await edit_or_reply(event, f"[{custom}](tg://user?id={user.id})")
    tag = user.first_name.replace("\u2060", "") if user.first_name else user.username
    await edit_or_reply(event, f"[{tag}](tg://user?id={user.id})")


@zedub.zed_cmd(pattern="اسمي$")
async def my_permalink(event):
    user = await event.client.get_me()
    tag = user.first_name.replace("\u2060", "") if user.first_name else user.username
    await edit_or_reply(event, f"[{tag}](tg://user?id={user.id})")


@zedub.zed_cmd(
    pattern="اسمه(?:\s|$)([\s\S]*)",
    command=("اسمه", plugin_category),
    info={
        "header": "لـ جـلب اسـم الشخـص بشكـل ماركـدون",
        "الاسـتخـدام": "{tr}اسمه <username/userid/reply>",
    },
)
async def permalink_name(event):
    """Generates a link to the user's PM."""
    user, custom = await get_user_from_event(event)
    if not user:
        return
    if custom:
        return await edit_or_reply(event, f"[{custom}](tg://user?id={user.id})")
    tag = user.first_name.replace("\u2060", "") if user.first_name else user.username
    await edit_or_reply(event, f"[{tag}](tg://user?id={user.id})")