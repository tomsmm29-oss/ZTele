import json
import os
import urllib.parse
import uuid
import aiohttp
from telethon import events
from telethon.tl.types import DocumentAttributeAudio

from .. import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id

plugin_category = "البحث"

# =========================================================
# نظام حفظ التفعيل/التعطيل ومجلد التخزين
# =========================================================
CONFIG_FILE = "yt_public_config.json"
DOWNLOAD_DIR = "yt_downloads"

# إنشاء مجلد التحميل المحلي
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def is_yt_public():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("is_public", False)
    return False

def set_yt_public(state: bool):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"is_public": state}, f)

# =========================================================
# دالة التحميل السريعة (عبر API TNT الخاص بك)
# =========================================================
async def download_via_tnt_api(query):
    # تحديد هل الطلب رابط أم نص بحث
    if query.startswith("http"):
        api_url = f"http://145.223.80.56:5095/download_youtube?url={urllib.parse.quote(query)}"
    else:
        api_url = f"http://145.223.80.56:5095/download_youtube?query={urllib.parse.quote(query)}"

    async with aiohttp.ClientSession() as session:
        # 1. جلب بيانات المقطع من الـ API
        async with session.get(api_url) as resp:
            if resp.status != 200:
                raise Exception("سيرفر API التحميل لا يستجيب حالياً.")
            
            data = await resp.json()
            
            if not data.get("success"):
                raise Exception("فشل العثور على المقطع عبر الـ API.")
            
            audio_url = data.get("audio")
            title = data.get("title", "صوتية غير معروفة")
            channel = data.get("channel", "غير معروف")
            duration = data.get("duration", 0)

            if not audio_url:
                raise Exception("لم يتم العثور على رابط الصوتية.")

        # 2. تحميل الملف الصوتي من الـ API إلى سيرفر البوت محلياً
        # نستخدم uuid لضمان اسم ملف فريد وعدم تداخل التحميلات
        file_path = os.path.join(DOWNLOAD_DIR, f"{uuid.uuid4().hex}.mp3")
        
        async with session.get(audio_url) as audio_resp:
            if audio_resp.status == 200:
                with open(file_path, "wb") as f:
                    f.write(await audio_resp.read())
                
                return {
                    'file_path': file_path,
                    'title': title,
                    'uploader': channel,
                    'duration': duration
                }
            else:
                raise Exception("فشل سحب الملف الصوتي من سيرفر الـ API.")

# =========================================================
# دالة الإرسال والرفع
# =========================================================
async def process_and_send_audio(
    client, chat_id, query, reply_msg_id, sender_mention, progress_msg=None
):
    file_path = None
    try:
        # 1. التحميل عبر الـ API
        info = await download_via_tnt_api(query)
        file_path = info['file_path']

        # 2. تعديل الرسالة إلى "جاري الرفع" مع تخطي خطأ تليجرام
        if progress_msg:
            try:
                await progress_msg.edit("**•❐• جـاري الـرفـع ..**")
            except:
                pass

        # الكابشن يحتوي فقط على بطلب من (الاسم ماركداون)
        caption_text = f"**⎉╎بطلـب مـن :** {sender_mention}"

        # دمج الاسم والفنان في معلومات الصوتية نفسها ليتعرف عليها تليجرام
        audio_attributes = [
            DocumentAttributeAudio(
                duration=info['duration'],
                title=info['title'],
                performer=info['uploader'],
            )
        ]

        # 3. الرفع الفعلي
        await client.send_file(
            chat_id,
            file_path,
            caption=caption_text,
            attributes=audio_attributes,
            reply_to=reply_msg_id,
        )

        # 4. حذف رسالة الانتظار بعد الرفع
        if progress_msg:
            await progress_msg.delete()

    except Exception as e:
        if progress_msg:
            try:
                await progress_msg.edit(f"**⎉╎عـذراً، حـدث خـطأ:**\n`{str(e)}`")
            except:
                pass
            
    finally:
        # تنظيف السيرفر من الملف لتوفير المساحة
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

# =========================================================
# أوامر التحكم للمالك
# =========================================================
@zedub.zed_cmd(pattern="تفعيل اليوتيوب")
async def enable_yt_public(event):
    set_yt_public(True)
    await edit_delete(
        event,
        "**•❐• تـم تفعيـل بـحـث اليوتيـوب للـعـامـة ..**\n**⎉╎الآن يمكـن للجميـع استخـدام أمـر ( يوت )**",
        7,
    )

@zedub.zed_cmd(pattern="تعطيل اليوتيوب")
async def disable_yt_public(event):
    set_yt_public(False)
    await edit_delete(
        event,
        "**•❐• تـم تعطيـل بـحـث اليوتيـوب للـعـامـة ..**\n**⎉╎الآن يمكـنـك أنـت فـقـط استخـدام الأمـر**",
        7,
    )

# =========================================================
# أمر المالك
# =========================================================
@zedub.zed_cmd(pattern=r"يوت(?:\s+([\s\S]*))?")
async def zed_yt_owner(event):
    query = event.pattern_match.group(1)

    if not query and event.is_reply:
        reply_msg = await event.get_reply_message()
        query = reply_msg.text

    query = (query or "").strip()

    if not query:
        return await edit_delete(
            event, "**╮ أرسـل أسـم المقطـع أو الرابـط مـع الأمـر أو بالـرد ... 𓅫╰**", 5
        )

    zedevent = await edit_or_reply(
        event, "**•❐• جـاري الـبـحـث والتـحـمـيـل ..**"
    )
    
    # إنشاء منشن ماركداون لاسم المالك
    me = await event.client.get_me()
    sender_mention = f"[{me.first_name}](tg://user?id={me.id})"

    await process_and_send_audio(
        event.client, event.chat_id, query, await reply_id(event), sender_mention, zedevent
    )

# =========================================================
# مستمع الجروبات للأعضاء
# =========================================================
@zedub.on(events.NewMessage(incoming=True))
async def public_yt_handler(event):
    if not is_yt_public() or not event.is_group or not event.message.message:
        return

    text = event.message.message.strip()

    if text.startswith("يوت ") or text.startswith(".يوت "):
        query = text.replace(".يوت", "", 1).replace("يوت", "", 1).strip()

        if not query:
            return

        progress_msg = await event.reply(
            "**•❐• جـاري الـبـحـث والتـحـمـيـل ..**"
        )
        sender = await event.get_sender()
        sender_name = getattr(sender, "first_name", "عضو")
        sender_id = getattr(sender, "id", 0)
        
        # إنشاء منشن ماركداون لاسم العضو
        sender_mention = f"[{sender_name}](tg://user?id={sender_id})"

        await process_and_send_audio(
            event.client,
            event.chat_id,
            query,
            event.message.id,
            sender_mention,
            progress_msg,
        )