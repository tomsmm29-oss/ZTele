# Zed-Thon - ZelZal (TikTok Native & Self-Destruct Fixed 2025 by Mikey)
# Merged: Native TikTok Downloader (yt-dlp) + Anti-Self Destruct
# No external bots required. Pure Python Power.

import asyncio
import os
import glob
from telethon import events

# استدعاء yt_dlp للتحميل المباشر
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# --- تصحيح المسارات والحقن النسبي ---
from . import zedub
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format, reply_id

# محاولة استدعاء SQL
try:
    from ..sql_helper.globals import addgvar, delgvar, gvarstatus
except ImportError:
    _GVAR_CACHE = {}
    def addgvar(name, val): _GVAR_CACHE[name] = val
    def delgvar(name): _GVAR_CACHE.pop(name, None)
    def gvarstatus(name): return _GVAR_CACHE.get(name)

try:
    from . import BOTLOG, BOTLOG_CHATID
except ImportError:
    BOTLOG = False
    BOTLOG_CHATID = None

plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)

# التأكد من مجلد التحميل
if not os.path.exists(Config.TMP_DOWNLOAD_DIRECTORY):
    os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)

# =========================================================
# 1. كود تيك توك (النسخة الأصلية بدون بوتات)
# =========================================================

CMD_HELP = {}

@zedub.zed_cmd(
    pattern="تيكتوك(?:\s|$)([\s\S]*)",
    command=("تيكتوك", plugin_category),
    info={
        "header": "لـ تحميل الفيـديـو من تيـك تـوك عبـر الرابـط",
        "الاستـخـدام": "{tr}تيكتوك بالـرد ع رابـط",
    },
)
async def tiktok_native(event):
    if event.fwd_from:
        return
        
    if not yt_dlp:
        return await edit_or_reply(event, "**⎉╎عذراً، مكتبة `yt-dlp` غير مثبتة.**")

    url = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    
    if not url and reply:
        url = reply.text
    
    if not url:
        return await edit_or_reply(event, "**```بالـرد على الرابـط حمبـي 🧸🎈```**")

    # تنظيف الرابط من الكلام الزايد
    if "http" in url:
        url = url[url.find("http"):]
        if " " in url:
            url = url.split(" ")[0]
            
    zzzzl1l = await edit_or_reply(event, "**╮ ❐ جـارِ التحميـل من تيـك تـوك انتظـر قليلاً  ▬▭... 𓅫╰**")
    
    # إعدادات التحميل (بدون علامة مائية إن أمكن)
    # نستخدم مجلد مؤقت فريد عشان التداخل
    output_template = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, f"%(id)s.%(ext)s")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # استخراج المعلومات والتحميل
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'TikTok Video')
            # تحديد اسم الملف المحمل
            filename = ydl.prepare_filename(info_dict)
            
        if os.path.exists(filename):
            await event.client.send_file(
                event.chat_id,
                filename,
                caption=f"**⎉╎{video_title}**\n**⎉╎تـم التحميـل بـواسطـة : زدثــون**",
                reply_to=reply or event
            )
            await zzzzl1l.delete()
            os.remove(filename)
        else:
            await zzzzl1l.edit("**🤨💔...فشل التحميل؟**")
            
    except Exception as e:
        LOGS.error(str(e))
        await zzzzl1l.edit(f"**- حدث خطأ أثناء التحميل:**\n`{str(e)}`")


CMD_HELP.update(
    {
        "تيك توك": "**اسم الاضافـه : **`تيك توك`\
    \n\n**╮•❐ الامـر ⦂ **`.تيكتوك` بالرد على الرابط\
    \n**الشـرح •• **تحميل مقاطـع الفيديـو من تيـك تـوك"
    }
)


# =========================================================
# 2. كود حفظ الذاتية (Anti-Self Destruct)
# =========================================================

POSC = gvarstatus("Z_POSC") or "(مم|ذاتية|ذاتيه|جلب الوقتيه)"

ZelzalSelf_cmd = (
    "𓆩 [ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗭𝗧𝗵𝗼𝗻 - حفـظ الذاتيـه 🧧](t.me/ZedThon) 𓆪\n\n"
    "**⪼** `.تفعيل الذاتيه`\n"
    "**لـ تفعيـل الحفظ التلقائي للذاتيـه**\n"
    "**سوف يقوم حسابك بحفظ الذاتيه تلقائياً في حافظة حسابك عندما يرسل لك اي شخص ميديـا ذاتيـه**\n\n\n"
    "**⪼** `.تعطيل الذاتيه`\n"
    "**لـ تعطيـل الحفظ التلقائي للذاتيـه**\n\n\n"
    "**⪼** `.ذاتيه`\n"
    "**بالـرد ؏ــلى صـوره ذاتيـه لحفظهـا في حال كان امر الحفظ التلقائي معطـل**\n\n"
    "\n 𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿](t.me/ZedThon) 𓆪"
)


@zedub.zed_cmd(pattern="الذاتيه")
async def self_help_cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalSelf_cmd)

@zedub.zed_cmd(pattern=f"{POSC}(?: |$)(.*)")
async def manual_save_cmd(event):
    if not event.is_reply:
        return await event.edit("**- ❝ ⌊بالـرد علـى صورة ذاتيـة التدميـر 𓆰...**")
    
    zzzzl1l = await event.get_reply_message()
    try:
        pic = await zzzzl1l.download_media()
        
        # حفظ في الرسائل المحفوظة
        await zedub.send_file("me", pic, caption=f"**⎉╎تم حفـظ الصـورة الذاتيـه .. بنجـاح ☑️𓆰**")
        
        # حفظ في جروب التخزين
        if BOTLOG_CHATID:
             await zedub.send_file(BOTLOG_CHATID, pic, caption=f"**⎉╎نسخة من الذاتية (يدوي) 🕵️**")
             
        await event.delete()
        if os.path.exists(pic): os.remove(pic)
    except Exception as e:
        await event.edit(f"**- خطأ:** {e}")

@zedub.zed_cmd(pattern="(تفعيل الذاتيه|تفعيل الذاتية)")
async def enable_self_cmd(event):
    if gvarstatus("zedself") == "true":
        return await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. مفعـله مسبقـاً ☑️**")
    addgvar("zedself", "true")
    await edit_or_reply(event, "**⎉╎تم تفعيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")

@zedub.zed_cmd(pattern="(تعطيل الذاتيه|تعطيل الذاتية)")
async def disable_self_cmd(event):
    if gvarstatus("zedself") != "true":
        return await edit_or_reply(event, "**⎉╎حفظ الذاتيـة التلقـائي .. معطلـه مسبقـاً ☑️**")
    delgvar("zedself")
    await edit_or_reply(event, "**⎉╎تم تعطيـل حفظ الذاتيـة التلقائـي .. بنجـاح ☑️**")

# المراقب السري (The Spy)
@zedub.on(events.NewMessage(func=lambda e: e.is_private and (e.photo or e.video) and e.media_unread))
async def auto_save_selfie_watcher(event):
    # التحقق من التفعيل
    if gvarstatus("zedself") != "true":
        return
        
    zelzal = event.sender_id
    malath = (await event.client.get_me()).id
    if zelzal == malath:
        return

    try:
        sender = await event.get_sender()
        pic = await event.download_media()
        
        caption_text = f"[ᯓ 𝗦𝗼𝘂𝗿𝗰𝗲 𝗭𝗧𝗵𝗼𝗻 - حفـظ الذاتيـه 🧧](t.me/ZEDthon) .\n\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n**⌔╎مࢪحبـاً عـزيـزي المـالك 🫂\n⌔╎ تـم حفـظ الذاتيـة تلقائيـاً .. بنجـاح ☑️** ❝\n**⌔╎المـرسـل** {_format.mentionuser(sender.first_name , sender.id)} ."
        
        # 1. الحفظ في الرسائل المحفوظة
        await zedub.send_file("me", pic, caption=caption_text)
        
        # 2. الحفظ في جروب التخزين
        if BOTLOG_CHATID:
            await zedub.send_file(BOTLOG_CHATID, pic, caption=caption_text + "\n**(نسخة للمخزن)**")
            
        if os.path.exists(pic): os.remove(pic)
    except Exception as e:
        LOGS.error(f"Error saving self-destruct media: {e}")


@zedub.zed_cmd(
    pattern="تست (\d*) ([\s\S]*)",
    command=("sdm", plugin_category),
    info={
        "header": "To self destruct the message after paticualr time.",
        "الاسـتخـدام": "{tr}sdm [number] [text]",
        "مثــال": "{tr}sdm 10 hi",
    },
)
async def selfdestruct_msg_cmd(destroy):
    "To self destruct the sent message"
    try:
        cat = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
        message = cat[1]
        ttl = int(cat[0])
        await destroy.delete()
        smsg = await destroy.client.send_message(destroy.chat_id, message)
        await asyncio.sleep(ttl)
        await smsg.delete()
    except:
        await edit_or_reply(destroy, "**- تأكد من الصيغة: .تست [الوقت] [النص]**")

@zedub.zed_cmd(
    pattern="محترقه (\d*) ([\s\S]*)",
    command=("selfdm", plugin_category),
    info={
        "header": "To self destruct the message after paticualr time. and in message will show the time.",
        "الاسـتخـدام": "{tr}selfdm [number] [text]",
        "مثــال": "{tr}selfdm 10 hi",
    },
)
async def selfdestruct_timer_cmd(destroy):
    "To self destruct the sent message"
    try:
        cat = ("".join(destroy.text.split(maxsplit=1)[1:])).split(" ", 1)
        message = cat[1]
        ttl = int(cat[0])
        text = message + f"\n\n`This message shall be self-destructed in {ttl} seconds`"

        await destroy.delete()
        smsg = await destroy.client.send_message(destroy.chat_id, text)
        await asyncio.sleep(ttl)
        await smsg.delete()
    except:
        await edit_or_reply(destroy, "**- تأكد من الصيغة: .محترقه [الوقت] [النص]**")