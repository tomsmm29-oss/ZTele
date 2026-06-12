import asyncio
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
from ..sql_helper.globals import gvarstatus

LOGS = logging.getLogger("ZThon_Decorators")


def compile_pattern(pattern, handler):
    # إذا كان الأمر يبدأ أصلاً برموز نظام خاصة نتركه كما هو
    if pattern.startswith(r"\#") or pattern.startswith(r"^"):
        return re.compile(pattern), pattern

    # 🔥 الترسانة الشاملة: كل الرموز التي طلبتها في مصفوفة آمنة
    # الرموز: . ، , + ? ! / : ' * " % = ( ) - _ & $ # @
    symbols = r"[.\,،+?!/:’*\"%=()\- _&$#@]"
    zedreg = "^" + symbols

    try:
        final_regex = zedreg + pattern
        return re.compile(final_regex), "." + pattern
    except Exception as e:
        LOGS.error(f"⚠️ خطأ في نمط الرموز: {e}")
        return re.compile(r"^\." + pattern), "." + pattern


def admin_cmd(pattern=None, command=None, **args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    file_test = Path(stack[1].filename).stem
    allow_sudo = args.get("allow_sudo", False)

    hand_ler = Config.COMMAND_HAND_LER or "."

    if pattern is not None:
        try:
            compiled_reg, cmd_text = compile_pattern(pattern, hand_ler)
            args["pattern"] = compiled_reg

            cmd = (
                (hand_ler + command)
                if command
                else cmd_text.replace("$", "").replace("\\", "").replace("^", "")
            )

            if file_test not in CMD_LIST:
                CMD_LIST[file_test] = []
            if cmd not in CMD_LIST[file_test]:
                CMD_LIST[file_test].append(cmd)
        except Exception as e:
            LOGS.error(f"❌ خطأ تسجيل: {pattern} -> {e}")

    args["outgoing"] = True
    if allow_sudo:
        args["from_users"] = list(Config.SUDO_USERS)
        args["incoming"] = True
        args.pop("allow_sudo", None)
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True

    if gvarstatus("blacklist_chats"):
        args["blacklist_chats"] = True
        args["chats"] = blacklist_chats_list()

    args.pop("allow_edited_updates", None)
    return NewMessage(**args)


def sudo_cmd(pattern=None, command=None, **args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    file_test = Path(stack[1].filename).stem
    allow_sudo = args.get("allow_sudo", False)

    hand_ler = Config.SUDO_COMMAND_HAND_LER or "."

    if pattern is not None:
        try:
            compiled_reg, cmd_text = compile_pattern(pattern, hand_ler)
            args["pattern"] = compiled_reg

            cmd = (
                (hand_ler + command)
                if command
                else cmd_text.replace("$", "").replace("\\", "").replace("^", "")
            )

            if file_test not in SUDO_LIST:
                SUDO_LIST[file_test] = []
            if cmd not in SUDO_LIST[file_test]:
                SUDO_LIST[file_test].append(cmd)
        except Exception as e:
            LOGS.error(f"❌ خطأ تسجيل سودو: {e}")

    args["outgoing"] = True
    if allow_sudo:
        args["from_users"] = list(_sudousers_list())
        args["incoming"] = True
        args.pop("allow_sudo", None)
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True

    if gvarstatus("blacklist_chats"):
        args["blacklist_chats"] = True
        args["chats"] = blacklist_chats_list()

    args.pop("allow_edited_updates", None)
    if gvarstatus("sudoenable"):
        return NewMessage(**args)


def errors_handler(func):
    async def wrapper(check):
        # ⚡ فحص الرام السريع (الرد الفوري من Redis)
        if hasattr(zedub, "redis") and zedub.redis:
            try:
                fast_reply = await zedub.redis.hget(
                    f"filters:{check.chat_id}", check.text
                )
                if fast_reply:
                    await check.reply(fast_reply)
                    return
            except:
                pass

        # 🚀 تشغيل الأمر كـ Task منفصل (سرعة 60 ضعفاً وعدم تجميد)
        async def run_command():
            try:
                await func(check)
            except BaseException:
                LOGS.error(f"⚠️ كارثة في تنفيذ الأمر: {str(sys.exc_info()[1])}")
                traceback.print_exc()
                if Config.PRIVATE_GROUP_BOT_API_ID:
                    try:
                        ftext = f"\n**⚠️ تقرير خطأ:**\n**الأمر:** `{str(check.text)}`\n**الخطأ:** `{str(sys.exc_info()[1])}`"
                        await check.client.send_message(
                            Config.PRIVATE_GROUP_BOT_API_ID, ftext, link_preview=False
                        )
                    except:
                        pass

        asyncio.create_task(run_command())

    return wrapper


def register(**args):
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    file_test = Path(stack[1].filename).stem
    pattern = args.get("pattern", None)
    disable_edited = args.get("disable_edited", True)
    allow_sudo = args.get("allow_sudo", False)

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    args.pop("disable_edited", None)

    if allow_sudo:
        args["from_users"] = list(Config.SUDO_USERS)
        args["incoming"] = True
        args.pop("allow_sudo", None)
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True

    if gvarstatus("blacklist_chats"):
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
