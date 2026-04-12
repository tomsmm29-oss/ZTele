#𝙕𝙏𝙝𝙤𝙣 ®
#الملـف حقـوق وكتابـة زلـزال الهيبـه ⤶ @zzzzl1l خاص بسـورس ⤶ 𝙕𝙏𝙝𝙤𝙣
#الملـف متعـوب عليه تخمـط اذكر المصـدر
#تعـديل بنيـتي 𝙈

import os
import random
from asyncio import sleep

from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName
from telethon.utils import get_input_location

from . import zedub
from ..core.logger import logging

from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete
from ..helpers import reply_id
from . import *
from . import mention

plugin_category = "العروض"
LOGS = logging.getLogger(__name__)

sts_animal = "https://telegra.ph/file/720a8d292301289bb7ca4.mp4"#مطي
sts_animal2 = "https://telegra.ph/file/fa43723297d16ebccfa94.mp4" #كلب
sts_animal3 = "https://telegra.ph/file/bc4c35ca805ab9e4ef8d7.mp4"#قرد
sts_animal4 = "https://telegra.ph/file/7cc42816b3e161f7183b6.mp4"#صخل
sts_animal5 = "https://telegra.ph/file/8beaf555e0d4e3f00c294.mp4"#طلي
sts_animal6 = "https://telegra.ph/file/c34cb870037a4ed2be972.mp4"#بزون
sts_animal7 = "https://telegra.ph/file/c499feb6a51dea16a1fe5.mp4"#ابو بريص
sts_animal8 = "https://telegra.ph/file/19b193f06d680e3ec79c0.mp4"#جريذي
sts_animal9 = "https://telegra.ph/file/cd1fcb86af78d83ba9002.mp4"#هايشه

jjj = [
    "100% مو حيوان غنبله 😱😂.",
    "90% مو حيوان ضيم 😱😂👆",
    "80%  ٴ😱😂",
    "70%  ٴ😱😂",
    "60% براسه 60 حظ 👌😂",
    "50% حيوان هجين👍😂",
    "( 40% ) خوش حيوان 👌😂",
    "30% ٴ😒😂",
    "20% ٴ😒😂",
    "10% ٴ😒😂",
    "0% ٴ😢😂",
]


ZEED_IMG = sts_animal or sts_animal2 or sts_animal3 or sts_animal4 or sts_animal5 or sts_animal6 or sts_animal7 or sts_animal8 or sts_animal9


async def get_user_from_event(event):
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
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None
    return user_object


async def fetch_info(replied_user, event):
    """Get details from the User object."""
    FullUser = (await event.client(GetFullUserRequest(replied_user.id))).full_user
    replied_user_profile_photos = await event.client(
        GetUserPhotosRequest(user_id=replied_user.id, offset=42, max_id=0, limit=80)
    )
    replied_user_profile_photos_count = "الحيوان مامخلي بروفايل"
    try:
        replied_user_profile_photos_count = replied_user_profile_photos.count
    except AttributeError:
        pass
    user_id = replied_user.id
    first_name = replied_user.first_name
    last_name = replied_user.last_name
    full_name = FullUser.private_forward_name
    common_chat = FullUser.common_chats_count
    username = replied_user.username
    yoy = random.choice(jjj)
    ZEED_IMG
    x = random.randrange(1, 9)
    if x == 1:
       username = "@{}".format(username) if username else ("لايوجد معرف")
       caption = f"<b>  ╮•🦦 الحيوان ⇦ </b> {first_name} {last_name} \n"
       caption += f"<b> ٴ╼──────────────────╾ </b>\n"
       caption += f"<b> • 🌚 | معـرفه  ⇦ </b> {username}\n"
       caption += f"<b> • 🌚 | ايـديه   ⇦ </b> <code>{user_id}</code>\n"
       caption += f"<b> • 🌚 | صـوره  ⇦ </b> {replied_user_profile_photos_count} </b>\n"
       caption += f"<b> • 🌚 | نــوعه   ⇦  مطي زربه 🦓 </b>\n"
       caption += f"<b> • 🌚 | نسبتـه  ⇦  {yoy} </b>\n\n\n"
       caption += f"<b> 𓆩 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿 𓆪 </b> - @ZThon "
       return sts_animal, caption
    if x == 2:
       username = "@{}".format(username) if username else ("لايوجد معرف")
       caption = f"<b>  ╮•🦦 الحيوان ⇦ </b> {first_name} {last_name} \n"
       caption += f"<b> ٴ╼──────────────────╾ </b>\n"
       caption += f"<b> • 🌚 | معـرفه  ⇦ </b> {username}\n"
       caption += f"<b> • 🌚 | ايـديه   ⇦ </b> <code>{user_id}</code>\n"
       caption += f"<b> • 🌚 | صـوره  ⇦ </b> {replied_user_profile_photos_count} </b>\n"
       caption += f"<b> • 🌚 | نــوعه   ⇦  جلب شوارع 🐕‍🦺 </b>\n"
       caption += f"<b> • 🌚 | نسبتـه  ⇦  {yoy} </b>\n\n\n"
       caption += f"<b> 𓆩 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿 𓆪 </b> - @ZThon "
       return sts_animal2, caption
    if x == 3:
       username = "@{}".format(username) if username else ("لايوجد معرف")
       caption = f"<b>  ╮•🦦 الحيوان ⇦ </b> {first_name} {last_name} \n"
       caption += f"<b> ٴ╼──────────────────╾ </b>\n"
       caption += f"<b> • 🌚 | معـرفه  ⇦ </b> {username}\n"
       caption += f"<b> • 🌚 | ايـديه   ⇦ </b> <code>{user_id}</code>\n"
       caption += f"<b> • 🌚 | صـوره  ⇦ </b> {replied_user_profile_photos_count} </b>\n"
       caption += f"<b> • 🌚 | نــوعه   ⇦  قرد لزكـه 🐒 </b>\n"
       caption += f"<b> • 🌚 | نسبتـه  ⇦  {yoy} </b>\n\n\n"
       caption += f"<b> 𓆩 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿 𓆪 </b> - @ZThon "
       return sts_animal3, caption
    if x == 4:
       username = "@{}".format(username) if username else ("لايوجد معرف")
       caption = f"<b>  ╮•🦦 الحيوان ⇦ </b> {first_name} {last_name} \n"
       caption += f"<b> ٴ╼──────────────────╾ </b>\n"
       caption += f"<b> • 🌚 | معـرفه  ⇦ </b> {username}\n"
       caption += f"<b> • 🌚 | ايـديه   ⇦ </b> <code>{user_id}</code>\n"
       caption += f"<b> • 🌚 | صـوره  ⇦ </b> {replied_user_profile_photos_count} </b>\n"
       caption += f"<b> • 🌚 | نــوعه   ⇦  صخل محترم 🐐 </b>\n"
       caption += f"<b> • 🌚 | نسبتـه  ⇦  {yoy} </b>\n\n\n"
       caption += f"<b> 𓆩 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿 𓆪 </b> - @ZThon "
       return sts_animal4, caption
    if x == 5:
       username = "@{}".format(username) if username else ("لايوجد معرف")
       caption = f"<b>  ╮•🦦 الحيوان ⇦ </b> {first_name} {last_name} \n"
       caption += f"<b> ٴ╼──────────────────╾ </b>\n"
       caption += f"<b> • 🌚 | معـرفه  ⇦ </b> {username}\n"
       caption += f"<b> • 🌚 | ايـديه   ⇦ </b> <code>{user_id}</code>\n"
       caption += f"<b> • 🌚 | صـوره  ⇦ </b> {replied_user_profile_photos_count} </b>\n"
       caption += f"<b> • 🌚 | نــوعه   ⇦  طلي ابو البعرور الوصخ 🐑 </b>\n"
       caption += f"<b> • 🌚 | نسبتـه  ⇦  {yoy} </b>\n\n\n"
       caption += f"<b> 𓆩 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿 𓆪 </b> - @ZThon "
       return sts_animal5, caption
    if x == 6:
       username = "@{}".format(username) if username else ("لايوجد معرف")
       caption = f"<b>  ╮•🦦 الحيوان ⇦ </b> {first_name} {last_name} \n"
       caption += f"<b> ٴ╼──────────────────╾ </b>\n"
       caption += f"<b> • 🌚 | معـرفه  ⇦ </b> {username}\n"
       caption += f"<b> • 🌚 | ايـديه   ⇦ </b> <code>{user_id}</code>\n"
       caption += f"<b> • 🌚 | صـوره  ⇦ </b> {replied_user_profile_photos_count} </b>\n"
       caption += f"<b> • 🌚 | نــوعه   ⇦  بزون ابوخالد 🐈 </b>\n"
       caption += f"<b> • 🌚 | نسبتـه  ⇦  {yoy} </b>\n\n\n"
       caption += f"<b> 𓆩 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿 𓆪 </b> - @ZThon "
       return sts_animal6, caption
    if x == 7:
       username = "@{}".format(username) if username else ("لايوجد معرف")
       caption = f"<b>  ╮•🦦 الحيوان ⇦ </b> {first_name} {last_name} \n"
       caption += f"<b> ٴ╼──────────────────╾ </b>\n"
       caption += f"<b> • 🌚 | معـرفه  ⇦ </b> {username}\n"
       caption += f"<b> • 🌚 | ايـديه   ⇦ </b> <code>{user_id}</code>\n"
       caption += f"<b> • 🌚 | صـوره  ⇦ </b> {replied_user_profile_photos_count} </b>\n"
       caption += f"<b> • 🌚 | نــوعه   ⇦  الزاحف ابو بريص 🦎 </b>\n"
       caption += f"<b> • 🌚 | نسبتـه  ⇦  {yoy} </b>\n\n\n"
       caption += f"<b> 𓆩 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿 𓆪 </b> - @ZThon "
       return sts_animal7, caption
    if x == 8:
       username = "@{}".format(username) if username else ("لايوجد معرف")
       caption = f"<b>  ╮•🦦 الحيوان ⇦ </b> {first_name} {last_name} \n"
       caption += f"<b> ٴ╼──────────────────╾ </b>\n"
       caption += f"<b> • 🌚 | معـرفه  ⇦ </b> {username}\n"
       caption += f"<b> • 🌚 | ايـديه   ⇦ </b> <code>{user_id}</code>\n"
       caption += f"<b> • 🌚 | صـوره  ⇦ </b> {replied_user_profile_photos_count} </b>\n"
       caption += f"<b> • 🌚 | نــوعه   ⇦  جريذي ابو المجاري 🐀 </b>\n"
       caption += f"<b> • 🌚 | نسبتـه  ⇦  {yoy} </b>\n\n\n"
       caption += f"<b> 𓆩 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿 𓆪 </b> - @ZThon "
       return sts_animal8, caption
    if x == 9:
       username = "@{}".format(username) if username else ("لايوجد معرف")
       caption = f"<b>  ╮•🦦 الحيوان ⇦ </b> {first_name} {last_name} \n"
       caption += f"<b> ٴ╼──────────────────╾ </b>\n"
       caption += f"<b> • 🌚 | معـرفه  ⇦ </b> {username}\n"
       caption += f"<b> • 🌚 | ايـديه   ⇦ </b> <code>{user_id}</code>\n"
       caption += f"<b> • 🌚 | صـوره  ⇦ </b> {replied_user_profile_photos_count} </b>\n"
       caption += f"<b> • 🌚 | نــوعه   ⇦  هايشه 🐄 </b>\n"
       caption += f"<b> • 🌚 | نسبتـه  ⇦  {yoy} </b>\n\n\n"
       caption += f"<b> 𓆩 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿 𓆪 </b> - @ZThon "
       return sts_animal9, caption


@zedub.zed_cmd(pattern="حيوان(?: |$)(.*)")
async def who(event):
    zed = await edit_or_reply(event, "⇆")
    zel_dev = (5176749470, 8241311871, 6269975462, 1985225531)
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    replied_user = await get_user_from_event(event)
    try:
        ZEED_IMG, caption = await fetch_info(replied_user, event)
    except AttributeError:
        return await edit_or_reply(zed, "**- لـم استطـع العثــور ع الشخــص**")
    if replied_user.id in zel_dev:
       return await edit_or_reply(zed, "**- دي . . انـهُ احـد المطـورين . . انتـه الحيـوان ولك**")
    if replied_user.id == 1111565135 or replied_user.id == 6114298715 or replied_user.id == 2095357462:
       return await edit_or_reply(zed, "**- دي . . انـهُ المطـور . . انتـه الحيـوان ولك**")
    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None
    try:
        await event.client.send_file(
            event.chat_id,
            ZEED_IMG,
            caption=caption,
            link_preview=False,
            force_document=False,
            reply_to=message_id_to_reply,
            parse_mode="html",
        )
        await zed.delete()
    except TypeError:
        await zed.edit(caption, parse_mode="html")

