import asyncio
import re
from telethon.errors import FloodWaitError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

from . import zedub
from ..core.managers import edit_or_reply

plugin_category = "الادمن"
zel_dev = [8241311871, 1111565135, 6114298715]

# حقوق الحظر الكامل
BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

def extract_entities(text):
    """استخراج اليوزرات والأيديات من النص"""
    usernames = re.findall(r"@[a-zA-Z0-9_]+", text)
    user_ids = re.findall(r"\b\d{7,13}\b", text)
    return list(set(usernames + user_ids))

@zedub.zed_cmd(pattern="^[.,]احظرهم([\s\S]*)")
async def mass_ban_admin(event):
    if event.is_private:
        return await edit_or_reply(event, "**•❐• عـذراً .. هـذا الامـر يـستخـدم داخـل المجمـوعـات فقـط**")

    input_text = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    
    # جمع النص من الأمر أو الرد
    combined_text = input_text
    if reply and reply.text:
        combined_text += " " + reply.text
    
    entities = extract_entities(combined_text)
    if not entities:
        return await edit_or_reply(event, "**•❐• يـرجى الـرد عـلى قـائمـة يـوزرات/ايـديات او كـتـابتهـم بـعد الامـر**")

    zed = await edit_or_reply(event, f"**•❐• جـاري مـعالجـة حـظر ( {len(entities)} ) مـستخـدم مـن المجمـوعـة ..**")
    
    done = 0
    failed = 0
    me = await event.client.get_me()

    for target in entities:
        if str(me.id) in target or any(str(dev) in target for dev in zel_dev):
            continue
        try:
            await event.client(EditBannedRequest(event.chat_id, target, BANNED_RIGHTS))
            done += 1
            await asyncio.sleep(0.2) # تأخير بسيط لتجنب الفلود
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception:
            failed += 1
            continue

    await zed.edit(f"**•❐• تـم تـنفيـذ الـحظر الـجمـاعـي بـنجـاح**\n\n**• المـحظـوريـن :** ( {done} )\n**• الـفاشـل :** ( {failed} )")


@zedub.zed_cmd(pattern="^[.,]حظرهم([\s\S]*)")
async def mass_ban_command(event):
    input_text = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    
    combined_text = input_text
    if reply and reply.text:
        combined_text += " " + reply.text
    
    entities = extract_entities(combined_text)
    if not entities:
        return await edit_or_reply(event, "**•❐• يـرجى الـرد عـلى قـائمـة يـوزرات/ايـديات او كـتـابتهـم بـعد الامـر**")

    await event.delete()
    me = await event.client.get_me()

    for target in entities:
        if str(me.id) in target or any(str(dev) in target for dev in zel_dev):
            continue
        try:
            # إرسال أمر نصي لكل مستخدم لتفعيل بوتات أخرى أو نظام الحماية
            await event.client.send_message(event.chat_id, f"حظر {target}")
            await asyncio.sleep(0.3)
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception:
            continue