import asyncio
import json
import os

# استخدام المكتبة الجديدة والحديثة في 2026 بدلاً من yt-dlp المزعجة
from pytubefix import Search, YouTube
from telethon import events
from telethon.tl.types import DocumentAttributeAudio

from .. import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id

plugin_category = "البحث"

# =========================================================
# نظام حفظ حالة "تفعيل/تعطيل اليوتيوب" لتعمل حتى بعد الريستارت
# =========================================================
CONFIG_FILE = "yt_public_config.json"


def is_yt_public():
    """التحقق مما إذا كان اليوتيوب مفعلاً للعامة"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("is_public", False)
    return False


def set_yt_public(state: bool):
    """تغيير حالة اليوتيوب للعامة وحفظها بملف"""
    with open(CONFIG_FILE, "w") as f:
        json.dump({"is_public": state}, f)


# =========================================================
# دالة التحميل بالمكتبة الجديدة (سريعة جداً ومحمية ضد الحظر)
# =========================================================
def download_audio_modern(query):
    # إذا كان المدخل رابطاً
    if query.startswith("http"):
        # use_po_token=True تتخطى حماية يوتيوب بشكل أصلي
        yt = YouTube(query, use_po_token=True)
    else:
        # إذا كان نص بحث
        s = Search(query)
        if not s.videos:
            raise Exception("لـم أتمكـن مـن العثـور علـى المقطـع.")
        yt = s.videos[0]

    # جلب معلومات المقطع (الفنان، الاسم، المدة)
    title = yt.title
    author = yt.author
    duration = yt.length

    # سحب أفضل جودة صوتية مباشرة (بدون الحاجة لتحويلات السيرفر البطيئة)
    stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()
    if not stream:
        raise Exception("الصيغـة الصوتيـة غيـر متـوفـرة لهـذا المقطـع.")

    # التحميل بسرعة جنونية
    out_file = stream.download()

    # تحويل الامتداد إلى m4a ليتعرف عليه تيليجرام كصوتية احترافية
    base, ext = os.path.splitext(out_file)
    final_file = base + ".m4a"

    if out_file != final_file:
        try:
            os.rename(out_file, final_file)
        except Exception:
            final_file = out_file

    return final_file, title, author, duration


# =========================================================
# معالج معتمد للردود ورفع الصوتيات (سواء للمالك أو للأعضاء)
# =========================================================
async def process_and_send_audio(
    client, chat_id, query, reply_msg_id, sender_name, progress_msg=None
):
    try:
        # تشغيل التحميل في الخلفية لمنع تعليق السورس
        loop = asyncio.get_event_loop()
        file_path, title, author, duration = await loop.run_in_executor(
            None, download_audio_modern, query
        )
    except Exception as e:
        if progress_msg:
            await progress_msg.edit(
                f"**⎉╎عـذراً، حـدث خـطأ أثنـاء جلـب المقطـع:**\n`{str(e)}`"
            )
        return

    try:
        # تحديث الكليشة أثناء الرفع للتفاعل مع المستخدم
        if progress_msg:
            await progress_msg.edit("**•❐• جـاري رفـع الصـوتـيـة ..**")

        caption_text = f"**⎉╎الاسـم :** `{title}`\n" f"**⎉╎بطلب مـن :** {sender_name}"

        # جعل الملف يبدو كأغنية موسيقية رسمية داخل تليجرام
        audio_attributes = [
            DocumentAttributeAudio(
                duration=int(duration) if duration else 0, title=title, performer=author
            )
        ]

        await client.send_file(
            chat_id,
            file_path,
            caption=caption_text,
            attributes=audio_attributes,
            reply_to=reply_msg_id,
        )

        # إزالة كليشة التحميل فور إرسال المقطع
        if progress_msg:
            await progress_msg.delete()

    except Exception as e:
        if progress_msg:
            await progress_msg.edit(f"**خطأ أثناء الإرسال:** `{e}`")
    finally:
        # تنظيف فوري لملفات السيرفر لعدم استهلاك المساحة
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)


# =========================================================
# 1. أوامر التحكم باليوتيوب (تفعيل / تعطيل) للمجموعات
# =========================================================
@zedub.zed_cmd(pattern="تفعيل اليوتيوب")
async def enable_yt_public(event):
    set_yt_public(True)
    await edit_delete(
        event,
        "**⎉╎تـم تفعيـل اليوتيـوب للأعضـاء بنجـاح ✅\nالآن يمكن لأي شخص كتابة (يوت + اسم المقطع).**",
        7,
    )


@zedub.zed_cmd(pattern="تعطيل اليوتيوب")
async def disable_yt_public(event):
    set_yt_public(False)
    await edit_delete(
        event,
        "**⎉╎تـم تعطيـل اليوتيـوب للأعضـاء بنجـاح ❌\nالآن أنت فقط (المالك) من يمكنه استخدامه.**",
        7,
    )


# =========================================================
# 2. أمر اليوتيوب الخاص بك (المالك) يعمل في أي وقت
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

    # النمط المطلوب لزدثون
    zedevent = await edit_or_reply(
        event, "**•❐• جـاري الـبـحـث وتـحـمـيـل الصـوتـيـة ..**"
    )

    sender_name = event.client.me.first_name
    await process_and_send_audio(
        event.client, event.chat_id, query, await reply_id(event), sender_name, zedevent
    )


# =========================================================
# 3. مستمع الجروبات الذكي (يستجيب للأعضاء إذا كان مفعلاً)
# =========================================================
@zedub.on(events.NewMessage(incoming=True))
async def public_yt_handler(event):
    # نتجاهل فوراً إذا كان معطلاً
    if not is_yt_public():
        return

    # نتجاهل إذا لم يكن هناك نص أو في الخاص
    if not event.is_group or not event.message.message:
        return

    text = event.message.message.strip()

    # الاستجابة لأمر (يوت) و (.يوت)
    if text.startswith("يوت ") or text.startswith(".يوت "):
        query = text.replace(".يوت", "", 1).replace("يوت", "", 1).strip()

        if not query:
            return

        # النمط المطلوب لزدثون للرد على العضو
        progress_msg = await event.reply(
            "**•❐• جـاري الـبـحـث وتـحـمـيـل الصـوتـيـة ..**"
        )

        sender = await event.get_sender()
        sender_name = getattr(sender, "first_name", "عضو")

        await process_and_send_audio(
            event.client,
            event.chat_id,
            query,
            event.message.id,
            sender_name,
            progress_msg,
        )
