import os
import asyncio
import json
from telethon import events
from telethon.tl.types import DocumentAttributeAudio
import yt_dlp

from .. import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id

plugin_category = "البحث"

# =========================================================
# نظام حفظ حالة "تفعيل/تعطيل اليوتيوب" لتعمل دائماً
# =========================================================
CONFIG_FILE = "yt_public_config.json"

def is_yt_public():
    """التحقق مما إذا كان اليوتيوب مفعلاً للأعضاء"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("is_public", False)
    return False

def set_yt_public(state: bool):
    """حفظ حالة التفعيل في ملف"""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"is_public": state}, f)

# =========================================================
# الحل الجذري: فصل مهام yt-dlp لتخطي الحظر 100%
# =========================================================
def download_yt_audio(query):
    # الخطوة 1: البحث (بشكل طبيعي حتى لا تتعطل قائمة النتائج)
    if not query.startswith("http"):
        search_opts = {
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(search_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if not info or 'entries' not in info or len(info['entries']) == 0:
                raise Exception("عذراً، لم أتمكن من العثور على نتائج.")
            
            # استخراج معرف الفيديو للنتيجة الأولى
            video_id = info['entries'][0].get('id')
            query = f"https://www.youtube.com/watch?v={video_id}"

    # الخطوة 2: التحميل (نستخدم التخطي القوي لتجاوز حظر البوتات نهائياً)
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        # الخدعة الجوهرية: استخدام عميل أندرويد وتخطي صفحة الويب المحمية
        'extractor_args': {
            'youtube': ['player_client=android', 'player_skip=webpage']
        }
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(query, download=True)
        file_path = ydl.prepare_filename(info_dict)
        return file_path, info_dict

# =========================================================
# دالة الرفع والإرسال (بأسلوب زدثون الأنيق)
# =========================================================
async def process_and_send_audio(client, chat_id, query, reply_msg_id, sender_name, progress_msg=None):
    try:
        loop = asyncio.get_event_loop()
        file_path, info = await loop.run_in_executor(None, download_yt_audio, query)
    except Exception as e:
        if progress_msg:
            await progress_msg.edit(f"**⎉╎عـذراً، حـدث خـطأ أثنـاء جلـب المقطـع:**\n`{str(e)}`")
        return

    try:
        if progress_msg:
            # التحديث للنمط الثاني أثناء الرفع
            await progress_msg.edit("**•❐• جـاري رفـع الصـوتـيـة ..**")

        title = info.get("title", "صوتية")
        uploader = info.get("uploader", "YouTube")
        duration = int(info.get("duration", 0) or 0)

        caption_text = (
            f"**⎉╎الاسـم :** `{title}`\n"
            f"**⎉╎بطلب مـن :** {sender_name}"
        )

        audio_attributes = [
            DocumentAttributeAudio(
                duration=duration,
                title=title,
                performer=uploader
            )
        ]

        await client.send_file(
            chat_id,
            file_path,
            caption=caption_text,
            attributes=audio_attributes,
            reply_to=reply_msg_id
        )
        
        # حذف كليشة الرفع تماماً لتبقى الصوتية فقط
        if progress_msg:
            await progress_msg.delete()

    except Exception as e:
        if progress_msg:
            await progress_msg.edit(f"**خطأ أثناء الإرسال:** `{e}`")
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)


# =========================================================
# 1. أوامر التحكم الخاصة بالمالك (تفعيل / تعطيل)
# =========================================================
@zedub.zed_cmd(pattern="تفعيل اليوتيوب")
async def enable_yt_public(event):
    set_yt_public(True)
    await edit_delete(event, "**⎉╎تـم تفعيـل اليوتيـوب للأعضـاء بنجـاح ✅\nالآن يمكن لأي شخص كتابة (يوت + اسم المقطع).**", 7)

@zedub.zed_cmd(pattern="تعطيل اليوتيوب")
async def disable_yt_public(event):
    set_yt_public(False)
    await edit_delete(event, "**⎉╎تـم تعطيـل اليوتيـوب للأعضـاء بنجـاح ❌\nالآن أنت فقط (المالك) من يمكنه استخدامه.**", 7)


# =========================================================
# 2. أمر اليوتيوب للمالك (يعمل في أي وقت وبدون تفعيل)
# =========================================================
@zedub.zed_cmd(pattern=r"يوت(?:\s+([\s\S]*))?")
async def zed_yt_owner(event):
    query = event.pattern_match.group(1)

    if not query and event.is_reply:
        reply_msg = await event.get_reply_message()
        query = reply_msg.text

    query = (query or "").strip()

    if not query:
        return await edit_delete(event, "**╮ أرسـل أسـم المقطـع أو الرابـط مـع الأمـر أو بالـرد ... 𓅫╰**", 5)

    zedevent = await edit_or_reply(event, "**•❐• جـاري الـبـحـث وتـحـمـيـل الصـوتـيـة ..**")
    sender_name = event.client.me.first_name
    await process_and_send_audio(event.client, event.chat_id, query, await reply_id(event), sender_name, zedevent)


# =========================================================
# 3. مستمع الجروبات الذكي (يستجيب للأعضاء إذا كان مفعلاً)
# =========================================================
@zedub.on(events.NewMessage(incoming=True))
async def public_yt_handler(event):
    # تجاهل إذا كان معطلاً أو لم تكن الرسالة في جروب
    if not is_yt_public() or not event.is_group or not event.message.message:
        return

    text = event.message.message.strip()
    
    # الاستجابة لأمر (يوت كذا) و (.يوت كذا) للأعضاء
    if text.startswith("يوت ") or text.startswith(".يوت "):
        query = text.replace(".يوت", "", 1).replace("يوت", "", 1).strip()
        
        if not query:
            return

        progress_msg = await event.reply("**•❐• جـاري الـبـحـث وتـحـمـيـل الصـوتـيـة ..**")
        sender = await event.get_sender()
        sender_name = getattr(sender, "first_name", "عضو")
        
        await process_and_send_audio(event.client, event.chat_id, query, event.message.id, sender_name, progress_msg)