import re
from datetime import datetime

from telethon import events
from telethon.events import StopPropagation
from telethon.utils import get_display_name

from ..Config import Config
from ..core import CMD_INFO, PLG_INFO
from ..core.data import _sudousers_list, sudo_enabled_cmds
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import get_user_from_event, mentionuser
from ..sql_helper import global_collectionjson as sql
from ..sql_helper import global_list as sqllist
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import zedub

plugin_category = "الادوات"

LOGS = logging.getLogger(__name__)

ZDEV = gvarstatus("sudoenable") or "true"

ZelzalDV_cmd = (
    "[ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - اوامــر المطـور المســاعد](https://t.me/+LoO1LGVxdqM3NWZk) .\n\n"
    "**⎉╎قائـمـه اوامـر رفـع المطـور المسـاعـد 🧑🏻‍💻✅ 🦾 :** \n"
    "**- اضغـط ع الامـر للنسـخ ثـم استخـدمهـا بالتـرتيـب** \n\n"
    "**⪼** `.رفع مطور` \n"
    "**- لـ رفـع الشخـص مطـور مسـاعـد معـك بالبـوت** \n\n"
    "**⪼** `.تنزيل مطور` \n"
    "**- لـ تنزيـل الشخـص مطـور مسـاعـد مـن البـوت** \n\n"
    "**⪼** `.المطورين` \n"
    "**- لـ عـرض قائمـة بمطـورين البـوت الخـاص بـك 🧑🏻‍💻📑** \n\n"
    "**⪼** `.حذف المطورين`  **او**  `.تنزيل المطورين`\n"
    "**- لـ تنزيـل وحـذف جميـع المطـورين المرفوعيـن سابقـاً 🗑** \n\n"
    "**⪼** `.وضع المطور تفعيل` \n"
    "**لـ تفعيـل وضـع المطـورين المسـاعدين** \n\n"
    "**⪼** `.وضع المطور تعطيل` \n"
    "**لـ تعطيـل وضـع المطـورين المسـاعدين** \n\n"
    "**⪼** `.تحكم كامل` \n"
    "**- اعطـاء المطـورين المرفـوعيـن صلاحيـة التحكـم الكـاملـه بالاوامــر ✓** \n\n"
    "**⪼** `.تحكم آمن` \n"
    "**- اعطـاء المطـورين المرفـوعيـن صلاحيـة التحكـم الآمـن لـ الاوامــر الامنـه فقـط ✓** \n\n"
    "**⪼** `.تحكم` + اسم الامـر\n"
    "**- اعطـاء المطـورين المرفـوعيـن صلاحيـة التحكـم بأمـر واحـد فقـط او عـدة اوامـر معينـه ✓ .. مثـال (.تحكم ايدي) او (.تحكم ايدي فحص كتم)**\n\n"
    "**⪼** `.ايقاف تحكم كامل` \n"
    "**- ايقـاف صلاحيـة التحكـم الكـاملـه بالاوامــر للمطـورين المرفـوعيـن ✓** \n\n"
    "**⪼** `.ايقاف تحكم آمن` \n"
    "**- ايقـاف صلاحيـة التحكـم الآمـن لـ الاوامــر الآمنـه للمطـورين المرفـوعيـن ✓** \n\n"
    "**⪼** `.ايقاف تحكم` + اسم الامـر \n"
    "**- ايقـاف صلاحيـة التحكـم المعطـاه لـ امـر واحـد فقـط او عـدة اوامـر للمطـورين المرفـوعيـن ✓ .. مثـال (.ايقاف تحكم ايدي) او (.ايقاف تحكم ايدي فحص كتم)** \n\n"
    "\n𓆩 [𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁](https://t.me/+LoO1LGVxdqM3NWZk) 𓆪"
)


# ========== مراقب الحماية: منع المطور المساعد من استخدام الأوامر الممنوعة ========== #
# استخدام مجموعة سالبة (group=-100) لضمان تشغيل هذا الفلتر أولاً وقبل أي أمر آخر في السورس
@zedub.on(events.NewMessage(incoming=True), group=-100)
async def block_bad_words_for_sudo(event):
    try:
        if not event.text or not event.sender_id:
            return

        # التحقق إذا كان المرسل من المطورين المساعدين (وليس المالك الأساسي)
        if event.sender_id in Config.SUDO_USERS and event.sender_id != event.client.uid:
            text = event.text.strip()
            if not text:
                return

            try:
                sudo_prefix = getattr(Config, "SUDO_COMMAND_HAND_LER", ".")
                if not sudo_prefix:
                    sudo_prefix = "."
                sudo_prefix = sudo_prefix.replace("\\", "")
            except Exception:
                sudo_prefix = "."

            # تعابير نمطية ذكية لمطابقة الأوامر الممنوعة بجميع حالاتها (مع أرقام، مسافات، معرفات، إلخ)
            pattern_neek = r"^" + re.escape(sudo_prefix) + r"نيكه(\s*\d+)?(\s|$)"
            pattern_accounts = r"^" + re.escape(sudo_prefix) + r"عرض الحسابات(\s|$)"

            is_blocked = False

            if re.match(pattern_neek, text):
                is_blocked = True
                reply_msg = "**⎉╎عـذراً عزيزي المطـور المسـاعـد 🧑🏻‍💻،**\n**⎉╎هـذا الأمـر ممنـوع تمـاماً لأنـه يحتـوي علـى ألفـاظ غيـر لائقـة (قـذف) 🚯**\n**⎉╎يُرجـى الالتـزام باوامـر بـوت زدثــون المحترمـة ✓**"
            elif re.match(pattern_accounts, text):
                is_blocked = True
                reply_msg = "**⎉╎عـذراً عزيزي المطـور المسـاعـد 🧑🏻‍💻،**\n**⎉╎هـذا الأمـر (عرض الحسابات) ممنـوع تمـاماً لخصوصيـة المـالك 🚯**\n**⎉╎يُرجـى الالتـزام باوامـر بـوت زدثــون المحترمـة ✓**"

            if is_blocked:
                await event.reply(reply_msg)
                # رفع الاستثناء لإيقاف الحدث هنا ومنعه كلياً من الوصول لباقي الأوامر
                raise StopPropagation

    except StopPropagation:
        raise
    except Exception:
        pass


# ============================================================================ #


async def _init() -> None:
    sudousers = _sudousers_list()
    Config.SUDO_USERS.clear()
    for user_d in sudousers:
        Config.SUDO_USERS.add(user_d)


async def clear_sudo_list():
    Config.SUDO_USERS.clear()
    sql.del_collection("sudousers_list")


def get_key(val):
    for key, value in PLG_INFO.items():
        for cmd in value:
            if val == cmd:
                return key
    return None


@zedub.zed_cmd(
    pattern="وضع المطور (تفعيل|تعطيل)$",
    command=("وضع المطور", plugin_category),
    info={
        "header": "لـ تفعيـل/تعطيـل وضـع المطــور وفتـح/قفـل التحكـم لـ المطــور",
        "الاستـخـدام": "{tr}وضع المطور تفعيل / تعطيل",
    },
)
async def chat_blacklist(event):
    "لـ تفعيـل/تعطيـل وضـع المطــور وفتـح/قفـل التحكـم لـ المطــور"
    input_str = event.pattern_match.group(1)
    if input_str == "تفعيل":
        if gvarstatus("sudoenable") is not None:
            return await edit_or_reply(
                event, "**- وضـع المطــور فـي وضـع التفعيـل مسبقــاً ✓**"
            )
        addgvar("sudoenable", "true")
        return await edit_or_reply(
            event, "**⎉╎تـم تفعـيل وضـع المطــور المسـاعـد .. بنجــاح✓**"
        )
    if input_str == "تعطيل":
        if gvarstatus("sudoenable") is None:
            return await edit_or_reply(
                event, "**- وضـع المطــور فـي وضـع التعطيـل مسبقــاً ✓**"
            )
        delgvar("sudoenable")
        return await edit_or_reply(
            event, "**⎉╎تـم تعطيـل وضـع المطــور المسـاعـد .. بنجــاح✓**"
        )


@zedub.zed_cmd(
    pattern="رفع مطور(?:\s|$)([\s\S]*)",
    command=("رفع مطور", plugin_category),
    info={
        "header": "لـ رفـع مطـورين فـي بـوتك",
        "الاستـخـدام": "{tr}رفع مطور بالـرد / المعرف / الايدي",
    },
)
async def add_sudo_user(event):
    "لـ رفـع مطـورين فـي بـوتك"
    replied_user, error_i_a = await get_user_from_event(event)
    if replied_user is None:
        return
    if replied_user.id == event.client.uid:
        return await edit_or_reply(event, "** عـذراً .. لايمكـنـك رفـع نفسـك**")
    if replied_user.id in _sudousers_list():
        return await edit_delete(
            event,
            f"**⎉╎المستخـدم**  {mentionuser(get_display_name(replied_user),replied_user.id)}  **موجـود بالفعـل فـي قائمـة مطـورين البـوت 🧑🏻‍💻...**",
        )
    date = str(datetime.now().strftime("%B %d, %Y"))
    userdata = {
        "chat_id": replied_user.id,
        "chat_name": get_display_name(replied_user),
        "chat_username": replied_user.username,
        "date": date,
    }
    try:
        sudousers = sql.get_collection("sudousers_list").json
    except AttributeError:
        sudousers = {}
    sudousers[str(replied_user.id)] = userdata
    addgvar("sudoenable", "true")

    # تحديث الذاكرة بشكل فوري ليعمل التغيير دون ريستارت السيرفر
    Config.SUDO_USERS.add(replied_user.id)

    sudocmds = sudo_enabled_cmds()
    loadcmds = CMD_INFO.keys()

    if len(sudocmds) > 0:
        sqllist.del_keyword_list("sudo_enabled_cmds")

    for cmd in loadcmds:
        # استثناء الأوامر الممنوعة من دخول قواعد بيانات التحكم نهائياً
        if not re.match(r"^نيكه\d*$", cmd) and cmd != "عرض الحسابات":
            sqllist.add_to_list("sudo_enabled_cmds", cmd)

    sql.del_collection("sudousers_list")
    sql.add_collection("sudousers_list", sudousers, {})
    output = f"**⎉╎تـم رفـع**  {mentionuser(userdata['chat_name'],userdata['chat_id'])}  **مطـور مسـاعـد معـك فـي البـوت 🧑🏻‍💻 بنجـاح ✓**\n\n"
    await edit_or_reply(event, output)


@zedub.zed_cmd(
    pattern="تنزيل مطور(?:\s|$)([\s\S]*)",
    command=("تنزيل مطور", plugin_category),
    info={
        "header": "لـ تنزيـل مطـور مـن بـوتك",
        "الاستـخـدام": "{tr}تنزيل مطور بالـرد / المعرف / الايدي",
    },
)
async def _(event):
    "لـ تنزيـل مطـور مـن بـوتك"
    replied_user, error_i_a = await get_user_from_event(event)
    if replied_user is None:
        return
    try:
        sudousers = sql.get_collection("sudousers_list").json
    except AttributeError:
        sudousers = {}
    if str(replied_user.id) not in sudousers:
        return await edit_delete(
            event,
            f"** - المسـتخـدم :** {mentionuser(get_display_name(replied_user),replied_user.id)} \n\n**- انـه ليـس في قائمـة مطـورين البــوت.**",
        )
    del sudousers[str(replied_user.id)]
    sql.del_collection("sudousers_list")
    sql.add_collection("sudousers_list", sudousers, {})

    # حذف المطور من الذاكرة الفورية
    Config.SUDO_USERS.discard(replied_user.id)

    output = f"**⎉╎تـم تنـزيـل**  {mentionuser(get_display_name(replied_user),replied_user.id)}  **مـن قـائمـة مطـورين البـوت 🧑🏻‍💻 بنجـاح ✓**\n\n"
    await edit_or_reply(event, output)


@zedub.zed_cmd(
    pattern="المطورين$",
    command=("المطورين", plugin_category),
    info={
        "header": "لـ عـرض قائمــه بمطـورين بــوتك",
        "الاستـخـدام": "{tr}المطورين",
    },
)
async def _(event):
    "لـ عـرض قائمــه بمطـورين بــوتك"
    sudochats = _sudousers_list()
    try:
        sudousers = sql.get_collection("sudousers_list").json
    except AttributeError:
        sudousers = {}
    if len(sudochats) == 0:
        return await edit_delete(
            event,
            "**•❐• لا يـوجـد هنـاك مطـورين في قائمــة مـطـورين البــوت الخـاص بـك الى الان**",
        )
    result = "**•❐• قائمــة مـطـورين البــوت الخـاص بـك مـن 𝗭𝗧𝗵𝗼𝗻 :**\n\n"
    for chat in sudochats:
        result += f"**🧑🏻‍💻╎المطــور :** {mentionuser(sudousers[str(chat)]['chat_name'],sudousers[str(chat)]['chat_id'])}\n\n"
        result += f"**- تـم رفعـه بتـاريـخ :** {sudousers[str(chat)]['date']}\n\n"
    await edit_or_reply(event, result)


@zedub.zed_cmd(pattern="حذف_المطورين")
async def _(event):
    await clear_sudo_list()
    output = f"**⎉╎تـم حـذف المطورين .. بنجـاح 🗑**\n"
    await edit_or_reply(event, output)


@zedub.zed_cmd(pattern="حذف المطورين")
async def _(event):
    await clear_sudo_list()
    output = f"**⎉╎تـم حـذف المطورين .. بنجـاح 🗑**\n"
    await edit_or_reply(event, output)


@zedub.zed_cmd(pattern="مسح المطورين")
async def _(event):
    await clear_sudo_list()
    output = f"**⎉╎تـم حـذف المطورين .. بنجـاح 🗑**\n"
    await edit_or_reply(event, output)


@zedub.zed_cmd(pattern="تنزيل المطورين")
async def _(event):
    await clear_sudo_list()
    output = f"**⎉╎تـم حـذف المطورين .. بنجـاح 🗑**\n"
    await edit_or_reply(event, output)


@zedub.zed_cmd(
    pattern="تحكم(s)?(?:\s|$)([\s\S]*)",
    command=("تحكم", plugin_category),
    info={
        "header": "To enable cmds for sudo users.",
        "flags": {
            "عام": "Will enable all cmds for sudo users. (except few like eval, exec, profile).",
            "الكل": "Will add all cmds including eval,exec...etc. compelete sudo.",
            "امر": "Will add all cmds from the given plugin names.",
        },
        "usage": [
            "{tr}تحكم آمن",
            "{tr}تحكم كامل",
            "{tr}addscmd -p <plugin names>",
            "{tr}addscmd <commands>",
        ],
        "مثــال": [
            "{tr}addscmd -p autoprofile botcontrols i.e, for multiple names use space between each name",
            "{tr}addscmd ping alive i.e, for multiple names use space between each name",
        ],
    },
)
async def _(event):  # sourcery no-metrics
    "To enable cmds for sudo users."
    input_str = event.pattern_match.group(2)
    errors = ""
    sudocmds = sudo_enabled_cmds()
    if not input_str:
        return
    input_str = input_str.split()
    if input_str[0] == "آمن":
        zedevent = await edit_or_reply(event, "**⎉╎جـاري تفعيـل التحكـم الآمـن ...**")
        totalcmds = CMD_INFO.keys()
        flagcmds = (
            PLG_INFO["botcontrols"]
            + PLG_INFO["الوقتي"]
            + PLG_INFO["التحديث"]
            + PLG_INFO["الاوامر"]
            + PLG_INFO["هيروكو"]
            + PLG_INFO["الادمن"]
            + PLG_INFO["الحمايه"]
            + PLG_INFO["الاغاني"]
            + PLG_INFO["المجموعه"]
            + PLG_INFO["النظام"]
            + PLG_INFO["الفارات"]
            + PLG_INFO["المطور"]
            + ["gauth"]
            + ["greset"]
        )
        loadcmds = list(set(totalcmds) - set(flagcmds))
        if len(sudocmds) > 0:
            sqllist.del_keyword_list("sudo_enabled_cmds")
    elif input_str[0] == "كامل" or input_str[0] == "الكل":
        zedevent = await edit_or_reply(
            event, "**⎉╎جـاري تفعيـل التحكـم الكـامـل لجميـع الاوامـر ...**"
        )
        loadcmds = CMD_INFO.keys()
        if len(sudocmds) > 0:
            sqllist.del_keyword_list("sudo_enabled_cmds")
    elif input_str[0] == "ملف":
        zedevent = event
        input_str.remove("ملف")
        loadcmds = []
        for plugin in input_str:
            if plugin not in PLG_INFO:
                errors += f"`{plugin}` __There is no such plugin in your ZThon__.\n"
            else:
                loadcmds += PLG_INFO[plugin]
    else:
        zedevent = event
        loadcmds = []
        for cmd in input_str:
            if cmd not in CMD_INFO:
                errors += (
                    f"**⎉╎عـذراً .. لايـوجـد امـر بـ اسـم** `{cmd}` **فـي السـورس**\n"
                )
            elif cmd in sudocmds:
                errors += f"**⎉╎تـم تفعيـل التحكـم بـ امـر** `{cmd}` \n**⎉╎لجميـع مطـوريـن البـوت .. بنجـاح🧑🏻‍💻✅**\n"
            else:
                loadcmds.append(cmd)

    count = 0
    for cmd in loadcmds:
        # فلترة شاملة: الأوامر الممنوعة لا تُضاف للتحكم مطلقاً
        if not re.match(r"^نيكه\d*$", cmd) and cmd != "عرض الحسابات":
            sqllist.add_to_list("sudo_enabled_cmds", cmd)
            count += 1

    result = f"**⎉╎تـم تفعيـل التحكـم بنجـاح لـ**  `{count}` **امـر 🧑🏻‍💻✅**\n"
    output = result
    if errors != "":
        output += "\n**- خطــأ :**\n" + errors
    await edit_or_reply(zedevent, output)


@zedub.zed_cmd(
    pattern="ايقاف تحكم(s)?(?:\s|$)([\s\S]*)?",
    command=("ايقاف تحكم", plugin_category),
    info={
        "header": "To disable given cmds for sudo.",
        "flags": {
            "-all": "Will disable all enabled cmds for sudo users.",
            "-flag": "Will disable all flaged cmds like eval, exec...etc.",
            "-p": "Will disable all cmds from the given plugin names.",
        },
        "الاستـخـدام": [
            "{tr}rmscmd -all",
            "{tr}rmscmd -flag",
            "{tr}rmscmd -p <plugin names>",
            "{tr}rmscmd <commands>",
        ],
        "مثــال": [
            "{tr}rmscmd -p autoprofile botcontrols i.e, for multiple names use space between each name",
            "{tr}rmscmd ping alive i.e, for multiple commands use space between each name",
        ],
    },
)
async def _(event):  # sourcery no-metrics
    "To disable cmds for sudo users."
    input_str = event.pattern_match.group(2)
    errors = ""
    sudocmds = sudo_enabled_cmds()
    if not input_str:
        return await edit_or_reply(
            event, "__Which command should I disable for sudo users . __"
        )
    input_str = input_str.split()
    if input_str[0] == "كامل" or input_str[0] == "الكل":
        zedevent = await edit_or_reply(
            event,
            "**⎉╎تـم تعطيـل التحكـم الكـامل للمطـوريـن لـ جميـع الاوامـر .. بنجـاح🧑🏻‍💻✅**",
        )
        flagcmds = sudocmds
    elif input_str[0] == "آمن":
        zedevent = await edit_or_reply(
            event,
            "**⎉╎تـم تعطيـل التحكـم للمطـوريـن لـ الاوامـر الآمـنـه .. بنجـاح🧑🏻‍💻✅**",
        )
        flagcmds = (
            PLG_INFO["botcontrols"]
            + PLG_INFO["الوقتي"]
            + PLG_INFO["التحديث"]
            + PLG_INFO["الاوامر"]
            + PLG_INFO["هيروكو"]
            + PLG_INFO["الادمن"]
            + PLG_INFO["الحمايه"]
            + PLG_INFO["الاغاني"]
            + PLG_INFO["المجموعه"]
            + PLG_INFO["النظام"]
            + PLG_INFO["الفارات"]
            + PLG_INFO["المطور"]
            + ["gauth"]
            + ["greset"]
        )
    elif input_str[0] == "ملف":
        zedevent = event
        input_str.remove("ملف")
        flagcmds = []
        for plugin in input_str:
            if plugin not in PLG_INFO:
                errors += f"`{plugin}` __There is no such plugin in your ZThon__.\n"
            else:
                flagcmds += PLG_INFO[plugin]
    else:
        zedevent = event
        flagcmds = []
        for cmd in input_str:
            if cmd not in CMD_INFO:
                errors += (
                    f"**⎉╎عـذراً .. لايـوجـد امـر بـ اسـم** `{cmd}` **فـي السـورس**\n"
                )
            elif cmd not in sudocmds:
                errors += f"**⎉╎تـم تعطيـل التحكـم بـ امـر** `{cmd}` \n**⎉╎لجميـع مطـوريـن البـوت .. بنجـاح🧑🏻‍💻✅**\n"
            else:
                flagcmds.append(cmd)
    count = 0
    for cmd in flagcmds:
        if sqllist.is_in_list("sudo_enabled_cmds", cmd):
            count += 1
            sqllist.rm_from_list("sudo_enabled_cmds", cmd)

    result = f"**⎉╎تـم تعطيـل التحكـم الكـامل لـ**  `{count}` **امـر 🧑🏻‍💻✅**\n"
    output = result
    if errors != "":
        output += "\n**- خطــأ :**\n" + errors
    await edit_or_reply(zedevent, output)


@zedub.zed_cmd(
    pattern="التحكم( المعطل)?$",
    command=("التحكم", plugin_category),
    info={
        "header": "To show list of enabled cmds for sudo.",
        "description": "will show you the list of all enabled commands",
        "flags": {"-d": "To show disabled cmds instead of enabled cmds."},
        "الاستـخـدام": [
            "{tr}التحكم",
            "{tr}التحكم المعطل",
        ],
    },
)
async def _(event):  # sourcery no-metrics
    "To show list of enabled cmds for sudo."
    input_str = event.pattern_match.group(1)
    sudocmds = sudo_enabled_cmds()
    clist = {}
    error = ""
    if not input_str:
        text = "**•🧑🏻‍💻• قائمــة الاوامـر المسمـوحـه لـ المطـوريـن المـرفـوعيـن فـي البـوت الخـاص بـك 🏧:**"
        result = "**- اوامـر تحكـم المطـوريـن 🛃**"
        if len(sudocmds) > 0:
            for cmd in sudocmds:
                plugin = get_key(cmd)
                if plugin in clist:
                    clist[plugin].append(cmd)
                else:
                    clist[plugin] = [cmd]
        else:
            error += "**⎉╎عـذراً .. لايـوجـد اي اوامـر تحكـم خاصـه بـ المطـوريـن**\n**⎉╎ارسـل (** `.المساعد` **) لـ تصفـح اوامـر التحكـم 🛂**"
        count = len(sudocmds)
    else:
        text = "**•🧑🏻‍💻• قائمــة الاوامـر الغيـر مسمـوحـه 📵 لـ المطـوريـن المـرفـوعيـن فـي البـوت الخـاص بـك :**"
        result = "**- اوامـر عـدم تحكـم المطـوريـن 🚸**"
        totalcmds = CMD_INFO.keys()
        cmdlist = list(set(totalcmds) - set(sudocmds))
        if cmdlist:
            for cmd in cmdlist:
                plugin = get_key(cmd)
                if plugin in clist:
                    clist[plugin].append(cmd)
                else:
                    clist[plugin] = [cmd]
        else:
            error += "**⎉╎التحكـم كـامـل لـ كـل اوامـر البـوت لـ المطـورين**\n**⎉╎لايـوجـد اوامـر معطلـه لـوصـول المطـور لهـا**\n\n**⎉╎ارسـل (** `.المساعد` **) لـ تصفـح اوامـر ايقـاف التحكـم 🚷**"
        count = len(cmdlist)
    if error != "":
        return await edit_delete(event, error, 10)
    pkeys = clist.keys()
    n_pkeys = [i for i in pkeys if i is not None]
    pkeys = sorted(n_pkeys)
    output = ""
    for plugin in pkeys:
        output += f"• {plugin}\n"
        for cmd in clist[plugin]:
            output += f"`{cmd}` "
        output += "\n\n"
    finalstr = (
        result
        + f"\n\n**⎉╎نقطـة اوامـر المطـوريـن هـي : ** `{Config.SUDO_COMMAND_HAND_LER}`\n**⎉╎عـدد الاوامـر :** {count}\n\n"
        + output
    )
    await edit_or_reply(event, finalstr, aslink=True, linktext=text)


zedub.loop.create_task(_init())


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="المساعد")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalDV_cmd)