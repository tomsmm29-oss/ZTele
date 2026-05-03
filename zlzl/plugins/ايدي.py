import contextlib
import html
import os
import base64
import random
from datetime import datetime
from requests import get

from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.tl.types import MessageEntityMentionName
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest

from . import zedub
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply

# محاول استدعا قاعدة البيانات
try:
    from ..sql_helper.globals import gvarstatus
except ImportError:
    def gvarstatus(val):
        return None

plugin_category = "العروض"
LOGS = logging.getLogger(__name__)

# --- نصوص الكليشة الفخمة (تصميم زدثون) ---
ZED_TEXT = gvarstatus("CUSTOM_ALIVE_TEXT") or "•⎚• مـعلومـات المسـتخـدم مـن بـوت زدثــون"
ZEDM = gvarstatus("CUSTOM_ALIVE_EMOJI") or "✦ "

# التحقق من الخطوط المخصصة أو وضع خطوط زدثون المطلوبة
CUSTOM_FONT = gvarstatus("CUSTOM_ALIVE_FONT")
ZEDF_TOP = CUSTOM_FONT or "⋆─┄─┄─┄─ 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉─┄─┄─┄─⋆"
ZEDF_BOT = CUSTOM_FONT or "⋆─┄─┄─┄─   🛂 ─┄─┄─┄─⋆"

# معرفات المطورين مدمجة (أيديك هو الأول والأساسي)
zed_dev =[6114298715, 1207625726, 6060337233, 5176749470, 1895219306, 925972505, 5280339206, 5426390871]
zel_dev =[6114298715, 1207625726, 6060337233, 5176749470, 5426390871]
zelzal =[6114298715, 1207625726, 1264384082, 8241311871, 1111565135]

# --- نظام التواريخ المطور ---
def get_real_looking_date(user_id):
    uid_str = str(user_id)
    if len(uid_str) < 9: year = random.choice(["2015", "2016"])
    elif uid_str.startswith("1"): year = random.choice(["2017", "2018", "2019"])
    elif uid_str.startswith("5"): year = random.choice(["2020", "2021", "2022"])
    elif uid_str.startswith("6"): year = random.choice(["2022", "2023"])
    elif uid_str.startswith("7"): year = random.choice(["2024", "2025"])
    elif uid_str.startswith("8"): year = "2026"
    else: year = "2026"

    random.seed(int(uid_str))
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"

# --- محرك البحث عن المستخدم الحديث ---
async def get_user_from_event_local(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        if previous_message.forward:
            replied_user = await event.client.get_entity(previous_message.forward.sender_id)
        else:
            replied_user = await event.client.get_entity(previous_message.sender_id)
        return replied_user
    else:
        input_str = event.pattern_match.group(1)
        if not input_str:
            return await event.client.get_me()
        try:
            if input_str.isnumeric():
                user = await event.client.get_entity(int(input_str))
            else:
                user = await event.client.get_entity(input_str)
            return user
        except:
            return None

# --- جلب البيانات القوي وبناء الكليشة المطلوبة ---
async def fetch_info(replied_user, event):
    user_id = replied_user.id
    me_id = (await event.client.get_me()).id
    common_chat = 0

    # 5 طرق قوية لجلب البايو والمجموعات المشتركة بدون أخطاء
    async def fast_bio_fetch():
        nonlocal common_chat
        uid = replied_user.id
        uname = replied_user.username

        try:
            ent = await event.client.get_entity(uid)
            if hasattr(ent, "about") and ent.about: return ent.about.strip()
        except: pass

        try:
            full_old = await event.client(GetFullUserRequest(uid))
            if full_old:
                if hasattr(full_old, "common_chats_count"):
                    common_chat = full_old.common_chats_count
                if full_old.about: return full_old.about.strip()
                if full_old.full_user and full_old.full_user.about: return full_old.full_user.about.strip()
        except: pass

        try:
            from telethon.tl.functions.users import GetFullUser
            full_new = await event.client(GetFullUser(id=uid))
            if full_new and full_new.full_user:
                if hasattr(full_new.full_user, "common_chats_count"):
                    common_chat = full_new.full_user.common_chats_count
                if full_new.full_user.about: return full_new.full_user.about.strip()
        except: pass

        try:
            if uname:
                from telethon.tl.functions.contacts import ResolveUsernameRequest
                res = await event.client(ResolveUsernameRequest(uname))
                ent2 = res.users[0] if res.users else None
                if ent2 and hasattr(ent2, "about") and ent2.about: return ent2.about.strip()
        except: pass

        try:
            from telethon.tl.functions.contacts import GetStatusesRequest
            st = await event.client(GetStatusesRequest())
            for s in st:
                if s.user_id == uid:
                    ent3 = await event.client.get_entity(uid)
                    if hasattr(ent3, "about") and ent3.about: return ent3.about.strip()
        except: pass

        return "لا يـوجـد"

    # البايو
    user_bio = await fast_bio_fetch()
    if not user_bio:
        user_bio = "لا يـوجـد"
    else:
        user_bio = user_bio.replace("\n", " ")

    # جلب الصور
    try:
        photos = await event.client.get_profile_photos(user_id)
        replied_user_profile_photos_count = len(photos)
    except:
        replied_user_profile_photos_count = "لا يـوجـد بروفـايـل"

    # المتغيرات الأساسية
    first_name = replied_user.first_name
    first_name = first_name.replace("\u2060", "") if first_name else "هذا المستخدم ليس له اسم أول"
    full_name = first_name
    username = f"@{replied_user.username}" if replied_user.username else "لا يـوجـد"
    creation_date = get_real_looking_date(user_id)

    photo = await event.client.download_profile_photo(
        user_id,
        Config.TMP_DOWNLOAD_DIRECTORY + str(user_id) + ".jpg",
        download_big=True,
    )

    # الرتب 
    if user_id in zelzal:
        rotbat = "⌁ مطـور السـورس 𓄂𓆃 ⌁" 
    elif user_id in zel_dev:
        rotbat = "⌁ مطـور مسـاعـد 𐏕⌁" 
    elif user_id == me_id and user_id not in zed_dev:
        rotbat = "⌁ مـالك الحساب 𓀫 ⌁" 
    else:
        rotbat = "⌁ العضـو 𓅫 ⌁"

    # =========================================================
    # الكليشة - ظهور البريميوم دائماً وإضافة التصميم المطلوب
    # =========================================================
    caption = f"<b> {ZED_TEXT} </b>\n"
    caption += f"ٴ<b>{ZEDF_TOP}</b>\n"
    caption += f"<b>{ZEDM}الاسـم    ⇠ </b> "
    caption += f'<a href="tg://user?id={user_id}">{full_name}</a>'
    caption += f"\n<b>{ZEDM}المعـرف  ⇠  {username}</b>"
    caption += f"\n<b>{ZEDM}الايـدي   ⇠ </b> <code>{user_id}</code>\n"
    caption += f"<b>{ZEDM}الرتبـــه   ⇠ {rotbat} </b>\n"
    
    # سطر البريميوم صار ثابت دائماً بدون أي شرط
    caption += f"<b>{ZEDM}الحسـاب ⇠  بـريميـوم 🌟</b>\n"
        
    caption += f"<b>{ZEDM}الصـور    ⇠ </b> {replied_user_profile_photos_count}\n"
    
    if user_id != me_id:
        caption += f"<b>{ZEDM}الـمجموعات المشتـركة ⇠ </b> {common_chat} \n"
        
    caption += f"<b>{ZEDM}الانشـاء  ⇠ </b> {creation_date} \n"
    caption += f"<b>{ZEDM}البايـو     ⇠  {user_bio}</b> \n"
    caption += f"ٴ<b>{ZEDF_BOT}</b>"

    return photo, caption


@zedub.zed_cmd(
    pattern="ايدي(?: |$)(.*)",
    command=("ايدي", plugin_category),
    info={
        "header": "لـ عـرض معلومـات الشخـص",
        "الاستـخـدام": "{tr}ايدي بالـرد او {tr}ايدي + معـرف/ايـدي الشخص",
    },
)
async def who_id(event):
    "Gets info of an user"
    zed = await edit_or_reply(event, "⇆")
    
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)

    replied_user = await get_user_from_event_local(event)
    if not replied_user:
        return await edit_or_reply(zed, "**- لـم استطـع العثــور ع الشخــص (تأكد من المعرف) ؟!**")

    try:
        photo, caption = await fetch_info(replied_user, event)
    except:
        return await edit_or_reply(zed, "**- حدث خطأ غير متوقع، حاول مرة أخرى!**")

    message_id_to_reply = event.message.reply_to_msg_id or None

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
    except:
        await zed.edit(caption, parse_mode="html")


@zedub.zed_cmd(
    pattern="ا(?: |$)(.*)",
    command=("ا", plugin_category),
    info={
        "header": "امـر مختصـر لـ عـرض معلومـات الشخـص",
        "الاستـخـدام": " {tr}ا بالـرد او {tr}ا + معـرف/ايـدي الشخص",
    },
)
async def who_short(event):
    return await who_id(event)


@zedub.zed_cmd(
    pattern="صورته(?:\s|$)([\s\S]*)",
    command=("صورته", plugin_category),
    info={
        "header": "لـ جـلب بـروفـايـلات الشخـص",
        "الاستـخـدام":[
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
        if int(uid) > len(photos):
            return await edit_delete(event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **")
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
            except:
                return await edit_delete(event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **")
    else:
        try:
            uid = int(uid)
            if uid <= 0:
                return await edit_or_reply(event, "**- رقـم خـاطـئ . . .**")
        except:
            return await edit_or_reply(event, "**- رقـم خـاطـئ . . .**")
            
        if int(uid) > len(photos):
            return await edit_delete(event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **")

        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)

    await event.delete()