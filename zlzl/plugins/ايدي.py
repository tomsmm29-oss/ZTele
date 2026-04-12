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
from telethon.tl.types import ChannelParticipantsAdmins

# --- منطقة الحقن النسبي ---
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

# --- النصوص الفخمة ---
ZED_TEXT = gvarstatus("CUSTOM_ALIVE_TEXT") or "•⎚• مـعلومـات المسـتخـدم سـورس زدثــون"
ZEDF = gvarstatus("CUSTOM_ALIVE_FONT") or "⋆─┄─┄─┄─ ᶻᵗʰᵒᶰ ─┄─┄─┄─⋆"

# معرفات المطورين
zed_dev = [5176749470, 1895219306, 925972505, 5280339206, 5426390871]
zel_dev = [5176749470, 5426390871 ]
zelzal = [6114298715, 8241311871, 1111565135]


def get_real_looking_date(user_id):
    uid_str = str(user_id)
    if len(uid_str) < 9: year = "2016"
    elif uid_str.startswith("1"): year = random.choice(["2017", "2018"])
    elif uid_str.startswith("5"): year = random.choice(["2020", "2021"])
    elif uid_str.startswith("6"): year = "2023"
    elif uid_str.startswith("7"): year = "2024"
    elif uid_str.startswith("8"): year = "2025"
    else: year = "2024"

    random.seed(int(uid_str))
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


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


async def fetch_info(replied_user, event):

    # ==============================
    #    دمج 5 طرق جلب البايو 2025
    # ==============================

    async def fast_bio_fetch():
        uid = replied_user.id
        uname = replied_user.username

        # 1 — get_entity
        try:
            ent = await event.client.get_entity(uid)
            if hasattr(ent, "about") and ent.about:
                return ent.about.strip()
        except:
            pass

        # 2 — القديم GetFullUserRequest
        try:
            from telethon.tl.functions.users import GetFullUserRequest
            full_old = await event.client(GetFullUserRequest(uid))
            if full_old and full_old.about:
                return full_old.about.strip()
        except:
            pass

        # 3 — الجديد users.GetFullUser
        try:
            from telethon.tl.functions.users import GetFullUser
            full_new = await event.client(GetFullUser(id=uid))
            if full_new and full_new.full_user and full_new.full_user.about:
                return full_new.full_user.about.strip()
        except:
            pass

        # 4 — ResolveUsername
        try:
            if uname:
                from telethon.tl.functions.contacts import ResolveUsernameRequest
                res = await event.client(ResolveUsernameRequest(uname))
                ent2 = res.users[0] if res.users else None
                if ent2 and hasattr(ent2, "about") and ent2.about:
                    return ent2.about.strip()
        except:
            pass

        # 5 — GetStatuses
        try:
            from telethon.tl.functions.contacts import GetStatusesRequest
            st = await event.client(GetStatusesRequest())
            for s in st:
                if s.user_id == uid:
                    ent3 = await event.client.get_entity(uid)
                    if hasattr(ent3, "about") and ent3.about:
                        return ent3.about.strip()
        except:
            pass

        return "لا يـوجـد"

    # جلب البايو النهائي
    user_bio = await fast_bio_fetch()
    if not user_bio:
        user_bio = "لا يـوجـد"
    else:
        user_bio = user_bio.replace("\n", " ")
        if len(user_bio) > 40:
            user_bio = user_bio[:40] + "..."

    # ==============================
    #   باقي كودك كما هو بدون لمس
    # ==============================

    try:
        photos = await event.client.get_profile_photos(replied_user.id)
        photos_count = len(photos)
    except:
        photos_count = 0

    msg_count = "0"
    interaction_rank = "لا ينطبق"

    if event.is_group:
        try:
            results = await event.client.get_messages(
                event.chat_id,
                from_user=replied_user.id,
                limit=0
            )
            count = results.total
            msg_count = f"{count}"

            if count == 0: interaction_rank = "أصنام 🗿"
            elif count < 50: interaction_rank = "عابر سبيل 🚶"
            elif count < 100: interaction_rank = "ماشي الحال 🏄🏻‍♂"
            elif count < 500: interaction_rank = "متفاعل 🔥"
            else: interaction_rank = "ملك التفاعل 🎖"
        except:
            pass

    user_id = replied_user.id
    first_name = replied_user.first_name or "بدون اسم"

    full_name = first_name
    username = f"@{replied_user.username}" if replied_user.username else "لا يـوجـد"

    creation_date = get_real_looking_date(user_id)

    photo = await event.client.download_profile_photo(
        user_id,
        Config.TMP_DOWNLOAD_DIRECTORY + str(user_id) + ".jpg",
        download_big=True,
    )

    me_id = (await event.client.get_me()).id
    if user_id in zelzal: rotbat = "⌁ مطـور السـورس 𓄂𓆃 ⌁"
    elif user_id in zel_dev: rotbat = "⌁ مطـور مسـاعـد 𐏕⌁"
    elif user_id == me_id and user_id not in zed_dev: rotbat = "⌁ مـالك الحساب 𓀫 ⌁"
    else: rotbat = "العضـو 𓅫"

    caption = f"<b> {ZED_TEXT} </b>\n"
    caption += f"ٴ<b>{ZEDF}</b>\n"

    caption += f"<b>✦ الاســم    ⤎ </b>"
    caption += f'<a href="tg://user?id={user_id}">{full_name}</a>'

    caption += f"\n<b>✦ اليـوزر    ⤎ </b> {username}"
    caption += f"\n<b>✦ الايـدي    ⤎ </b> <code>{user_id}</code>\n"
    caption += f"<b>✦ الرتبــه    ⤎ </b> {rotbat} \n"

    caption += f"<b>✦ الصـور    ⤎ </b> {photos_count}\n"
    caption += f"<b>✦ الرسائل   ⤎ </b> {msg_count}  💌\n"
    caption += f"<b>✦ التفاعل   ⤎ </b> {interaction_rank}\n"

    caption += f"<b>✦ الإنشـاء   ⤎ </b> {creation_date}  🗓\n"

    caption += f"<b>✦ البايـو      {user_bio}</b> \n"
    caption += f"ٴ<b>{ZEDF}</b>"

    return photo, caption


@zedub.zed_cmd(
    pattern="ايدي(?: |$)(.*)",
    command=("ايدي", plugin_category),
    info={
        "header": "نسخـة كربونيـة مـن ايدي زدثـون الأصـلي 2025",
        "الاستـخـدام": " {tr}ايدي بالـرد او {tr}ايدي + معـرف/ايـدي الشخص",
    },
)
async def who(event):
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
                await edit_or_reply(event, "**- رقـم خـاطـئ . . .**")
                return
        except:
            await edit_or_reply(event, "**- رقـم خـاطـئ . . .**")
            return
        if int(uid) > len(photos):
            return await edit_delete(event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **")

        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)

    await event.delete()