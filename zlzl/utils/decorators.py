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


    def compile_pattern(pattern, handler):
    # إذا كان الأمر يبدأ أصلاً برموز نظام خاصة نتركه كما هو
    if pattern.startswith(r"\#") or pattern.startswith(r"^"):
        return re.compile(pattern), pattern

    # 🔥 الترسانة الشاملة: وضعنا كل الرموز اللي طلبتها داخل [ ]
    # لاحظ وضعنا الـ - في البداية والـ \ قبل الـ . والـ * لضمان الأمان التام
    # الرموز المدعومة: . ، , + ? ! / : ' * " % = ( ) - _ & $ # @
    symbols = r"[.\,،+?!/:’*\"%=()\- _&$#@]"
    
    # البادئة تعني: ابدأ البحث من بداية الرسالة ^ عن أحد هذه الرموز
    zedreg = "^" + symbols

    try:
        # دمج البادئة مع نص الأمر
        final_regex = zedreg + pattern
        return re.compile(final_regex), "." + pattern
    except Exception as e:
        # في حال حدوث خطأ نادر، نعود للنقطة الافتراضية كأمان
        LOGS.error(f"⚠️ خطأ في نمط الرموز: {e}")
        return re.compile(r"^\." + pattern), "." + pattern
    


def admin_cmd(pattern=None, command=None, **args):
    # تحسين الفانكشن الأساسي ليكون أسرع في التحقق
    args["func"] = lambda e: e.via_bot_id is None
    stack = inspect.stack()
    # جلب اسم الملف بسرعة بدون تعقيد
    file_test = Path(stack[1].filename).stem
    allow_sudo = args.get("allow_sudo", False)

    # سحب النقطة (الهاندلر)
    hand_ler = Config.COMMAND_HAND_LER or "."

    if pattern is not None:
        try:
            compiled_reg, cmd_text = compile_pattern(pattern, hand_ler)
            args["pattern"] = compiled_reg

            # تنظيف وتسجيل الأمر في القائمة بضغطة واحدة
            cmd = (hand_ler + command) if command else cmd_text.replace("$", "").replace("\\", "").replace("^", "")
            
            if file_test not in CMD_LIST:
                CMD_LIST[file_test] = []
            if cmd not in CMD_LIST[file_test]:
                CMD_LIST[file_test].append(cmd)

        except Exception as e:
            LOGS.error(f"❌ خطأ تسجيل: {pattern} -> {e}")

    # إعدادات الإرسال والاستقبال (تحسين الأداء)
    args["outgoing"] = True
    if allow_sudo:
        args["from_users"] = list(Config.SUDO_USERS)
        args["incoming"] = True
        args.pop("allow_sudo", None)
    elif "incoming" in args and not args["incoming"]:
        args["outgoing"] = True

    # فحص القائمة السوداء بسرعة (Caching)
    if gvarstatus("blacklist_chats"):
        args["blacklist_chats"] = True
        args["chats"] = blacklist_chats_list()

    # إزالة التحديثات غير الضرورية لتقليل الحمل
    args.pop("allow_edited_updates", None)

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
        # ⚡ فحص الرام السريع (الرد الفوري)
        if hasattr(zedub, 'redis') and zedub.redis:
            # هل الكلمة اللي وصلت هي "فلتر" مسجل في الرام؟
            fast_reply = await zedub.redis.hget(f"filters:{check.chat_id}", check.text)
            if fast_reply:
                await check.reply(fast_reply)
                return # انتهى! رد بلمح البصر بدون ما يفتح أي ملف

        # إذا لم يكن فلتر، يكمل للأوامر العادية في مسار منفصل
        asyncio.create_task(func(check))
        
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