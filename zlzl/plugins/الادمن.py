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
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator
from telethon.utils import get_display_name
from datetime import datetime

# --- ☢️ أمـر الآيـدي الشيطـاني (ZedThon Devil ID) ☢️ ---
@zedub.zed_cmd(pattern="(?:ايدي|ا|ايديي)(?: |$)(.*)")
async def zed_id_devil(event):
    await edit_or_reply(event, "**⪼ جـارِ استدعـاء المعلومـات ... 🕷**")
    
    # 1. صيد الضحية
    input_str = event.pattern_match.group(1)
    if input_str:
        try:
            user = await event.client.get_entity(input_str)
        except:
            return await edit_delete(event, "**❌ هـذا المستخـدم في عالـم آخـر (غير موجود).**", 5)
    elif event.reply_to_msg_id:
        r_msg = await event.get_reply_message()
        if r_msg.sender_id:
            user = await event.client.get_entity(r_msg.sender_id)
        else:
            return await edit_delete(event, "**❌ شبـح! لا يمكـن جلـب معلوماتـه.**", 5)
    else:
        user = await event.client.get_me()

    # 2. استخراج البيانات
    try:
        full_user = await event.client(GetFullUserRequest(user.id))
        bio = full_user.full_user.about or "لم يكتـب شيئـاً، غامـض 🦇."
        bio = bio.replace("\n", " ")[:50] + "..." if len(bio) > 50 else bio
        photos_count = full_user.full_user.profile_photo.count if hasattr(full_user.full_user, 'profile_photo') and full_user.full_user.profile_photo else 0
        common_chats = full_user.full_user.common_chats_count
    except:
        bio = "بيانات مشفرة"
        photos_count = 0
        common_chats = 0

    # 3. عدد الرسائل
    msgs_count = "خـاص 🔒"
    if not event.is_private:
        try:
            results = await event.client(GetHistoryRequest(
                peer=event.chat_id, limit=0, offset_date=None, offset_id=0,
                max_id=0, min_id=0, add_offset=0, hash=0, from_user=user.id
            ))
            msgs_count = results.count
        except:
            msgs_count = "مجهول"

    # 4. الرتب
    if user.id == Config.OWNER_ID:
        sys_rank = "👑 زعـيـم السـورس 👑"
    elif user.id in Config.SUDO_USERS:
        sys_rank = "👮‍♂️ نائـب الزعيـم"
    elif user.bot:
        sys_rank = "🤖 خـادم آلـي"
    else:
        sys_rank = "👤 مـواطـن"

    group_rank = "لا يوجـد"
    if not event.is_private:
        try:
            participant = await event.client.get_permissions(event.chat_id, user.id)
            if participant.is_creator:
                group_rank = "الـرأس الكبيـرة (المنشئ) 🌟"
            elif participant.is_admin:
                group_rank = "رافـع خشمه (مشـرف) 👮‍♂️"
            else:
                group_rank = "عضـو مسكيـن 🙍‍♂️"

    # 5. تجهيز البيانات
    f_name = user.first_name or ""
    l_name = user.last_name or ""
    full_name = f"{f_name} {l_name}".strip()
    username = f"@{user.username}" if user.username else "بـدون يـوزر"
    
    # الهياط والكوميديا
    is_prem = "غنـي 🤑💎" if getattr(user, 'premium', False) else "فقيـر (مطفر) 💸"
    is_scam = "نصـاب (اهرب) 🏃‍♂️" if user.scam else "نظيـف ✨"
    is_rest = "مكلبـش (مقيد) ⛓️" if user.restricted else "حـر طليـق 🕊️"
    is_verif = "موثـق ✅" if user.verified else "غير موثق"
    
    # تخمين تاريخ الانضمام (تقريبي بناء على الآيدي)
    if user.id < 1000000000:
        join_date = "قديـم جـداً (ديناصور) 🦖"
    elif user.id < 5000000000:
        join_date = "مخضـرم (وسط) 🦅"
    else:
        join_date = "جديـد (ورع) 👶"

    dc_loc = f"DC {user.photo.dc_id}" if user.photo else "N/A"

    # 6. الكليشة
    caption = f"""
**𓆩 𝙕𝙏𝙝𝙤𝙣 𝙑𝙄𝙋 𝙄𝘿 - بطاقـة تعريـف 𓆪**
━━━━━━━━━━━━━━━━━━━━━━
**⚜️╎الاســم       :** `{full_name}`
**🎟╎الآيــدي       :** `{user.id}`
**🌀╎المعــرف      :** {username}
**🎖╎الرتبــة       :** {sys_rank}
**🏷╎المنصــب      :** {group_rank}
**📸╎الصــور       :** `{photos_count}`
**💬╎الرسائــل      :** `{msgs_count}`
**💰╎الوضـع المادي :** {is_prem}
**📝╎النبــذة        :** `{bio}`
**📡╎اتصـال الداتـا  :** {dc_loc}
**👥╎كروبات مشتركـة :** `{common_chats}`
**📅╎تاريخ الانضمام :** {join_date}
**⚠️╎سوابـق احتيـال :** {is_scam}
**🚫╎قيـود امنيــة   :** {is_rest}
**💠╎التوثيــق      :** {is_verif}
**🔗╎الرابـط الدائـم :** [اضغـط هنـا](tg://user?id={user.id})
━━━━━━━━━━━━━━━━━━━━━━
**𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - 𝗭𝗲𝗹𝗭𝗮𝗹 𓆪**
    """

    try:
        photo = await event.client.download_profile_photo(user.id)
        if photo:
            await event.client.send_file(event.chat_id, photo, caption=caption)
            await event.delete()
        else:
            await edit_or_reply(event, caption)
    except Exception as e:
        await edit_or_reply(event, caption)