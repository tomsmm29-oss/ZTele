# 🚬 ZThon PM Permit - The Royal Heavy Edition 2025
# By Mikey & Kalvari 🍁
# المسار: zlzl/plugins/الحمايه.py

import os
import asyncio
import random
import re
from datetime import datetime

from telethon import functions, Button
from telethon.utils import get_display_name

# 👇 استدعاءات السورس
from zlzl import zedub
from zlzl.core.logger import logging
from zlzl.Config import Config
from zlzl.core.managers import edit_delete, edit_or_reply
from zlzl.helpers.utils import _format, get_user_from_event, reply_id
from zlzl.sql_helper import global_collectionjson as sql
from zlzl.sql_helper import global_list as sqllist
from zlzl.sql_helper import pmpermit_sql
from zlzl.sql_helper.globals import addgvar, delgvar, gvarstatus
from . import BOTLOG_CHATID

# 👇 مكتبة بايروجرام للانلاين
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

plugin_category = "البوت"
LOGS = logging.getLogger(__name__)
cmdhd = Config.COMMAND_HAND_LER

# ====================================================================
# 🏗 إعداد الحارس المستقل (Pyrogram Guard Client)
# ====================================================================
api_id = zedub.api_id
api_hash = zedub.api_hash
bot_token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("BOT_TOKEN")

pm_guard = Client(
    name="zthon_pm_royal_guard",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    in_memory=True
)

async def start_guard():
    if bot_token:
        try:
            if not pm_guard.is_connected:
                await pm_guard.start()
        except Exception as e:
            print(f"🚬 Mikey Error (PM Guard): {e}")

zedub.loop.create_task(start_guard())

# ====================================================================
# ⚙️ الثوابت والإعدادات
# ====================================================================
MAX_FLOOD = 4

class PMPERMIT:
    def __init__(self):
        self.TEMPAPPROVED = []

PMPERMIT_ = PMPERMIT()

def get_pm_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("•❶• إستفسـار خـاص", callback_data=f"to_enquire|{user_id}")],
        [InlineKeyboardButton("•❷• طـلـب ضــروري", callback_data=f"to_request|{user_id}")],
        [InlineKeyboardButton("•❸• دردشـة عامــة", callback_data=f"to_chat|{user_id}")],
        [InlineKeyboardButton("•❹• إزعـاج (تجربة)", callback_data=f"to_spam|{user_id}")],
    ])

# ====================================================================
# 🔥 السيناريوهات المتعددة (تم حذف العناوين من الردود المباشرة)
# ====================================================================

async def do_pm_enquire_action(event, chat):
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    if str(chat.id) not in PM_WARNS: PM_WARNS[str(chat.id)] = 0
    warns = PM_WARNS[str(chat.id)] + 1

    if warns >= MAX_FLOOD:
        BLOCK_MSG = f"**⛔️ لقـد تـم حظـرك نهـائيـاً !**\n\n• السـبب ↶ إختـرت **(الاستفسـار)** ولكـن لـم تنتظـر الـرد.\n• النتيجـة ↶ تجـاوزت الحـد المسمـوح (4/4).\n\n**⚰️ ودعــاً ..**"
        await event.reply(BLOCK_MSG)
        await event.client(functions.contacts.BlockRequest(chat.id))
        await log_block(event, chat, "إختار الاستفسار واستمر بالتكرار المزعج")
        clean_db(chat.id)
        return

    if warns == 3:
        MSG = f"**☢️ تحذيــر أخيــر (3/4) !**\n\n• لـقـد قلـت لـك أن استفسـارك تـم تسجيـلـه.\n• التكـرار لـن يجعـل المـالـك يـرد أسـرع.\n\n**✋🏻 رسـالـة أخـرى = بـلـوك فــوري.**"
        await event.reply(MSG)
    elif warns == 2:
        MSG = f"**⚠️ تـنـبـيــه (2/4)**\n\n• أنـت الآن فـي قـائـمـة الانتظـار للاستفسـارات.\n• الـرجـاء عـدم إرسـال المـزيـد مـن الـرسـائـل.\n\n**⏳ انتظـر بصمـت.**"
        await event.reply(MSG)

    PM_WARNS[str(chat.id)] = warns
    sql.add_collection("pmwarns", PM_WARNS, {})

async def do_pm_request_action(event, chat):
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    if str(chat.id) not in PM_WARNS: PM_WARNS[str(chat.id)] = 0
    warns = PM_WARNS[str(chat.id)] + 1

    if warns >= MAX_FLOOD:
        BLOCK_MSG = f"**⛔️ لقـد تـم حظـرك نهـائيـاً !**\n\n• السـبب ↶ إختـرت **(طـلـب ضـروري)** وأزعجـت المـالك.\n• النتيجـة ↶ تجـاوزت الحـد المسمـوح (4/4).\n\n**⚰️ انتهــت فرصـك.**"
        await event.reply(BLOCK_MSG)
        await event.client(functions.contacts.BlockRequest(chat.id))
        await log_block(event, chat, "إختار الطلب واستمر بالتكرار")
        clean_db(chat.id)
        return

    if warns == 3:
        MSG = f"**☢️ تحذيــر أخيــر (3/4) !**\n\n• طلـبـك وصـل بـالـفـعـل.\n• الإلـحـاح لـن يـغـيـر شـيـئـاً.\n\n**✋🏻 هـذا الإنـذار النـهـائـي.**"
        await event.reply(MSG)
    elif warns == 2:
        MSG = f"**⚠️ تـنـبـيــه (2/4)**\n\n• لقـد تـم رفـع طلـبـك.\n• لا داعـي للتكـرار، المـالك سيـرى رسالتـك.\n\n**⏳ انتظـر.**"
        await event.reply(MSG)

    PM_WARNS[str(chat.id)] = warns
    sql.add_collection("pmwarns", PM_WARNS, {})

async def do_pm_chat_action(event, chat):
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    if str(chat.id) not in PM_WARNS: PM_WARNS[str(chat.id)] = 0
    warns = PM_WARNS[str(chat.id)] + 1

    if warns >= MAX_FLOOD:
        BLOCK_MSG = f"**⛔️ لقـد تـم حظـرك نهـائيـاً !**\n\n• السـبب ↶ تريـد **(الدردشـة)** وأنـا لسـت متفـرغـاً.\n• النتيجـة ↶ تجـاوزت الحـد المسمـوح (4/4).\n\n**⚰️ إبحـث عـن شخـص آخـر.**"
        await event.reply(BLOCK_MSG)
        await event.client(functions.contacts.BlockRequest(chat.id))
        await log_block(event, chat, "إختار الدردشة وأصر على الإزعاج")
        clean_db(chat.id)
        return

    if warns == 3:
        MSG = f"**☢️ تحذيــر أخيــر (3/4) !**\n\n• لـسـت مـتـفـرغـاً لـتـراهـاتـك.\n• وقـتـي مـهـم جـداً.\n\n**✋🏻 آخـر فـرصـة قـبـل الـحـظـر.**"
        await event.reply(MSG)
    elif warns == 2:
        MSG = f"**⚠️ تـنـبـيــه (2/4)**\n\n• قـلـت لـك أنـا مـشـغـول.\n• الـدردشـة غـيـر مـتـاحـة الآن.\n\n**⏳ تـوقـف.**"
        await event.reply(MSG)

    PM_WARNS[str(chat.id)] = warns
    sql.add_collection("pmwarns", PM_WARNS, {})

async def do_pm_spam_action(event, chat):
    BLOCK_MSG = f"**⛔️ تـم تـحـقـيـق رغ_بـتـك (الـبـلـوك) !**\n\n• السـبب ↶ إختـرت **(الإزعــاج)** بـإرادتـك.\n• النتيجـة ↶ حـظـر فـوري بـدون نـقـاش.\n\n**⚰️ Game Over.**"
    await event.reply(BLOCK_MSG)
    await event.client(functions.contacts.BlockRequest(chat.id))
    await log_block(event, chat, "إختار خيار الإزعاج (انتحار)")
    clean_db(chat.id)

async def do_pm_permit_action(event, chat):
    reply_to_id = await reply_id(event)
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    try: PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
    except: PMMESSAGE_CACHE = {}

    me = await event.client.get_me()
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"

    if str(chat.id) not in PM_WARNS: PM_WARNS[str(chat.id)] = 0
    warns = PM_WARNS[str(chat.id)] + 1

    if warns >= MAX_FLOOD:
        BLOCK_MSG = f"**⛔️ لقـد تـم حظـرك نهـائيـاً !**\n\n• السـبب ↶ تجـاهلـت الإختيـار واستمـريت بـالثرثـرة.\n• النتيجـة ↶ تجـاوزت الحـد المسمـوح (4/4).\n\n**⚰️ ودعــاً.**"
        await event.reply(BLOCK_MSG)
        await event.client(functions.contacts.BlockRequest(chat.id))
        await log_block(event, chat, "لم يختر أي خيار واستمر بالتكرار")
        clean_db(chat.id)
        return

    if warns == 3:
        WARNING_MSG = f"**☢️ تحذيــر أخيــر (3/4) !**\n\n**⛔️ لـسـت مـتـفـرغـاً لـتـراهـاتـك !**\n**⤶ هـذا هـو تـحـذيـرك الأخـي_ر ... .**\n\n**✋🏻 إخـتـر سـبـب مـراسـلـتـك أو سـيـتـم حـظـرك.**"
    elif warns == 2:
        WARNING_MSG = f"**⚠️ تـنـبـيــه (2/4)**\n\n**⤶ أرى أنـك مـازلـت تـكـرر الـرسـائـل !**\n**⤶ يجـب عـلـيـك إختيـار سـبـب مـن الأزرار أولاً.**\n\n**⏳ هـذا تـحـذيـر جــاد.**"
    else:
        # الرسالة الترحيبية الأولى فقط تحتوي على العنوان والرابط المخفي
        WARNING_MSG = f"نضام الحمايه  [𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪](https://t.me/ZThon)\n🧑🏻‍💻┊المستخـدم ↶ {my_mention}\n\n**✋🏻 أهـلاً بـك فـي مـنـطـقـة {me.first_name} الخـاصـة.**\n\n• حـالـة الـحـساب ↶ **( مـشـغـول حـالـيـاً )**\n• وضـع الحـمـايـة ↶ **( مـفـعــل 🔒 )**\n• عـداد تحذيـراتك ↶ **( {warns} / {MAX_FLOOD} )**\n\n**👇🏻 مـن فـضـلـك .. حـدد سـبـب قـدومـك :**"

    PM_WARNS[str(chat.id)] = warns
    sql.add_collection("pmwarns", PM_WARNS, {})

    try:
        if str(chat.id) in PMMESSAGE_CACHE:
            await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
    except: pass

    try:
        if warns == 1:
            # استخدام بايروجرام لضمان ظهور الأزرار
            msg = await pm_guard.send_message(
                chat.id,
                WARNING_MSG,
                reply_markup=get_pm_keyboard(chat.id),
                disable_web_page_preview=True
            )
            PMMESSAGE_CACHE[str(chat.id)] = msg.id
        else:
            msg = await event.reply(WARNING_MSG)
            PMMESSAGE_CACHE[str(chat.id)] = msg.id
    except:
        msg = await event.reply(WARNING_MSG)
        PMMESSAGE_CACHE[str(chat.id)] = msg.id

    sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})

# ====================================================================
# 🔥 معالجات الزراير (Pyrogram Callbacks)
# ====================================================================

@pm_guard.on_callback_query()
async def pm_callbacks(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    try:
        target_id = int(data.split("|")[1])
        if user_id != target_id:
            return await callback_query.answer("⚠️ هذا الخيار ليس لك !", show_alert=True)
    except: pass

    if data.startswith("to_enquire"):
        text = "**📝 تـم تسجيـل إستفـسـارك بـنـجـاح.**\n\n• سـيـقـوم المـالـك بـالـرد عـلـيـك قـريـبـاً.\n• الـرجـاء عـدم تـكـرار الـرسـائـل.\n\n**🤫 الـزم الـصـمـت.**"
        sqllist.add_to_list("pmenquire", user_id)
        reset_warns(user_id)
        await callback_query.edit_message_text(text)

    elif data.startswith("to_request"):
        text = "**📥 تـم رفـع طـلـبـك إلـى المـالـك.**\n\n• رسـالـتـك فـي صـنـدوق الأولـويـات.\n• الإنـتـظـار هـو الـحـل الـوحـيـد الآن.\n\n**🛡 تـم الـحـفـظ.**"
        sqllist.add_to_list("pmrequest", user_id)
        reset_warns(user_id)
        await callback_query.edit_message_text(text)

    elif data.startswith("to_chat"):
        text = "**🥀 الـمـالـك لـيـس فـي مـزاج للـدردشـة.**\n\n• أترك رسـالـتـك (واحـدة فقـط) وإخـتـفِ.\n• إذا كـان الأمـر مـهـمـاً .. سـيـتـم الـرد.\n\n**⏳ إنـتـهـى.**"
        sqllist.add_to_list("pmchat", user_id)
        reset_warns(user_id)
        await callback_query.edit_message_text(text)

    elif data.startswith("to_spam"):
        text = "**☠️ لـقـد إخـتـرت الـطـريـق الـخـطـأ !**\n\n• هـذا الخـيـار للـمـتـطـفـلـيـن فـقـط.\n• أي رسـالـة إضـافـيـة سـتـؤدي للـحـظـر.\n\n**⚠️ تـم تـفـعـيـل الإنـذار الأحـمـر.**"
        sqllist.add_to_list("pmspam", user_id)
        set_warns_critical(user_id)
        await callback_query.edit_message_text(text)

# ====================================================================
# 🛠 دوال مساعدة وأوامر التصفير
# ====================================================================

@zedub.zed_cmd(pattern="(صفر|صفره)$")
async def zero_user(event):
    if not event.is_private: return
    chat = await event.get_chat()
    clean_db(chat.id)
    await edit_delete(event, "**✅ تم تصفير ذاكرة البوت لهذا المستخدم .. سيتم معاملته كشخص جديد الآن.**")

def reset_warns(user_id):
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
        if str(user_id) in PM_WARNS:
            del PM_WARNS[str(user_id)]
            sql.add_collection("pmwarns", PM_WARNS, {})
    except: pass

def set_warns_critical(user_id):
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
        PM_WARNS[str(user_id)] = MAX_FLOOD - 1
        sql.add_collection("pmwarns", PM_WARNS, {})
    except: pass

def clean_db(user_id):
    try:
        for lst in ["pmspam", "pmchat", "pmrequest", "pmenquire", "pmoptions"]:
            sqllist.rm_from_list(lst, user_id)
        PM_WARNS = sql.get_collection("pmwarns").json
        if str(user_id) in PM_WARNS: del PM_WARNS[str(user_id)]
        sql.add_collection("pmwarns", PM_WARNS, {})
        PMM_CACHE = sql.get_collection("pmmessagecache").json
        if str(user_id) in PMM_CACHE: del PMM_CACHE[str(user_id)]
        sql.add_collection("pmmessagecache", PMM_CACHE, {})
    except: pass

async def log_block(event, chat, reason):
    try:
        if BOTLOG_CHATID:
            msg = f"#حمـايـة_الخـاص\n**👤 العضـو:** [{get_display_name(chat)}](tg://user?id={chat.id})\n**🏷 السـبب:** {reason}"
            await event.client.send_message(BOTLOG_CHATID, msg)
    except: pass

# ====================================================================
# 📬 مراقب الرسائل
# ====================================================================

@zedub.zed_cmd(incoming=True, func=lambda e: e.is_private, edited=False, forword=None)
async def on_new_private_message(event):
    if gvarstatus("pmpermit") is None: return
    chat = await event.get_chat()
    zel_dev = [8241311871, 5176749470, 5426390871, 925972505, 1895219306, 2095357462, 5280339206]
    if event.chat_id in zel_dev or chat.bot or chat.verified: return
    if pmpermit_sql.is_approved(chat.id): return

    if str(chat.id) in sqllist.get_collection_list("pmspam"): return await do_pm_spam_action(event, chat)
    if str(chat.id) in sqllist.get_collection_list("pmchat"): return await do_pm_chat_action(event, chat)
    if str(chat.id) in sqllist.get_collection_list("pmrequest"): return await do_pm_request_action(event, chat)
    if str(chat.id) in sqllist.get_collection_list("pmenquire"): return await do_pm_enquire_action(event, chat)

    await do_pm_permit_action(event, chat)

@zedub.zed_cmd(outgoing=True, func=lambda e: e.is_private, edited=False, forword=None)
async def you_dm_other(event):
    if gvarstatus("pmpermit") is None: return
    chat = await event.get_chat()
    if chat.bot or chat.verified: return
    if event.text and event.text.startswith(cmdhd): return
    if not pmpermit_sql.is_approved(chat.id):
        pmpermit_sql.approve(chat.id, get_display_name(chat), str(datetime.now().strftime("%B %d, %Y")), chat.username, "موافقة تلقائية")
        clean_db(chat.id)

# ====================================================================
# ⚙️ أوامر التحكم (قبول، رفض، بلوك)
# ====================================================================

@zedub.zed_cmd(pattern="الحمايه (تفعيل|تعطيل)$")
async def pmpermit_on(event):
    input_str = event.pattern_match.group(1)
    if input_str == "تفعيل":
        addgvar("pmpermit", "true")
        await edit_delete(event, "**🖥┊نظام الحماية 𝗭𝗧𝗵𝗼𝗻\n\n🔒 تم تشغيل الدروع .. الخاص مغلق.**")
    else:
        delgvar("pmpermit")
        await edit_delete(event, "**🖥┊نظام الحماية 𝗭𝗧𝗵𝗼𝗻\n\n🔓 تم إيقاف الدروع .. الخاص مفتوح.**")

@zedub.zed_cmd(pattern="(قبول|سماح)(?:\s|$)([\s\S]*)")
async def approve_p_m(event):
    if gvarstatus("pmpermit") is None: return await edit_delete(event, "**⚠️ فعـل الحمايـة أولاً !**")
    user, reason = await get_user_from_event(event, secondgroup=True)
    if not user: return
    if not reason: reason = "**أمر ملكي 👑**"
    pmpermit_sql.approve(user.id, get_display_name(user), str(datetime.now().strftime("%B %d, %Y")), user.username, reason)
    clean_db(user.id)
    await edit_delete(event, f"**✅ تم السماح لـ** [{user.first_name}](tg://user?id={user.id})\n**🏷 السبب:** {reason}")

@zedub.zed_cmd(pattern="(رف|رفض)(?:\s|$)([\s\S]*)")
async def disapprove_p_m(event):
    if gvarstatus("pmpermit") is None: return await edit_delete(event, "**⚠️ فعـل الحمايـة أولاً !**")
    user, reason = await get_user_from_event(event, secondgroup=True)
    if not user: return
    pmpermit_sql.disapprove(user.id)
    await edit_or_reply(event, f"**❌ تم رفض** [{user.first_name}](tg://user?id={user.id})")

@zedub.zed_cmd(pattern="بلوك(?:\s|$)([\s\S]*)")
async def block_p_m(event):
    user, reason = await get_user_from_event(event)
    if not user: return
    if pmpermit_sql.is_approved(user.id): pmpermit_sql.disapprove(user.id)
    await event.client(functions.contacts.BlockRequest(user.id))
    await edit_or_reply(event, f"**⛔️ تم حظر** [{user.first_name}](tg://user?id={user.id})")

@zedub.zed_cmd(pattern="الغاء بلوك(?:\s|$)([\s\S]*)")
async def unblock_pm(event):
    user, reason = await get_user_from_event(event)
    if not user: return
    await event.client(functions.contacts.UnblockRequest(user.id))
    await edit_or_reply(event, f"**🔓 تم الغاء حظر** [{user.first_name}](tg://user?id={user.id})")

@zedub.zed_cmd(pattern="المقبولين$")
async def show_approved(event):
    approved_users = pmpermit_sql.get_all_approved()
    APPROVED_PMs = "**- 📋 قائمة المقبولين :**\n\n"
    if len(approved_users) > 0:
        for user in approved_users:
            APPROVED_PMs += f"**• 👤 الاسم :** {_format.mentionuser(user.first_name , user.user_id)}\n**- الايدي :** `{user.user_id}`\n\n"
    else: APPROVED_PMs = "**- لا يوجد أحد في القائمة حالياً.**"
    await edit_or_reply(event, APPROVED_PMs)