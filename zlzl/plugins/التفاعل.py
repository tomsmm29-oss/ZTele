import asyncio
import re

import emoji
from telethon import events
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import (
    MessageEntityCustomEmoji,
    ReactionCustomEmoji,
    ReactionEmoji,
)

from ..core.managers import edit_or_reply
from . import zedub

plugin_category = "الادمن"

# ==========================================
# ===== الذاكرة الحية للتفاعلات (Real-Time) =====
# ==========================================
ACTIVE_REACTIONS = {}

# ==========================================
# ====== دوال RAW API المفصولة والمستقلة ======
# ==========================================


async def react_normal_raw(client, peer, msg_id, emoji_str):
    """تفاعل ايموجي عادي - Raw API"""
    try:
        await client(
            SendReactionRequest(
                peer=peer, msg_id=msg_id, reaction=[ReactionEmoji(emoticon=emoji_str)]
            )
        )
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        await react_normal_raw(client, peer, msg_id, emoji_str)
    except Exception:
        pass


async def react_premium_raw(client, peer, msg_id, document_id):
    """تفاعل ايموجي مميز (Premium) - Raw API"""
    try:
        await client(
            SendReactionRequest(
                peer=peer,
                msg_id=msg_id,
                reaction=[ReactionCustomEmoji(document_id=document_id)],
            )
        )
    except FloodWaitError as e:
        await asyncio.sleep(e.seconds)
        await react_premium_raw(client, peer, msg_id, document_id)
    except Exception:
        pass


async def remove_reaction_raw(client, peer, msg_id):
    """إلغاء التفاعل - Raw API"""
    try:
        await client(SendReactionRequest(peer=peer, msg_id=msg_id, reaction=[]))
    except Exception:
        pass


# ==========================================
# =============== المحلل الذكي ================
# ==========================================


def parse_reaction_args(text, entities):
    count = 20  # الافتراضي
    is_all = False

    if "الكل" in text:
        is_all = True
        count = 999999
    else:
        match_count = re.search(r"\b(\d+)\b", text)
        if match_count:
            count = int(match_count.group(1))

    mentioned_users = re.findall(r"@[a-zA-Z0-9_]+", text)
    is_exclude = "استبعاد" in text

    emoji_obj = None
    is_premium = False

    if entities:
        for ent in entities:
            if isinstance(ent, MessageEntityCustomEmoji):
                emoji_obj = ent.document_id
                is_premium = True
                break

    if not emoji_obj:
        for char in text:
            if char in emoji.EMOJI_DATA:
                emoji_obj = char
                break

    return emoji_obj, is_premium, count, is_all, mentioned_users, is_exclude


async def get_target_ids(client, mentioned_users):
    """تحويل اليوزرات لأيديات مرة واحدة لتسريع المراقب الفوري"""
    target_ids = []
    if mentioned_users:
        for user in mentioned_users:
            try:
                ent = await client.get_entity(user)
                target_ids.append(ent.id)
            except Exception:
                pass
    return target_ids


# ==========================================
# ============ خوارزميات التنفيذ ============
# ==========================================


async def process_pm_reactions(event, peer, emoji_obj, is_premium, count, is_all):
    messages_to_react = []
    async for msg in event.client.iter_messages(peer, limit=count + 1):
        if msg.id == event.id:
            continue
        messages_to_react.append(msg.id)

    tasks = []
    for msg_id in messages_to_react:
        if is_premium:
            tasks.append(react_premium_raw(event.client, peer, msg_id, emoji_obj))
        else:
            tasks.append(react_normal_raw(event.client, peer, msg_id, emoji_obj))

    await asyncio.gather(*tasks)
    return len(messages_to_react)


async def process_group_reactions(
    event, peer, emoji_obj, is_premium, count, is_all, target_ids, is_exclude
):
    messages_to_react = []
    fetch_limit = count * 3 if not is_all else None

    async for msg in event.client.iter_messages(peer, limit=fetch_limit):
        if msg.id == event.id:
            continue

        sender = msg.sender_id
        if target_ids:
            if is_exclude and sender in target_ids:
                continue
            elif not is_exclude and sender not in target_ids:
                continue

        messages_to_react.append(msg.id)
        if len(messages_to_react) >= count:
            break

    tasks = []
    for msg_id in messages_to_react:
        if is_premium:
            tasks.append(react_premium_raw(event.client, peer, msg_id, emoji_obj))
        else:
            tasks.append(react_normal_raw(event.client, peer, msg_id, emoji_obj))

    await asyncio.gather(*tasks)
    return len(messages_to_react)


# ==========================================
# ================= الأوامر ==================
# ==========================================


# تم تعديل الريجيكس ليلتقط (رمز واحد) أو (رمزين) بذكاء
@zedub.zed_cmd(pattern=r"^([.,?!\"*'\_&$#@]{1,2})جر\s*(.*)$")
async def start_reactions(event):
    prefix = event.pattern_match.group(1)
    cmd_text = event.pattern_match.group(2)

    # تحديد نوع الأمر: رمز واحد (ماضي + جديد) | رمزين (جديد فقط)
    is_future_only = len(prefix) == 2

    zed = await edit_or_reply(event, "**•❐• جـاري الـتـجـهـيـز ...**")

    emoji_obj, is_premium, count, is_all, mentioned_users, is_exclude = (
        parse_reaction_args(cmd_text, event.message.entities)
    )

    if not emoji_obj:
        return await zed.edit("**•❐• يـرجـى إضـافـة إيـمـوجـي!**")

    chat_id = event.chat_id
    peer = await event.get_input_chat()
    is_group = event.is_group or event.is_channel

    # جلب الأيديات مسبقاً للسرعة
    target_ids = await get_target_ids(event.client, mentioned_users) if is_group else []

    if is_future_only:
        # النظام المزدوج (..جر): مراقبة الجديد فقط وتجاهل القديم
        ACTIVE_REACTIONS[chat_id] = {
            "emoji_obj": emoji_obj,
            "is_premium": is_premium,
            "target": count,
            "current": 0,
            "target_ids": target_ids,
            "is_exclude": is_exclude,
            "is_group": is_group,
            "peer": peer,
            "msg_zed": zed,
        }
        await zed.edit(
            f"**•❐• تـم تـفـعـيـل الـمـراقـبـة لـلـجـديـد ⩥ {count} رسـالـة**"
        )

    else:
        # النظام الفردي (.جر): التفاعل على القديم أولاً
        if is_group:
            done_count = await process_group_reactions(
                event,
                peer,
                emoji_obj,
                is_premium,
                count,
                is_all,
                target_ids,
                is_exclude,
            )
        else:
            done_count = await process_pm_reactions(
                event, peer, emoji_obj, is_premium, count, is_all
            )

        if done_count < count and not is_all:
            ACTIVE_REACTIONS[chat_id] = {
                "emoji_obj": emoji_obj,
                "is_premium": is_premium,
                "target": count,
                "current": done_count,
                "target_ids": target_ids,
                "is_exclude": is_exclude,
                "is_group": is_group,
                "peer": peer,
                "msg_zed": zed,
            }
            await zed.edit(
                f"**•❐• تـم الـتـفـاعـل ⩥ {done_count}**\n**• يـتـم الانـتـظـار لـلـجـديـد ...**"
            )
        else:
            await zed.edit(f"**•❐• تـم اكـتـمـال الـتـفـاعـل ⩥ {done_count} رسـالـة**")


# ==========================================
# ======== متصيد الرسائل الجديدة (Real-Time) =======
# ==========================================
@zedub.on(events.NewMessage())
async def real_time_reactions(event):
    chat_id = event.chat_id
    if chat_id not in ACTIVE_REACTIONS:
        return

    job = ACTIVE_REACTIONS[chat_id]

    # فحص شروط الجروبات في الوقت الفعلي (بسرعة البرق عبر الـ ID)
    if job["is_group"] and job["target_ids"]:
        sender = event.sender_id
        is_target = sender in job["target_ids"]

        if job["is_exclude"] and is_target:
            return  # مستبعد
        if not job["is_exclude"] and not is_target:
            return  # فقط للمذكورين

    # التفاعل الفوري
    if job["is_premium"]:
        await react_premium_raw(event.client, job["peer"], event.id, job["emoji_obj"])
    else:
        await react_normal_raw(event.client, job["peer"], event.id, job["emoji_obj"])

    job["current"] += 1

    # تحديث الكليشة (لتجنب باند التعديل المستمر)
    if job["current"] % 5 == 0 or job["current"] >= job["target"]:
        try:
            await job["msg_zed"].edit(
                f"**•❐• تـم الـتـفـاعـل ⩥ {job['current']} رسـالـة**"
            )
        except Exception:
            pass

    # إنهاء الجلسة عند بلوغ الهدف
    if job["current"] >= job["target"]:
        del ACTIVE_REACTIONS[chat_id]


# ==========================================
# ================= الإلغـاء ==================
# ==========================================
@zedub.zed_cmd(pattern=r"^([.,?!\"*'\_&$#@]{1,2})الغاء جر\s*(.*)$")
async def cancel_reactions(event):
    cmd_text = event.pattern_match.group(2)
    zed = await edit_or_reply(event, "**•❐• جـاري الـمـسـح ...**")

    if event.chat_id in ACTIVE_REACTIONS:
        del ACTIVE_REACTIONS[event.chat_id]

    _, _, count, is_all, _, _ = parse_reaction_args(cmd_text, event.message.entities)
    peer = await event.get_input_chat()
    limit = None if is_all else (count + 1)

    messages_to_clear = []
    async for msg in event.client.iter_messages(peer, limit=limit):
        if msg.id == event.id:
            continue
        messages_to_clear.append(msg.id)

    tasks = [
        remove_reaction_raw(event.client, peer, msg_id) for msg_id in messages_to_clear
    ]
    await asyncio.gather(*tasks)

    await zed.edit(f"**•❐• تـم مـسـح تـفـاعـل ⩥ {len(messages_to_clear)} رسـالـة**")
