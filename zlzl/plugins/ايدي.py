# Zed-Thon - ZelZal (Luxury Edition 2025 by Mikey)
# "Stolen" Logic + New Statistics + Relative Imports
# Matches the exact requested "Fakhama" design

import contextlib
import html
import os
import base64
from datetime import datetime
from requests import get
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.tl.types import MessageEntityMentionName
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import ChannelParticipantsAdmins

# --- منطقة الحقن النسبي (The Relative Injection) ---
from . import zedub
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply

# محاولة استدعاء قاعدة البيانات
try:
    from ..sql_helper.globals import gvarstatus
except ImportError:
    def gvarstatus(val): return None

plugin_category = "العروض"
LOGS = logging.getLogger(__name__)

# --- النصوص الفخمة (كما طلبت بالضبط) ---
ZED_TEXT = gvarstatus("CUSTOM_ALIVE_TEXT") or "•⎚• مـعلومـات المسـتخـدم سـورس زدثــون"
ZEDF = gvarstatus("CUSTOM_ALIVE_FONT") or "⋆─┄─┄─┄─ ᶻᵗʰᵒᶰ ─┄─┄─┄─⋆"

# معرفات المطورين
zed_dev = [5176749470, 1895219306, 925972505, 5280339206, 5426390871]
zel_dev = [5176749470, 5426390871]
zelzal = [925972505, 1895219306, 5280339206]

def get_creation_date(user_id):
    """
    خوارزمية مايكي لتقدير تاريخ إنشاء الحساب بناءً على الآيدي
    """
    uid_str = str(user_id)
    # هذه تقديرات تقريبية بناءً على تاريخ التليجرام
    if len(uid_str) < 9:
        return "2015-2016 🕰"
    if uid_str.startswith("1"):
        return "2019-2020 🗓"
    if uid_str.startswith("5"):
        return "2021-2022 🗓"
    if uid_str.startswith("6"):
        return "2023 🗓"
    if uid_str.startswith("7"):
        return "2024 🗓"
    if uid_str.startswith("8"):
        return "2025 🗓"
    return "قـديم جـداً 🦕"

async def get_user_from_event_local(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_object = await event.client.get_entity(previous_message.sender_id)
    else:
        user = event.pattern_match.group(1)
        if user.isnumeric():
            user = int(user)
        if not user:
            self_user = await event.client.get_me()
            user = self_user.id
        if event.message.entities:
            probable_user_mention_entity = event.message.entities[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        if isinstance(user, int) or user.startswith("@"):
            user_obj = await event.client.get_entity(user)
            return user_obj
        try:
            user_object = await event.client.get_entity(user)
        except (TypeError, ValueError):
            return None
    return user_object

async def fetch_info(replied_user, event):
    """جلب التفاصيل وحشوها في اللوحة الفخمة"""
    
    # 1. جلب المعلومات الكاملة (Bio, Common Chats)
    try:
        full_user_req = await event.client(GetFullUserRequest(replied_user.id))
        FullUser = full_user_req.full_user
    except:
        FullUser = None

    # 2. جلب الصور
    try:
        photos = await event.client.get_profile_photos(replied_user.id)
        photos_count = len(photos)
    except:
        photos_count = 0

    # 3. حساب عدد الرسائل والتفاعل (حصري لمايكي)
    # يعمل فقط داخل المجموعات
    msg_count = 0
    interaction_rank = "غير معروف ☁️"
    if event.is_group:
        try:
            # نبحث عن عدد الرسائل (Count only) ليكون سريعاً
            results = await event.client.get_messages(
                event.chat_id, 
                from_user=replied_user.id, 
                limit=0
            )
            msg_count = results.total
            
            # تقييم التفاعل
            if msg_count == 0:
                interaction_rank = "أصنام 🗿"
            elif msg_count < 50:
                interaction_rank = "عابر سبيل 🚶"
            elif msg_count < 200:
                interaction_rank = "ماشي الحال 🏄🏻‍♂"
            elif msg_count < 500:
                interaction_rank = "متفاعل 🔥"
            else:
                interaction_rank = "ملك التفاعل 🎖"
        except:
            msg_count = "مخفي"
            interaction_rank = "لا يمكن الحساب"
    else:
        msg_count = "خاص"
        interaction_rank = "لا ينطبق"

    # 4. تجهيز البيانات الأساسية
    user_id = replied_user.id
    first_name = replied_user.first_name or "بدون اسم"
    # نحاول جلب الاسم الكامل من الريكويست الكامل
    full_name = getattr(FullUser, 'private_forward_name', first_name) if FullUser else first_name
    full_name = full_name or first_name # تأكيد
    
    username = f"@{replied_user.username}" if replied_user.username else "لا يـوجـد"
    
    # البايو
    user_bio = getattr(FullUser, 'about', "لا يـوجـد") if FullUser else "لا يـوجـد"
    user_bio = user_bio.replace("\n", " ") if user_bio else "لا يـوجـد" # إزالة النزول لسطر جديد لتنسيق أجمل

    # المجموعات المشتركة
    common_chat = getattr(FullUser, 'common_chats_count', 0) if FullUser else 0
    
    # تاريخ الانشاء التقريبي
    creation_date = get_creation_date(user_id)

    # تحميل الصورة الشخصية
    photo = await event.client.download_profile_photo(
        user_id,
        Config.TMP_DOWNLOAD_DIRECTORY + str(user_id) + ".jpg",
        download_big=True,
    )

    # 5. منطق الرتب (Rank Logic)
    me_id = (await event.client.get_me()).id
    if user_id in zelzal:
        rotbat = "⌁ مطـور السـورس 𓄂𓆃 ⌁" 
    elif user_id in zel_dev:
        rotbat = "⌁ مطـور مسـاعـد 𐏕⌁" 
    elif user_id == me_id and user_id not in zed_dev:
        rotbat = "⌁ مـالك الحساب 𓀫 ⌁" 
    else:
        rotbat = "⌁ العضـو 𓅫 ⌁"

    # 6. بناء اللوحة الفنية (نفس التنسيق المطلوب)
    caption = f"<b> {ZED_TEXT} </b>\n"
    caption += f"ٴ<b>{ZEDF}</b>\n"
    
    caption += f"<b>✦ الاســم    ⤎ </b> "
    caption += f'<a href="tg://user?id={user_id}">{full_name}</a>'
    
    caption += f"\n<b>✦ اليـوزر    ⤎  {username}</b>"
    caption += f"\n<b>✦ الايـدي    ⤎ </b> <code>{user_id}</code>\n"
    caption += f"<b>✦ الرتبــه    ⤎ {rotbat} </b>\n"
    
    caption += f"<b>✦ الصـور    ⤎ </b> {photos_count}\n"
    caption += f"<b>✦ الرسائل   ⤎ </b> {msg_count}  💌\n"
    caption += f"<b>✦ التفاعل   ⤎  {interaction_rank}</b>\n"
    
    if user_id != me_id:
        caption += f"<b>✦ الـمجموعات المشتـركة ⤎ </b> {common_chat} \n"
        
    caption += f"<b>✦ الإنشـاء   ⤎  {creation_date}</b>\n"
    caption += f"<b>✦ البايـو     ⤎  {user_bio}</b> \n"
    
    caption += f"ٴ<b>{ZEDF}</b>"
    
    return photo, caption


@zedub.zed_cmd(
    pattern="ايدي(?: |$)(.*)",
    command=("ايدي", plugin_category),
    info={
        "header": "لـ عـرض معلومـات الشخـص بستايل فخـم",
        "الاستـخـدام": " {tr}ايدي بالـرد او {tr}ايدي + معـرف/ايـدي الشخص",
    },
)
async def who(event):
    "Gets info of an user"
    zed = await edit_or_reply(event, "⇆")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    
    replied_user = await get_user_from_event_local(event)
    
    try:
        photo, caption = await fetch_info(replied_user, event)
    except (AttributeError, TypeError) as e:
        return await edit_or_reply(zed, "**- لـم استطـع العثــور ع الشخــص ؟!**")
    
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
    except Exception as e:
        await zed.edit(f"**Error:** {str(e)}")


@zedub.zed_cmd(
    pattern="ا(?: |$)(.*)",
    command=("ا", plugin_category),
    info={
        "header": "امـر مختصـر لـ عـرض معلومـات الشخـص",
        "الاستـخـدام": " {tr}ا بالـرد او {tr}ا + معـرف/ايـدي الشخص",
    },
)
async def who_short(event):
    return await who(event)


@zedub.zed_cmd(
    pattern="صورته(?:\s|$)([\s\S]*)",
    command=("صورته", plugin_category),
    info={
        "header": "لـ جـلب بـروفـايـلات الشخـص",
        "الاستـخـدام": [
            "{tr}صورته + عدد",
            "{tr}صورته الكل",
            "{tr}صورته",
        ],
    },
)
async def potocmd(event):
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
        if len(photos) == 0:
             return await edit_delete(event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **")
        if int(uid) > (len(photos)):
            return await edit_delete(
                event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **"
            )
        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    
    elif uid.strip() == "الكل":
        if len(photos) > 0:
            await event.client.send_file(event.chat_id, photos)
        else:
            try:
                if u:
                    photo = await event.client.download_profile_photo(user.sender)
                else:
                    photo = await event.client.download_profile_photo(event.input_chat)
                await event.client.send_file(event.chat_id, photo)
            except Exception:
                return await edit_delete(event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **")
    else:
        try:
            uid = int(uid)
            if uid <= 0:
                await edit_or_reply(event, "**- رقـم خـاطـئ . . .**")
                return
        except BaseException:
            await edit_or_reply(event, "**- رقـم خـاطـئ . . .**")
            return
        if int(uid) > (len(photos)):
            return await edit_delete(
                event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **"
            )

        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    await event.delete()