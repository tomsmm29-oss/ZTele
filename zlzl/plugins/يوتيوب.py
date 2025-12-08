# Zed-Thon - ZelZal (Ultimate Downloader Fixed for ZTele 2025 by Mikey)
# Includes: YouTube, Facebook, Instagram, Pinterest, Snapchat, TikTok
# Fixed: Imports, Relative Paths, Helper Calls
# Visuals: 100% Original Preserved

import asyncio
import glob
import io
import os
import re
import pathlib
import requests
from time import time

# محاولة استدعاء pyquery أو تثبيتها (كما في الكود الأصلي)
try:
    from pyquery import PyQuery as pq
except ImportError:
    try:
        os.system("pip3 install pyquery")
        from pyquery import PyQuery as pq
    except: pass

from telethon import types
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.utils import get_attributes

# استدعاء المكتبات الخارجية
try:
    from urlextract import URLExtract
    from wget import download
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import (
        ContentTooShortError,
        DownloadError,
        ExtractorError,
        GeoRestrictedError,
        MaxDownloadsReached,
        PostProcessingError,
        UnavailableVideoError,
        XAttrMetadataError,
    )
except ImportError:
    # لتجنب توقف الملف بالكامل إذا كانت المكتبات ناقصة
    URLExtract = None
    YoutubeDL = None

# --- تصحيح المسارات والحقن النسبي ---
from . import zedub
from ..Config import Config
from ..core import pool
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import progress, reply_id
from ..helpers.functions import delete_conv

# محاولة استدعاء دوال اليوتيوب المساعدة
try:
    from ..helpers.functions.utube import _mp3Dl, get_yt_video_id, get_ytthumb, ytsearch
except ImportError:
    # دوال وهمية لمنع الكراش
    async def _mp3Dl(**kwargs): return 1
    async def get_yt_video_id(url): return "error"
    async def get_ytthumb(id): return ""
    async def ytsearch(q, limit=10): return "Error: Helper functions missing"

try:
    from ..helpers.utils import _format
except ImportError:
    pass

try:
    from . import BOTLOG, BOTLOG_CHATID
except ImportError:
    BOTLOG = False
    BOTLOG_CHATID = None


BASE_YT_URL = "https://www.youtube.com/watch?v="
extractor = URLExtract() if URLExtract else None
LOGS = logging.getLogger(__name__)

plugin_category = "البحث"

# إعدادات yt-dlp
video_opts = {
    "format": "best",
    "addmetadata": True,
    "key": "FFmpegMetadata",
    "writethumbnail": True,
    "prefer_ffmpeg": True,
    "geo_bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [
        {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
        {"key": "FFmpegMetadata"},
    ],
    "outtmpl": "cat_ytv.mp4",
    "logtostderr": False,
    "quiet": True,
}

# --- دوال المساعدة الداخلية ---

async def ytdl_down(event, opts, url):
    ytdl_data = None
    if not YoutubeDL:
        await event.edit("**- عذراً، مكتبة `yt-dlp` غير مثبتة.**")
        return None
        
    try:
        await event.edit("**╮ ❐ يتـم جلـب البيانـات انتظـر قليلاً ...𓅫╰▬▭ **")
        with YoutubeDL(opts) as ytdl:
            ytdl_data = ytdl.extract_info(url)
    except DownloadError as DE:
        await event.edit(f"`{DE}`")
    except ContentTooShortError:
        await event.edit("**- عذرا هذا المحتوى قصير جدا لتنزيله ⚠️**")
    except GeoRestrictedError:
        await event.edit(
            "**- الفيديو غير متاح من موقعك الجغرافي بسبب القيود الجغرافية التي يفرضها موقع الويب ❕**"
        )
    except MaxDownloadsReached:
        await event.edit("**- تم الوصول إلى الحد الأقصى لعدد التنزيلات ❕**")
    except PostProcessingError:
        await event.edit("**كان هناك خطأ أثناء المعالجة**")
    except UnavailableVideoError:
        await event.edit("**⌔∮عـذراً .. الوسائط غير متوفـره بالتنسيق المطلـوب**")
    except XAttrMetadataError as XAME:
        await event.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
    except ExtractorError:
        await event.edit("**حدث خطأ أثناء استخراج المعلومات يرجى وضعها بشكل صحيح ⚠️**")
    except Exception as e:
        await event.edit(f"**- خطـأ : **\n__{e}__")
    return ytdl_data


async def fix_attributes(
    path, info_dict: dict, supports_streaming: bool = False, round_message: bool = False
) -> list:
    """Avoid multiple instances of an attribute."""
    new_attributes = []
    video = False
    audio = False

    uploader = info_dict.get("uploader", "Unknown artist")
    duration = int(info_dict.get("duration", 0))
    suffix = path.suffix[1:]
    if supports_streaming and suffix != "mp4":
        supports_streaming = True

    attributes, mime_type = get_attributes(path)
    if suffix == "mp3":
        title = str(info_dict.get("title", info_dict.get("id", "Unknown title")))
        audio = types.DocumentAttributeAudio(
            duration=duration, voice=None, title=title, performer=uploader
        )
    elif suffix == "mp4":
        width = int(info_dict.get("width", 0))
        height = int(info_dict.get("height", 0))
        for attr in attributes:
            if isinstance(attr, types.DocumentAttributeVideo):
                duration = duration or attr.duration
                width = width or attr.w
                height = height or attr.h
                break
        video = types.DocumentAttributeVideo(
            duration=duration,
            w=width,
            h=height,
            round_message=round_message,
            supports_streaming=supports_streaming,
        )

    if audio and isinstance(audio, types.DocumentAttributeAudio):
        new_attributes.append(audio)
    if video and isinstance(video, types.DocumentAttributeVideo):
        new_attributes.append(video)

    new_attributes.extend(
        attr
        for attr in attributes
        if (
            isinstance(attr, types.DocumentAttributeAudio)
            and not audio
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not video
            or not isinstance(attr, types.DocumentAttributeAudio)
            and not isinstance(attr, types.DocumentAttributeVideo)
        )
    )
    return new_attributes, mime_type


# =========================================================
# 1. تحميل الصوت (YouTube/SoundCloud etc)
# =========================================================

@zedub.zed_cmd(
    pattern="(تحميل صوت|ساوند)(?:\s|$)([\s\S]*)",
    command=("تحميل صوت", plugin_category),
    info={
        "header": "تحميـل الاغـاني مـن يوتيوب .. فيسبوك .. انستا .. الـخ عـبر الرابـط",
        "مثــال": ["{tr}تحميل صوت بالــرد ع رابــط", "{tr}تحميل صوت + رابــط"],
    },
)
async def download_audio_cmd(event):
    """To download audio from YouTube and many other sites."""
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
        
    if not extractor:
        return await edit_or_reply(event, "**- عذراً مكتبة `urlextract` مفقودة.**")
        
    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    
    for url in urls:
        try:
            if YoutubeDL:
                try:
                    vid_data = YoutubeDL({"no-playlist": True}).extract_info(
                        url, download=False
                    )
                except ExtractorError:
                    vid_data = {"title": url, "uploader": "Catuserbot", "formats": []}
            else:
                vid_data = {"title": url, "uploader": "Catuserbot", "formats": []}

            startTime = time()
            # استخدام دالة Helper (قد تفشل لو مش موجودة)
            try:
                retcode = await _mp3Dl(url=url, starttime=startTime, uid="320")
            except:
                retcode = 1
                
            if retcode != 0:
                return await event.edit(f"**- خطأ في التحميل (تأكد من وجود دوال المساعدة). Code: {retcode}**")
                
            _fpath = ""
            thumb_pic = None
            for _path in glob.glob(os.path.join(Config.TEMP_DIR, str(startTime), "*")):
                if _path.lower().endswith((".jpg", ".png", ".webp")):
                    thumb_pic = _path
                else:
                    _fpath = _path
                    
            if not _fpath:
                return await edit_delete(zedevent, "__Unable to upload file__")
                
            await zedevent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{vid_data.get('title', 'Audio')}***"
            )
            
            attributes, mime_type = get_attributes(str(_fpath))
            ul = io.open(pathlib.Path(_fpath), "rb")
            
            if thumb_pic is None:
                try:
                     thumb_pic = str(
                        await pool.run_in_thread(download)(
                            await get_ytthumb(get_yt_video_id(url))
                        )
                    )
                except: pass
                
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, zedevent, startTime, "trying to upload",
                        file_name=os.path.basename(pathlib.Path(_fpath)),
                    )
                ),
            )
            ul.close()
            
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
                force_file=False,
                thumb=await event.client.upload_file(thumb_pic) if thumb_pic else None,
            )
            
            await event.client.send_file(
                event.chat_id,
                file=media,
                caption=f"<b>File Name : </b><code>{vid_data.get('title', os.path.basename(pathlib.Path(_fpath)))}</code>",
                supports_streaming=True,
                reply_to=reply_to_id,
                parse_mode="html",
            )
            
            for _path in [_fpath, thumb_pic]:
                if _path and os.path.exists(_path):
                    os.remove(_path)
                    
        except Exception as e:
            await zedevent.edit(f"**- خطأ:** {e}")
            
    await zedevent.delete()


# =========================================================
# 2. تحميل الفيديو (YouTube/Facebook/Snapchat/Tiktok/Likee)
# =========================================================

@zedub.zed_cmd(
    pattern="(تحميل فيديو|فيس|سناب|تيك|لايكي)(?:\s|$)([\s\S]*)",
    command=("تحميل فيديو", plugin_category),
    info={
        "header": "تحميـل مقـاطـع الفيـديــو مـن يوتيوب .. فيسبوك .. انستا .. الـخ عـبر الرابـط",
        "مثــال": [
            "{tr}تحميل فيديو بالــرد ع رابــط",
            "{tr}تحميل فيديو + رابــط",
        ],
    },
)
async def download_video_cmd(event):
    """To download video from YouTube and many other sites."""
    msg = event.pattern_match.group(2)
    rmsg = await event.get_reply_message()
    if not msg and rmsg:
        msg = rmsg.text
        
    if not extractor:
        return await edit_or_reply(event, "**- عذراً مكتبة `urlextract` مفقودة.**")

    urls = extractor.find_urls(msg)
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")
    
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)
    
    for url in urls:
        ytdl_data = await ytdl_down(zedevent, video_opts, url)
        if ytdl_data is None:
            return
        try:
            f = pathlib.Path("cat_ytv.mp4")
            catthumb = pathlib.Path("cat_ytv.jpg")
            if not os.path.exists(catthumb):
                catthumb = pathlib.Path("cat_ytv.webp")
            if not os.path.exists(catthumb):
                catthumb = None
                
            await zedevent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{ytdl_data['title']}**"
            )
            
            ul = io.open(f, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(
                f, ytdl_data, supports_streaming=True
            )
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, zedevent, c_time, "Upload :", file_name=ytdl_data["title"]
                    )
                ),
            )
            ul.close()
            
            media = types.InputMediaUploadedDocument(
                file=uploaded,
                mime_type=mime_type,
                attributes=attributes,
            )
            
            await event.client.send_file(
                event.chat_id,
                file=media,
                reply_to=reply_to_id,
                caption=f'**⎉╎المقطــع :** `{ytdl_data["title"]}`',
                thumb=catthumb,
            )
            
            if os.path.exists(f): os.remove(f)
            if catthumb and os.path.exists(catthumb): os.remove(catthumb)
            
        except TypeError:
            await asyncio.sleep(2)
        except Exception as e:
            await zedevent.edit(f"**- خطأ:** {e}")
            
    await event.delete()


# =========================================================
# 3. انستا (عن طريق البوتات)
# =========================================================

@zedub.zed_cmd(
    pattern="انستا(?: |$)([\s\S]*)",
    command=("انستا", plugin_category),
    info={
        "header": "لـ تحميـل الصـور والفيـديـو مـن الانستـا",
        "مثــال": [
            "{tr}انستا + رابــط",
        ],
    },
)
async def insta_dl(event):
    "For downloading instagram media"
    link = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if not link and reply:
        link = reply.text
    if not link:
        return await edit_delete(event, "**- احتـاج الـر رابــط للتحميــل**", 10)
    if "instagram.com" not in link:
        return await edit_delete(
            event, "**- احتـاج الـر رابــط للتحميــل**", 10
        )
    
    # قائمة البوتات (للمرونة)
    v1 = "Fullsavebot"
    v2 = "@videomaniacbot"
    media_list = []
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    
    # محاولة مع البوت الأول
    async with event.client.conversation(v1) as conv:
        try:
            try:
                v1_flag = await conv.send_message("/start")
            except YouBlockedUserError:
                await zedub(unblock("Fullsavebot"))
                v1_flag = await conv.send_message("/start")
                
            checker = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            
            if "Choose the language you like" in checker.message:
                await checker.click(1)
                await conv.send_message(link)
                await conv.get_response()
            
            await conv.send_message(link)
            await conv.get_response()
            
            try:
                media = await conv.get_response(timeout=10)
                if media.media:
                    while True:
                        media_list.append(media)
                        try:
                            media = await conv.get_response(timeout=2)
                        except asyncio.TimeoutError:
                            break
                    
                    details = media_list[0].message.splitlines()
                    await zedevent.delete()
                    await event.client.send_file(
                        event.chat_id,
                        media_list,
                        caption=f"**{details[0] if details else 'Instagram'}**",
                    )
                    await delete_conv(event, v1, v1_flag)
                    return
            except asyncio.TimeoutError:
                await delete_conv(event, v1, v1_flag)
                
        except Exception:
            pass # فشل البوت الأول، ننتقل للثاني

    # محاولة مع البوت الثاني (Fallback)
    await edit_or_reply(zedevent, "**Switching v2...**")
    async with event.client.conversation(v2) as conv:
        try:
            try:
                v2_flag = await conv.send_message("/start")
            except YouBlockedUserError:
                await zedub(unblock("videomaniacbot"))
                v2_flag = await conv.send_message("/start")
                
            await conv.get_response()
            await asyncio.sleep(1)
            await conv.send_message(link)
            await conv.get_response()
            
            media = await conv.get_response()
            if media.media:
                await zedevent.delete()
                await event.client.send_file(event.chat_id, media)
            else:
                await edit_delete(zedevent, "**- فشل التحميل من كلا البوتيين!**", 10)
                
            await delete_conv(event, v2, v2_flag)
        except Exception as e:
             await edit_delete(zedevent, f"**- خطأ:** {e}", 10)


# =========================================================
# 4. بنترست (Pinterest)
# =========================================================

@zedub.zed_cmd(
    pattern="بنترست?(?:\s|$)([\s\S]*)",
    command=("بنترست", plugin_category),
    info={
        "header": "تحميـل مقـاطـع الفيـديـو والصــور مـن بنتـرسـت عـبر الرابـط",
        "مثــال": ["{tr}بنترست + رابــط"],
    },
)
async def pinterest_dl(event):
    M = event.pattern_match.group(1)
    if not M:
        await event.delete()
        N = await event.respond("**ارسل الامـر + الرابـط ... 🧸🎈**")
        await asyncio.sleep(2)
        await N.delete()
        return

    links = re.findall(r"\bhttps?://.*\.\S+", M)
    if not links:
        return

    await event.delete()
    A = await event.respond("**╮•⎚ جـارِ التحميل مـن بنتـرسـت ... 🧸🎈**")
    
    # دالة بسيطة لجلب الرابط (بديلة لـ get_download_url المفقودة)
    try:
        # هنا نفترض وجود دالة get_download_url أو نستخدم yt-dlp كبديل قوي
        # للتبسيط، سنستخدم المنطق العام
        if YoutubeDL:
             with YoutubeDL({'quiet':True}) as ydl:
                 info = ydl.extract_info(M, download=False)
                 url = info['url']
                 await event.client.send_file(event.chat.id, url, caption="**Pinterest Download**")
        else:
             await A.edit("**- yt-dlp غير مثبتة.**")
    except Exception as e:
        await A.edit(f"**- خطأ:** {e}")
        
    await A.delete()


# =========================================================
# 5. بحث يوتيوب (YouTube Search)
# =========================================================

@zedub.zed_cmd(
    pattern="يوتيوب(?: |$)(\d*)? ?([\s\S]*)",
    command=("يوتيوب", plugin_category),
    info={
        "header": "لـ البحـث عـن روابــط بالكلمــه المحــدده علـى يـوتيــوب",
        "مثــال": [
            "{tr}يوتيوب + كلمـه",
            "{tr}يوتيوب + عدد + كلمـه",
        ],
    },
)
async def yt_search_cmd(event):
    "Youtube search command"
    if event.is_reply and not event.pattern_match.group(2):
        query = await event.get_reply_message()
        query = str(query.message)
    else:
        query = str(event.pattern_match.group(2))
        
    if not query:
        return await edit_delete(
            event, "**╮ بالـرد ﮼؏ كلمـٓھہ للبحث أو ضعها مـع الأمـر ... 𓅫╰**"
        )
        
    video_q = await edit_or_reply(event, "**╮ جـارِ البحث ▬▭... ╰**")
    
    lim = int(event.pattern_match.group(1)) if event.pattern_match.group(1) else 10
    
    try:
        # استخدام دالة البحث المساعدة
        full_response = await ytsearch(query, limit=lim)
    except Exception as e:
        return await edit_delete(video_q, str(e), time=10)
        
    reply_text = f"**⎉╎اليك عزيزي قائمة بروابط الكلمة اللتي بحثت عنها:**\n`{query}`\n\n**⎉╎النتائج:**\n{full_response}"
    await edit_or_reply(video_q, reply_text)