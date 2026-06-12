import asyncio
import json
import re

from telethon import events

from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, gvarstatus
from . import zedub

plugin_category = "الادمن"

# ==========================================
# 🛠️ دوال قاعدة البيانات
# ==========================================


def get_db(key):
    data = gvarstatus(key)
    try:
        return json.loads(data) if data else {}
    except:
        return {}


def save_db(key, data_dict):
    addgvar(key, json.dumps(data_dict))


def format_reply_text(text, sender):
    if not text:
        return text
    if not sender:
        return text

    first_name = sender.first_name or "عزيزي"
    user_id = sender.id
    username = (
        f"@{sender.username}"
        if sender.username
        else f"[{first_name}](tg://user?id={user_id})"
    )
    mention = f"[{first_name}](tg://user?id={user_id})"

    text = text.replace("#الاسم", first_name)
    text = text.replace("#يوزره", mention)
    text = text.replace("#اليوزر", username)
    text = text.replace("#الايدي", str(user_id))
    return text


# ==========================================
# ⚙️ أوامر التفعيل والتعطيل للعامة
# ==========================================


@zedub.zed_cmd(pattern=r"^[.,*]تفعيل اضافه رد$")
async def enable_public_reply(event):
    chat_id = str(event.chat_id)
    save_db(f"ZED_PUB_REP_{chat_id}", {"status": True})
    await edit_or_reply(
        event,
        "**•❐• تـم تـفـعـيـل إضـافـة الـردود للأعـضـاء فـي هـذه الـدردشـة بـنـجـاح ✓**",
    )


@zedub.zed_cmd(pattern=r"^[.,*]تعطيل اضافه رد$")
async def disable_public_reply(event):
    chat_id = str(event.chat_id)
    save_db(f"ZED_PUB_REP_{chat_id}", {"status": False})
    await edit_or_reply(
        event,
        "**•❐• تـم تـعـطـيـل إضـافـة الـردود للأعـضـاء فـي هـذه الـدردشـة بـنـجـاح ✓**",
    )


# ==========================================
# ➕ أمر إضافة الرد (سؤال ↤ جواب ↤ تنفيذ)
# ==========================================


@zedub.zed_cmd(pattern=r"^[.,*]اضف رد(?:\s+(عام|خاص))?$")
async def add_reply_cmd(event):
    is_owner = event.sender_id == zedub.uid
    scope_match = event.pattern_match.group(1)
    chat_id = str(event.chat_id)

    if scope_match and not is_owner:
        return

    scope = "local"
    db_key = f"ZED_REP_CHAT_{chat_id}"

    if is_owner:
        if scope_match == "عام":
            scope = "global"
            db_key = "ZED_REP_GLOBAL"
        elif scope_match == "خاص":
            scope = "private"
            db_key = "ZED_REP_PVT"
    else:
        pub_status = get_db(f"ZED_PUB_REP_{chat_id}").get("status", False)
        if not pub_status:
            return

    async with event.client.conversation(event.chat_id) as conv:
        try:
            # 1. يطلب الكلمة
            await conv.send_message(
                "**↢ أرسـل الكـلـمـة المـفـتـاحـيـة (الـتـي سـيـرد عـلـيـهـا الـبـوت) الان :\n\n•❐• لـ الالغـاء ارسـل `الغاء`**"
            )

            trigger_msg = None
            while True:
                trigger_msg = await conv.get_response(timeout=60)
                if trigger_msg.sender_id == event.sender_id:
                    break

            trigger_word = trigger_msg.text.strip() if trigger_msg.text else ""

            if trigger_word == "الغاء":
                return await conv.send_message("**•❐• تـم الغـاء الأمـر بـنـجـاح ✓**")
            if not trigger_word:
                return await conv.send_message(
                    "**•❐• عـذراً يـجـب أن تـكـون الـكـلـمـة نـصـاً .. تـم الالغـاء ✕**"
                )

            # 2. يطلب الرد
            info_text = (
                "**↢ حـسـنـاً، أرسـل الان الـرد الـذي تـريـده (نـص, صـوره, فـيـديـو, مـتـحـركـه, بـصـمـه, الخ..).**\n\n"
                "**• مـلاحـظـة هـامـة :**\n"
                "يـمـكـنـك اسـتـخـدام هـذه الإضـافـات فـي الـنـص:\n"
                "▹ `#الاسم` -  اسـم الـعـضـو\n"
                "▹ `#يوزره` -  يـوزر الـرد مـع مـنـشـن\n"
                "▹ `#اليوزر` -  يـوزر مـرسـل الـرسـالـة\n"
                "▹ `#الايدي` -  ايـدي المـسـتـخـدم"
            )
            await conv.send_message(info_text)

            reply_msg = None
            while True:
                reply_msg = await conv.get_response(timeout=60)
                if reply_msg.sender_id == event.sender_id:
                    break

            # 3. يحفظ وينفذ
            reply_data = {
                "text": reply_msg.text or "",
                "has_media": False,
                "msg_id": None,
            }

            if reply_msg.media:
                saved_msg = await event.client.forward_messages("me", reply_msg)
                reply_data["has_media"] = True
                reply_data["msg_id"] = saved_msg.id

            db = get_db(db_key)
            db[trigger_word] = reply_data
            save_db(db_key, db)

            scope_text = (
                "فـي هـذه الـدردشـة"
                if scope == "local"
                else ("فـي كـل الـكـروبـات" if scope == "global" else "فـي كـل الـخـاص")
            )
            await conv.send_message(
                f"**•❐• تـم حـفـظ الـرد `{trigger_word}` بـنـجـاح {scope_text} ✓**"
            )

        except asyncio.TimeoutError:
            await conv.send_message(
                "**•❐• عـذراً .. تـم الغـاء الأمـر بـسـبـب نـفـاذ الـوقـت ✕**"
            )


# ==========================================
# ➕ أمر إضافة ترحيب
# ==========================================


@zedub.zed_cmd(pattern=r"^[.,*]اضف ترحيب(?:\s+(عام|خاص))?(?:\s+(.*))?$")
async def add_greeting_cmd(event):
    scope_match = event.pattern_match.group(1)
    custom_text = event.pattern_match.group(2)
    chat_id = str(event.chat_id)

    scope = "local"
    db_key = f"ZED_GRT_CHAT_{chat_id}"

    if scope_match == "عام":
        scope = "global"
        db_key = "ZED_GRT_GLOBAL"
    elif scope_match == "خاص":
        scope = "private"
        db_key = "ZED_GRT_PVT"

    async with event.client.conversation(event.chat_id) as conv:
        try:
            await conv.send_message(
                "**↢ أرسـل الكـلـمـة او الاسـم (الـذي سـيـفـعـل الـتـرحـيـب) الان :\n\n•❐• لـ الالغـاء ارسـل `الغاء`**"
            )

            trigger_msg = None
            while True:
                trigger_msg = await conv.get_response(timeout=60)
                if trigger_msg.sender_id == event.sender_id:
                    break

            trigger_word = trigger_msg.text.strip() if trigger_msg.text else ""

            if trigger_word == "الغاء":
                return await conv.send_message("**•❐• تـم الغـاء الأمـر بـنـجـاح ✓**")
            if not trigger_word:
                return await conv.send_message(
                    "**•❐• عـذراً يـجـب أن تـكـون الـكـلـمـة نـصـاً .. تـم الالغـاء ✕**"
                )

            reply_text = custom_text if custom_text else "anim_zed"

            db = get_db(db_key)
            db[trigger_word] = {"text": reply_text}
            save_db(db_key, db)

            scope_text = (
                "فـي هـذه الـدردشـة"
                if scope == "local"
                else ("فـي كـل الـكـروبـات" if scope == "global" else "فـي كـل الـخـاص")
            )
            await conv.send_message(
                f"**•❐• تـم حـفـظ تـرحـيـب `{trigger_word}` بـنـجـاح {scope_text} ✓**"
            )

        except asyncio.TimeoutError:
            await conv.send_message(
                "**•❐• عـذراً .. تـم الغـاء الأمـر بـسـبـب نـفـاذ الـوقـت ✕**"
            )


# ==========================================
# 🗑️ أوامر الحذف
# ==========================================


@zedub.zed_cmd(pattern=r"^[.,*]حذف (رد|ترحيب)(?:\s+(عام|خاص))?(?:\s+(.*))?$")
async def delete_trigger_cmd(event):
    cmd_type = event.pattern_match.group(1)
    scope_match = event.pattern_match.group(2)
    trigger_word = event.pattern_match.group(3)
    chat_id = str(event.chat_id)

    if cmd_type == "رد":
        if scope_match == "عام":
            db_key = "ZED_REP_GLOBAL"
        elif scope_match == "خاص":
            db_key = "ZED_REP_PVT"
        else:
            db_key = f"ZED_REP_CHAT_{chat_id}"
    else:
        if scope_match == "عام":
            db_key = "ZED_GRT_GLOBAL"
        elif scope_match == "خاص":
            db_key = "ZED_GRT_PVT"
        else:
            db_key = f"ZED_GRT_CHAT_{chat_id}"

    if not trigger_word:
        async with event.client.conversation(event.chat_id) as conv:
            try:
                await conv.send_message(
                    f"**↢ أرسـل {cmd_type} الـذي تـريـد حـذفـه الان :**"
                )

                res = None
                while True:
                    res = await conv.get_response(timeout=60)
                    if res.sender_id == event.sender_id:
                        break

                trigger_word = res.text.strip() if res.text else ""
            except asyncio.TimeoutError:
                return await conv.send_message(
                    "**•❐• عـذراً .. تـم الغـاء الأمـر بـسـبـب نـفـاذ الـوقـت ✕**"
                )

    db = get_db(db_key)
    if trigger_word in db:
        del db[trigger_word]
        save_db(db_key, db)
        await edit_or_reply(
            event, f"**•❐• تـم حـذف الـ{cmd_type} `{trigger_word}` بـنـجـاح ✓**"
        )
    else:
        await edit_or_reply(
            event, f"**•❐• عـذراً الـ{cmd_type} `{trigger_word}` غـيـر مـوجـود !**"
        )


# ==========================================
# 📋 أوامر العرض
# ==========================================


@zedub.zed_cmd(pattern=r"^[.,*]عرض (الردود|الترحيب)(?:\s+(عام|خاص))?$")
async def list_triggers_cmd(event):
    cmd_type = event.pattern_match.group(1)
    scope_match = event.pattern_match.group(2)
    chat_id = str(event.chat_id)

    if cmd_type == "الردود":
        if scope_match == "عام":
            db_key, title = "ZED_REP_GLOBAL", "الـردود الـعـامـة"
        elif scope_match == "خاص":
            db_key, title = "ZED_REP_PVT", "ردود الـخـاص"
        else:
            db_key, title = f"ZED_REP_CHAT_{chat_id}", "ردود هـذه الـدردشـة"
        cmd_del = "رد"
    else:
        if scope_match == "عام":
            db_key, title = "ZED_GRT_GLOBAL", "تـرحـيـبـات الـعـام"
        elif scope_match == "خاص":
            db_key, title = "ZED_GRT_PVT", "تـرحـيـبـات الـخـاص"
        else:
            db_key, title = f"ZED_GRT_CHAT_{chat_id}", "تـرحـيـبـات هـذه الـدردشـة"
        cmd_del = "ترحيب"

    db = get_db(db_key)
    if not db:
        return await edit_or_reply(
            event, f"**•❐• لا تـوجـد {title} مـحـفـوظـة حـالـيـاً !**"
        )

    scope_prefix = f" {scope_match}" if scope_match else ""
    msg = f"**•❐• قـائـمـة {title} :**\n\n"
    for key in db.keys():
        msg += f"▹ {key}  ↢  انسخ للحذف: `.حذف {cmd_del}{scope_prefix} {key}`\n"

    await edit_or_reply(event, msg)


# ==========================================
# 🧠 المحرك الذكي للردود والترحيب (المستمع)
# ==========================================

BOT_SENT_MSG_IDS = set()


@zedub.on(events.NewMessage())
async def auto_reply_engine(event):
    if hasattr(event, "id") and event.id in BOT_SENT_MSG_IDS:
        return

    if not event.text:
        return

    chat_id = str(event.chat_id)
    text = event.text
    sender = await event.get_sender()

    if not sender:
        return

    dbs_to_check = [
        get_db(f"ZED_GRT_CHAT_{chat_id}"),
        get_db("ZED_GRT_GLOBAL") if event.is_group else {},
        get_db("ZED_GRT_PVT") if event.is_private else {},
        get_db(f"ZED_REP_CHAT_{chat_id}"),
        get_db("ZED_REP_GLOBAL") if event.is_group else {},
        get_db("ZED_REP_PVT") if event.is_private else {},
    ]

    if len(BOT_SENT_MSG_IDS) > 1000:
        BOT_SENT_MSG_IDS.clear()

    for index, db in enumerate(dbs_to_check):
        if not db:
            continue

        for trigger_word, data in db.items():
            trigger_regex = r"(?:\s|^)" + re.escape(trigger_word) + r"(?:\s|$)"

            if re.search(trigger_regex, text, re.IGNORECASE):
                # إذا كان ترحيب (نظام الأنيميشن الزخرفي الصامت بدون كلام)
                if index <= 2:
                    if data["text"] == "anim_zed":
                        sent_msg = await event.reply("**⎔ • ┈┈┈┈┈┈┈┈┈┈┈┈ • ⎔**")
                        BOT_SENT_MSG_IDS.add(sent_msg.id)
                        await asyncio.sleep(1)
                        await sent_msg.edit("**⎔ ✦ ┈┈┈┈┈┈┈┈┈┈┈┈ ✦ ⎔**")
                        await asyncio.sleep(1)
                        await sent_msg.edit("**⎔ ━─ ✦ ┈┈┈┈┈┈ ✦ ─━ ⎔**")
                        await asyncio.sleep(1)
                        await sent_msg.edit("**⎔ ━─━─ ✦ ┈┈ ✦ ─━─━ ⎔**")
                        await asyncio.sleep(1)
                        await sent_msg.edit("**⎔ ━─━─━─ ✦ ─━─━─━ ⎔**")
                        await asyncio.sleep(1)
                        # الشكل النهائي הפخم يتضمن اليوزر في المنتصف
                        final_text = "**⋄━─━─━─━─ ✦ ─━─━─━─━⋄**\n\n             #يوزره\n\n**⋄━─━─━─━─ ✦ ─━─━─━─━⋄**"
                        await sent_msg.edit(format_reply_text(final_text, sender))
                    else:
                        sent_msg = await event.reply(
                            format_reply_text(data["text"], sender)
                        )
                        BOT_SENT_MSG_IDS.add(sent_msg.id)
                    return

                # إذا كان رد عادي
                else:
                    final_reply_text = format_reply_text(data.get("text", ""), sender)
                    if data.get("has_media") and data.get("msg_id"):
                        try:
                            saved_media_msg = await event.client.get_messages(
                                "me", ids=data["msg_id"]
                            )
                            sent_msg = await event.reply(
                                message=final_reply_text, file=saved_media_msg.media
                            )
                            BOT_SENT_MSG_IDS.add(sent_msg.id)
                        except:
                            if final_reply_text:
                                sent_msg = await event.reply(final_reply_text)
                                BOT_SENT_MSG_IDS.add(sent_msg.id)
                    else:
                        sent_msg = await event.reply(final_reply_text)
                        BOT_SENT_MSG_IDS.add(sent_msg.id)
                    return
