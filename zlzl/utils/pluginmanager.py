import contextlib
import importlib
import sys
from pathlib import Path
from zlzl import CMD_HELP, LOAD_PLUG
from ..Config import Config
from ..core import LOADED_CMDS, PLG_INFO
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..core.session import zedub
from ..helpers.tools import media_type
# استيراد reply_id الحقيقي
from ..helpers.utils import _zedtools, _zedutils, _format, install_pip, reply_id
from .decorators import admin_cmd, sudo_cmd

LOGS = logging.getLogger("ZThon")

def load_module(shortname, plugin_path=None):
    if shortname.startswith("__"):
        pass
    elif shortname.endswith("_"):
        path = Path(f"zlzl/plugins/{shortname}.py")
        checkplugins(path)
        name = "zlzl.plugins.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        LOGS.info(f"Successfully imported {shortname}")
    else:
        if plugin_path is None:
            path = Path(f"zlzl/plugins/{shortname}.py")
            name = f"zlzl.plugins.{shortname}"
        else:
            path = Path((f"{plugin_path}/{shortname}.py"))
            name = f"{plugin_path}/{shortname}".replace("/", ".")
        
        checkplugins(path)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        
        # =================================================
        # 💉 الحقن الذكي (Smart Injection) 💉
        # =================================================
        mod.bot = zedub
        mod.LOGS = LOGS
        mod.Config = Config
        mod._format = _format
        mod.tgbot = zedub.tgbot
        mod.sudo_cmd = sudo_cmd
        mod.CMD_HELP = CMD_HELP
        mod.admin_cmd = admin_cmd
        mod._zedutils = _zedutils
        mod._zedtools = _zedtools
        mod.install_pip = install_pip
        mod.parse_pre = _format.parse_pre
        mod.edit_or_reply = edit_or_reply
        mod.logger = logging.getLogger(shortname)
        mod.borg = zedub

        # هنا السحر: نعطيه الدالة الحقيقية عشان الأوامر تشتغل
        mod.reply_id = reply_id 
        mod.media_type = media_type
        mod.edit_delete = edit_delete
        
        # =================================================

        try:
            spec.loader.exec_module(mod)
            sys.modules[f"zlzl.plugins.{shortname}"] = mod
            LOGS.info(f"✅ Successfully imported {shortname}")
        except TypeError as e:
            # إذا الملف حاول يجمع (+=) بنصيده هنا
            if "unsupported operand type(s) for +=" in str(e):
                LOGS.warning(f"⚠️ الملف {shortname} قديم ويسبب مشاكل (+). تم تخطيه لسلامة البوت.")
            else:
                LOGS.error(f"❌ Failed to load {shortname}: {e}")
        except Exception as e:
            LOGS.error(f"❌ Failed to load {shortname}: {e}")


def lload_module(shortname, plugin_path=None):
    if shortname.startswith("__"):
        pass
    elif shortname.endswith("_"):
        path = Path(f"zlzl/plugins/{shortname}.py")
        checkplugins(path)
        name = "zlzl.plugins.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print("Successfully imported library")
    else:
        if plugin_path is None:
            path = Path(f"zlzl/plugins/{shortname}.py")
            name = f"zlzl.plugins.{shortname}"
        else:
            path = Path((f"{plugin_path}/{shortname}.py"))
            name = f"{plugin_path}/{shortname}".replace("/", ".")
        
        checkplugins(path)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        
        mod.bot = zedub
        mod.LOGS = LOGS
        mod.Config = Config
        mod._format = _format
        mod.tgbot = zedub.tgbot
        mod.sudo_cmd = sudo_cmd
        mod.CMD_HELP = CMD_HELP
        mod.admin_cmd = admin_cmd
        mod._zedutils = _zedutils
        mod._zedtools = _zedtools
        mod.install_pip = install_pip
        mod.parse_pre = _format.parse_pre
        mod.edit_or_reply = edit_or_reply
        mod.logger = logging.getLogger(shortname)
        mod.borg = zedub
        
        # الحقن الذكي هنا أيضاً
        mod.reply_id = reply_id
        mod.media_type = media_type
        mod.edit_delete = edit_delete

        try:
            spec.loader.exec_module(mod)
            sys.modules[f"zlzl.plugins.{shortname}"] = mod
            print("Successfully imported library")
        except Exception as e:
             print(f"Failed to load {shortname}: {e}")


def remove_plugin(shortname):
    try:
        cmd = []
        if shortname in PLG_INFO:
            cmd += PLG_INFO[shortname]
        else:
            cmd = [shortname]
        for cmdname in cmd:
            if cmdname in LOADED_CMDS:
                for i in LOADED_CMDS[cmdname]:
                    zedub.remove_event_handler(i)
                del LOADED_CMDS[cmdname]
        return True
    except Exception as e:
        LOGS.error(e)
    with contextlib.suppress(BaseException):
        for i in LOAD_PLUG[shortname]:
            zedub.remove_event_handler(i)
        del LOAD_PLUG[shortname]
    try:
        name = f"zlzl.plugins.{shortname}"
        for i in reversed(range(len(zedub._event_builders))):
            ev, cb = zedub._event_builders[i]
            if cb.__module__ == name:
                del zedub._event_builders[i]
    except BaseException as exc:
        raise ValueError from exc


def checkplugins(filename):
    with open(filename, "r") as f:
        filedata = f.read()
    filedata = filedata.replace("sendmessage", "send_message")
    filedata = filedata.replace("sendfile", "send_file")
    filedata = filedata.replace("editmessage", "edit_message")
    with open(filename, "w") as f:
        f.write(filedata)