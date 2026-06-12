import json
import os
import re
import urllib.parse

import aiohttp
from telethon import events
from telethon.tl.types import DocumentAttributeAudio

from .. import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id

plugin_category = "البحث"

# =========================================================
# نظام حفظ التفعيل/التعطيل
# =========================================================
CONFIG_FILE = "yt_public_config.json"


def is_yt_public():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("is_public", False)
    return False


def set_yt_public(state: bool):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"is_public": state}, f)


# =========================================================
# البحث وسحب الصوتية عبر API (الحل الجذري لتخطي الحظر)
# =========================================================
async def get_yt_audio_fast(query):
    # 1. البحث السريع جداً وجلب الرابط (بدون مكتبات)
    if not query.startswith("http"):
        search_query = urllib.parse.quote(query)
        search_url = f"https://www.youtube.com/results?search_query={search_query}"

        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as resp:
                html = await resp.text()
                # سحب أول آيدي فيديو من النتائج
                video_ids = re.findall(r"watch\?v=(\S{11})", html)
                if not video_ids:
                    raise Exception("لم يتم العثور على المقطع.")
                video_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
    else:
        video_url = query

    # 2. سحب الصوتية المباشرة باستخدام أقوى API مجاني (Cobalt)
    api_url = "https://api.cobalt.tools/api/json"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    payload = {"url": video_url, "aFormat": "mp3", "isAudioOnly": True}

    async with aiohttp.ClientSession() as session:
        async with session.post(api_url, json=payload, headers=headers) as resp:
            if resp.status != 200:
                raise Exception("سيرفر التحميل الخارجي عليه ضغط، جرب مرة أخرى.")

            data = await resp.json()
            if "url" not in data:
                raise Exception("فشل في سحب الصوتية.")

            # إرجاع الرابط المباشر للملف الصوتي
            return data["url"], video_url


# =========================================================
# دالة الإرسال الأنيقة
# =========================================================
async def process_and_send_audio(
    client, chat_id, query, reply_msg_id, sender_name, progress_msg=None
):
    try:
        # جلب الرابط المباشر
        audio_url, yt_url = await get_yt_audio_fast(query)

        if progress_msg:
            await progress_msg.edit("**•❐• جـاري رفـع الصـوتـيـة ..**")

        caption_text = (
            f"**⎉╎الاسـم :** [المقطـع الصـوتـي]({yt_url})\n"
            f"**⎉╎بطلب مـن :** {sender_name}"
        )

        audio_attributes = [
            DocumentAttributeAudio(
                duration=0,
                title=query if not query.startswith("http") else "صوتية",
                performer="YouTube",
            )
        ]

        # تيليجرام يحمل من الرابط المباشر بسرعة البرق دون المرور بسيرفرك
        await client.send_file(
            chat_id,
            audio_url,
            caption=caption_text,
            attributes=audio_attributes,
            reply_to=reply_msg_id,
        )

        if progress_msg:
            await progress_msg.delete()

    except Exception as e:
        if progress_msg:
            await progress_msg.edit(f"**⎉╎عـذراً، حـدث خـطأ:**\n`{str(e)}`")


# =========================================================
# 1. أوامر التحكم للمالك (تفعيل / تعطيل)
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
# 2. أمر المالك (يعمل في أي وقت)
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
        event, "**•❐• جـاري الـبـحـث وتـحـمـيـل الصـوتـيـة ..**"
    )
    sender_name = event.client.me.first_name
    await process_and_send_audio(
        event.client, event.chat_id, query, await reply_id(event), sender_name, zedevent
    )


# =========================================================
# 3. مستمع الجروبات للأعضاء
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
