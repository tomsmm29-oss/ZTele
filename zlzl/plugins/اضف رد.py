import asyncio
import json
import re

from telethon import events

from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, gvarstatus
from . import zedub

plugin_category = "الادمن"

# ==========================================
# ⚙️ تتبع الرسائل النشطة والمحادثات لمنع التعارض والتكرار
# ==========================================
ACTIVE_CONVS = {}
BOT_SENT_MSG_IDS = set()

# ==========================================
# 🛠️ دوال قاعدة البيانات المساعدة
# ==========================================


def get_db(key):
    data = gvarstatus(key)
    try:
        return json.loads(data) if data else {}
    except Exception:
        return {}


def save_db(key, data_dict):
    addgvar(key, json.dumps(data_dict))


def format_reply_text(text, sender):
    if not text or not sender:
        return text

    first_name = getattr(sender, "first_name", "") or "عزيزي"
    user_id = getattr(sender, "id", 0)
    username = (
        f"@{sender.username}"
        if getattr(sender, "username", None)
        else f"[{first_name}](tg://user?id={user_id})"
    )
    mention = f"[{first_name}](tg://user?id={user_id})"

    text = text.replace("#الاسم", first_name)
    text = text.replace("#يوزره", mention)
    text = text.replace("#اليوزر", username)
    text = text.replace("#الايدي", str(user_id))
    return text


# دالة مخصصة لتعويض يوزر المطور (صاحب الحساب) في رد اللقب
def format_owner_reply_text(text, owner):
    if not text or not owner:
        return text

    first_name = getattr(owner, "first_name", "") or "المطور"
    user_id = getattr(owner, "id", 0)
    username = (
        f"@{owner.username}"
        if getattr(owner, "username", None)
        else f"[{first_name}](tg://user?id={user_id})"
    )
    mention = f"[{first_name}](tg://user?id={user_id})"

    text = text.replace("#يوزري", username)
    text = text.replace("#اسمي", first_name)
    text = text.replace("#ايديي", str(user_id))
    return text


# دالة سريعة لالتقاط رد المستخدم المباشر وتخطي مشاكل التعليق
async def wait_for_next_message(client, chat_id, user_id, future, timeout=60):
    @client.on(events.NewMessage(chats=chat_id, from_users=user_id))
    async def handler(event):
        if not future.done():
            future.set_result(event.message)

    try:
        return await asyncio.wait_for(future, timeout=timeout)
    finally:
        client.remove_event_handler(handler)


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
# ➕ أمر إضافة الرد
# ==========================================


@zedub.zed_cmd(pattern=r"^[.,*]اضف رد(?:\s+(عام|خاص))?$")
async def add_reply_cmd(event):
    is_owner = event.sender_id == zedub.uid
    scope_match = event.pattern_match.group(1)
    chat_id = event.chat_id
    user_id = event.sender_id

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

    # إلغاء أي عملية سابقة معلقة لهذا المستخدم في هذه الدردشة لمنع التداخل
    conv_key = (chat_id, user_id)
    if conv_key in ACTIVE_CONVS:
        prev_future = ACTIVE_CONVS[conv_key]
        if not prev_future.done():
            prev_future.cancel()
        del ACTIVE_CONVS[conv_key]

    loop = asyncio.get_event_loop()
    current_future = loop.create_future()
    ACTIVE_CONVS[conv_key] = current_future

    try:
        # 1. طلب الكلمة المفتاحية
        await event.respond(
            "**↢ أرسـل الكـلـمـة المـفـتـاحـيـة (الـتـي سـيـرد عـلـيـهـا الـبـوت) الان :\n\n•❐• لـ الالغـاء ارسـل `الغاء`**"
        )

        trigger_msg = await wait_for_next_message(
            event.client, chat_id, user_id, current_future, timeout=60
        )
        trigger_word = trigger_msg.text.strip() if trigger_msg.text else ""

        if trigger_word in ["الغاء", ".الغاء"]:
            await event.respond("**•❐• تـم الغـاء الأمـر بـنـجـاح ✓**")
            return
        if not trigger_word:
            await event.respond(
                "**•❐• عـذراً يـجـب أن تـكـون الـكـلـمـة نـصـاً .. تـم الالغـاء ✕**"
            )
            return

        # تهيئة المستقبل للخطوة الثانية
        current_future = loop.create_future()
        ACTIVE_CONVS[conv_key] = current_future

        # 2. طلب الرد
        info_text = (
            "**↢ حـسـنـاً، أرسـل الان الـرد الـذي تـريـده (نـص, صـوره, فـيـديـو, مـتـحـركـه, بـصـمـه, الخ..).**\n\n"
            "**• مـلاحـظـة هـامـة :**\n"
            "يـمـكـنـك اسـتـخـدام هـذه الإضـافـات فـي الـنـص:\n"
            "▹ `#الاسم` -  اسـم الـعـضـو\n"
            "▹ `#يوزره` -  يـوزر الـرد مـع مـنـشـن\n"
            "▹ `#اليوزر` -  يـوزر مـرسـل الـرسـالـة\n"
            "▹ `#الايدي` -  ايـدي المـسـتـخـدم"
        )
        await event.respond(info_text)

        reply_msg = await wait_for_next_message(
            event.client, chat_id, user_id, current_future, timeout=60
        )

        # 3. حفظ البيانات والوسائط
        reply_data = {"text": reply_msg.text or "", "has_media": False, "msg_id": None}

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
        await event.respond(
            f"**•❐• تـم حـفـظ الـرد `{trigger_word}` بـنـجـاح {scope_text} ✓**"
        )

    except asyncio.TimeoutError:
        await event.respond(
            "**•❐• عـذراً .. تـم الغـاء الأمـر بـسـبـب نـفـاذ الـوقـت ✕**"
        )
    except asyncio.CancelledError:
        pass
    finally:
        if conv_key in ACTIVE_CONVS and ACTIVE_CONVS[conv_key] == current_future:
            del ACTIVE_CONVS[conv_key]


# ==========================================
# 👑 أمر ترحيب اللقب الخاص بك (المطور)
# ==========================================


@zedub.zed_cmd(pattern=r"^[.,*]اضف ترحيب(?:\s+(عام|خاص))?(?:\s+(.*))?$")
async def add_greeting_cmd(event):
    is_owner = event.sender_id == zedub.uid
    scope_match = event.pattern_match.group(1)
    custom_text = event.pattern_match.group(2)
    chat_id = event.chat_id
    user_id = event.sender_id

    if scope_match and not is_owner:
        return

    scope = "local"
    db_key = f"ZED_GRT_CHAT_{chat_id}"

    if is_owner:
        if scope_match == "عام":
            scope = "global"
            db_key = "ZED_GRT_GLOBAL"
        elif scope_match == "خاص":
            scope = "private"
            db_key = "ZED_GRT_PVT"
    else:
        pub_status = get_db(f"ZED_PUB_REP_{chat_id}").get("status", False)
        if not pub_status:
            return

    # إلغاء أي عملية سابقة معلقة لمنع التداخل
    conv_key = (chat_id, user_id)
    if conv_key in ACTIVE_CONVS:
        prev_future = ACTIVE_CONVS[conv_key]
        if not prev_future.done():
            prev_future.cancel()
        del ACTIVE_CONVS[conv_key]

    loop = asyncio.get_event_loop()
    current_future = loop.create_future()
    ACTIVE_CONVS[conv_key] = current_future

    # الحالة الأولى: إذا تم تحديد نص مخصص بعد الأمر (مثل: .اضف ترحيب هلا يا روحي)
    if custom_text:
        existing_data = get_db(db_key)
        nickname = existing_data.get("nickname") if existing_data else None

        if not nickname:
            await event.respond(
                "**↢ لـم تـقـم بـتـعـيـين لـقـبـك بـعـد، أرسـل لـقـبـك الآن لـربـط الـرد الـمـخـصـص بـه:**"
            )
            try:
                trigger_msg = await wait_for_next_message(
                    event.client, chat_id, user_id, current_future, timeout=60
                )
                nickname = trigger_msg.text.strip() if trigger_msg.text else ""
            except asyncio.TimeoutError:
                await event.respond(
                    "**•❐• عـذراً .. تـم الغـاء الأمـر بـسـبـب نـفـاذ الـوقـت ✕**"
                )
                return

            if nickname in ["الغاء", ".الغاء"] or not nickname:
                await event.respond("**•❐• تـم الغـاء الأمـر بـنـجـاح ✓**")
                return

        # حفظ الرد المخصص دون الزخرفة الكبيرة مع يوزرك أنت فقط
        greeting_text = f"{custom_text} #يوزري"
        save_db(
            db_key,
            {
                "nickname": nickname,
                "text": greeting_text,
                "has_media": False,
                "msg_id": None,
            },
        )

        scope_text = (
            "في هذه الدردشة"
            if scope == "local"
            else ("في كل الكروبات" if scope == "global" else "في كل الخاص")
        )
        await event.respond(
            f"**•❐• تم حفظ رد اللقب المخصص للـلقب `{nickname}` بنجاح {scope_text} ✓**\n**الرد الجديد:** {custom_text}"
        )
        return

    # الحالة الثانية: تفاعلي بالكامل مع رد الزخرفة الزمني الصامت (anim_zed)
    try:
        await event.respond(
            "**↢ أرسـل لـقـبـك الآن (الكلمة المفتاحية التي سيكتبها الأعضاء ليرد البوت بالزخرفة المتحركة ويوزرك) :\n\n•❐• لـ الالغـاء ارسـل `الغاء`**"
        )

        trigger_msg = await wait_for_next_message(
            event.client, chat_id, user_id, current_future, timeout=60
        )
        nickname = trigger_msg.text.strip() if trigger_msg.text else ""

        if nickname in ["الغاء", ".الغاء"]:
            await event.respond("**•❐• تـم الغـاء الأمـر بـنـجـاح ✓**")
            return
        if not nickname:
            await event.respond(
                "**•❐• عـذراً يـجـب أن تـكـون الـكـلـمـة نـصـاً .. تـم الالغـاء ✕**"
            )
            return

        # حفظ الإشارة المرجعية anim_zed لتدل على الترحيب الزخرفي الصامت
        save_db(
            db_key,
            {
                "nickname": nickname,
                "text": "anim_zed",
                "has_media": False,
                "msg_id": None,
            },
        )

        scope_text = (
            "فـي هـذه الدردشة"
            if scope == "local"
            else ("فـي كـل الـكـروبـات" if scope == "global" else "فـي كـل الـخـاص")
        )
        await event.respond(
            f"**•❐• تـم حـفـظ رد الـلـقـب `{nickname}` مـع الـزخـرفـة الـمـتـحـركـة بـنـجـاح {scope_text} ✓**"
        )

    except asyncio.TimeoutError:
        await event.respond(
            "**•❐• عـذراً .. تـم الغـاء الأمـر بـسـبـب نـفـاذ الـوقـت ✕**"
        )
    except asyncio.CancelledError:
        pass
    finally:
        if conv_key in ACTIVE_CONVS and ACTIVE_CONVS[conv_key] == current_future:
            del ACTIVE_CONVS[conv_key]


# ==========================================
# ⚡ مشغل الردود التلقائية ورعاية اللقب (لك وللغير)
# ==========================================


@zedub.on(events.NewMessage)
async def reply_trigger_handler(event):
    # تفادي الرد التلقائي المتكرر على الرسائل المرسلة من الرسوم البرمجية للبوت نفسه
    if event.id in BOT_SENT_MSG_IDS:
        return

    text = event.text.strip() if event.text else ""
    if not text or text.startswith((".", "*", "!", "?")):
        return

    sender = await event.get_sender()
    if not sender:
        return

    chat_id = str(event.chat_id)
    owner_entity = await event.client.get_me()

    # تجميع قواعد البيانات بحسب الدردشة
    databases_to_check = []

    if event.is_private:
        databases_to_check.append((get_db("ZED_GRT_PVT"), "grt"))
        databases_to_check.append((get_db("ZED_REP_PVT"), "rep"))
    else:
        databases_to_check.append((get_db(f"ZED_GRT_CHAT_{chat_id}"), "grt"))
        databases_to_check.append((get_db("ZED_GRT_GLOBAL"), "grt"))
        databases_to_check.append((get_db(f"ZED_REP_CHAT_{chat_id}"), "rep"))
        databases_to_check.append((get_db("ZED_REP_GLOBAL"), "rep"))

    # البحث الدقيق عن التطابقات باستخدام Regex
    for db, db_type in databases_to_check:
        if not db:
            continue

        for trigger_word, data in db.items():
            actual_trigger = data.get("nickname") if db_type == "grt" else trigger_word
            if not actual_trigger:
                continue

            trigger_regex = r"(?:\s|^)" + re.escape(actual_trigger) + r"(?:\s|$)"

            if re.search(trigger_regex, text, re.IGNORECASE):
                # 1. إذا كان ترحيب لقب (نظام الأنيميشن الزخرفي الصامت بدون كلام)
                if db_type == "grt":
                    if data.get("text") == "anim_zed":
                        # المرحلة الأولى الزخرفية الصامتة
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

                        # الوقفة والشكل النهائي الفخم يوضح يوزرك أنت (المطور المالك) بالمنتصف
                        final_text = "**⋄━─━─━─━─ ✦ ─━─━─━─━⋄**\n\n             #يوزري\n\n**⋄━─━─━─━─ ✦ ─━─━─━─━⋄**"
                        await sent_msg.edit(
                            format_owner_reply_text(final_text, owner_entity)
                        )
                    else:
                        reply_text = format_owner_reply_text(
                            data.get("text", ""), owner_entity
                        )
                        sent_msg = await event.reply(reply_text)
                        BOT_SENT_MSG_IDS.add(sent_msg.id)
                    return

                # 2. إذا كان رد مخصص عادي
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
                        except Exception:
                            if final_reply_text:
                                sent_msg = await event.reply(final_reply_text)
                                BOT_SENT_MSG_IDS.add(sent_msg.id)
                    else:
                        sent_msg = await event.reply(final_reply_text)
                        BOT_SENT_MSG_IDS.add(sent_msg.id)
                    return

    # تنظيف ذاكرة المعرفات دورياً لمنع التضخم واستهلاك الذاكرة
    if len(BOT_SENT_MSG_IDS) > 400:
        BOT_SENT_MSG_IDS.clear()
