import contextlib
import os
from pathlib import Path

from ..Config import Config
from ..core import CMD_INFO, PLG_INFO
from ..utils import load_module, remove_plugin
from . import CMD_HELP, CMD_LIST, SUDO_LIST, zedub, edit_delete, edit_or_reply, reply_id

plugin_category = "الادوات"

DELETE_TIMEOUT = 5
thumb_image_path = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, "thumb_image.jpg")

MAIN_DEV = 8241311871  # صلاحيات المطور الأساسي (أنت فقط)


def plug_checker(plugin):
    return f"./zlzl/plugins/{plugin}.py"


@zedub.zed_cmd(
    pattern="(تنصيب|نصب)$",
    command=("نصب", plugin_category),
    info={
        "header": "لـ تنصيب ملفـات اضافيـه.",
        "الوصـف": "بالـرد ع اي ملف (يدعم سورس زدثــون) لـ تنصيبه في بوتك.",
        "الاستخـدام": "{tr}نصب بالــرد ع ملـف",
    },
)
async def install(event):
    zelzal = event.sender_id
    if zelzal != MAIN_DEV:
        return await edit_delete(event, "**- عـذراً .. هذا الأمر خاص بالمطوّر الأساسي فقط ⚠️**", 10)

    if event.reply_to_msg_id:
        try:
            downloaded_file_name = await event.client.download_media(
                await event.get_reply_message(),
                "zlzl/plugins/",
            )
            if "(" not in downloaded_file_name:
                path1 = Path(downloaded_file_name)
                shortname = path1.stem
                load_module(shortname.replace(".py", ""))
                await edit_delete(
                    event,
                    f"**⎉╎تـم تنصـيب المـلف** `{os.path.basename(downloaded_file_name)}` **بنجـاح ✓**",
                    10,
                )
            else:
                os.remove(downloaded_file_name)
                await edit_delete(event, "**- خطأ .. هذا الملف منصّب مسبقاً !**", 10)
        except Exception as e:
            await edit_delete(event, f"**- خطأ :**\n`{e}`", 10)
            os.remove(downloaded_file_name)


@zedub.zed_cmd(
    pattern="حمل ([\s\S]*)",
    command=("حمل", plugin_category),
    info={
        "header": "لـ تحميل ملف ملغي تحميله سابقاً.",
        "الاستخـدام": "{tr}حمل + اسم الملـف",
    },
)
async def load(event):
    zelzal = event.sender_id
    if zelzal != MAIN_DEV:
        return await edit_delete(event, "**- هذا الأمر خاص بالمطوّر الأساسي فقط ⚠️**", 10)

    shortname = event.pattern_match.group(1)
    try:
        with contextlib.suppress(BaseException):
            remove_plugin(shortname)
        load_module(shortname)
        await edit_delete(event, f"**⎉╎تـم تحميـل الملـف** {shortname} **بنجـاح ✓**", 10)
    except Exception as e:
        await edit_or_reply(
            event,
            f"**- لا يمكن تحميل الملف** {shortname} **بسبب الخطأ التالي:**\n{e}",
        )


@zedub.zed_cmd(
    pattern="ارسل ([\s\S]*)",
    command=("ارسل", plugin_category),
    info={
        "header": "لـ جلب أي ملف من ملفات السورس.",
        "الاستخـدام": "{tr}ارسل + اسم الملف",
    },
)
async def send(event):
    zelzal = event.sender_id
    if zelzal != MAIN_DEV:
        return await edit_delete(event, "**- هذا الأمر خاص بالمطوّر الأساسي فقط ⚠️**", 10)

    reply_to_id = await reply_id(event)
    thumb = thumb_image_path if os.path.exists(thumb_image_path) else None
    input_str = event.pattern_match.group(1)
    the_plugin_file = plug_checker(input_str)

    if os.path.exists(the_plugin_file):
        await event.client.send_file(
            event.chat_id,
            the_plugin_file,
            force_document=True,
            allow_cache=False,
            reply_to=reply_to_id,
            thumb=thumb,
            caption=f"**➥ اسم الاضافة:** `{input_str}`",
        )
        await event.delete()
    else:
        await edit_or_reply(event, "**- الملف غير موجود !**")


@zedub.zed_cmd(
    pattern="الغاء حمل ([\s\S]*)",
    command=("الغاء حمل", plugin_category),
    info={
        "header": "لـ إلغاء تحميل أي ملف.",
        "الاستخـدام": "{tr}الغاء حمل + اسم الملف",
    },
)
async def unload(event):
    zelzal = event.sender_id
    if zelzal != MAIN_DEV:
        return await edit_delete(event, "**- هذا الأمر خاص بالمطوّر الأساسي فقط ⚠️**", 10)

    shortname = event.pattern_match.group(1)
    try:
        remove_plugin(shortname)
        await edit_or_reply(event, f"**⎉╎تـم الغـاء تحميـل** {shortname} **بنجاح ✓**")
    except Exception as e:
        await edit_or_reply(event, f"**⎉╎تم الغـاء التحميل** {shortname} **بنجـاح ✓**\n{e}")


@zedub.zed_cmd(
    pattern="الغاء نصب ([\s\S]*)",
    command=("الغاء تنصيب", plugin_category),
    info={
        "header": "لـ إزالة أي ملف من السورس نهائياً.",
        "الاستخـدام": "{tr}الغاء نصب + اسم الملف",
    },
)
async def uninstall(event):
    zelzal = event.sender_id
    if zelzal != MAIN_DEV:
        return await edit_delete(event, "**- هذا الأمر خاص بالمطوّر الأساسي فقط ⚠️**", 10)

    shortname = event.pattern_match.group(1)
    path = plug_checker(shortname)

    if not os.path.exists(path):
        return await edit_delete(event, f"**- الملف `{shortname}` غير موجود لإلغاء تنصيبه !**")

    os.remove(path)

    if shortname in CMD_LIST:
        CMD_LIST.pop(shortname)
    if shortname in SUDO_LIST:
        SUDO_LIST.pop(shortname)
    if shortname in CMD_HELP:
        CMD_HELP.pop(shortname)

    try:
        remove_plugin(shortname)
        await edit_or_reply(event, f"**⎉╎تـم الغـاء تنصيب الملف** {shortname} **بنجـاح ✓**")
    except Exception as e:
        await edit_or_reply(event, f"**⎉╎تـم الغـاء تنصيب الملف** {shortname} **بنجـاح ✓**\n{e}")

    if shortname in PLG_INFO:
        for cmd in PLG_INFO[shortname]:
            CMD_INFO.pop(cmd)
        PLG_INFO.pop(shortname) 