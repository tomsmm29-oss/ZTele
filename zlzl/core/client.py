import asyncio
import datetime
import inspect
import re
import os
import sys
import traceback
from telethon import events

@events.register(events.NewMessage(outgoing=True))
async def normalize_prefix(event):
    if not event.raw_text:
        return

    if event.raw_text.startswith(("،", "!")):
        try:
            event.message.message = "." + event.raw_text[1:]
        except Exception:
            pass
from pathlib import Path
from typing import Dict, List, Union

from telethon import TelegramClient, events
from telethon.errors import (
    AlreadyInConversationError,
    BotInlineDisabledError,
    BotResponseTimeoutError,
    ChatSendInlineForbiddenError,
    ChatSendMediaForbiddenError,
    ChatSendStickersForbiddenError,
    FloodWaitError,
    MessageIdInvalidError,
    MessageNotModifiedError,
)

from ..Config import Config
from ..helpers.utils.events import checking
from ..helpers.utils.format import paste_message
from ..helpers.utils.utils import runcmd
from ..sql_helper.globals import gvarstatus
from . import BOT_INFO, CMD_INFO, GRP_INFO, LOADED_CMDS, PLG_INFO
from .cmdinfo import _format_about
from .data import _sudousers_list, blacklist_chats_list, sudo_enabled_cmds
from .events import *
from .fasttelethon import download_file, upload_file
from .logger import logging
from .managers import edit_delete
from .pluginManager import get_message_link, restart_script

LOGS = logging.getLogger(__name__)
ZDEV = (5176749470, 1895219306, 925972505, 5280339206, 5426390871, 8241311871, 6550930943)

class REGEX:
    def __init__(self):
        self.regex = ""
        self.regex1 = ""
        self.regex2 = ""


REGEX_ = REGEX()
sudo_enabledcmds = sudo_enabled_cmds()


class ZedUserBotClient(TelegramClient):
    def zed_cmd(
        self: TelegramClient,
        pattern: str or tuple = None,
        info: Union[str, Dict[str, Union[str, List[str], Dict[str, str]]]]
        or tuple = None,
        groups_only: bool = False,
        private_only: bool = False,
        allow_sudo: bool = True,
        edited: bool = True,
        forword=False,
        disable_errors: bool = False,
        command: str or tuple = None,
        **kwargs,
    ) -> callable:
        kwargs["func"] = kwargs.get("func", lambda e: e.via_bot_id is None)
        kwargs.setdefault("forwards", forword)

        if gvarstatus("blacklist_chats") is not None:
            kwargs["blacklist_chats"] = True
            kwargs["chats"] = blacklist_chats_list()

        stack = inspect.stack()
        previous_stack_frame = stack[1]
        file_test = Path(previous_stack_frame.filename)
        file_test = file_test.stem.replace(".py", "")

        if command is not None:
            command = list(command)
            if not command[1] in BOT_INFO:
                BOT_INFO.append(command[1])
            try:
                if file_test not in GRP_INFO[command[1]]:
                    GRP_INFO[command[1]].append(file_test)
            except BaseException:
                GRP_INFO.update({command[1]: [file_test]})
            try:
                if command[0] not in PLG_INFO[file_test]:
                    PLG_INFO[file_test].append(command[0])
            except BaseException:
                PLG_INFO.update({file_test: [command[0]]})
            if not command[0] in CMD_INFO:
                CMD_INFO[command[0]] = [_format_about(info)]

        # ================= PREFIX SUPPORT (. ، !) =================
        if pattern is not None:
            if (
                pattern.startswith(r"\#")
                or not pattern.startswith(r"\#")
                and pattern.startswith(r"^")
            ):
                REGEX_.regex1 = REGEX_.regex2 = re.compile(pattern)
            else:
                # دعم النقطة + الفاصلة العربية + !
                prefix_regex = r"[\.،!]"
                REGEX_.regex1 = re.compile(prefix_regex + pattern)
                REGEX_.regex2 = re.compile(prefix_regex + pattern)
        # ==========================================================

        def decorator(func):
            async def wrapper(check):
                if groups_only and not check.is_group:
                    return await edit_delete(
                        check, "**⪼ عذرا هذا الامر يستخدم في المجموعات فقط 𓆰،**", 10
                    )
                if private_only and not check.is_private:
                    return await edit_delete(
                        check, "**⪼ هذا الامر يستخدم فقط في الدردشات الخاصه 𓆰،**", 10
                    )
                try:
                    await func(check)
                except events.StopPropagation as e:
                    raise events.StopPropagation from e
                except KeyboardInterrupt:
                    pass
                except MessageNotModifiedError:
                    LOGS.error("كانت الرسالة مماثلة للرسالة السابقة")
                except MessageIdInvalidError:
                    LOGS.error("الرسالة تم حذفها او لم يتم العثور عليها")
                except BotInlineDisabledError:
                    await edit_delete(check, "**⌔∮ يجب عليك تفعيل وضع الانلاين اولاً**", 10)
                except ChatSendStickersForbiddenError:
                    await edit_delete(
                        check, "**- هـذه المجمـوعـه لا تسمح بارسـال الملصقـات هنا**", 10
                    )
                except BotResponseTimeoutError:
                    await edit_delete(
                        check, "⪼ استخدم الميزه بعد وقت قليل لا يمكن الاستجابه الان", 10
                    )
                except ChatSendMediaForbiddenError:
                    await edit_delete(check, "**⪼ هذه المجموعه تمنع ارسال الميديا هنا 𓆰،**", 10)
                except AlreadyInConversationError:
                    await edit_delete(
                        check,
                        "**- المحادثه تجري بالفعل مع الدردشة المحددة .. حاول مرة أخرى بعد قليل**",
                        10,
                    )
                except ChatSendInlineForbiddenError:
                    await edit_delete(
                        check, "**- عـذراً .. الانـلايـن فـي هـذه المجمـوعـة مغـلق**", 10
                    )
                except FloodWaitError as e:
                    LOGS.error(
                        f"ايقاف مؤقت بسبب التكرار {e.seconds} حدث. انتظر {e.seconds} ثانيه و حاول مجددا"
                    )
                    await check.delete()
                    await asyncio.sleep(e.seconds + 5)
                except BaseException as e:
                    LOGS.exception(e)
                    if not disable_errors:
                        if check.sender_id not in ZDEV:
                            return
                        if Config.PRIVATE_GROUP_BOT_API_ID == 0:
                            return
                        date = (datetime.datetime.now()).strftime("%m/%d/%Y, %H:%M:%S")
                        ftext = f"\n-------- تقرير خطأ زدثون --------\n"
                        ftext += f"- التاريخ : {date}\n"
                        ftext += f"- ايدي الكروب : {check.chat_id}\n"
                        ftext += f"- ايدي الشخص : {check.sender_id}\n"
                        ftext += f"- نص الرسالة : {check.text}\n\n"
                        ftext += traceback.format_exc()
                        pastelink = await paste_message(
                            ftext, pastetype="s", markdown=False
                        )
                        await check.client.send_message(
                            Config.PRIVATE_GROUP_BOT_API_ID,
                            f"**✘ تقرير اشعار زدثون ✘**\n\n{pastelink}",
                            link_preview=False,
                        )

            from .session import zedub

            if pattern is not None:
                if edited:
                    zedub.add_event_handler(
                        wrapper,
                        MessageEdited(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                    )
                zedub.add_event_handler(
                    wrapper,
                    NewMessage(pattern=REGEX_.regex1, outgoing=True, **kwargs),
                )

                if allow_sudo and gvarstatus("sudoenable") is not None:
                    if edited:
                        zedub.add_event_handler(
                            wrapper,
                            MessageEdited(
                                pattern=REGEX_.regex2,
                                from_users=_sudousers_list(),
                                **kwargs,
                            ),
                        )
                    zedub.add_event_handler(
                        wrapper,
                        NewMessage(
                            pattern=REGEX_.regex2,
                            from_users=_sudousers_list(),
                            **kwargs,
                        ),
                    )
            else:
                if edited:
                    zedub.add_event_handler(wrapper, events.MessageEdited(**kwargs))
                zedub.add_event_handler(wrapper, events.NewMessage(**kwargs))

            return wrapper

        return decorator