import os
import asyncio
from telethon import events
from telethon.tl.types import DocumentAttributeAudio
import yt_dlp

from .. import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id

plugin_category = "البحث"

def download_yt_audio(query):
    # إعدادات تخطي الحماية الجديدة ليوتيوب (Bypass Bot Detection)
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True, # تخطي فحص الشهادات الذي قد يكشف السيرفر
        # الخدعة الأهم: إيهام يوتيوب أن الطلب قادم من هاتف آيفون/أندرويد وليس سيرفر
        'extractor_args': {
            'youtube': ['player_client=ios,android', 'player_skip=webpage']
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate'
        }
    }
    
    if not query.startswith("http"):
        query = f"ytsearch1:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(query, download=True)
        if 'entries' in info_dict:
            info_dict = info_dict['entries'][0]
            
        file_path = ydl.prepare_filename(info_dict)
        return file_path, info_dict

# =========================================================
# 1. تحميل الصوتيات من يوتيوب (بحث مباشر أو رابط) بسرعة فائقة
# =========================================================
@zedub.zed_cmd(
    pattern=r"يوت(?:\s+([\s\S]*))?",
    command=("يوت", plugin_category),
    info={
        "header": "تحميل صوتيات يوتيوب بسرعة جنونية",
        "شرح": "يبحث في يوتيوب وينزل الصوتية مباشرة بدون بوتات وبأعلى جودة",
        "طرق الاستخدام": [
            "{tr}يوت + اسم الاغنية أو المقطع",
            "{tr}يوت + رابط يوتيوب",
            "{tr}يوت (بالرد على اسم أو رابط)"
        ],
    },
)
async def zed_yt_audio(event):
    query = event.pattern_match.group(1)

    if not query and event.is_reply:
        reply_msg = await event.get_reply_message()
        query = reply_msg.text

    query = (query or "").strip()

    if not query:
        return await edit_delete(event, "**╮ أرسـل أسـم المقطـع أو الرابـط مـع الأمـر أو بالـرد ... 𓅫╰**", 5)

    zedevent = await edit_or_reply(event, "**•❐• جـاري الـبـحـث وتـحـمـيـل الصـوتـيـة ..**")

    try:
        loop = asyncio.get_event_loop()
        file_path, info = await loop.run_in_executor(None, download_yt_audio, query)
    except Exception as e:
        error_text = str(e)
        if "Sign in to confirm" in error_text:
            error_text = "يوتيوب ما زال يحظر سيرفرك (يطلب Cookies). يرجى التأكد من تحديث مكتبة yt-dlp بأمر `pip install --upgrade yt-dlp`"
        
        return await edit_delete(zedevent, f"**⎉╎عـذراً، حـدث خـطأ أثنـاء جلـب المقطـع:**\n`{error_text}`", 10)

    try:
        title = info.get("title", "صوتية")
        uploader = info.get("uploader", "YouTube")
        duration = int(info.get("duration", 0))

        caption_text = (
            f"**⎉╎الاسـم :** `{title}`\n"
            f"**⎉╎بواسطـة :** {event.client.me.first_name}"
        )

        audio_attributes = [
            DocumentAttributeAudio(
                duration=duration,
                title=title,
                performer=uploader
            )
        ]

        await event.client.send_file(
            event.chat_id,
            file_path,
            caption=caption_text,
            attributes=audio_attributes,
            reply_to=await reply_id(event)
        )
        
        await zedevent.delete()

    except Exception as e:
        await edit_delete(zedevent, f"**خطأ أثناء الإرسال:** `{e}`", 5)
    
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)