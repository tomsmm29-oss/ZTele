# ZThon module for purging unneeded messages(usually spam or ot).
import re
from asyncio import sleep

from telethon.errors import rpcbaseerrors
from telethon.tl.types import (
    InputMessagesFilterDocument,
    InputMessagesFilterEmpty,
    InputMessagesFilterGeo,
    InputMessagesFilterGif,
    InputMessagesFilterMusic,
    InputMessagesFilterPhotos,
    InputMessagesFilterRoundVideo,
    InputMessagesFilterUrl,
    InputMessagesFilterVideo,
    InputMessagesFilterVoice,
)

from ..core.managers import edit_delete, edit_or_reply

# # from ..helpers.utils import reply_id
from . import BOTLOG, BOTLOG_CHATID, zedub

plugin_category = "الادوات"


purgelist = {}

purgetype = {
    "ب": InputMessagesFilterVoice,
    "م": InputMessagesFilterDocument,
    "ح": InputMessagesFilterGif,
    "ص": InputMessagesFilterPhotos,
    "خ": InputMessagesFilterGeo,
    "غ": InputMessagesFilterMusic,
    "د": InputMessagesFilterRoundVideo,
    "ق": InputMessagesFilterEmpty,
    "ر": InputMessagesFilterUrl,
    "ف": InputMessagesFilterVideo,
    # "s": search
}


@zedub.zed_cmd(
    pattern="مسح(\s*| \d+)$",
    command=("del", plugin_category),
    info={
        "header": "لـ حذف رسـاله بالـرد",
        "الوصـف": "Deletes the message you replied to in x(count) seconds if count is not used then deletes immediately",
        "الاستخـدام": ["{tr}del <time in seconds>", "{tr}del"],
        "مثــال": "{tr}del 2",
    },
)
async def delete_it(event):
    "To delete replied message."
    input_str = event.pattern_match.group(1).strip()
    msg_src = await event.get_reply_message()
    if msg_src:
        if input_str and input_str.isnumeric():
            await event.delete()
            await sleep(int(input_str))
            try:
                await msg_src.delete()
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#الحـذف \n\n**- تـم حـذف الرسـالة .. بـ نجـاح ☑️**",
                    )
            except rpcbaseerrors.BadRequestError:
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "**- لا استطيـع الحـذف ليـس لـدي صلاحيـات المشـرف**",
                    )
        elif input_str:
            if not input_str.startswith("var"):
                await edit_or_reply(event, "**- عـذراً .. الرسـالة غيـر موجـودة**")
        else:
            try:
                await msg_src.delete()
                await event.delete()
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#الحـذف \n\n**- تـم حـذف الرسـالة .. بـ نجـاح ☑️**",
                    )
            except rpcbaseerrors.BadRequestError:
                await edit_or_reply(event, "**- عـذرا لا استـطيع حـذف هـذه الرسـالة**")
    elif not input_str:
        await event.delete()


@zedub.zed_cmd(
    pattern=".مسح(\s*| \d+)$",
    command=("del", plugin_category),
    info={
        "header": "لـ حذف رسـاله بالـرد",
        "الوصـف": "Deletes the message you replied to in x(count) seconds if count is not used then deletes immediately",
        "الاستخـدام": ["{tr}del <time in seconds>", "{tr}del"],
        "مثــال": "{tr}del 2",
    },
)
async def delete_it(event):  # Code by T.me/zzzzl1l
    "To delete replied message."
    input_str = event.pattern_match.group(1).strip()
    msg_src = await event.get_reply_message()
    if msg_src:
        if input_str and input_str.isnumeric():
            await event.delete()
            await sleep(int(input_str))
            try:
                await msg_src.delete()
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#الحـذف \n\n**- تـم حـذف الرسـالة .. بـ نجـاح ☑️**",
                    )
            except rpcbaseerrors.BadRequestError:
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "**- لا استطيـع الحـذف ليـس لـدي صلاحيـات المشـرف**",
                    )
        elif input_str:
            if not input_str.startswith("var"):
                await edit_or_reply(event, "**- عـذراً .. الرسـالة غيـر موجـودة**")
        else:
            try:
                await msg_src.delete()
                await event.delete()
                if BOTLOG:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        "#الحـذف \n\n**- تـم حـذف الرسـالة .. بـ نجـاح ☑️**",
                    )
            except rpcbaseerrors.BadRequestError:
                await edit_or_reply(event, "**- عـذرا لا استـطيع حـذف هـذه الرسـالة**")
    elif not input_str:
        await event.delete()


@zedub.zed_cmd(pattern="بداية الحذف")
async def purge_from(event):
    reply = await event.get_reply_message()
    if reply:
        reply_message = await reply_id(event)
        purgelist[event.chat_id] = reply_message
        await edit_delete(
            event,
            "**- تم تحديد رسالة بداية الحذف 🗑✅**\n**- الان قم بالـرد على آخر رسالة عبر الامر**\n\n`.نهاية الحذف`",
        )
    else:
        await edit_delete(event, "**- بالـرد على اول رسالة تريد الحذف من عندهـا**")


@zedub.zed_cmd(pattern="نهاية الحذف")
async def purge_to(event):
    chat = await event.get_input_chat()
    reply = await event.get_reply_message()
    try:
        from_message = purgelist[event.chat_id]
    except KeyError:
        return await edit_delete(
            event,
            "**- اولاً قم بالـرد ع اول رسالة تريد ان تبدأ منهـا الحذف عبر الامـر**\n `.بداية الحذف` \n**بالـرد ع الرسالة**\n\n**- ثم بعـد ذلك قم باستخدام الامـر**\n`.نهاية الحذف`\n**- بالـرد على آخر سالة تريـد الحذف اليهـا**",
        )
    if not reply or not from_message:
        return await edit_delete(
            event,
            "**- اولاً قم بالـرد ع اول رسالة تريد ان تبدأ منهـا الحذف عبر الامـر**\n `.بداية الحذف` \n**بالـرد ع الرسالة**\n\n**- ثم بعـد ذلك قم باستخدام الامـر**\n`.نهاية الحذف`\n**- بالـرد على آخر سالة تريـد الحذف اليهـا**",
        )
    try:
        to_message = await reply_id(event)
        msgs = []
        count = 0
        async for msg in event.client.iter_messages(
            event.chat_id, min_id=(from_message - 1), max_id=(to_message + 1)
        ):
            msgs.append(msg)
            count += 1
            msgs.append(event.reply_to_msg_id)
            if len(msgs) == 100:
                await event.client.delete_messages(chat, msgs)
                msgs = []
        if msgs:
            await event.client.delete_messages(chat, msgs)
        await edit_delete(
            event,
            "**- التنظيف السريـع تم بنجـاح ✅**\n**- تم حـذف** "
            + str(count)
            + " **رسالـه 🗑**",
        )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#التنظيف 🗑 \n**- تم حـذف **" + str(count) + "**رسـالة .. بنجـاح ☑️**",
            )
    except Exception as e:
        await edit_delete(event, f"**- خطـأ :**\n`{e}`")


@zedub.zed_cmd(pattern="حذف رسائلي")
async def purgeme(event):
    message = event.text
    if message:  # Code by T.me/zzzzl1l
        count = int(message[12:])
    else:  # Code by T.me/zzzzl1l
        count = int(10000)
    i = 1
    async for message in event.client.iter_messages(event.chat_id, from_user="me"):
        if i > count + 1:
            break
        i += 1
        await message.delete()

    smsg = await event.client.send_message(
        event.chat_id,
        f"**❈╎تـم حـذف** " + str(count) + " **رسـالـة . . بنجـاح ☑️**",
    )
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#حـذف_رسـائلي \n\n**❈╎تـم حـذف** "
            + str(count)
            + "**رسـالـة . . بنجـاح ☑️**",
        )
    await sleep(5)
    await smsg.delete()


# TODO: only sticker messages.
@zedub.zed_cmd(
    pattern="تنظيف(?:\s|$)([\s\S]*)",
    command=("تنظيف", plugin_category),
    info={
        "header": "To purge messages from the replied message.",
        "الوصـف": "•  Deletes the x(count) amount of messages from the replied message\
        \n•  If you don't use count then deletes all messages from the replied messages\
        \n•  If you haven't replied to any message and used count then deletes recent x messages.\
        \n•  If you haven't replied to any message or havent mentioned any flag or count then doesnt do anything\
        \n•  If flag is used then selects that type of messages else will select all types\
        \n•  You can use multiple flags like -gi 10 (It will delete 10 images and 10 gifs but not 10 messages of combination images and gifs.)\
        ",
        "امـر اضافـي": {
            "a": "To delete Voice messages.",
            "f": "To delete documents.",
            "g": "To delete gif's.",
            "i": "To delete images/photos.",
            "l": "To delete locations/gps.",
            "m": "To delete Audio files(music files).",
            "r": "To delete Round video messages.",
            "t": "To delete stickers and text messages.",
            "u": "To delete url/links.",
            "v": "To delete Video messages.",
            "s": "To search paticular message and delete",
        },
        "الاستخـدام": [
            "{tr}purge <flag(optional)> <count(x)> <reply> - to delete x flagged messages after reply",
            "{tr}purge <flag> <count(x)> - to delete recent x messages",
        ],
        "مثــال": [
            "{tr}purge 10",
            "{tr}purge -f 10",
            "{tr}purge -gi 10",
        ],
    },
)
async def fastpurger(event):  # sourcery no-metrics
    "To purge messages from the replied message"
    chat = await event.get_input_chat()
    msgs = []
    count = 0
    input_str = event.pattern_match.group(1)
    ptype = re.findall(r"-\w+", input_str)
    try:
        p_type = ptype[0].replace("-", "")
        input_str = input_str.replace(ptype[0], "").strip()
    except IndexError:
        p_type = None
    error = ""
    result = ""
    await event.delete()
    reply = await event.get_reply_message()
    if reply:
        if input_str and input_str.isnumeric():
            if p_type is not None:
                for ty in p_type:
                    if ty in purgetype:
                        async for msg in event.client.iter_messages(
                            event.chat_id,
                            limit=int(input_str),
                            offset_id=reply.id - 1,
                            reverse=True,
                            filter=purgetype[ty],
                        ):
                            count += 1
                            msgs.append(msg)
                            if len(msgs) == 50:
                                await event.client.delete_messages(chat, msgs)
                                msgs = []
                        if msgs:
                            await event.client.delete_messages(chat, msgs)
                    elif ty == "كلمه":
                        error += "\n✾╎الكلمـه المضـافه خـطأ"
                    else:
                        error += f"\n\n✾╎`{ty}`  : هـذه الكلمـه المضـافه خاطئـة "
            else:
                count += 1
                async for msg in event.client.iter_messages(
                    event.chat_id,
                    limit=(int(input_str) - 1),
                    offset_id=reply.id,
                    reverse=True,
                ):
                    msgs.append(msg)
                    count += 1
                    if len(msgs) == 50:
                        await event.client.delete_messages(chat, msgs)
                        msgs = []
                if msgs:
                    await event.client.delete_messages(chat, msgs)
        elif input_str and p_type is not None:
            if p_type == "كلمه":
                try:
                    cont, inputstr = input_str.split(" ")
                except ValueError:
                    cont = "error"
                    inputstr = input_str
                cont = cont.strip()
                inputstr = inputstr.strip()
                if cont.isnumeric():
                    async for msg in event.client.iter_messages(
                        event.chat_id,
                        limit=int(cont),
                        offset_id=reply.id - 1,
                        reverse=True,
                        search=inputstr,
                    ):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await event.client.delete_messages(chat, msgs)
                            msgs = []
                else:
                    async for msg in event.client.iter_messages(
                        event.chat_id,
                        offset_id=reply.id - 1,
                        reverse=True,
                        search=input_str,
                    ):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await event.client.delete_messages(chat, msgs)
                            msgs = []
                if msgs:
                    await event.client.delete_messages(chat, msgs)
            else:
                error += f"\n✾╎`{ty}`  : هـذه الكلمـه المضـافه خاطئـة "
        elif input_str:
            error += f"\n✾╎`.تنظيف {input_str}` الامـر خـطأ يـرجى الكتابة بـشكل صحيح"
        elif p_type is not None:
            for ty in p_type:
                if ty in purgetype:
                    async for msg in event.client.iter_messages(
                        event.chat_id,
                        min_id=event.reply_to_msg_id - 1,
                        filter=purgetype[ty],
                    ):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await event.client.delete_messages(chat, msgs)
                            msgs = []
                    if msgs:
                        await event.client.delete_messages(chat, msgs)
                else:
                    error += f"\n✾╎`{ty}`  : هـذه الكلمـه المضـافه خاطئـة"
        else:
            async for msg in event.client.iter_messages(
                chat, min_id=event.reply_to_msg_id - 1
            ):
                count += 1
                msgs.append(msg)
                if len(msgs) == 50:
                    await event.client.delete_messages(chat, msgs)
                    msgs = []
            if msgs:
                await event.client.delete_messages(chat, msgs)
    elif p_type is not None and input_str:
        if p_type != "كلمه" and input_str.isnumeric():
            for ty in p_type:
                if ty in purgetype:
                    async for msg in event.client.iter_messages(
                        event.chat_id, limit=int(input_str), filter=purgetype[ty]
                    ):
                        count += 1
                        msgs.append(msg)
                        if len(msgs) == 50:
                            await event.client.delete_messages(chat, msgs)
                            msgs = []
                    if msgs:
                        await event.client.delete_messages(chat, msgs)
                elif ty == "الكتابه":
                    error += "\n✾╎لا تستطـيع استـخدام امر التنظيف عبر البحث مع الكلمـه المضـافه"

                else:
                    error += f"\n✾╎`{ty}`  : هـذه الكلمـه المضـافه خاطئـة "
        elif p_type == "كلمه":
            try:
                cont, inputstr = input_str.split(" ")
            except ValueError:
                cont = "error"
                inputstr = input_str
            cont = cont.strip()
            inputstr = inputstr.strip()
            if cont.isnumeric():
                async for msg in event.client.iter_messages(
                    event.chat_id, limit=int(cont), search=inputstr
                ):
                    count += 1
                    msgs.append(msg)
                    if len(msgs) == 50:
                        await event.client.delete_messages(chat, msgs)
                        msgs = []
            else:
                async for msg in event.client.iter_messages(
                    event.chat_id, search=input_str
                ):
                    count += 1
                    msgs.append(msg)
                    if len(msgs) == 50:
                        await event.client.delete_messages(chat, msgs)
                        msgs = []
            if msgs:
                await event.client.delete_messages(chat, msgs)
        else:
            error += f"\n✾╎`{ty}`  : هـذه الكلمـه المضـافه خاطئـة "
    elif p_type is not None:
        for ty in p_type:
            if ty in purgetype:
                async for msg in event.client.iter_messages(
                    event.chat_id, filter=purgetype[ty]
                ):
                    count += 1
                    msgs.append(msg)
                    if len(msgs) == 50:
                        await event.client.delete_messages(chat, msgs)
                        msgs = []
                if msgs:
                    await event.client.delete_messages(chat, msgs)
            elif ty == "كلمه":
                error += (
                    "\n✾╎لا تستطـيع استـخدام امر التنظيف عبر البحث مع الكلمـه المضـاف"
                )

            else:
                error += f"\n✾╎`{ty}`  : هـذه الكلمـه المضـافه خاطئـة "
    elif input_str.isnumeric():
        async for msg in event.client.iter_messages(chat, limit=int(input_str) + 1):
            count += 1
            msgs.append(msg)
            if len(msgs) == 50:
                await event.client.delete_messages(chat, msgs)
                msgs = []
        if msgs:
            await event.client.delete_messages(chat, msgs)
    else:
        error += "\n✾╎لم يتـم تحـديد كلمـه مضـافه ارسـل  (`.اوامر التنظيف`) لـ رؤيـة اوامـر التنظـيف"
    if msgs:
        await event.client.delete_messages(chat, msgs)
    if count > 0:
        result += (
            "✾╎اكـتمل الـتنظيف السـريع\n✾╎تـم حـذف  " + str(count) + "من الـرسائل "
        )
    if error != "":
        result += f"\n\n**خـطأ:**{error}"
    if result == "":
        result += "✾╎لا تـوجد رسـائل لـتنظيفها"
    hi = await event.client.send_message(event.chat_id, result)
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#التنظيـف \n{result}",
        )
    await sleep(5)
    await hi.delete()


@zedub.zed_cmd(
    pattern="حذف رسائله( الكل)?(?:\s|$)([\s\S]*)",
    command=("حذف رسائله", plugin_category),
    info={
        "header": "To purge messages from the replied message of replied user.",
        "الوصـف": "•  Deletes the x(count) amount of messages from the replied message of replied user\
        \n•  If you don't use count then deletes all messages from the replied messages of replied user\
        \n•  Use -a flag to delete all his messages or mention x to delete x recent messages of his\
        \n•  Use -s flag to delete all his messages which contatins given word.\
        \n•  You cann't use both flags at a time\
        ",
        "امـر اضافـي": {
            "الكل": "To delete all messages of replied user.",
            "كلمة": "To delete all messages of replied user with the given query.",
        },
        "الاستخـدام": [
            "{tr}upurge <count> <reply>",
            "{tr}upurge -a <count(optional)> <reply>",
            "{tr}upurge -s <query> <reply>",
        ],
        "مثــال": [
            "{tr}حذف رسائله 10",
            "{tr}upurge -s fuck",
            "{tr}upurge -a",
        ],
    },
)
async def fast_purger(event):  # sourcery no-metrics
    "To purge messages from the replied message of replied user."
    chat = await event.get_input_chat()
    msgs = []
    count = 0
    flag = event.pattern_match.group(1)
    input_str = event.pattern_match.group(2)
    ptype = re.findall(r"-\w+", input_str)
    try:
        p_type = ptype[0].replace("-", "")
        input_str = input_str.replace(ptype[0], "").strip()
    except IndexError:
        p_type = None
    error = ""
    result = ""
    await event.delete()
    reply = await event.get_reply_message()
    if not reply or reply.sender_id is None:
        return await edit_delete(
            event, "**- خطـأ :**\n__This cmd Works only if you reply to user message.__"
        )
    if not flag:
        if input_str and p_type == "كلمة":
            async for msg in event.client.iter_messages(
                event.chat_id,
                search=input_str,
                from_user=reply.sender_id,
            ):
                count += 1
                msgs.append(msg)
                if len(msgs) == 50:
                    await event.client.delete_messages(chat, msgs)
                    msgs = []
        elif input_str and input_str.isnumeric():
            async for msg in event.client.iter_messages(
                event.chat_id,
                limit=int(input_str),
                offset_id=reply.id - 1,
                reverse=True,
                from_user=reply.sender_id,
            ):
                msgs.append(msg)
                count += 1
                if len(msgs) == 50:
                    await event.client.delete_messages(chat, msgs)
                    msgs = []
        elif input_str:
            error += f"\n• `.upurge {input_str}` __is invalid syntax try again by reading__ `.help -c purge`"
        else:
            async for msg in event.client.iter_messages(
                chat,
                min_id=event.reply_to_msg_id - 1,
                from_user=reply.sender_id,
            ):
                count += 1
                msgs.append(msg)
                if len(msgs) == 50:
                    await event.client.delete_messages(chat, msgs)
                    msgs = []
    elif input_str.isnumeric():
        async for msg in event.client.iter_messages(
            chat,
            limit=int(input_str),
            from_user=reply.sender_id,
        ):
            count += 1
            msgs.append(msg)
            if len(msgs) == 50:
                await event.client.delete_messages(chat, msgs)
                msgs = []
    else:
        async for msg in event.client.iter_messages(
            chat,
            from_user=reply.sender_id,
        ):
            count += 1
            msgs.append(msg)
            if len(msgs) == 50:
                await event.client.delete_messages(chat, msgs)
                msgs = []
    if msgs:
        await event.client.delete_messages(chat, msgs)
    if count > 0:
        result += (
            "**- حـذف رسائلـه تم بنجـاح ✅**\n**- تم حـذف** "
            + str(count)
            + "**رسالـه 🗑**"
        )
    if error != "":
        result += f"\n\n**- خطـأ :**{error}"
    if not result:
        result += "**- عـذراً .. الرسـالة غيـر موجـودة**"
    hi = await event.client.send_message(event.chat_id, result)
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#حـذف_رسائلـه \n{result}",
        )
    await sleep(5)
    await hi.delete()
