# تم تعديل هذا الملف بأسلوب مايكي لحل مشكلة العمى 🚬😎
import inspect
import re
import sys
import traceback
from pathlib import Path

from .. import CMD_LIST, LOAD_PLUG, SUDO_LIST
from ..Config import Config
from ..core.data import _sudousers_list, blacklist_chats_list
from ..core.events import MessageEdited, NewMessage
from ..core.logger import logging
from ..core.session import zedub
from ..helpers.utils.format import paste_message
from ..helpers.utils.utils import runcmd
from ..sql_helper.globals import gvarstatus

LOGS = logging.getLogger("ZThon_Decorators")

# دالة لتصحيح النمط (Regex) - هنا كان مربط الفرس
def compile_pattern(pattern, handler):
    if pattern.startswith(r"\#"):
        return re.compile(pattern), pattern
    elif pattern.startswith(r"^"):
        return re.compile(pattern), pattern
    
    # تنظيف الهاندلر: إذا كان نقطة، لازم يصير \.
    try:
        if handler == ".":
            zedreg = r"^\."
        elif len(handler) == 1:
            zedreg = "^\\" + handler
        else:
            zedreg = "^" + handler
    except:
        zedreg = r"^\."

    # دمج الهاندلر مع الأمر
    final_regex = zedreg + pattern
    return re.compile(final_regex), handler + pattern

def admin_cmd(pattern=None, command=None, **args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    allow_sudo = args.get("allow_sudo", False)
    
    # سحب النقطة من الكونفج
    hand_ler = Config.COMMAND_HAND_LER or "."

    if pattern is not None:
        try:
            compiled_reg, cmd_text = compile_pattern(pattern, hand_ler)
            args["pattern"] = compiled_reg
            
            # تنظيف اسم الأمر للقائمة
            if command is not None:
                cmd = hand_ler + command
            else:
                cmd = cmd_text.replace("$", "").replace("\\", "").replace("^", "")
                
            # تسجيل في القوائم
            if file_test not in CMD_LIST:
                CMD_LIST[file_test] = []
            CMD_LIST[file_test].append(cmd)
            
        except Exception as e:
            LOGS.error(f"❌ خطأ في تسجيل الأمر {pattern}: {e}")

    args["outgoing"] = True
    if allow_sudo:
        args["from_users"] = list(Config.SUDO_USERS)
        args["incoming"] = True
        del args["allow_sudo"]
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True
        
    if gvarstatus("blacklist_chats") is not None:
        args["blacklist_chats"] = True
        args["chats"] = blacklist_chats_list()
        
    if "allow_edited_updates" in args and args["allow_edited_updates"]:
        del args["allow_edited_updates"]
        
    return NewMessage(**args)


def sudo_cmd(pattern=None, command=None, **args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    allow_sudo = args.get("allow_sudo", False)
    
    hand_ler = Config.SUDO_COMMAND_HAND_LER or "."

    if pattern is not None:
        try:
            compiled_reg, cmd_text = compile_pattern(pattern, hand_ler)
            args["pattern"] = compiled_reg
            
            if command is not None:
                cmd = hand_ler + command
            else:
                cmd = cmd_text.replace("$", "").replace("\\", "").replace("^", "")

            if file_test not in SUDO_LIST:
                SUDO_LIST[file_test] = []
            SUDO_LIST[file_test].append(cmd)
        except Exception as e:
            LOGS.error(f"❌ خطأ في تسجيل أمر السودو {pattern}: {e}")

    args["outgoing"] = True
    if allow_sudo:
        args["from_users"] = list(_sudousers_list())
        args["incoming"] = True
        del args["allow_sudo"]
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True
        
    if gvarstatus("blacklist_chats") is not None:
        args["blacklist_chats"] = True
        args["chats"] = blacklist_chats_list()
        
    if "allow_edited_updates" in args and args["allow_edited_updates"]:
        del args["allow_edited_updates"]
        
    if gvarstatus("sudoenable") is not None:
        return NewMessage(**args)


def errors_handler(func):
    async def wrapper(check):
        try:
            await func(check)
        except BaseException:
            # طباعة الخطأ في اللوجز دائماً
            LOGS.error(f"⚠️ كارثة في تنفيذ الأمر: {str(sys.exc_info()[1])}")
            traceback.print_exc()
            
            if not Config.PRIVATE_GROUP_BOT_API_ID:
                return
            try:
                date = (datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                ftext = f"\n**⚠️ تقرير خطأ:**\n\n**الأمر:** `{str(check.text)}`\n**الخطأ:** `{str(sys.exc_info()[1])}`"
                await check.client.send_message(
                    Config.PRIVATE_GROUP_BOT_API_ID, ftext, link_preview=False
                )
            except:
                pass
    return wrapper


def register(**args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    previous_stack_frame = stack[1]
    file_test = Path(previous_stack_frame.filename)
    file_test = file_test.stem.replace(".py", "")
    pattern = args.get("pattern", None)
    disable_edited = args.get("disable_edited", True)
    allow_sudo = args.get("allow_sudo", False)

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    if "disable_edited" in args:
        del args["disable_edited"]

    reg = re.compile("(.*)")
    if pattern is not None:
        try:
            cmd = re.search(reg, pattern)
            try:
                cmd = cmd.group(1).replace("$", "").replace("\\", "").replace("^", "")
            except:
                pass

            if file_test not in CMD_LIST:
                CMD_LIST[file_test] = []
            CMD_LIST[file_test].append(cmd)
        except:
            pass

    if allow_sudo:
        args["from_users"] = list(Config.SUDO_USERS)
        args["incoming"] = True
        del args["allow_sudo"]
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True

    if gvarstatus("blacklist_chats") is not None:
        args["blacklist_chats"] = True
        args["chats"] = blacklist_chats_list()

    def decorator(func):
        if not disable_edited:
            zedub.add_event_handler(func, MessageEdited(**args))
        zedub.add_event_handler(func, NewMessage(**args))
        
        if file_test not in LOAD_PLUG:
            LOAD_PLUG[file_test] = []
        LOAD_PLUG[file_test].append(func)
        return func

    return decorator

def command(**args):
    return register(**args)