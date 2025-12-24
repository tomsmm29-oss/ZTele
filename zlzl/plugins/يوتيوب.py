import asyncio
import glob
import io
import os
import re
import pathlib
import requests
import subprocess
import shutil
from time import time
from uuid import uuid4

# محاولة استدعاء pyquery أو تثبيتها (كما في الكود الأصلي)
try:
    from pyquery import PyQuery as pq
except ImportError:
    try:
        os.system("pip3 install pyquery")
        from pyquery import PyQuery as pq
    except:
        pass

from telethon import types, events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.utils import get_attributes
from telethon import Button

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

# ==========
# إعدادات عامة
# ==========
AUDIO_MIN_SEC = 60
AUDIO_MAX_SEC = 25 * 60

YT_QUALITIES = {
    "144p": 144,
    "240p": 240,
    "360p": 360,
    "480p": 480,
    "720p": 720,
}

# تخزين طلبات الفيديو للجودة (جلسة بسيطة)
_ZED_VID_REQUESTS = {}

# إعدادات yt-dlp (فيديو افتراضي)
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


# =========================================================
# دوال مساعدة قوية (ytdlp + fallback)
# =========================================================

def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)
    return p

def _safe_rm(path: str):
    try:
        if path and os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
    except:
        pass

def _ffmpeg_exists():
    return shutil.which("ffmpeg") is not None

def _pick_audio_entry(info: dict, min_s=AUDIO_MIN_SEC, max_s=AUDIO_MAX_SEC):
    """
    يختار نتيجة مناسبة من ytsearch (مدتها بين 1 و25 دقيقة)
    """
    if not info:
        return None
    if info.get("duration") and min_s <= int(info["duration"]) <= max_s:
        return info
    entries = info.get("entries") or []
    for e in entries:
        try:
            d = int(e.get("duration") or 0)
            if min_s <= d <= max_s:
                return e
        except:
            continue
    return None

def _ytdlp_extract(url_or_search: str, quiet=True):
    if not YoutubeDL:
        raise RuntimeError("yt-dlp missing")
    opts = {
        "quiet": quiet,
        "no_warnings": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "noplaylist": True,
        "extract_flat": False,
        "skip_download": True,
    }
    with YoutubeDL(opts) as ydl:
        return ydl.extract_info(url_or_search, download=False)

def _ytdlp_download_audio(url: str, outdir: str, method: int = 1):
    """
    4 طرق متناسقة لتنزيل الصوت:
    1) bestaudio -> mp3
    2) bestaudio[ext=m4a] -> mp3
    3) bestaudio[protocol^=https] -> mp3
    4) تنزيل mp4 ثم استخراج mp3 بـ ffmpeg
    يرجّع: (filepath, info_dict)
    """
    if not YoutubeDL:
        raise RuntimeError("yt-dlp missing")

    _ensure_dir(outdir)
    outtmpl = os.path.join(outdir, "%(title).180s [%(id)s].%(ext)s")

    common = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "noplaylist": True,
        "outtmpl": outtmpl,
        "retries": 5,
        "fragment_retries": 5,
        "concurrent_fragment_downloads": 8,
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"},
        ],
        "prefer_ffmpeg": True,
    }

    # METHOD 4 يحتاج ffmpeg
    if method == 4:
        if not _ffmpeg_exists():
            raise RuntimeError("ffmpeg missing for method 4")

        mp4tmpl = os.path.join(outdir, "%(title).180s [%(id)s].%(ext)s")
        opts = {
            **common,
            "format": "best[ext=mp4]/best",
            "outtmpl": mp4tmpl,
            "postprocessors": [],  # لا نحول هنا
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # اعثر على الملف الذي تم تنزيله (mp4)
        mp4_file = None
        for f in os.listdir(outdir):
            if f.lower().endswith(".mp4"):
                mp4_file = os.path.join(outdir, f)
                break
        if not mp4_file:
            raise RuntimeError("method4 mp4 not found")

        mp3_file = os.path.splitext(mp4_file)[0] + ".mp3"
        cmd = ["ffmpeg", "-y", "-i", mp4_file, "-vn", "-acodec", "libmp3lame", "-b:a", "192k", mp3_file]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

        if not os.path.exists(mp3_file):
            raise RuntimeError("method4 mp3 extract failed")

        # نظّف mp4
        _safe_rm(mp4_file)
        info["ext"] = "mp3"
        return mp3_file, info

    # METHODS 1-3
    if method == 1:
        fmt = "bestaudio/best"
    elif method == 2:
        fmt = "bestaudio[ext=m4a]/bestaudio/best"
    else:
        fmt = "bestaudio[protocol^=https]/bestaudio/best"

    opts = {**common, "format": fmt}

    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # ابحث عن mp3 النهائي
    mp3_file = None
    for f in os.listdir(outdir):
        if f.lower().endswith(".mp3"):
            mp3_file = os.path.join(outdir, f)
            break
    if not mp3_file:
        # أحياناً ينتج ext مختلف، جرّب تلقط أي ملف صوتي
        for f in os.listdir(outdir):
            if f.lower().endswith((".m4a", ".webm", ".opus", ".mp3")):
                mp3_file = os.path.join(outdir, f)
                break

    if not mp3_file:
        raise RuntimeError("audio file not found after download")

    return mp3_file, info

def _ytdlp_download_video(url: str, outdir: str, height: int, method: int = 1):
    """
    3 طرق لتنزيل فيديو بجودة محددة:
    1) bestvideo[<=h]+bestaudio -> mp4 merge
    2) best[ext=mp4][<=h] (progressive)
    3) best[<=h] ثم تحويل/دمج إن لزم
    يرجّع: (filepath, info_dict, thumb_path_or_none)
    """
    if not YoutubeDL:
        raise RuntimeError("yt-dlp missing")
    _ensure_dir(outdir)

    outtmpl = os.path.join(outdir, "cat_ytv_%(id)s.%(ext)s")
    common = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "noplaylist": True,
        "outtmpl": outtmpl,
        "retries": 5,
        "fragment_retries": 5,
        "concurrent_fragment_downloads": 8,
        "writethumbnail": True,
        "prefer_ffmpeg": True,
        "merge_output_format": "mp4",
    }

    if method == 1:
        fmt = f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best[height<={height}]"
    elif method == 2:
        fmt = f"best[ext=mp4][height<={height}]/best[height<={height}]"
    else:
        fmt = f"best[height<={height}]/best"

    opts = {**common, "format": fmt}

    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # ابحث عن mp4 النهائي
    mp4_file = None
    for f in os.listdir(outdir):
        if f.lower().endswith(".mp4") and f.startswith("cat_ytv_"):
            mp4_file = os.path.join(outdir, f)
            break
    if not mp4_file:
        # أي mp4
        for f in os.listdir(outdir):
            if f.lower().endswith(".mp4"):
                mp4_file = os.path.join(outdir, f)
                break
    if not mp4_file:
        raise RuntimeError("video mp4 not found after download")

    # thumb
    thumb = None
    for f in os.listdir(outdir):
        if f.lower().endswith((".jpg", ".webp", ".png")):
            thumb = os.path.join(outdir, f)
            break

    return mp4_file, info, thumb


# --- دوال المساعدة الداخلية (كما هي) ---

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
# 1. تحميل الصوت (YouTube/SoundCloud etc) - محسّن
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

    urls = extractor.find_urls(msg or "")
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")

    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)

    for url in urls:
        try:
            # اجلب بيانات سريعة
            try:
                vid_data = await pool.run_in_thread(_ytdlp_extract)(url)
            except:
                vid_data = {"title": url, "uploader": "Catuserbot", "formats": []}

            startTime = time()

            # 0) حاول helper القديم (لو موجود) ثم fallback
            retcode = 1
            try:
                retcode = await _mp3Dl(url=url, starttime=startTime, uid="320")
            except:
                retcode = 1

            temp_dir = os.path.join(Config.TEMP_DIR, f"zed_aud_{int(startTime)}_{uuid4().hex[:6]}")
            _ensure_dir(temp_dir)

            _fpath = ""
            thumb_pic = None

            if retcode == 0:
                # استخرج من مجلد helper (كما كان)
                for _path in glob.glob(os.path.join(Config.TEMP_DIR, str(startTime), "*")):
                    if _path.lower().endswith((".jpg", ".png", ".webp")):
                        thumb_pic = _path
                    else:
                        _fpath = _path

            # لو helper فشل، شغل 4 طرق متناسقة
            if not _fpath:
                last_err = None
                for method in (1, 2, 3, 4):
                    try:
                        _fpath, info = await pool.run_in_thread(_ytdlp_download_audio)(url, temp_dir, method)
                        # حدّث بيانات العنوان لو ناقصة
                        if isinstance(info, dict) and info.get("title"):
                            vid_data["title"] = info.get("title")
                            vid_data["uploader"] = info.get("uploader") or vid_data.get("uploader")
                            vid_data["duration"] = info.get("duration") or vid_data.get("duration")
                        break
                    except Exception as e:
                        last_err = e
                        _fpath = ""
                        continue
                if not _fpath:
                    _safe_rm(temp_dir)
                    return await event.edit(f"**- خطأ في التحميل.**\n__{last_err}__")

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
                            await get_ytthumb(await get_yt_video_id(url))
                        )
                    )
                except:
                    pass

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

            # تنظيف
            if retcode == 0:
                for _path in [_fpath, thumb_pic]:
                    if _path and os.path.exists(_path):
                        _safe_rm(_path)
            else:
                _safe_rm(temp_dir)
                _safe_rm(thumb_pic)

        except Exception as e:
            await zedevent.edit(f"**- خطأ:** {e}")

    await zedevent.delete()


# =========================================================
# 1.1 يوت (بحث + تنزيل صوت مباشر من 1 لـ 25 دقيقة)
# =========================================================

@zedub.zed_cmd(
    pattern="يوت(?:\s|$)([\s\S]*)",
    command=("يوت", plugin_category),
    info={
        "header": "بحث يوتيوب وتنزيل الصوت مباشرة (من 1 إلى 25 دقيقة)",
        "مثــال": ["{tr}يوت حلمي تحطم واختفى"],
    },
)
async def yt_song_search_and_audio(event):
    q = event.pattern_match.group(1)
    if event.is_reply and not q:
        r = await event.get_reply_message()
        q = r.text
    q = (q or "").strip()
    if not q:
        return await edit_delete(event, "**╮ بالـرد ﮼؏ كلمـٓھہ للبحث أو ضعها مـع الأمـر ... 𓅫╰**")

    if not YoutubeDL:
        return await edit_or_reply(event, "**- عذراً، مكتبة `yt-dlp` غير مثبتة.**")

    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)

    try:
        # ابحث عدة نتائج وخذ المناسب بالمدة
        info = await pool.run_in_thread(_ytdlp_extract)(f"ytsearch8:{q}")
        picked = _pick_audio_entry(info, AUDIO_MIN_SEC, AUDIO_MAX_SEC)
        if not picked:
            return await edit_delete(zedevent, "**- لم أجد نتيجة مناسبة (لازم 1 - 25 دقيقة).**", 10)

        url = picked.get("webpage_url") or picked.get("url")
        if not url:
            return await edit_delete(zedevent, "**- حدث خطأ أثناء جلب الرابط.**", 10)

        startTime = time()
        temp_dir = os.path.join(Config.TEMP_DIR, f"zed_song_{int(startTime)}_{uuid4().hex[:6]}")
        _ensure_dir(temp_dir)

        last_err = None
        _fpath = ""
        vid_data = {
            "title": picked.get("title") or q,
            "uploader": picked.get("uploader") or "Unknown artist",
            "duration": picked.get("duration") or 0,
        }

        # 4 طرق متناسقة
        for method in (1, 2, 3, 4):
            try:
                _fpath, info2 = await pool.run_in_thread(_ytdlp_download_audio)(url, temp_dir, method)
                if isinstance(info2, dict) and info2.get("title"):
                    vid_data["title"] = info2.get("title")
                    vid_data["uploader"] = info2.get("uploader") or vid_data["uploader"]
                    vid_data["duration"] = info2.get("duration") or vid_data["duration"]
                break
            except Exception as e:
                last_err = e
                _fpath = ""
                continue

        if not _fpath:
            _safe_rm(temp_dir)
            return await zedevent.edit(f"**- خطأ في التحميل.**\n__{last_err}__")

        await zedevent.edit(
            f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
            \n**{vid_data.get('title', 'Audio')}***"
        )

        # thumb
        thumb_pic = None
        try:
            vid = picked.get("id") or await get_yt_video_id(url)
            thumb_pic = str(await pool.run_in_thread(download)(await get_ytthumb(vid)))
        except:
            thumb_pic = None

        attributes, mime_type = get_attributes(str(_fpath))
        ul = io.open(pathlib.Path(_fpath), "rb")

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

        _safe_rm(temp_dir)
        _safe_rm(thumb_pic)
        await zedevent.delete()

    except Exception as e:
        await zedevent.edit(f"**- خطأ:** {e}")


# =========================================================
# 2. تحميل الفيديو (YouTube/Facebook/Snapchat/Tiktok/Likee) - كما هو لكن أقوى
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

    urls = extractor.find_urls(msg or "")
    if not urls:
        return await edit_or_reply(event, "**- قـم بادخــال رابـط مع الامـر او بالــرد ع رابـط ليتـم التحميـل**")

    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    reply_to_id = await reply_id(event)

    for url in urls:
        try:
            # نزّل بجودة أفضل (Best) مع fallback داخلي
            outdir = os.path.join(Config.TEMP_DIR, f"zed_vid_{int(time())}_{uuid4().hex[:6]}")
            _ensure_dir(outdir)

            last_err = None
            fpath = None
            info = None
            thumb = None

            for method in (1, 2, 3):
                try:
                    fpath, info, thumb = await pool.run_in_thread(_ytdlp_download_video)(url, outdir, 720, method)
                    break
                except Exception as e:
                    last_err = e
                    fpath = None
                    continue

            if not fpath or not info:
                _safe_rm(outdir)
                return await zedevent.edit(f"**- خطأ:** {last_err}")

            await zedevent.edit(
                f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
                \n**{info.get('title','Video')}**"
            )

            ul = io.open(fpath, "rb")
            c_time = time()
            attributes, mime_type = await fix_attributes(
                pathlib.Path(fpath), info, supports_streaming=True
            )
            uploaded = await event.client.fast_upload_file(
                file=ul,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(
                        d, t, zedevent, c_time, "Upload :", file_name=info.get("title", "Video")
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
                caption=f'**⎉╎المقطــع :** `{info.get("title","Video")}`',
                thumb=thumb if thumb and os.path.exists(thumb) else None,
                supports_streaming=True,
            )

            _safe_rm(outdir)

        except TypeError:
            await asyncio.sleep(2)
        except Exception as e:
            await zedevent.edit(f"**- خطأ:** {e}")

    await event.delete()


# =========================================================
# 2.1 فيديو (بحث/رابط + لوحة انلاين لاختيار الجودة)
# =========================================================

def _build_quality_buttons(req_id: str):
    rows = [
        [Button.inline("144p", data=f"ZEDVID|{req_id}|144p".encode()),
         Button.inline("240p", data=f"ZEDVID|{req_id}|240p".encode()),
         Button.inline("360p", data=f"ZEDVID|{req_id}|360p".encode())],
        [Button.inline("480p", data=f"ZEDVID|{req_id}|480p".encode()),
         Button.inline("720p", data=f"ZEDVID|{req_id}|720p".encode())],
    ]
    return rows

async def _resolve_video_url(query_or_url: str):
    """
    إذا رابط => يرجع الرابط
    إذا اسم => يبحث ويجيب أول نتيجة
    """
    if not YoutubeDL:
        return None, None
    q = (query_or_url or "").strip()
    if not q:
        return None, None

    # إذا فيه رابط واضح
    if extractor:
        urls = extractor.find_urls(q)
        if urls:
            return urls[0], None

    # بحث
    info = await pool.run_in_thread(_ytdlp_extract)(f"ytsearch1:{q}")
    if info.get("entries"):
        e = info["entries"][0]
        url = e.get("webpage_url") or e.get("url")
        title = e.get("title")
        return url, title
    # أحياناً يرجع مباشرة
    url = info.get("webpage_url") or info.get("url")
    return url, info.get("title")

@zedub.zed_cmd(
    pattern="فيديو(?:\s|$)([\s\S]*)",
    command=("فيديو", plugin_category),
    info={
        "header": "بحث/تحميل فيديو من يوتيوب مع اختيار الجودة من لوحة انلاين",
        "مثــال": [
            "{tr}فيديو توبز مع باري",
            "{tr}فيديو + رابط",
            "{tr}فيديو بالرد على رابط",
        ],
    },
)
async def zed_video_inline_quality(event):
    q = event.pattern_match.group(1)
    if event.is_reply and not q:
        r = await event.get_reply_message()
        q = r.text
    q = (q or "").strip()
    if not q:
        return await edit_delete(
            event, "**╮ بالـرد ﮼؏ كلمـٓھہ للبحث أو ضعها مـع الأمـر ... 𓅫╰**"
        )
    if not YoutubeDL:
        return await edit_or_reply(event, "**- عذراً، مكتبة `yt-dlp` غير مثبتة.**")

    video_q = await edit_or_reply(event, "**╮ جـارِ البحث ▬▭... ╰**")
    try:
        url, title = await _resolve_video_url(q)
        if not url:
            return await edit_delete(video_q, "**- لم أستطع الوصول للرابط.**", 10)

        req_id = uuid4().hex[:10]
        _ZED_VID_REQUESTS[req_id] = {
            "url": url,
            "chat_id": event.chat_id,
            "user_id": event.sender_id,
            "reply_to": await reply_id(event),
            "title": title or q,
            "ts": int(time()),
        }

        # نفس الستايل (ما غيرت فخامة، بس زرار)
        await video_q.edit(
            "**╮ ❐ اختر الجودة من اللوحة بالأسفل ...𓅫╰**",
            buttons=_build_quality_buttons(req_id),
        )
    except Exception as e:
        await edit_delete(video_q, str(e), time=10)


@zedub.on(events.CallbackQuery(pattern=b"ZEDVID\\|"))
async def zed_video_quality_cb(event):
    """
    Callback: ZEDVID|<req_id>|<quality>
    """
    try:
        data = event.data.decode("utf-8")
        _, req_id, q = data.split("|", 2)
        req = _ZED_VID_REQUESTS.get(req_id)
        if not req:
            return await event.answer("انتهت الجلسة.", alert=True)

        # السماح لصاحب الطلب فقط
        if int(req.get("user_id", 0)) != int(event.sender_id):
            return await event.answer("هذا الطلب ليس لك.", alert=True)

        quality = q.strip()
        height = YT_QUALITIES.get(quality)
        if not height:
            return await event.answer("جودة غير صالحة.", alert=True)

        # إظهار أنه تم اختيار الجودة
        await event.answer(f"تم اختيار {quality}", alert=False)

        # عدّل نفس الرسالة (بدون تغيير فخامة كبيرة)
        await event.edit(f"**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**\n**⎉╎الجودة:** `{quality}`")

        url = req["url"]
        chat_id = req["chat_id"]
        reply_to_id = req["reply_to"]

        outdir = os.path.join(Config.TEMP_DIR, f"zed_vidq_{req_id}_{quality}")
        _ensure_dir(outdir)

        last_err = None
        fpath = None
        info = None
        thumb = None

        # 3 طرق قوية
        for method in (1, 2, 3):
            try:
                fpath, info, thumb = await pool.run_in_thread(_ytdlp_download_video)(url, outdir, height, method)
                break
            except Exception as e:
                last_err = e
                fpath = None
                continue

        if not fpath or not info:
            _safe_rm(outdir)
            return await event.edit(f"**- خطأ:** {last_err}")

        await event.edit(
            f"**╮ ❐ جـارِ التحضيـر للـرفع انتظـر ...𓅫╰**:\
            \n**{info.get('title','Video')}**"
        )

        # رفع كفيديو/Streaming
        ul = io.open(fpath, "rb")
        c_time = time()

        attributes, mime_type = await fix_attributes(
            pathlib.Path(fpath), info, supports_streaming=True
        )
        uploaded = await event.client.fast_upload_file(
            file=ul,
            progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                progress(
                    d, t, event, c_time, "Upload :", file_name=info.get("title", "Video")
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
            chat_id,
            file=media,
            reply_to=reply_to_id,
            caption=f'**⎉╎المقطــع :** `{info.get("title","Video")}`',
            thumb=thumb if thumb and os.path.exists(thumb) else None,
            supports_streaming=True,
        )

        _safe_rm(outdir)
        _ZED_VID_REQUESTS.pop(req_id, None)

        # احذف رسالة اللوحة بعد الإرسال (اختياري) - نخليها كما هي لكن نحدّثها
        await event.edit("**- تـم ✅**")

    except Exception as e:
        try:
            await event.edit(f"**- خطأ:** {e}")
        except:
            pass


# =========================================================
# 3. انستا (عن طريق البوتات) - كما هو
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

    v1 = "Fullsavebot"
    v2 = "@videomaniacbot"
    media_list = []
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")

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
            pass

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
# 4. بنترست (Pinterest) - كما هو
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

    try:
        if YoutubeDL:
            with YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(M, download=False)
                url = info.get('url')
                await event.client.send_file(event.chat.id, url, caption="**Pinterest Download**")
        else:
            await A.edit("**- yt-dlp غير مثبتة.**")
    except Exception as e:
        await A.edit(f"**- خطأ:** {e}")

    await A.delete()


# =========================================================
# 5. بحث يوتيوب (YouTube Search) - كما هو (روابط فقط)
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
        full_response = await ytsearch(query, limit=lim)
    except Exception as e:
        return await edit_delete(video_q, str(e), time=10)

    reply_text = f"**⎉╎اليك عزيزي قائمة بروابط الكلمة اللتي بحثت عنها:**\n`{query}`\n\n**⎉╎النتائج:**\n{full_response}"
    await edit_or_reply(video_q, reply_text)