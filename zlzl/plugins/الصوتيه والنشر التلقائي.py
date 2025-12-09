# Zed-Thon - ZelZal (AutoPost & TTS Combined 2025 by Mikey)
# Merged: AutoPost + Global Broadcast + Google TTS
# Fixed: Relative Imports, FFmpeg, SQL Mocking

import asyncio
import os
import subprocess
import logging
from datetime import datetime

from telethon import functions, types
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
    # دوال وهمية لمنع الكراش
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

plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)
GCAST_LOOP_RUNNING = False

# دالة تنظيف النص (محلية لضمان عمل TTS)
def deEmojify(text):
    try:
        return text.encode('ascii', 'ignore').decode('ascii')
    except:
        return text

ZelzalNSH_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗭𝗧𝗵𝗼𝗻 - اوامـر النشـر التلقـائي](t.me/ZEDthon) 𓆪\n\n"
    "**- اضغـط ع الامـر للنسـخ** \n\n\n"
    "**⪼** `.تلقائي` \n"
    "**- الامـر + (معـرف/ايـدي/رابـط) القنـاة المـراد النشـر التلقـائي منهـا** \n"
    "**- استخـدم الامـر بقنـاتـك \n\n\n"
    "**⪼** `.ايقاف النشر` \n"
    "**- الامـر + (معـرف/ايـدي/رابـط) القنـاة المـراد ايقـاف النشـر التلقـائي منهـا** \n"
    "**- استخـدم الامـر بقنـاتـك \n\n\n"
    "**⪼** `.الكل [عدد] [وقت] [نص]` \n"
    "**- لنشـر رسالـة في كـل المجموعـات بتكـرار زمنـي**\n"
    "**- مثـال:** `.الكل 20 1 هلا` (يرسل هلا 20 مرة، كل ثانية، لكل المجموعات)\n\n"
    "**⪼** `.ايقاف الكل` \n"
    "**- لإيقـاف عمليـة النشـر العـام المتكـررة فوراً**\n"
)


# =========================================================
# 1. كود الترجمة الصوتية (Google TTS)
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
        lan = input_str or "ar" # تعديل الافتراضي للعربية
    else:
        if not input_str:
            return await edit_or_reply(event, "**⌔∮ قم برد على الرساله**")
        text = input_str
        lan = "ar" # تعديل الافتراضي للعربية
        
    catevent = await edit_or_reply(event, "**- جـاري الترجمـه**")
    
    # تنظيف النص
    try:
        text = deEmojify(text.strip())
    except: pass
        
    lan = lan.strip()
    
    if not os.path.isdir("./temp/"):
        os.makedirs("./temp/")
        
    required_file_name = "./temp/" + "voice.ogg"
    
    try:
        # تحويل النص لصوت
        tts = gTTS(text, lang=lan)
        tts.save(required_file_name)
        
        # تحويل الصيغة باستخدام ffmpeg
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


# =========================================================
# 2. كود النشر التلقائي (AutoPost)
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


@zedub.zed_cmd(incoming=True, forword=None)
async def autopost_watcher(event):
    if event.is_private: return
    chat_id = str(event.chat_id).replace("-100", "")
    try:
        channels_set  = get_all_post(chat_id)
    except: return
    if not channels_set: return
    
    for chat in channels_set:
        try:
            if event.media:
                await event.client.send_file(int(chat), event.media, caption=event.text)
            elif event.message.text:
                await zedub.send_message(int(chat), event.message)
        except: pass


# =========================================================
# 3. المدفع الرشاش (Global Loop Broadcast)
# =========================================================

@zedub.zed_cmd(pattern="الكل(?: |$)(.*)")
async def gcast_loop(event):
    global GCAST_LOOP_RUNNING
    args = event.pattern_match.group(1)
    
    if not args:
        return await edit_or_reply(event, "**⎉╎طريقة الاستخدام:**\n`.الكل [عدد المرات] [الوقت بالثواني] [الرسالة]`")

    parts = args.split(" ", 2)
    if len(parts) < 3:
        return await edit_or_reply(event, "**⎉╎تأكد من الصيغة: عدد المرات + الوقت + الرسالة**")
        
    try:
        count = int(parts[0])
        delay = int(parts[1])
        msg = parts[2]
    except ValueError:
        return await edit_or_reply(event, "**⎉╎الأرقام لازم تكون انجليزية!**")
        
    GCAST_LOOP_RUNNING = True
    zed = await edit_or_reply(event, f"**⎉╎جاري تشغيل المدفع... 🔫**\n**⎉╎العدد:** {count} مرات\n**⎉╎الفاصل:** {delay} ثانية")
    
    groups = []
    async for dialog in event.client.iter_dialogs():
        if dialog.is_group:
            groups.append(dialog.id)
            
    if not groups:
        return await zed.edit("**⎉╎معندكش جروبات يا فقري!**")

    for i in range(count):
        if not GCAST_LOOP_RUNNING:
            await zed.edit("**⎉╎تم إيقاف القصف! 🛑**")
            return
            
        tasks = []
        for chat_id in groups:
            tasks.append(event.client.send_message(chat_id, msg))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        await zed.edit(f"**⎉╎تمت الجولة {i+1} من {count} ✅**\n**⎉╎انتظار {delay} ثانية...**")
        await asyncio.sleep(delay)
        
    await zed.edit("**⎉╎انتهى القصف بنجاح! 🚀**")
    GCAST_LOOP_RUNNING = False


@zedub.zed_cmd(pattern="ايقاف الكل$")
async def stop_gcast_loop(event):
    global GCAST_LOOP_RUNNING
    if GCAST_LOOP_RUNNING:
        GCAST_LOOP_RUNNING = False
        await edit_or_reply(event, "**⎉╎تم إرسال إشارة الإيقاف! 🛑**")
    else:
        await edit_or_reply(event, "**⎉╎مفيش نشر شغال أصلاً!**")


@zedub.zed_cmd(pattern="النشر")
async def autopost_help(zelzallll):
    await edit_or_reply(zelzallll, ZelzalNSH_cmd)