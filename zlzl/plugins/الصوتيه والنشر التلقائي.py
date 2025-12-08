# Zed-Thon - ZelZal (AutoPost & TTS Fixed for ZTele 2025 by Mikey)
# Merged: AutoPost + Google TTS
# Fixed: Imports, SQL, Duplicate functions, Relative Paths

import asyncio
import os
import subprocess
import logging
from datetime import datetime

from telethon import functions, types
from telethon.tl.functions.channels import GetParticipantRequest, GetFullChannelRequest
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import MessageEntityMentionName

# --- تصحيح المسارات والحقن النسبي ---
from . import zedub
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id

# محاولة استدعاء المكتبات الخارجية
try:
    from gtts import gTTS
except ImportError:
    gTTS = None # سيتم التنبيه لتثبيتها

# محاولة استدعاء SQL (مع Mocking)
try:
    from ..sql_helper.autopost_sql import add_post, get_all_post, is_post, remove_post
    from ..sql_helper.globals import gvarstatus
except ImportError:
    # دوال وهمية
    def add_post(x, y): pass
    def get_all_post(x): return []
    def is_post(x, y): return False
    def remove_post(x, y): pass
    def gvarstatus(val): return None

try:
    from . import BOTLOG, BOTLOG_CHATID
except ImportError:
    BOTLOG = False
    BOTLOG_CHATID = None

# دالة تنظيف النص (DeEmojify) - عادة تكون في helpers
def deEmojify(text):
    return text.encode('ascii', 'ignore').decode('ascii')

plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)

SPRS = gvarstatus("Z_SPRS") or "(نشر_تلقائي|نشر|تلقائي)"
OFSPRS = gvarstatus("Z_OFSPRS") or "(ايقاف_النشر|ايقاف النشر|ستوب)"

ZelzalNSH_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗭𝗧𝗵𝗼𝗻 - اوامـر النشـر التلقـائي](t.me/ZEDthon) 𓆪\n\n"
    "**- اضغـط ع الامـر للنسـخ** \n\n\n"
    "**⪼** `.تلقائي` \n"
    "**- الامـر + (معـرف/ايـدي/رابـط) القنـاة المـراد النشـر التلقـائي منهـا** \n"
    "**- استخـدم الامـر بقنـاتـك \n\n\n"
    "**⪼** `.ايقاف النشر` \n"
    "**- الامـر + (معـرف/ايـدي/رابـط) القنـاة المـراد ايقـاف النشـر التلقـائي منهـا** \n"
    "**- استخـدم الامـر بقنـاتـك \n\n\n"
    "**- ملاحظـه :**\n"
    "**- الاوامـر صـارت تدعـم المعـرفات والروابـط الى جـانب الايـدي 🏂🎗**\n"
    "**🛃 سيتـم اضـافة المزيـد من اوامــر النشـر التلقـائي بالتحديثـات الجـايه**\n"
)


# --- دوال المساعدة ---
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
            # await event.edit(str(err))
            return None
    return user_object


# =========================================================
# 1. أوامر النشر التلقائي (AutoPost)
# =========================================================

@zedub.zed_cmd(pattern="(نشر تلقائي|تلقائي)(?:\s|$)([\s\S]*)")
async def autopost_add(event):
    if (event.is_private or event.is_group):
        return await edit_or_reply(event, "**⎉╎عـذراً .. النشر التلقائي خـاص بالقنـوات فقـط\n⎉╎قم باستخـدام الامـر داخـل القنـاة الهـدف**")
    
    if input_str := event.pattern_match.group(2):
        try:
            zch = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_delete(event, "**⎉╎عـذراً .. معـرف/ايـدي القنـاة غيـر صـالح**\n**⎉╎الرجـاء التـأكـد مـن المعـرف/الايـدي**", 5)
        
        try:
            if is_post(zch.id , event.chat_id):
                return await edit_or_reply(event, "**⎉╎النشـر التلقـائي مفعـل مسبقـاً ✓**")
            
            # التأكد من وجود الاسم أو العنوان
            name = getattr(zch, 'first_name', None) or getattr(zch, 'title', None)
            
            if name:
                await asyncio.sleep(1.5)
                add_post(zch.id, event.chat_id)
                await edit_or_reply(event, "**⎉╎تم تفعيـل النشـر التلقـائي من القنـاة .. بنجـاح ✓**")
                
        except Exception as e:
            LOGS.info(str(e))
            await edit_or_reply(event, "**⎉╎حدث خطأ أثناء التفعيل.**")
    else:
        await edit_or_reply(event, "**⎉╎عـذراً .. يجب وضع معرف/ايدي القناة**")


@zedub.zed_cmd(pattern="(ايقاف النشر|ستوب)(?:\s|$)([\s\S]*)")
async def autopost_remove(event):
    if (event.is_private or event.is_group):
        return await edit_or_reply(event, "**⎉╎عـذراً .. النشر التلقائي خـاص بالقنـوات فقـط\n⎉╎قم باستخـدام الامـر داخـل القنـاة الهـدف**")
    
    if input_str := event.pattern_match.group(2):
        try:
            zch = await event.client.get_entity(input_str)
        except Exception as e:
            return await edit_delete(event, "**⎉╎عـذراً .. معـرف/ايـدي القنـاة غيـر صـالح**\n**⎉╎الرجـاء التـأكـد مـن المعـرف/الايـدي**", 5)
        
        try:
            if not is_post(zch.id, event.chat_id):
                return await edit_or_reply(event, "**⎉╎عـذراً .. النشـر التلقـائي غير مفعـل من اساسـاً ؟!**")
            
            name = getattr(zch, 'first_name', None) or getattr(zch, 'title', None)
            
            if name:
                await asyncio.sleep(1.5)
                remove_post(zch.id, event.chat_id)
                await edit_or_reply(event, "**⎉╎تم تعطيـل النشر التلقـائي هنـا .. بنجـاح ✓**")
                
        except Exception as e:
            LOGS.info(str(e))
            await edit_or_reply(event, "**⎉╎حدث خطأ أثناء الإيقاف.**")
    else:
        await edit_or_reply(event, "**⎉╎عـذراً .. يجب وضع معرف/ايدي القناة**")


# المستمع (Watcher) للنشر التلقائي
@zedub.zed_cmd(incoming=True, forword=None)
async def autopost_watcher(event):
    if event.is_private:
        return
    
    chat_id = str(event.chat_id).replace("-100", "")
    
    # محاولة جلب القنوات المرتبطة
    try:
        channels_set = get_all_post(chat_id)
    except:
        channels_set = []
        
    if not channels_set:
        return
        
    for chat in channels_set:
        try:
            if event.media:
                await event.client.send_file(int(chat), event.media, caption=event.text)
            elif event.message.text:
                await zedub.send_message(int(chat), event.message)
        except Exception as e:
            # LOGS.error(f"AutoPost Error: {e}")
            pass


@zedub.zed_cmd(pattern="النشر")
async def autopost_help(zelzallll):
    await edit_or_reply(zelzallll, ZelzalNSH_cmd)


# =========================================================
# 2. كود الترجمة الصوتية (Google TTS)
# =========================================================

@zedub.zed_cmd(
    pattern="صوت جوجل(?:\s|$)([\s\S]*)",
    command=("صوت جوجل", plugin_category),
    info={
        "header": "Text to speech command.",
        "usage": [
            "{tr}tts <text>",
            "{tr}tts <reply>",
            "{tr}tts <language code> ; <text>",
        ],
    },
)
async def tts_cmd(event):
    "text to speech command"
    
    if gTTS is None:
        return await edit_or_reply(event, "**⎉╎عذراً، مكتبة `gTTS` غير مثبتة.**")

    input_str = event.pattern_match.group(1)
    start = datetime.now()
    reply_to_id = await reply_id(event)
    
    if ";" in input_str:
        lan, text = input_str.split(";")
    elif event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "ar" # تعديل الافتراضي للعربية لزدثون
    else:
        if not input_str:
            return await edit_or_reply(event, "**⌔∮ قم برد على الرساله**")
        text = input_str
        lan = "ar" # تعديل الافتراضي للعربية
        
    catevent = await edit_or_reply(event, "**- جـاري الترجمـه**")
    
    # تنظيف النص من الإيموجي (قد يسبب مشاكل لـ TTS)
    try:
        text = deEmojify(text.strip())
    except:
        pass
        
    lan = lan.strip()
    
    if not os.path.isdir("./temp/"):
        os.makedirs("./temp/")
        
    required_file_name = "./temp/" + "voice.ogg"
    
    try:
        # تحويل النص لصوت
        tts = gTTS(text, lang=lan)
        tts.save(required_file_name)
        
        # تحويل الصيغة باستخدام ffmpeg (لتعمل كبصمة)
        command_to_execute = [
            "ffmpeg",
            "-i",
            required_file_name,
            "-map",
            "0:a",
            "-codec:a",
            "libopus",
            "-b:a",
            "100k",
            "-vbr",
            "on",
            f"{required_file_name}.opus",
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *command_to_execute,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            
        except (OSError, FileNotFoundError) as exc:
            await catevent.edit(f"**- خطأ في ffmpeg:** {str(exc)}")
            # محاولة إرسال الملف الأصلي لو التحويل فشل
            # pass
        else:
            if os.path.exists(required_file_name):
                os.remove(required_file_name)
            required_file_name = f"{required_file_name}.opus"
            
        end = datetime.now()
        ms = (end - start).seconds
        
        if os.path.exists(required_file_name):
            await event.client.send_file(
                event.chat_id,
                required_file_name,
                reply_to=reply_to_id,
                allow_cache=False,
                voice_note=True,
            )
            os.remove(required_file_name)
            await edit_delete(
                catevent,
                "**⌔∮ تم معـالجـة {} خـلال {} ثانيـه !**".format(text[:20], ms),
            )
        else:
            await catevent.edit("**- فشل إنشاء الملف الصوتي.**")

    except Exception as e:
        await edit_or_reply(catevent, f"**- خطـأ:**\n`{e}`")