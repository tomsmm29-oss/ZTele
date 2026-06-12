import asyncio
import os

import yt_dlp
from telethon.tl.types import DocumentAttributeAudio

from .. import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id

plugin_category = "البحث"


# دالة مساعدة لتشغيل التحميل في الخلفية بدون تعليق البوت
def download_yt_audio(query):
    # إعدادات التحميل لأقصى سرعة وأفضل جودة
    ydl_opts = {
        "format": "m4a/bestaudio/best",  # جلب الصوت مباشرة بصيغة تدعمها تيليجرام لتجنب وقت التحويل
        "outtmpl": "%(id)s.%(ext)s",  # اسم الملف (معرف الفيديو لمنع التداخل)
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    # إذا كان المدخل ليس رابطاً، نجعله يبحث في يوتيوب ويأخذ النتيجة الأولى
    if not query.startswith("http"):
        query = f"ytsearch1:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(query, download=True)
        # إذا كان بحث، نستخرج معلومات أول فيديو
        if "entries" in info_dict:
            info_dict = info_dict["entries"][0]

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
            "{tr}يوت (بالرد على اسم أو رابط)",
        ],
    },
)
async def zed_yt_audio(event):
    query = event.pattern_match.group(1)

    # حالة الرد على رسالة
    if not query and event.is_reply:
        reply_msg = await event.get_reply_message()
        query = reply_msg.text

    query = (query or "").strip()

    if not query:
        return await edit_delete(
            event, "**╮ أرسـل أسـم المقطـع أو الرابـط مـع الأمـر أو بالـرد ... 𓅫╰**", 5
        )

    # كليشة التحميل بستايل زدثون المطلوب
    zedevent = await edit_or_reply(
        event, "**•❐• جـاري الـبـحـث وتـحـمـيـل الصـوتـيـة ..**"
    )

    try:
        # تشغيل دالة التحميل بدون إيقاف مهام البوت الأخرى (Asyncio Executor)
        loop = asyncio.get_event_loop()
        file_path, info = await loop.run_in_executor(None, download_yt_audio, query)
    except Exception as e:
        return await edit_delete(
            zedevent,
            f"**⎉╎عـذراً، لـم أتمكـن مـن العثـور علـى المقطـع أو حـدث خـطأ:**\n`{str(e)}`",
            10,
        )

    try:
        title = info.get("title", "صوتية")
        uploader = info.get("uploader", "YouTube")
        duration = int(info.get("duration", 0))
        webpage_url = info.get("webpage_url", "")

        caption_text = (
            f"**⎉╎الاسـم :** `{title}`\n"
            f"**⎉╎بواسطـة :** {event.client.me.first_name}"
        )

        # تجهيز خصائص الصوتية لتظهر بشكل احترافي (مشغل الموسيقى)
        audio_attributes = [
            DocumentAttributeAudio(duration=duration, title=title, performer=uploader)
        ]

        # إرسال الملف لتيليجرام
        await event.client.send_file(
            event.chat_id,
            file_path,
            caption=caption_text,
            attributes=audio_attributes,
            reply_to=await reply_id(event),
        )

        # حذف كليشة "جاري البحث"
        await zedevent.delete()

    except Exception as e:
        await edit_delete(zedevent, f"**خطأ أثناء الإرسال:** `{e}`", 5)

    finally:
        # حذف الملف من السيرفر بعد الإرسال لتوفير المساحة
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)
