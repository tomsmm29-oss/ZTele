import asyncio
import shutil
import contextlib
from datetime import datetime

from telethon.errors import (
    BadRequestError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
)
from telethon.errors.rpcerrorlist import UserAdminInvalidError, UserIdInvalidError
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.types import (
    ChatAdminRights,
    ChatBannedRights,
    InputChatPhotoEmpty,
    MessageMediaPhoto,
)
from telethon.utils import get_display_name

from . import zedub
from ..Config import Config
from ..core.data import _sudousers_list
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import media_type
from ..helpers.utils import _format, get_user_from_event
from ..sql_helper.mute_sql import is_muted, mute, unmute
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..sql_helper.echo_sql import addecho, get_all_echos, get_echos, is_echo, remove_all_echos, remove_echo, remove_echos
from ..sql_helper import gban_sql_helper as gban_sql
from . import BOTLOG, BOTLOG_CHATID, admin_groups

# --- تم إزالة استيراد reply_id المسبب للمشاكل ---

plugin_category = "الادمن"
LOGS = logging.getLogger(__name__)

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

zel_dev = (5176749470, 5426390871, 6269975462, 1985225531)

# --- متغيرات أسماء الأوامر ---
ADMZ = gvarstatus("Z_ADMIN") or "رفع مشرف"
UNADMZ = gvarstatus("Z_UNADMIN") or "تنزيل مشرف"
BANN = gvarstatus("Z_BAN") or "حظر"
UNBANN = gvarstatus("Z_UNBAN") or "الغاء حظر"
MUTE = gvarstatus("Z_MUTE") or "كتم"
UNMUTE = gvarstatus("Z_UNMUTE") or "الغاء كتم"
KICK = gvarstatus("Z_KICK") or "طرد"
PC_BANE = gvarstatus("PC_BANE")

# ================================================
#   أوامر الحظر العام (تم تغيير اسم الدوال)
# ================================================

@zedub.zed_cmd(pattern="ح عام(?:\s|$)([\s\S]*)")
async def zed_gban_cmd(event): 
    zede = await edit_or_reply(event, "**╮ ❐... جـاࢪِ حـظـࢪ الشخـص عـام**")
    start = datetime.now()
    user, reason = await get_user_from_event(event, zede)
    if not user:
        return
    if user.id == zedub.uid:
        return await edit_delete(zede, "**⎉╎عـذراً ..لا استطيـع حظـࢪ نفسـي **")
    if user.id in zel_dev:
        return await edit_delete(zede, "**⎉╎عـذراً ..لا استطيـع حظـࢪ احـد المطـورين عـام **")
    
    if gban_sql.is_gbanned(user.id):
        await zede.edit(f"**⎉╎المسـتخـدم ↠** [{user.first_name}](tg://user?id={user.id}) \n**⎉╎مـوجــود بالفعــل فـي ↠ قائمـة المحظــورين عــام**")
    else:
        gban_sql.zedgban(user.id, reason)
    
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(zede, "**⎉╎عــذراً .. يجـب ان تكــون مشـرفـاً فـي مجموعـة واحـده ع الأقــل **")
    
    await zede.edit(f"**⎉╎جـاري بـدء حظـر ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎مـن ↠ {len(san)} كــروب**")
    
    for i in range(sandy):
        try:
            await event.client(EditBannedRequest(san[i], user.id, BANNED_RIGHTS))
            await asyncio.sleep(0.5)
            count += 1
        except BadRequestError:
            pass
    
    end = datetime.now()
    zedtaken = (end - start).seconds
    if reason:
        await zede.edit(f"**⎉╎المستخـدم :** [{user.first_name}](tg://user?id={user.id})\n\n**⎉╎تم حـظـࢪه عـام مـن {count} كــࢪوب خـلال {zedtaken} ثـانيـه**\n**⎉╎السـبب :** {reason}")
    else:
        await zede.edit(f"**╮ ❐... الشخـص :** [{user.first_name}](tg://user?id={user.id})\n\n**╮ ❐... تـم حـظـࢪه عـام مـن {count} كــࢪوب خـلال {zedtaken} ثـانيـه**")

@zedub.zed_cmd(pattern="الغاء ح عام(?:\s|$)([\s\S]*)")
async def zed_ungban_cmd(event):
    zede = await edit_or_reply(event, "**╮ ❐  جـاري الغــاء الحظـر العــام ❏╰**")
    start = datetime.now()
    user, reason = await get_user_from_event(event, zede)
    if not user: return
    
    if gban_sql.is_gbanned(user.id):
        gban_sql.catungban(user.id)
    else:
        return await edit_delete(zede, f"**⎉╎المسـتخـدم ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎ليـس مـوجــود فـي ↠ قائمـة المحظــورين عــام**")
    
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(zede, "**⎉╎عــذراً .. يجـب ان تكــون مشـرفـاً فـي مجموعـة واحـده ع الأقــل **")
    
    await zede.edit(f"**⎉╎جـاري الغــاء حظـر ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎مـن ↠ {len(san)} كــروب**")
    
    for i in range(sandy):
        try:
            await event.client(EditBannedRequest(san[i], user.id, UNBAN_RIGHTS))
            await asyncio.sleep(0.5)
            count += 1
        except BadRequestError:
            pass
            
    end = datetime.now()
    zedtaken = (end - start).seconds
    await zede.edit(f"**⎉╎المستخـدم :** [{user.first_name}](tg://user?id={user.id})\n\n**⎉╎تم الغــاء حـظـࢪه عـام مـن {count} كــࢪوب خـلال {zedtaken} ثـانيـه**")

@zedub.zed_cmd(pattern="العام$")
async def zed_gban_list_cmd(event):
    gbanned_users = gban_sql.get_all_gbanned()
    GBANNED_LIST = "- قائمـة المحظـورين عــام :\n\n"
    if len(gbanned_users) > 0:
        for a_user in gbanned_users:
            if a_user.reason:
                GBANNED_LIST += f"**⎉╎المستخـدم :**  [{a_user.chat_id}](tg://user?id={a_user.chat_id}) \n**⎉╎سـبب الحظـر : {a_user.reason} ** \n\n"
            else:
                GBANNED_LIST += f"**⎉╎المستخـدم :**  [{a_user.chat_id}](tg://user?id={a_user.chat_id}) \n**⎉╎سـبب الحظـر : لا يـوجـد ** \n\n"
    else:
        GBANNED_LIST = "**- لايــوجـد محظــورين عــام بعــد**"
    await edit_or_reply(event, GBANNED_LIST)

@zedub.zed_cmd(pattern="ط عام(?:\s|$)([\s\S]*)")
async def zed_gkick_cmd(event):
    zede = await edit_or_reply(event, "**╮ ❐ ... جــاࢪِ طــرد الشخــص عــام ... ❏╰**")
    start = datetime.now()
    user, reason = await get_user_from_event(event, zede)
    if not user: return
    if user.id == zedub.uid: return await edit_delete(zede, "**╮ ❐ ... عــذراً لا استطــيع طــرد نفســي ... ❏╰**")
    
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0: return await edit_delete(zede, "**⎉╎عــذراً .. يجـب ان تكــون مشـرفـاً فـي مجموعـة واحـده ع الأقــل **")
    
    await zede.edit(f"**⎉╎بـدء طـرد ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎فـي ↠ {len(san)} كــروب**")
    
    for i in range(sandy):
        try:
            await event.client.kick_participant(san[i], user.id)
            await asyncio.sleep(0.5)
            count += 1
        except BadRequestError:
            pass
    
    end = datetime.now()
    zedtaken = (end - start).seconds
    await zede.edit(f"[{user.first_name}](tg://user?id={user.id}) `was gkicked in {count} groups in {zedtaken} seconds`!!")


# ================================================
#   أوامر المجموعة (الصورة، المشرفين)
# ================================================

@zedub.zed_cmd(pattern="الصورة (وضع|حذف)$")
async def zed_set_group_photo(event):
    flag = (event.pattern_match.group(1)).strip()
    if flag == "وضع":
        replymsg = await event.get_reply_message()
        photo = None
        if replymsg and replymsg.media:
            if isinstance(replymsg.media, MessageMediaPhoto):
                photo = await event.client.download_media(message=replymsg.photo)
            elif "image" in replymsg.media.document.mime_type.split("/"):
                photo = await event.client.download_file(replymsg.media.document)
            else:
                return await edit_delete(event, INVALID_MEDIA)
        if photo:
            try:
                await event.client(EditPhotoRequest(event.chat_id, await event.client.upload_file(photo)))
                await edit_delete(event, CHAT_PP_CHANGED)
            except Exception as e:
                return await edit_delete(event, f"**- خطــأ : **`{str(e)}`")
    else:
        try:
            await event.client(EditPhotoRequest(event.chat_id, InputChatPhotoEmpty()))
            await edit_delete(event, "**- صورة الدردشـه تم حذفهـا . . بنجـاح ✓**")
        except Exception as e:
            return await edit_delete(event, f"**- خطــأ : **`{e}`")

# --- أوامر الرفع (تغيير الأسماء) ---
@zedub.zed_cmd(pattern=f"{ADMZ}(?:\s|$)([\s\S]*)")
async def zed_promote_admin(event): # اسم فريد
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, NO_ADMIN)
        return
    new_rights = ChatAdminRights(add_admins=False, invite_users=True, change_info=False, ban_users=False, delete_messages=True, pin_messages=True)
    user, rank = await get_user_from_event(event)
    if not rank: rank = "admin"
    if not user: return
    zzevent = await edit_or_reply(event, "**╮ ❐  جـارِ  ࢪفعـه مشـرف  . . .❏╰**")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
        await zzevent.edit(f"**⎉╎المستخـدم** [{user.first_name}](tg://user?id={user.id}) \n**⎉╎تم رفعـه مشـرفـاً .. بنجـاح✓**")
    except BadRequestError:
        return await zzevent.edit(NO_PERM)

@zedub.zed_cmd(pattern="رفع مالك(?:\s|$)([\s\S]*)")
async def zed_promote_owner(event): # اسم فريد
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, NO_ADMIN)
        return
    new_rights = ChatAdminRights(add_admins=True, invite_users=True, change_info=True, ban_users=True, delete_messages=True, pin_messages=True, manage_call=True)
    user, rank = await get_user_from_event(event)
    if not rank: rank = "admin"
    if not user: return
    zzevent = await edit_or_reply(event, "**╮ ❐  جـاري ࢪفعه مشـرف بكـل الصـلاحيـات  ❏╰**")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
        await zzevent.edit(f"**⎉╎المستخـدم** [{user.first_name}](tg://user?id={user.id}) \n**⎉╎تم رفعـه مشـرفـاً بكل الصلاحيـات ✓**")
    except BadRequestError:
        return await zzevent.edit(NO_PERM)

@zedub.zed_cmd(pattern="اخفاء(?:\s|$)([\s\S]*)")
async def zed_promote_hidden(event): # اسم فريد
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, NO_ADMIN)
        return
    new_rights = ChatAdminRights(add_admins=True, invite_users=True, change_info=True, ban_users=True, delete_messages=True, pin_messages=True, manage_call=True, anonymous=True)
    user, rank = await get_user_from_event(event)
    if not rank: rank = "admin"
    if not user: return
    zzevent = await edit_or_reply(event, "**╮ ❐  ا . . .  ❏╰**")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
        await zzevent.edit("**- ❝ ⌊   تم  . . .𓆰**")
    except BadRequestError:
        return await zzevent.edit(NO_PERM)

@zedub.zed_cmd(pattern=f"{UNADMZ}(?:\s|$)([\s\S]*)")
async def zed_demote_cmd(event): # اسم فريد
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(event, NO_ADMIN)
        return
    user, _ = await get_user_from_event(event)
    if not user: return
    zzevent = await edit_or_reply(event, "↮")
    newrights = ChatAdminRights(add_admins=None, invite_users=None, change_info=None, ban_users=None, delete_messages=None, pin_messages=None)
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, newrights, "مشرف"))
        await zzevent.edit("**⎉╎المستخـدم** [{user.first_name}](tg://user?id={user.id}) \n**⎉╎تم تنـزيلـه مشـرف .. بنجـاح✓**")
    except BadRequestError:
        return await zzevent.edit(NO_PERM)

# ================================================
#   أوامر الحظر والطرد والكتم (بأسماء فريدة)
# ================================================

@zedub.zed_cmd(pattern=f"{BANN}(?:\s|$)([\s\S]*)")
async def zed_ban_user_cmd(event): # اسم فريد
    user, reason = await get_user_from_event(event)
    if not user: return
    if user.id == event.client.uid: return await edit_delete(event, "**⪼ عـذراً ..لا استطيـع حظـࢪ نفسـي 𓆰**")
    
    zedevent = await edit_or_reply(event, "**╮ ❐... جـاࢪِ الحـظـࢪ ...❏╰**")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, BANNED_RIGHTS))
        await zedevent.edit(f"**⎉╎المستخـدم :** {_format.mentionuser(user.first_name ,user.id)}  \n**⎉╎تم حظـࢪه بنجـاح ☑️**")
    except BadRequestError:
        return await zedevent.edit(NO_PERM)

@zedub.zed_cmd(pattern=f"{UNBANN}(?:\s|$)([\s\S]*)")
async def zed_unban_user_cmd(event): # اسم فريد
    user, _ = await get_user_from_event(event)
    if not user: return
    zedevent = await edit_or_reply(event, "**╮ ❐.. جـاري الغاء حـظࢪه ..❏╰**")
    try:
        await event.client(EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS))
        await zedevent.edit(f"**⎉╎المستخـدم :** {_format.mentionuser(user.first_name ,user.id)}  \n**⎉╎تم الغـاء حظــࢪه .. بنجــاح✓**")
    except Exception as e:
        await zedevent.edit(f"**- خطــأ :**\n`{e}`")

@zedub.zed_cmd(pattern=f"{KICK}(?:\s|$)([\s\S]*)")
async def zed_kick_user_cmd(event): # اسم فريد
    user, reason = await get_user_from_event(event)
    if not user: return
    zedevent = await edit_or_reply(event, "**╮ ❐... جـاࢪِ الطــࢪد ...❏╰**")
    try:
        await event.client.kick_participant(event.chat_id, user.id)
        await zedevent.edit(f"**⎉╎تم طــࢪد**. [{user.first_name}](tg://user?id={user.id})  **بنجــاح ✓**")
    except Exception as e:
        return await zedevent.edit(f"{NO_PERM}\n{e}")

# ================================================
#   أوامر التثبيت (Pin)
# ================================================

@zedub.zed_cmd(pattern="تثبيت( بالاشعار|$)", command=("تثبيت", plugin_category))
async def zed_pin_cmd(event): # اسم فريد
    to_pin = event.reply_to_msg_id
    if not to_pin: return await edit_delete(event, "**- بالــرد ع رسـالـه لـ تثبيتـهـا...**", 5)
    options = event.pattern_match.group(1)
    is_silent = bool(options)
    try:
        await event.client.pin_message(event.chat_id, to_pin, notify=is_silent)
        await edit_delete(event, "**⎉╎تم تثبيـت الرسـالـه .. بنجــاح ✓**", 3)
    except BadRequestError:
        return await edit_delete(event, NO_PERM, 5)

@zedub.zed_cmd(pattern="الغاء تثبيت( الكل|$)", command=("الغاء تثبيت", plugin_category))
async def zed_unpin_cmd(event): # اسم فريد
    to_unpin = event.reply_to_msg_id
    options = (event.pattern_match.group(1)).strip()
    try:
        if options == "الكل":
            await event.client.unpin_message(event.chat_id)
            await edit_delete(event, "**⎉╎تم الغـاء تثبيـت كـل الرسـائـل .. بنجــاح ✓**", 3)
        elif to_unpin:
            await event.client.unpin_message(event.chat_id, to_unpin)
            await edit_delete(event, "**⎉╎تم الغـاء تثبيـت الرسـالـه .. بنجــاح ✓**", 3)
        else:
            return await edit_delete(event, "**- بالــرد ع رســالـه او استخـدم (الكل)**", 5)
    except BadRequestError:
        return await edit_delete(event, NO_PERM, 5)


from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.types import MessageEntityMentionName
import contextlib
import os

# --- إعدادات الآيدي الفخم (ZedThon Style) ---
ZED_TEXT = gvarstatus("CUSTOM_ALIVE_TEXT") or "•⎚• مـعلومـات المسـتخـدم مـن بـوت زدثــون"
ZEDM = gvarstatus("CUSTOM_ALIVE_EMOJI") or "✦ "
ZEDF = gvarstatus("CUSTOM_ALIVE_FONT") or "⋆─┄─┄─┄─ ᶻᵗʰᵒᶰ ─┄─┄─┄─⋆"
zelzal = (925972505, 1895219306, 5280339206)

async def fetch_info(replied_user, event):
    """Get details from the User object."""
    try:
        FullUser = (await event.client(GetFullUserRequest(replied_user.id))).full_user
    except:
        return None, "تعذر جلب المعلومات الكاملة"

    replied_user_profile_photos = await event.client(
        GetUserPhotosRequest(user_id=replied_user.id, offset=42, max_id=0, limit=80)
    )
    replied_user_profile_photos_count = "لا يـوجـد بروفـايـل"
    try:
        replied_user_profile_photos_count = replied_user_profile_photos.count
    except:
        pass
        
    user_id = replied_user.id
    first_name = replied_user.first_name
    full_name = FullUser.private_forward_name
    common_chat = FullUser.common_chats_count
    username = replied_user.username
    user_bio = FullUser.about
    
    # التحقق من البريميوم (طريقة حديثة)
    try:
        zilzal = replied_user.premium
    except:
        zilzal = False

    # تحميل الصورة
    photo = await event.client.download_profile_photo(
        user_id,
        Config.TMP_DOWNLOAD_DIRECTORY + str(user_id) + ".jpg",
        download_big=True,
    )
    
    first_name = first_name.replace("\u2060", "") if first_name else ("هذا المستخدم ليس له اسم أول")
    full_name = full_name or first_name
    username = "@{}".format(username) if username else ("لا يـوجـد")
    user_bio = "لا يـوجـد" if not user_bio else user_bio

    # الرتب (محدثة لتتوافق مع سورسنا)
    if user_id == Config.OWNER_ID:
        rotbat = "⌁ مـالك الحساب 𓀫 ⌁"
    elif user_id in Config.SUDO_USERS:
        rotbat = "⌁ مطـور مسـاعـد 𐏕⌁"
    elif user_id in zelzal:
        rotbat = "⌁ مطـور السـورس 𓄂𓆃 ⌁"
    else:
        rotbat = "⌁ العضـو 𓅫 ⌁"

    # بناء الكليشة الفخمة
    caption = f"<b> {ZED_TEXT} </b>\n"
    caption += f"ٴ<b>{ZEDF}</b>\n"
    caption += f"<b>{ZEDM}الاسـم    ⇠ </b> "
    caption += f'<a href="tg://user?id={user_id}">{full_name}</a>'
    caption += f"\n<b>{ZEDM}المعـرف  ⇠  {username}</b>"
    caption += f"\n<b>{ZEDM}الايـدي   ⇠ </b> <code>{user_id}</code>\n"
    caption += f"<b>{ZEDM}الرتبـــه   ⇠ {rotbat} </b>\n"
    
    if zilzal:
        caption += f"<b>{ZEDM}الحسـاب ⇠  بـريميـوم 🌟</b>\n"
    
    caption += f"<b>{ZEDM}الصـور    ⇠ </b> {replied_user_profile_photos_count}\n"
    
    if user_id != (await event.client.get_me()).id:
        caption += f"<b>{ZEDM}الـمجموعات المشتـركة ⇠ </b> {common_chat} \n"
    
    caption += f"<b>{ZEDM}البايـو     ⇠  {user_bio}</b> \n"
    caption += f"ٴ<b>{ZEDF}</b>"
    
    return photo, caption

# --- دالة واحدة للأمر (.ايدي و .ا) ---
@zedub.zed_cmd(pattern="(?:ايدي|ا)(?: |$)(.*)")
async def zed_who_cmd(event):
    "Gets info of an user"
    zed = await edit_or_reply(event, "⇆")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
        
    replied_user = await get_user_from_event(event) # نستخدم دالتنا الموجودة في الملف
    if not replied_user:
        return await edit_or_reply(zed, "**- لـم استطـع العثــور ع الشخــص ؟!**")

    try:
        photo, caption = await fetch_info(replied_user, event)
    except (AttributeError, TypeError) as e:
        return await edit_or_reply(zed, f"**- خطأ:** {e}")

    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None

    try:
        if photo:
            await event.client.send_file(
                event.chat_id,
                photo,
                caption=caption,
                link_preview=False,
                force_document=False,
                reply_to=message_id_to_reply,
                parse_mode="html",
            )
            if not photo.startswith("http"):
                os.remove(photo)
            await zed.delete()
        else:
            await zed.edit(caption, parse_mode="html")
    except TypeError:
        await zed.edit(caption, parse_mode="html")

# --- أمر صورته (إضافي) ---
@zedub.zed_cmd(pattern="صورته(?:\s|$)([\s\S]*)")
async def zed_poto_cmd(event):
    "To get user or group profile pic"
    uid = "".join(event.raw_text.split(maxsplit=1)[1:])
    user = await event.get_reply_message()
    chat = event.input_chat
    if user and user.sender:
        photos = await event.client.get_profile_photos(user.sender)
        u = True
    else:
        photos = await event.client.get_profile_photos(chat)
        u = False
    
    if uid.strip() == "":
        uid = 1
        if int(uid) > (len(photos)):
            return await edit_delete(event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **")
        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    elif uid.strip() == "الكل":
        if len(photos) > 0:
            await event.client.send_file(event.chat_id, photos)
        else:
            return await edit_delete(event, "**- لا يـوجـد صـور.**")
    else:
        try:
            uid = int(uid)
            if uid <= 0: return await edit_or_reply(event, "**- رقـم خـاطـئ . . .**")
        except:
            return await edit_or_reply(event, "**- رقـم خـاطـئ . . .**")
            
        if int(uid) > (len(photos)):
            return await edit_delete(event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **")

        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    await event.delete()