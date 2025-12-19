import os
import asyncio
import random
import re
from datetime import datetime

from telethon import functions
from telethon.utils import get_display_name

# 👇 استدعاء السورس (بدل zthon)
from . import zedub
from .core.logger import logging

# 👇 استدعاء مكتبة الباشا (Pyrogram) للزراير
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format, get_user_from_event, reply_id
from ..sql_helper import global_collectionjson as sql
from ..sql_helper import global_list as sqllist
from ..sql_helper import pmpermit_sql
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG_CHATID, mention 

plugin_category = "البوت"
LOGS = logging.getLogger(__name__)
cmdhd = Config.COMMAND_HAND_LER

# =========================
# 🏗 إعداد الحارس المستقل (Pyrogram Worker)
# =========================
api_id = zedub.api_id
api_hash = zedub.api_hash
bot_token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("BOT_TOKEN")

# جلسة خاصة للحماية (عشان ميتعارضش مع القائمة)
pm_worker = Client(
    name="zthon_pm_guard",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    in_memory=True
)

# تشغيل الحارس في الخلفية
async def start_pm_worker():
    if bot_token:
        try:
            await pm_worker.start()
            print("🚬 Mikey: تم تشغيل نظام الحماية (PM Guard) بنجاح!")
        except Exception as e:
            print(f"🚬 Mikey Error (PM Guard): {e}")

zedub.loop.create_task(start_pm_worker())

# =========================
# ⚙️ إعدادات التحذيرات
# =========================
# 3 تحذيرات والرابعة بلوك
MAX_FLOOD = 4 

class PMPERMIT:
    def __init__(self):
        self.TEMPAPPROVED = []

PMPERMIT_ = PMPERMIT()

# =========================
# 🎮 هندسة زراير الحماية (Pyrogram)
# =========================
def get_pm_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⤶ لـ إسـتـفـسـار مـعـيـن", callback_data=f"to_enquire|{user_id}")],
        [InlineKeyboardButton("⤶ لـ طـلـب مـعـيـن", callback_data=f"to_request|{user_id}")],
        [InlineKeyboardButton("⤶ لـ الـدردشــه فـقـط", callback_data=f"to_chat|{user_id}")],
        [InlineKeyboardButton("⤶ لـ إزعـاجـي فـقـط", callback_data=f"to_spam|{user_id}")],
    ])

# =========================
# 🔥 دوال التعامل مع الرسائل (The Logic)
# =========================

async def do_pm_permit_action(event, chat):
    reply_to_id = await reply_id(event)
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError:
        PM_WARNS = {}
    try:
        PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
    except AttributeError:
        PMMESSAGE_CACHE = {}

    me = await event.client.get_me()
    mention = f"[{chat.first_name}](tg://user?id={chat.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"

    # تهيئة العداد
    if str(chat.id) not in PM_WARNS:
        PM_WARNS[str(chat.id)] = 0

    warns = PM_WARNS[str(chat.id)] + 1
    remwarns = MAX_FLOOD - warns

    # ☠️ مرحلة الحظر (Game Over)
    if warns >= MAX_FLOOD:
        # مسح رسائل التحذير القديمة
        try:
            if str(chat.id) in PMMESSAGE_CACHE:
                await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
                del PMMESSAGE_CACHE[str(chat.id)]
        except: pass

        # رسالة البلوك النهائية الفخمة
        USER_BOT_WARN_ZERO = f"**⤶ لقـد حذرتـڪ مـسـبـقـاً مـن الـتـڪـرار 📵** \n**⤶ تـم حـظـرڪ تلقـائيـاً .. الان لا يـمـڪـنـڪ ازعـاجـي🔕**\n\n**⤶ تحيـاتـي** {my_mention}  🫡**"

        await event.reply(USER_BOT_WARN_ZERO)
        await event.client(functions.contacts.BlockRequest(chat.id))

        # اللوج
        the_message = f"#حمـايـة_الخـاص\n** ⎉╎المستخـدم** [{get_display_name(chat)}](tg://user?id={chat.id}) .\n** ⎉╎تم حظـره .. تلقائيـاً**\n** ⎉╎عـدد رسـائله :** {warns}"

        del PM_WARNS[str(chat.id)]
        sql.del_collection("pmwarns")
        sql.add_collection("pmwarns", PM_WARNS, {})
        try:
            return await event.client.send_message(BOTLOG_CHATID, the_message)
        except: return

    # ⚠️ مرحلة التحذير (The Warning)

    # النص الافتراضي الفخم
    USER_BOT_NO_WARN = f"""ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 **- الـرد التلقـائي 〽️**
**•─────────────────•**

❞ **مرحبـاً**  {mention} ❝

**⤶ قد اكـون مشغـول او غيـر موجـود حـاليـاً ؟!**
**⤶ ❨ لديـك** {warns} **مـن** {MAX_FLOOD} **تحذيـرات ⚠️❩**
**⤶ لا تقـم بـ إزعاجـي والا سـوف يتم حظـرك تلقـائياً . . .**

**⤶ فقط قل سبب مجيئك وانتظـر الـرد ⏳**"""

    # زيادة العداد
    PM_WARNS[str(chat.id)] += 1
    sql.del_collection("pmwarns")
    sql.add_collection("pmwarns", PM_WARNS, {})

    # إرسال الرسالة عبر Pyrogram (عشان الزراير)
    try:
        # مسح الرسالة القديمة لو موجودة
        if str(chat.id) in PMMESSAGE_CACHE:
            await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
            del PMMESSAGE_CACHE[str(chat.id)]
    except: pass

    try:
        # استخدام الحارس لارسال الرسالة بالزراير
        msg = await pm_worker.send_message(
            chat.id,
            USER_BOT_NO_WARN,
            reply_markup=get_pm_keyboard(chat.id)
        )
        # حفظ ايدي الرسالة عشان نمسحها بعدين (بنحفظها كـ integer)
        PMMESSAGE_CACHE[str(chat.id)] = msg.id
    except Exception as e:
        # لو فشل (مثلا البوت مش ادمن او محظور)، ابعت بالتليثون عادي
        LOGS.error(f"PM Guard Error: {e}")
        msg = await event.reply(USER_BOT_NO_WARN)
        PMMESSAGE_CACHE[str(chat.id)] = msg.id

    sql.del_collection("pmmessagecache")
    sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})


# =========================
# 🔥 معالجات الخيارات (Pyrogram Callbacks)
# =========================

@pm_worker.on_callback_query()
async def pm_guard_callbacks(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id

    # التأكد من ان الضغط جاي من صاحب الشات (security)
    try:
        target_id = int(data.split("|")[1])
        if user_id != target_id:
            await callback_query.answer("⚠️ هذه الأزرار ليست لك!", show_alert=True)
            return
    except: pass

    # 1. خيار الاستفسار
    if data.startswith("to_enquire"):
        text = "**⤶ حـسـنـاً عـزيـزي ، تـم أرسـال طـلـبـڪ بـنـجـاح 📨 . لا تـقـم بـ إخـتـيـار خـيـار آخــر .**\n**⤶ سيـتـم الـرد عـلـيـڪ عـنـد تـفـرغ الـمـالـڪ .🧸🤍**"
        sqllist.add_to_list("pmenquire", user_id)
        # تصفير العداد مؤقتا لانه استجاب
        reset_warns(user_id)
        await callback_query.edit_message_text(text)

    # 2. خيار الطلب
    elif data.startswith("to_request"):
        text = "**⤶ حـسـنـاً عـزيـزي .. قـمـت بـإبـلاغ مـالـڪ الـحـسـاب بـطلبـڪ**\n**⤶ عـنـدمـا يـڪـون مـالـڪ الـحـسـاب مـتـاحـاً سـوف يـقـوم بـالـرد عـلـيـڪ .. الرجـاء الإنـتـظـار ⏳**\n**⤶ لا تـڪـرر الـرسـائـل حـاليـاً لـ تـجـنـب الـحـظـر 🚷**"
        sqllist.add_to_list("pmrequest", user_id)
        reset_warns(user_id)
        await callback_query.edit_message_text(text)

    # 3. خيار الدردشة
    elif data.startswith("to_chat"):
        text = "**⤶ بـالـطـبـع عـزيـزي يـمـكـنـك الـتـحـدث مـع مـالـك الـحـسـاب لـكـن لـيـس الان 🤷🏻‍♂\n\n⤶ نـسـتـطـيـع الـتـكـلـم فـي وقـت آخـر حـالـيـاً أنـا مـشـغـول قـلـيـلاً  - عـنـد تـفـرغـي سـأكـلـمـك بالتـأكيــد .😇🤍**"
        sqllist.add_to_list("pmchat", user_id)
        reset_warns(user_id)
        await callback_query.edit_message_text(text)

    # 4. خيار الإزعاج (البلوك المباشر)
    elif data.startswith("to_spam"):
        text = "**⤶ لسـت متفـرغـاً لـ تـراهـاتـك.\n\n⤶ وهـذا هـو تحذيرك الأخيـر إذا قـمـت بإرسـال رسـالة أخـرى فـ سيتـم حـظـرك تلقـائـيًـا 🚷**"
        sqllist.add_to_list("pmspam", user_id)
        # هنا بنحط العداد على الحافة عشان الضربة الجاية بلوك
        set_warns_critical(user_id)
        await callback_query.edit_message_text(text)


# =========================
# 🛠 دوال مساعدة لادارة العداد
# =========================
def reset_warns(user_id):
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    if str(user_id) in PM_WARNS:
        del PM_WARNS[str(user_id)]
        sql.del_collection("pmwarns")
        sql.add_collection("pmwarns", PM_WARNS, {})

def set_warns_critical(user_id):
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    # بنخليه فاضله غلطة واحدة
    PM_WARNS[str(user_id)] = MAX_FLOOD - 1
    sql.del_collection("pmwarns")
    sql.add_collection("pmwarns", PM_WARNS, {})


# =========================
# 🔥 دوال العقاب (للي بيخالف بعد الاختيار)
# =========================

async def punish_user(event, chat, reason_text, list_name):
    # دالة موحدة للعقاب عشان منكررش الكود
    USER_BOT_WARN_ZERO = "**⤶ لقـد حـذرتــڪ مـسـبـقـاً مـن تـڪـرار الـرسـائـل ...📵**\n**⤶ تـم حـظـرڪ تلقـائيـاً 🚷** \n**⤶ الـى ان يـاتـي مـالـڪ الـحـسـاب 😕**"
    await event.reply(USER_BOT_WARN_ZERO)
    await event.client(functions.contacts.BlockRequest(chat.id))

    the_message = f"#حمـايـة_الخـاص\n** ⎉╎المستخـدم** [{get_display_name(chat)}](tg://user?id={chat.id}) .\n** ⎉╎تم حظـره .. تلقائيـاً**\n** ⎉╎السـبب:** {reason_text}"

    sqllist.rm_from_list(list_name, chat.id)
    try:
        if BOTLOG_CHATID:
            await event.client.send_message(BOTLOG_CHATID, the_message)
    except: pass


async def do_pm_enquire_action(event, chat):
    await punish_user(event, chat, "اختار الاستفسار واستمر بالتكرار المزعج", "pmenquire")

async def do_pm_request_action(event, chat):
    await punish_user(event, chat, "اختار الطلب واستمر بالتكرار المزعج", "pmrequest")

async def do_pm_chat_action(event, chat):
    await punish_user(event, chat, "اختار الدردشة واستمر بالتكرار المزعج", "pmchat")

async def do_pm_spam_action(event, chat):
    await punish_user(event, chat, "اختار الإزعاج وتم تأديبه بنجاح", "pmspam")

async def do_pm_options_action(event, chat):
    # دي لو لسه مختارش حاجة وقعد يرغي
    await punish_user(event, chat, "لم يختر أي خيار واستمر بالتكرار", "pmoptions")


# =========================
# 📬 مراقب الرسائل (The Listener)
# =========================

@zedub.zed_cmd(incoming=True, func=lambda e: e.is_private, edited=False, forword=None)
async def on_new_private_message(event):
    if gvarstatus("pmpermit") is None:
        return

    chat = await event.get_chat()

    # قائمة المطورين (تخطي الحماية)
    zel_dev = [8241311871, 5176749470, 5426390871, 925972505, 1895219306, 2095357462, 5280339206]
    if event.chat_id in zel_dev:
        return

    if chat.bot or chat.verified:
        return
    if pmpermit_sql.is_approved(chat.id):
        return

    # التحقق من القوائم الخاصة (لو الشخص اختار قبل كده وبيبعت تاني)
    if str(chat.id) in sqllist.get_collection_list("pmspam"):
        return await do_pm_spam_action(event, chat)
    if str(chat.id) in sqllist.get_collection_list("pmchat"):
        return await do_pm_chat_action(event, chat)
    if str(chat.id) in sqllist.get_collection_list("pmrequest"):
        return await do_pm_request_action(event, chat)
    if str(chat.id) in sqllist.get_collection_list("pmenquire"):
        return await do_pm_enquire_action(event, chat)

    # لو الشخص ده جديد (أو لسه مختارش)
    await do_pm_permit_action(event, chat)


# =========================
# 📤 أوامر الرد اليدوي (Outgoing)
# =========================
@zedub.zed_cmd(outgoing=True, func=lambda e: e.is_private, edited=False, forword=None)
async def you_dm_other(event):
    if gvarstatus("pmpermit") is None:
        return
    chat = await event.get_chat()
    if chat.bot or chat.verified:
        return
    if event.text and event.text.startswith(cmdhd):
        return

    # لو أنا رديت عليه، يبقى وافقت عليه
    start_date = str(datetime.now().strftime("%B %d, %Y"))
    if not pmpermit_sql.is_approved(chat.id):
        pmpermit_sql.approve(chat.id, get_display_name(chat), start_date, chat.username, "موافقة تلقائية (أنا رديت)")
        try:
            # مسح كاش الرسائل
            PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
            if str(chat.id) in PMMESSAGE_CACHE:
                try:
                    # بنحاول نمسحها بالتليثون، لو معرفش (عشان هي بتاعة بايروجرام) بنسيبها
                    await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
                except: pass
                del PMMESSAGE_CACHE[str(chat.id)]
            sql.del_collection("pmmessagecache")
            sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})
        except: pass


# =========================
# ⚙️ أوامر التحكم (تفعيل/تعطيل/سماح/رفض)
# =========================

@zedub.zed_cmd(pattern="الحمايه (تفعيل|تعطيل)$")
async def pmpermit_on(event):
    input_str = event.pattern_match.group(1)
    if input_str == "تفعيل":
        if gvarstatus("pmpermit") is None:
            addgvar("pmpermit", "true")
            await edit_delete(event, "**⎉╎تـم تفعيـل امـر حمايـه الخـاص .. بنجـاح 🔕☑️...**")
        else:
            await edit_delete(event, "** ⎉╎ امـر حمايـه الخـاص بالفعـل .. مُفعـل  🔐✅**")
    else:
        if gvarstatus("pmpermit") is not None:
            delgvar("pmpermit")
            await edit_delete(event, "**⎉╎تـم تعطيـل أمـر حمايـة الخـاص .. بنجـاح 🔔☑️...**")
        else:
            await edit_delete(event, "** ⎉╎ امـر حمايـه الخـاص بالفعـل .. مُعطـل 🔓✅**")

@zedub.zed_cmd(pattern="(قبول|سماح)(?:\s|$)([\s\S]*)")
async def approve_p_m(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, f"** ⎉╎يـجب تفعيـل امـر الحـمايـه اولاً **")

    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(2)
    else:
        user, reason = await get_user_from_event(event, secondgroup=True)
        if not user: return

    if not reason: reason = "**⎉╎لـم يـذكـر 🤷🏻‍♂**"

    if not pmpermit_sql.is_approved(user.id):
        pmpermit_sql.approve(user.id, get_display_name(user), str(datetime.now().strftime("%B %d, %Y")), user.username, reason)

        # تنظيف القوائم والتحذيرات
        try:
            for lst in ["pmspam", "pmchat", "pmrequest", "pmenquire", "pmoptions"]:
                sqllist.rm_from_list(lst, user.id)
            PM_WARNS = sql.get_collection("pmwarns").json
            if str(user.id) in PM_WARNS:
                del PM_WARNS[str(user.id)]
                sql.del_collection("pmwarns")
                sql.add_collection("pmwarns", PM_WARNS, {})
        except: pass

        await edit_delete(event, f"**⎉╎المستخـدم**  [{user.first_name}](tg://user?id={user.id})\n**⎉╎تـم السـمـاح لـه بـإرسـال الـرسـائـل 💬✓** \n **⎉╎ الـسـبـب ❔  :** {reason}")
    else:
        await edit_delete(event, f"**⎉╎المستخـدم** [{user.first_name}](tg://user?id={user.id}) \n**⎉╎هـو بـالـفـعل فـي قـائـمـة الـسـمـاح ✅**")

@zedub.zed_cmd(pattern="(رف|رفض)(?:\s|$)([\s\S]*)")
async def disapprove_p_m(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, f"** ⎉╎يـجب تفعيـل امـر الحـمايـه اولاً **")

    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(2)
    else:
        reason = event.pattern_match.group(2)
        if reason != "الكل":
            user, reason = await get_user_from_event(event, secondgroup=True)
            if not user: return

    if reason == "الكل":
        pmpermit_sql.disapprove_all()
        return await edit_delete(event, "**⎉╎حــسـنـا تــم رفـض الـجـمـيـع .. بنجـاح 💯**")

    if not reason: reason = "**⎉╎ لـم يـذكـر 💭**"

    if pmpermit_sql.is_approved(user.id):
        pmpermit_sql.disapprove(user.id)
        await edit_or_reply(event, f"**⎉╎المستخـدم**  [{user.first_name}](tg://user?id={user.id})\n**⎉╎تـم رفـضـه مـن أرسـال الـرسـائـل ⚠️**\n**⎉╎ الـسـبـب ❔  :** {reason}")
    else:
        await edit_delete(event, f"**⎉╎المستخـدم**  [{user.first_name}](tg://user?id={user.id})\n **⎉╎لــم تـتـم الـمـوافـقـة عـلـيـه مـسـبـقـاً ❕ **")

@zedub.zed_cmd(pattern="بلوك(?:\s|$)([\s\S]*)")
async def block_p_m(event):
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user: return
    if not reason: reason = "**⎉╎ لـم يـذكـر 💭**"

    if pmpermit_sql.is_approved(user.id):
        pmpermit_sql.disapprove(user.id)

    await event.client(functions.contacts.BlockRequest(user.id))
    await edit_or_reply(event, f"**- المسـتخـدم :**  [{user.first_name}](tg://user?id={user.id}) **تم حظـره بنجـاح .. لايمكنـه ازعـاجـك الان**\n\n**- السـبب :** {reason}")

@zedub.zed_cmd(pattern="الغاء بلوك(?:\s|$)([\s\S]*)")
async def unblock_pm(event):
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user: return
    if not reason: reason = "**⎉╎ لـم يـذكـر 💭**"

    await event.client(functions.contacts.UnblockRequest(user.id))
    await edit_or_reply(event, f"**- المسـتخـدم :**  [{user.first_name}](tg://user?id={user.id}) **تم الغـاء حظـره بنجـاح .. يمكنـه التكلـم معـك الان**\n\n**- السـبب :** {reason}")

@zedub.zed_cmd(pattern="المقبولين$")
async def show_approved(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, f"** ⎉╎يـجب تفعيـل امـر الحـمايـه اولاً **")

    approved_users = pmpermit_sql.get_all_approved()
    APPROVED_PMs = "**- قائمـة المسمـوح لهـم ( المقبـوليـن ) :**\n\n"
    if len(approved_users) > 0:
        for user in approved_users:
            APPROVED_PMs += f"**• 👤 الاسـم :** {_format.mentionuser(user.first_name , user.user_id)}\n**- الايـدي :** `{user.user_id}`\n**- المعـرف :** @{user.username}\n**- التـاريخ : **__{user.date}__\n**- السـبب : **__{user.reason}__\n\n"
    else:
        APPROVED_PMs = "**- انت لـم توافـق على اي شخـص بعـد**"

    await edit_or_reply(event, APPROVED_PMs, file_name="قائمـة الحمايـة.txt", caption="**- ️قائمـة المسمـوح لهـم ( المقبوليـن )**\n\n**- سـورس زدثــون** 𝙕𝙏𝙝𝙤𝙣 ")