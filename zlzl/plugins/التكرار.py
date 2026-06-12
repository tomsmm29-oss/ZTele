import asyncio

from telethon.errors.rpcerrorlist import ForbiddenError
from telethon.tl import functions, types
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.utils import get_display_name

from ..core.managers import edit_delete, edit_or_reply
from ..helpers import media_type
from ..helpers.utils import _zedutils
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG, BOTLOG_CHATID, zedub

plugin_category = "الخدمات"
SPAM = gvarstatus("Z_MOKRR") or "(مؤقت|مكرر)"
UNSPAM = gvarstatus("Z_UNMOKRR") or "(ايقاف مؤقت|ايقاف مكرر)"

ZelzalSP_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗭𝗧𝗵𝗼𝗻 - اوامـر السبـام والتكـرار](t.me/ZThon) 𓆪\n\n"
    "`.كرر` + عـدد + كلمـه\n"
    "**⪼ لـ تكـرار كلمـه معينـه لعـدد معيـن من المـرات**\n\n"
    "`.مكرر` + الوقت بالثواني + العدد + النص\n"
    "**⪼ لـ تكـرار نص لوقت معين وعدد معين من المـرات**\n"
    "**⪼ الامر يفيد جماعة الاعلانات وكروبات الشراء**\n\n"
    "`.تكرار ملصق`\n"
    "**⪼ لـ تكـرار ملصقـات من حزمـه معينـه**\n\n"
    "`.سبام` + كلمـه\n"
    "**⪼ لـ تكـرار كلمـة او جملـة نصيـه**\n\n"
    "`.وسبام` + كلمـه\n"
    "**⪼ لـ تكـرار حـروف كلمـة على حرف حرف**\n\n"
    "`.تعبير مكرر`\n"
    "**⪼ لـ تكـرار تفاعـلات رياكشـن** 👍👎❤🔥🥰👏😁🤔🤯😱🤬😢🎉🤩🤮💩\n\n"
    "`.ايقاف التكرار`\n"
    "**⪼ لـ إيقـاف أي تكـرار جـاري تنفيـذه**\n\n"
)


async def spam_mokrr(event, sandy, zed, sleeptimem, sleeptimet, DelaySpam=False):
    # sourcery no-metrics
    counter = int(zed[0])
    if len(zed) == 2:
        spam_message = str(zed[1])
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            if event.reply_to_msg_id:
                await sandy.reply(spam_message)
            else:
                await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    elif event.reply_to_msg_id and sandy.media:
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            sandy = await event.client.send_file(
                event.chat_id, sandy, caption=sandy.text
            )
            await _zedutils.unsavegif(event, sandy)
            await asyncio.sleep(sleeptimem)
        if BOTLOG:
            if DelaySpam is not True:
                if event.is_private:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "**- التڪـرار ♽**\n"
                        + f"**- تم تنفيـذ التڪـرار بنجاح في ** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع** {counter} **عدد المرات مع الرسالة أدناه**",
                    )
                else:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "**- التڪـرار ♽**\n"
                        + f"**- تم تنفيـذ التڪـرار بنجاح في ** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **مع** {counter} **عدد المرات مع الرسالة أدناه**",
                    )
            elif event.is_private:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "**- التڪـرار الوقتـي ♽**\n"
                    + f"**- تم تنفيـذ التڪـرار الوقتي  بنجاح في ** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع** {counter} **عدد المرات مع الرسالة أدناه مع التأخير** {sleeptimet} ** الثواني **",
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "**- التڪـرار الوقتـي ♽**\n"
                    + f"**- تم تنفيـذ التڪـرار الوقتي  بنجاح في ** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **مع** {counter} **عدد المرات مع الرسالة أدناه مع التأخير** {sleeptimet} ** الثواني **",
                )

            sandy = await event.client.send_file(BOTLOG_CHATID, sandy)
            await _zedutils.unsavegif(event, sandy)
        return
    elif event.reply_to_msg_id and sandy.text:
        spam_message = sandy.text
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    else:
        return
    if DelaySpam is not True:
        if BOTLOG:
            if event.is_private:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "**- التڪـرار ♽**\n"
                    + f"**- تم تنفيـذ التڪـرار بنجاح في ** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع** {counter} **رسائل ال   :** \n"
                    + f"- `{spam_message}`",
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "**- التڪـرار ♽**\n"
                    + f"**- تم تنفيـذ التڪـرار بنجاح في ** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشة مع** {counter} **رسائل الـ   :** \n"
                    + f"- `{spam_message}`",
                )
    elif BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- التڪـرار الوقتـي ♽**\n"
                + f"**- تم تنفيـذ التڪـرار الوقتي  بنجاح في ** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع** {sleeptimet} seconds and with {counter} **رسائل الـ   :** \n"
                + f"- `{spam_message}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- التڪـرار الوقتـي ♽**\n"
                + f"**- تم تنفيـذ التڪـرار الوقتي  بنجاح في ** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشة مع** {sleeptimet} **الثواني و مع** {counter} **رسائل الـ  ️ :** \n"
                + f"- `{spam_message}`",
            )


@zedub.zed_cmd(pattern=f"{SPAM} ([\s\S]*)")
async def spammer(event):
    # return await edit_or_reply(event, "**- امـر (.مكرر) متوقف للصيانه ...🚧**\n\n**- استخدم اوامر السوبر المحدثه (متخطية الحظر) ☑️**\n**- ارسـل (.مساعده) ثم زر اوامـر السوبرات 🎡**")
    reply = await event.get_reply_message()
    input_str = "".join(event.text.split(maxsplit=1)[1:]).split(" ", 2)
    try:
        sleeptimet = sleeptimem = int(input_str[0])
    except Exception:
        return await edit_delete(
            event,
            "**- ارسـل الامـر بالشكـل الآتي**\n\n`.مؤقت` **+ عدد الثواني + عدد المرات + الرسالة**\n**- مثـال : .مؤقت 12 12 السلام عليكم**",
        )
    zed = input_str[1:]
    await event.delete()
    addgvar("spamwork", True)
    await spam_mokrr(event, reply, zed, sleeptimem, sleeptimet, DelaySpam=True)


@zedub.zed_cmd(pattern=f"{UNSPAM} ?(.*)")
async def spammer(event):
    reply = await event.get_reply_message()
    await event.delete()
    delgvar("spamwork")
    await spam_mokrr(event, reply, sleeptimem, sleeptimet, DelaySpam=False)


async def spam_function(event, sandy, zed, sleeptimem, sleeptimet, DelaySpam=False):
    # sourcery no-metrics
    counter = int(zed[0])
    if len(zed) == 2:
        spam_message = str(zed[1])
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            if event.reply_to_msg_id:
                await sandy.reply(spam_message)
            else:
                await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    elif event.reply_to_msg_id and sandy.media:
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            sandy = await event.client.send_file(
                event.chat_id, sandy, caption=sandy.text
            )
            await _zedutils.unsavegif(event, sandy)
            await asyncio.sleep(sleeptimem)
        if BOTLOG:
            if DelaySpam is not True:
                if event.is_private:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "**- التڪـرار ♽**\n"
                        + f"**- تم تنفيـذ التڪـرار بنجاح في ** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع** {counter} **عدد المرات مع الرسالة أدناه**",
                    )
                else:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "**- التڪـرار ♽**\n"
                        + f"**- تم تنفيـذ التڪـرار بنجاح في ** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **مع** {counter} **عدد المرات مع الرسالة أدناه**",
                    )
            elif event.is_private:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "**- التڪـرار الوقتـي ♽**\n"
                    + f"**- تم تنفيـذ التڪـرار الوقتي  بنجاح في ** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع** {counter} **عدد المرات مع الرسالة أدناه مع التأخير** {sleeptimet} ** الثواني **",
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "**- التڪـرار الوقتـي ♽**\n"
                    + f"**- تم تنفيـذ التڪـرار الوقتي  بنجاح في ** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **مع** {counter} **عدد المرات مع الرسالة أدناه مع التأخير** {sleeptimet} ** الثواني **",
                )

            sandy = await event.client.send_file(BOTLOG_CHATID, sandy)
            await _zedutils.unsavegif(event, sandy)
        return
    elif event.reply_to_msg_id and sandy.text:
        spam_message = sandy.text
        for _ in range(counter):
            if gvarstatus("spamwork") is None:
                return
            await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(sleeptimet)
    else:
        return
    if DelaySpam is not True:
        if BOTLOG:
            if event.is_private:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "**- التڪـرار ♽**\n"
                    + f"**- تم تنفيـذ التڪـرار بنجاح في ** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع** {counter} **رسائل ال   :** \n"
                    + f"- `{spam_message}`",
                )
            else:
                await event.client.send_message(
                    BOTLOG_CHATID,
                    "**- التڪـرار ♽**\n"
                    + f"**- تم تنفيـذ التڪـرار بنجاح في ** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشة مع** {counter} **رسائل الـ   :** \n"
                    + f"- `{spam_message}`",
                )
    elif BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- التڪـرار الوقتـي ♽**\n"
                + f"**- تم تنفيـذ التڪـرار الوقتي  بنجاح في ** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع** {sleeptimet} seconds and with {counter} **رسائل الـ   :** \n"
                + f"- `{spam_message}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- التڪـرار الوقتـي ♽**\n"
                + f"**- تم تنفيـذ التڪـرار الوقتي  بنجاح في ** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشة مع** {sleeptimet} **الثواني و مع** {counter} **رسائل الـ  ️ :** \n"
                + f"- `{spam_message}`",
            )


@zedub.zed_cmd(
    pattern="كرر ([\s\S]*)",
    command=("كرر", plugin_category),
    info={
        "header": "لـ تكـرار كلمـه معينـه لعـدد معيـن من المـرات",
        "ملاحظـه": "لـ ايقـاف التكـرار استخـدم الامـر  {tr}ايقاف التكرار",
        "الاستخـدام": ["{tr}كرر + العدد + الكلمـه", "{tr}كرر + العدد بالـرد ع رسـاله"],
        "مثــال": "{tr}كرر 10 هلو",
    },
)
async def spammer(event):
    "لـ تكـرار كلمـه معينـه لعـدد معيـن من المـرات"
    sandy = await event.get_reply_message()
    zed = ("".join(event.text.split(maxsplit=1)[1:])).split(" ", 1)
    try:
        counter = int(zed[0])
    except Exception:
        return await edit_delete(
            event,
            "**- ارسـل الامـر بالشكـل الآتي**\n\n`.كرر` **+ عدد الثواني + الرسالة او بالـرد ع رسالة**\n**- مثـال : .كرر 12 السلام عليكم**",
        )
    if counter > 50:
        sleeptimet = 0.5
        sleeptimem = 1
    else:
        sleeptimet = 0.1
        sleeptimem = 0.3
    await event.delete()
    addgvar("spamwork", True)
    await spam_function(event, sandy, zed, sleeptimem, sleeptimet)


@zedub.zed_cmd(
    pattern="تكرار ملصق$",
    command=("تكرار ملصق", plugin_category),
    info={
        "header": "لـ تكـرار ملصقـات من حزمـه معينـه",
        "الوصـف": "لعمل تكرار حزمة ملصقات بالرد ع ملصق من حزمة الملصقات المطلوبه",
        "الاستخـدام": "{tr}تكرار ملصق",
    },
)
async def stickerpack_spam(event):
    "لـ تكـرار ملصقـات من حزمـه معينـه"
    reply = await event.get_reply_message()
    if (
        not reply
        or await media_type(reply) is None
        or await media_type(reply) != "Sticker"
    ):
        return await edit_delete(
            event, "**- بالـرد ع أي ملصق لـ تڪـرار جميع ملصقـات الحـزمة ♽**"
        )
    try:
        stickerset_attr = reply.document.attributes[1]
        zedevent = await edit_or_reply(
            event, "**- جـارِ إحضـار تفاصيل حـزمة الملصقات .. يرجى الإنتظـار**"
        )
    except BaseException:
        await edit_delete(
            event,
            "**- هذا الملصق ليس مرتبط بـ أي حـزمة .. لذا تعذر إيجـاد الحـزمة ؟!**",
            5,
        )
        return
    try:
        get_stickerset = await event.client(
            GetStickerSetRequest(
                types.InputStickerSetID(
                    id=stickerset_attr.stickerset.id,
                    access_hash=stickerset_attr.stickerset.access_hash,
                ),
                hash=0,
            )
        )
    except Exception:
        return await edit_delete(
            zedevent,
            "**- هذا الملصق ليس مرتبط بـ أي حـزمة .. لذا تعذر إيجـاد الحـزمة ؟!**",
        )
    reqd_sticker_set = await event.client(
        functions.messages.GetStickerSetRequest(
            stickerset=types.InputStickerSetShortName(
                short_name=f"{get_stickerset.set.short_name}"
            ),
            hash=0,
        )
    )
    addgvar("spamwork", True)
    for m in reqd_sticker_set.documents:
        if gvarstatus("spamwork") is None:
            return
        await event.client.send_file(event.chat_id, m)
        await asyncio.sleep(0.7)
    await zedevent.delete()
    if BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- تڪـرار ملصــق ♽**\n"
                + f"**- تم تنفيذ الإزعاج بواسطـة حزمة الملصقات في  :** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع الحزمة **",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- تڪـرار ملصــق ♽**\n"
                + f"**- تم تنفيذ الإزعاج بواسطـة حزمة الملصقات في   :** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشة مع الحزمة **",
            )
        await event.client.send_file(BOTLOG_CHATID, reqd_sticker_set.documents[0])


@zedub.zed_cmd(
    pattern="وسبام ([\s\S]*)",
    command=("وسبام", plugin_category),
    info={
        "header": "تكـرار الكلمـه حـرف حـرف",
        "الاستخـدام": "{tr}وسبام + كلمـه",
        "مثــال": "{tr}وسبام احبك",
    },
)
async def tmeme(event):
    "تكـرار الكلمـه حـرف حـرف"
    cspam = str("".join(event.text.split(maxsplit=1)[1:]))
    message = cspam.replace(" ", "")
    await event.delete()
    addgvar("spamwork", True)
    for letter in message:
        if gvarstatus("spamwork") is None:
            return
        await event.respond(letter)
    if BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- تڪـرار بالحـرف 📝**\n"
                + f"**- تم تنفيذ الإزعاج بواسطـة الأحرف في  :** [User](tg://user?id={event.chat_id}) **الدردشة مع** : `{message}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- تڪـرار بالحـرف 📝**\n"
                + f"**- تم تنفيذ الإزعاج بواسطـة الأحرف في  :** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشة مع** : `{message}`",
            )


@zedub.zed_cmd(
    pattern="سبام ([\s\S]*)",
    command=("سبام", plugin_category),
    info={
        "header": "تكرار كلمـة او جملـة نصيـه",
        "الاستخـدام": "{tr}سبام + كلمـه",
        "مثــال": "{tr}سبام زدثــون",
    },
)
async def tmeme(event):
    "تكرار كلمـة او جملـة نصيـه"
    wspam = str("".join(event.text.split(maxsplit=1)[1:]))
    message = wspam.split()
    await event.delete()
    addgvar("spamwork", True)
    for word in message:
        if gvarstatus("spamwork") is None:
            return
        await event.respond(word)
    if BOTLOG:
        if event.is_private:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- تڪـرار بالكلمـه ♽**\n"
                + f"**- تم تنفيـذ التڪـرار بواسطـة الڪلمات في   :** [المستخدم](tg://user?id={event.chat_id}) **الدردشة مع :** `{message}`",
            )
        else:
            await event.client.send_message(
                BOTLOG_CHATID,
                "**- تڪـرار بالكلمـه ♽**\n"
                + f"**- تم تنفيـذ التڪـرار بواسطـة الڪلمات في   :** {get_display_name(await event.get_chat())}(`{event.chat_id}`) **الدردشة مع :** `{message}`",
            )


@zedub.zed_cmd(pattern="تعبير مكرر$")
async def react_spam(event):
    msg = await event.get_reply_message()
    if not msg:
        return await edit_delete(event, "**- بالـرد على الرسـالة اولاً ...**", 10)
    zedevent = await edit_or_reply(event, "**- جـارِ بدء التفاعـلات انتظـر ...**")
    if isinstance(msg.peer_id, types.PeerUser):
        emoji = [
            "👍",
            "👎",
            "❤",
            "🔥",
            "🥰",
            "👏",
            "😁",
            "🤔",
            "🤯",
            "😱",
            "🤬",
            "😢",
            "🎉",
            "🤩",
            "🤮",
            "💩",
        ]
    else:
        getchat = await event.client(GetFullChannelRequest(channel=event.chat_id))
        grp_emoji = getchat.full_chat.available_reactions
        if not grp_emoji:
            return await edit_delete(
                event, "**- اووبـس .. التعابير غير مفعلة في هـذه الدردشـة**", 6
            )
        emoji = grp_emoji
    addgvar("spamwork", True)
    await zedevent.delete()
    while gvarstatus("spamwork"):
        for i in emoji:
            await asyncio.sleep(0.2)
            try:
                await msg.react(i, True)
            except ForbiddenError:
                pass


@zedub.zed_cmd(pattern="ايقاف التكرار ?(.*)")
async def stopspamrz(event):
    if gvarstatus("spamwork") is not None and gvarstatus("spamwork") == "true":
        delgvar("spamwork")
        return await edit_delete(event, "**- تم ايقـاف التڪـرار .. بنجـاح ✅**")
    return await edit_delete(event, "**- لايوجـد هنـاك تڪرار لـ إيقافه ؟!**")


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="التكرار")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalSP_cmd)
