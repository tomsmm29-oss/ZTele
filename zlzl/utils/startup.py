import glob
import logging
import os
import sys
import urllib.request
from datetime import datetime as dt
from pathlib import Path

import heroku3
from pytz import timezone
from telethon import functions, types, utils
from telethon.errors import BadRequestError
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights

from zlzl import BOTLOG, BOTLOG_CHATID, PM_LOGGER_GROUP_ID

from ..Config import Config
from ..core.logger import logging
from ..core.session import zedub
from ..helpers.utils import install_pip
from ..helpers.utils.utils import runcmd
from ..sql_helper.global_collection import (
    del_keyword_collectionlist,
    get_item_collectionlist,
)
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from .pluginmanager import load_module
from .tools import create_supergroup

ENV = bool(os.environ.get("ENV", False))
LOGS = logging.getLogger("zlzl")
cmdhr = Config.COMMAND_HAND_LER

# --- تعديل مايكي: تعريف المتغير غصب عشان ما يكرش ---
VPS_NOLOAD = []
# --------------------------------------------------

Zel_Dev = ()
Zed_Dev = ()
Zed_Vip = ()
Zzz_Vip = ()
zchannel = set()
zzprivatech = set()

heroku_api = "https://api.heroku.com"
if Config.HEROKU_APP_NAME is not None and Config.HEROKU_API_KEY is not None:
    Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
    app = Heroku.app(Config.HEROKU_APP_NAME)
    heroku_var = app.config()
else:
    app = None

# المنطق القديم (نخليه، بس إحنا آمنا نفسنا فوق بـ [])
if ENV:
    VPS_NOLOAD = ["vps"]
elif os.path.exists("config.py"):
    VPS_NOLOAD = ["heroku"]

bot = zedub
DEV = 8241311871


async def autovars():
    if "ENV" in heroku_var and "TZ" in heroku_var:
        return
    if "ENV" in heroku_var and "TZ" not in heroku_var:
        zzcom = "."
        zzztz = "Asia/Baghdad"
        heroku_var["COMMAND_HAND_LER"] = zzcom
        heroku_var["TZ"] = zzztz
    if "ENV" not in heroku_var and "TZ" not in heroku_var:
        zzenv = "ANYTHING"
        zzcom = "."
        zzztz = "Asia/Baghdad"
        heroku_var["ENV"] = zzenv
        heroku_var["COMMAND_HAND_LER"] = zzcom
        heroku_var["TZ"] = zzztz


async def autoname():
    if Config.ALIVE_NAME:
        return
    zlzlal = await bot.get_me()
    zzname = f"{zlzlal.first_name}"
    tz = Config.TZ
    tzDateTime = dt.now(timezone(tz))
    zdate = tzDateTime.strftime("%Y/%m/%d")
    militaryTime = tzDateTime.strftime("%H:%M")
    ztime = dt.strptime(militaryTime, "%H:%M").strftime("%I:%M %p")
    zzd = f"‹ {zdate} ›"
    zzt = f"‹ {ztime} ›"
    if gvarstatus("z_date") is None:
        zd = "z_date"
        zt = "z_time"
        addgvar(zd, zzd)
        addgvar(zt, zzt)
    heroku_var["ALIVE_NAME"] = zzname


async def setup_bot():
    try:
        await zedub.connect()
        config = await zedub(functions.help.GetConfigRequest())
        for option in config.dc_options:
            if option.ip_address == zedub.session.server_address:
                if zedub.session.dc_id != option.id:
                    LOGS.warning(
                        f"ايـدي DC ثـابت فـي الجلسـة مـن {zedub.session.dc_id}"
                        f" الـى {option.id}"
                    )
                zedub.session.set_dc(option.id, option.ip_address, option.port)
                zedub.session.save()
                break
        bot_details = await zedub.tgbot.get_me()
        Config.TG_BOT_USERNAME = f"@{bot_details.username}"
        zedub.me = await zedub.get_me()
        zedub.uid = zedub.tgbot.uid = utils.get_peer_id(zedub.me)
        if Config.OWNER_ID == 0:
            Config.OWNER_ID = utils.get_peer_id(zedub.me)
    except Exception as e:
        LOGS.error(f"Setup Error: {str(e)}")
        sys.exit()


async def mybot():
    if gvarstatus("z_assistant"):
        pass
    else:
        addgvar("z_assistant", True)


async def startupmessage():
    if gvarstatus("PMLOG") and gvarstatus("PMLOG") != "false":
        delgvar("PMLOG")
    if gvarstatus("GRPLOG") and gvarstatus("GRPLOG") != "false":
        delgvar("GRPLOG")
    try:
        if BOTLOG:
            zzz = bot.me
            f"{zzz.first_name} {zzz.last_name}" if zzz.last_name else zzz.first_name
            try:
                await zedub.tgbot.send_message(
                    BOTLOG_CHATID,
                    f"**⌔ تـم تشغـيل سـورس زدثــون (نسخة مايكي) بنجـاح ✅**",
                )
            except:
                pass
    except Exception as e:
        LOGS.error(e)
        return None
    try:
        msg_details = list(get_item_collectionlist("restart_update"))
        if msg_details:
            msg_details = msg_details[0]
            await zedub.check_testcases()
            message = await zedub.get_messages(msg_details[0], ids=msg_details[1])
            text = message.text + "\n\n**•⎆┊تـم اعـادة تشغيـل السـورس بنجــاح 🧸♥️**"
            await zedub.edit_message(msg_details[0], msg_details[1], text)
            del_keyword_collectionlist("restart_update")
    except Exception as e:
        LOGS.error(e)
        return None


async def add_bot_to_logger_group(chat_id):
    bot_details = await zedub.tgbot.get_me()
    try:
        await zedub(
            functions.messages.AddChatUserRequest(
                chat_id=chat_id,
                user_id=bot_details.username,
                fwd_limit=1000000,
            )
        )
    except BaseException:
        try:
            await zedub(
                functions.channels.InviteToChannelRequest(
                    channel=chat_id,
                    users=[bot_details.username],
                )
            )
        except Exception as e:
            LOGS.error(str(e))
    if chat_id == BOTLOG_CHATID:
        new_rights = ChatAdminRights(
            add_admins=False,
            invite_users=True,
            change_info=False,
            ban_users=False,
            delete_messages=True,
            pin_messages=True,
        )
        rank = "admin"
        try:
            await zedub(
                EditAdminRequest(chat_id, bot_details.username, new_rights, rank)
            )
        except BadRequestError as e:
            LOGS.error(str(e))
        except Exception as e:
            LOGS.error(str(e))


# دوال فارغة لمنع الاشتراك الإجباري
async def saves():
    pass


async def supscrips():
    pass


async def load_plugins(folder, extfolder=None):
    """
    To load plugins from the mentioned folder
    """
    if extfolder:
        path = f"{extfolder}/*.py"
        plugin_path = extfolder
    else:
        path = f"zlzl/{folder}/*.py"
        plugin_path = f"zlzl/{folder}"
    files = glob.glob(path)
    files.sort()
    success = 0
    failure = []
    for name in files:
        with open(name) as f:
            path1 = Path(f.name)
            shortname = path1.stem
            pluginname = shortname.replace(".py", "")
            try:
                # هنا التعديل: VPS_NOLOAD صار معرف فوق، فما راح يكرش
                if (pluginname not in Config.NO_LOAD) and (
                    pluginname not in VPS_NOLOAD
                ):
                    flag = True
                    retry_count = 0
                    while flag:
                        try:
                            load_module(
                                pluginname,
                                plugin_path=plugin_path,
                            )
                            if shortname in failure:
                                failure.remove(shortname)
                            success += 1
                            break
                        except ModuleNotFoundError as e:
                            install_pip(e.name)
                            retry_count += 1
                            if shortname not in failure:
                                failure.append(shortname)
                            if retry_count > 5:
                                break
                else:
                    os.remove(Path(f"{plugin_path}/{shortname}.py"))
            except Exception as e:
                if shortname not in failure:
                    failure.append(shortname)
                # os.remove(Path(f"{plugin_path}/{shortname}.py"))
                LOGS.info(
                    f"لا يمكنني تحميل {shortname} بسبب الخطأ {e}\nمجلد القاعده {plugin_path}"
                )
    if extfolder:
        if not failure:
            failure.append("None")
        await zedub.tgbot.send_message(
            BOTLOG_CHATID,
            f'Your external repo plugins have imported \n**No of imported plugins :** `{success}`\n**Failed plugins to import :** `{", ".join(failure)}`',
        )


async def verifyLoggerGroup():
    flag = False
    if BOTLOG:
        try:
            entity = await zedub.get_entity(BOTLOG_CHATID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        "- الصلاحيات غير كافيه لأرسال الرسالئل في مجموعه فار ااـ PRIVATE_GROUP_BOT_API_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "لا تمتلك صلاحيات اضافه اعضاء في مجموعة فار الـ PRIVATE_GROUP_BOT_API_ID."
                    )
        except ValueError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID لم يتم العثور عليه . يجب التاكد من ان الفار صحيح."
            )
        except TypeError:
            LOGS.error(
                "PRIVATE_GROUP_BOT_API_ID قيمه هذا الفار غير مدعومه. تأكد من انه صحيح."
            )
        except Exception as e:
            LOGS.error(
                "حدث خطأ عند محاولة التحقق من فار PRIVATE_GROUP_BOT_API_ID.\n" + str(e)
            )
    else:
        try:
            descript = "لا تقم بحذف هذه المجموعة."
            photozed = await zedub.upload_file(file="zlzl/zilzal/logozed.jpg")
            _, groupid = await create_supergroup(
                "مجمـوعـة السجـل زدثـــون",
                zedub,
                Config.TG_BOT_USERNAME,
                descript,
                photozed,
            )
            addgvar("PRIVATE_GROUP_BOT_API_ID", groupid)
            print("تم انشاء مجموعة السجل.")
            flag = True
        except Exception as e:
            print(str(e))

    if PM_LOGGER_GROUP_ID != -100:
        try:
            entity = await zedub.get_entity(PM_LOGGER_GROUP_ID)
            if not isinstance(entity, types.User) and not entity.creator:
                if entity.default_banned_rights.send_messages:
                    LOGS.info(
                        " الصلاحيات غير كافيه لأرسال الرسالئل في مجموعه فار ااـ PM_LOGGER_GROUP_ID."
                    )
                if entity.default_banned_rights.invite_users:
                    LOGS.info(
                        "لا تمتلك صلاحيات اضافه اعضاء في مجموعة فار الـ  PM_LOGGER_GROUP_ID."
                    )
        except ValueError:
            LOGS.error(
                "PM_LOGGER_GROUP_ID لم يتم العثور على قيمه هذا الفار . تاكد من أنه صحيح ."
            )
        except TypeError:
            LOGS.error("PM_LOGGER_GROUP_ID قيمه هذا الفار خطا. تاكد من أنه صحيح.")
        except Exception as e:
            LOGS.error("حدث خطأ اثناء التعرف على فار PM_LOGGER_GROUP_ID.\n" + str(e))
    else:
        try:
            descript = "لا تقم بحذف هذه المجموعة."
            photozed = await zedub.upload_file(file="zlzl/zilzal/logozed.jpg")
            _, groupid = await create_supergroup(
                "مجمـوعـة التخـزين", zedub, Config.TG_BOT_USERNAME, descript, photozed
            )
            addgvar("PM_LOGGER_GROUP_ID", groupid)
            print("تم عمل المجموعة التخزين بنجاح واضافة الفارات اليه.")
            flag = True
            if flag:
                executable = sys.executable.replace(" ", "\\ ")
                args = [executable, "-m", "zlzl"]
                os.execle(executable, *args, os.environ)
                sys.exit(0)
        except Exception as e:
            print(str(e))


async def install_externalrepo(repo, branch, cfolder):
    zedREPO = repo
    rpath = os.path.join(cfolder, "requirements.txt")
    if zedBRANCH := branch:
        repourl = os.path.join(zedREPO, f"tree/{zedBRANCH}")
        gcmd = f"git clone -b {zedBRANCH} {zedREPO} {cfolder}"
        errtext = f"There is no branch with name `{zedBRANCH}`"
    else:
        repourl = zedREPO
        gcmd = f"git clone {zedREPO} {cfolder}"
        errtext = f"The link({zedREPO}) is invalid"
    response = urllib.request.urlopen(repourl)
    if response.code != 200:
        LOGS.error(errtext)
        return await zedub.tgbot.send_message(BOTLOG_CHATID, errtext)
    await runcmd(gcmd)
    if not os.path.exists(cfolder):
        LOGS.error("- حدث خطأ اثناء استدعاء رابط الملفات الاضافية")
        return await zedub.tgbot.send_message(
            BOTLOG_CHATID,
            "**- حدث خطأ**",
        )
    if os.path.exists(rpath):
        await runcmd(f"pip3 install --no-cache-dir -r {rpath}")
    await load_plugins(folder="zlzl", extfolder=cfolder)
