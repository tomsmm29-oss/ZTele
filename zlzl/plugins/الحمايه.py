# 🚬 ZThon PM Permit - The Royal Heavy Edition 2025
# By Mikey & Kalvari 🍁
# المسار: zlzl/plugins/الحمايه.py
# المميزات: بايروجرام، زراير ذكية، نصوص فخمة، سيناريوهات متعددة، كود ضخم وتفصيلي.

import os
import asyncio
import random
import re
from datetime import datetime

from telethon import functions, Button
from telethon.utils import get_display_name

# 👇 استدعاءات السورس (المسارات الصحيحة)
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

# 👇 مكتبة الباشا (Pyrogram) للانلاين
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

# جلسة خاصة للحماية (عشان ميتعارضش مع القائمة)
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
            await pm_guard.start()
            print("🚬 Mikey: تم تفعيل نظام الحماية الملكي (ZThon Royal Guard)!")
        except Exception as e:
            print(f"🚬 Mikey Error (PM Guard): {e}")

zedub.loop.create_task(start_guard())

# ====================================================================
# ⚙️ الثوابت والإعدادات
# ====================================================================
MAX_FLOOD = 4  # 1:قائمة، 2:تنبيه، 3:اخير، 4:بلوك

class PMPERMIT:
    def __init__(self):
        self.TEMPAPPROVED = []

PMPERMIT_ = PMPERMIT()

# ====================================================================
# 🎮 هندسة الزراير (Pyrogram Style)
# ====================================================================
def get_pm_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("•❶• إستفسـار خـاص", callback_data=f"to_enquire|{user_id}")],
        [InlineKeyboardButton("•❷• طـلـب ضــروري", callback_data=f"to_request|{user_id}")],
        [InlineKeyboardButton("•❸• دردشـة عامــة", callback_data=f"to_chat|{user_id}")],
        [InlineKeyboardButton("•❹• إزعـاج (تجربة)", callback_data=f"to_spam|{user_id}")],
    ])

# ====================================================================
# 🔥 السيناريوهات المتعددة (Heavy Logic Functions)
# ====================================================================

# --------------------------------------------------------------------
# 1. سيناريو الاستفسار (Enquire Scenario)
# --------------------------------------------------------------------
async def do_pm_enquire_action(event, chat):
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError: PM_WARNS = {}

    me = await event.client.get_me()
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"

    if str(chat.id) not in PM_WARNS:
        PM_WARNS[str(chat.id)] = 0

    warns = PM_WARNS[str(chat.id)] + 1

    # --- مرحلة البلوك ---
    if warns >= MAX_FLOOD:
        BLOCK_MSG = f"""
🖥┊**نظــام الحـمـايـة 𝗭𝗧𝗵𝗼𝗻**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**⛔️ لقـد تـم حظـرك نهـائيـاً !**

• السـبب ↶ إختـرت **(الاستفسـار)** ولكـن لـم تنتظـر الـرد.
• النتيجـة ↶ تجـاوزت الحـد المسمـوح (4/4).

**⚰️ ودعــاً ..**
"""
        await event.reply(BLOCK_MSG)
        await event.client(functions.contacts.BlockRequest(chat.id))
        await log_block(event, chat, "إختار الاستفسار واستمر بالتكرار المزعج")
        clean_db(chat.id)
        return

    # --- التحذير الثالث (الأخير) ---
    if warns == 3:
        MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**☢️ تحذيــر أخيــر (3/4) !**

• لـقـد قلـت لـك أن استفسـارك تـم تسجيـلـه.
• التكـرار لـن يجعـل المـالـك يـرد أسـرع.

**✋🏻 رسـالـة أخـرى = بـلـوك فــوري.**
"""
        await event.reply(MSG)

    # --- التحذير الثاني ---
    elif warns == 2:
        MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**⚠️ تـنـبـيــه (2/4)**

• أنـت الآن فـي قـائـمـة الانتظـار للاستفسـارات.
• الـرجـاء عـدم إرسـال المـزيـد مـن الـرسـائـل.

**⏳ انتظـر بصمـت.**
"""
        await event.reply(MSG)

    # حفظ العداد
    PM_WARNS[str(chat.id)] = warns
    sql.add_collection("pmwarns", PM_WARNS, {})


# --------------------------------------------------------------------
# 2. سيناريو الطلب (Request Scenario)
# --------------------------------------------------------------------
async def do_pm_request_action(event, chat):
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError: PM_WARNS = {}

    me = await event.client.get_me()
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"

    if str(chat.id) not in PM_WARNS:
        PM_WARNS[str(chat.id)] = 0

    warns = PM_WARNS[str(chat.id)] + 1

    # --- مرحلة البلوك ---
    if warns >= MAX_FLOOD:
        BLOCK_MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**⛔️ لقـد تـم حظـرك نهـائيـاً !**

• السـبب ↶ إختـرت **(طـلـب ضـروري)** وأزعجـت المـالك.
• النتيجـة ↶ تجـاوزت الحـد المسمـوح (4/4).

**⚰️ انتهــت فرصـك.**
"""
        await event.reply(BLOCK_MSG)
        await event.client(functions.contacts.BlockRequest(chat.id))
        await log_block(event, chat, "إختار الطلب واستمر بالتكرار")
        clean_db(chat.id)
        return

    # --- التحذير الثالث ---
    if warns == 3:
        MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**☢️ تحذيــر أخيــر (3/4) !**

• طلـبـك وصـل بـالـفـعـل.
• الإلـحـاح لـن يـغـيـر شـيـئـاً.

**✋🏻 هـذا الإنـذار النـهـائـي.**
"""
        await event.reply(MSG)

    # --- التحذير الثاني ---
    elif warns == 2:
        MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**⚠️ تـنـبـيــه (2/4)**

• لقـد تـم رفـع طلـبـك.
• لا داعـي للتكـرار، المـالك سيـرى رسالتـك.

**⏳ انتظـر.**
"""
        await event.reply(MSG)

    # حفظ العداد
    PM_WARNS[str(chat.id)] = warns
    sql.add_collection("pmwarns", PM_WARNS, {})


# --------------------------------------------------------------------
# 3. سيناريو الدردشة (Chat Scenario)
# --------------------------------------------------------------------
async def do_pm_chat_action(event, chat):
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError: PM_WARNS = {}

    me = await event.client.get_me()
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"

    if str(chat.id) not in PM_WARNS:
        PM_WARNS[str(chat.id)] = 0

    warns = PM_WARNS[str(chat.id)] + 1

    # --- مرحلة البلوك ---
    if warns >= MAX_FLOOD:
        BLOCK_MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**⛔️ لقـد تـم حظـرك نهـائيـاً !**

• السـبب ↶ تريـد **(الدردشـة)** وأنـا لسـت متفـرغـاً.
• النتيجـة ↶ تجـاوزت الحـد المسمـوح (4/4).

**⚰️ إبحـث عـن شخـص آخـر.**
"""
        await event.reply(BLOCK_MSG)
        await event.client(functions.contacts.BlockRequest(chat.id))
        await log_block(event, chat, "إختار الدردشة وأصر على الإزعاج")
        clean_db(chat.id)
        return

    # --- التحذير الثالث ---
    if warns == 3:
        MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**☢️ تحذيــر أخيــر (3/4) !**

• لـسـت مـتـفـرغـاً لـتـراهـاتـك.
• وقـتـي مـهـم جـداً.

**✋🏻 آخـر فـرصـة قـبـل الـحـظـر.**
"""
        await event.reply(MSG)

    # --- التحذير الثاني ---
    elif warns == 2:
        MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**⚠️ تـنـبـيــه (2/4)**

• قـلـت لـك أنـا مـشـغـول.
• الـدردشـة غـيـر مـتـاحـة الآن.

**⏳ تـوقـف.**
"""
        await event.reply(MSG)

    # حفظ العداد
    PM_WARNS[str(chat.id)] = warns
    sql.add_collection("pmwarns", PM_WARNS, {})


# --------------------------------------------------------------------
# 4. سيناريو الإزعاج (Spam Scenario)
# --------------------------------------------------------------------
async def do_pm_spam_action(event, chat):
    # ده سيناريو سريع، ملوش فرص كتير
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError: PM_WARNS = {}

    me = await event.client.get_me()
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"

    BLOCK_MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**⛔️ تـم تـحـقـيـق رغـبـتـك (الـبـلـوك) !**

• السـبب ↶ إختـرت **(الإزعــاج)** بـإرادتـك.
• النتيجـة ↶ حـظـر فـوري بـدون نـقـاش.

**⚰️ Game Over.**
"""
    await event.reply(BLOCK_MSG)
    await event.client(functions.contacts.BlockRequest(chat.id))
    await log_block(event, chat, "إختار خيار الإزعاج (انتحار)")
    clean_db(chat.id)


# --------------------------------------------------------------------
# 5. سيناريو الزائر الجديد (The Welcome Action)
# --------------------------------------------------------------------
async def do_pm_permit_action(event, chat):
    reply_to_id = await reply_id(event)
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError: PM_WARNS = {}
    try: PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
    except AttributeError: PMMESSAGE_CACHE = {}

    me = await event.client.get_me()
    mention = f"[{chat.first_name}](tg://user?id={chat.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"

    if str(chat.id) not in PM_WARNS:
        PM_WARNS[str(chat.id)] = 0

    warns = PM_WARNS[str(chat.id)] + 1

    # --- مرحلة البلوك (لو كرر بدون اختيار) ---
    if warns >= MAX_FLOOD:
        BLOCK_MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**⛔️ لقـد تـم حظـرك نهـائيـاً !**

• السـبب ↶ تجـاهلـت الإختيـار واستمـريت بـالثرثـرة.
• النتيجـة ↶ تجـاوزت الحـد المسمـوح (4/4).

**⚰️ ودعــاً.**
"""
        await event.reply(BLOCK_MSG)
        await event.client(functions.contacts.BlockRequest(chat.id))
        await log_block(event, chat, "لم يختر أي خيار واستمر بالتكرار")
        clean_db(chat.id)
        return

    # --- التحذير الثالث (الأخير) ---
    if warns == 3:
        WARNING_MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**☢️ تحذيــر أخيــر (3/4) !**

**⛔️ لـسـت مـتـفـرغـاً لـتـراهـاتـك !**
**⤶ هـذا هـو تـحـذيـرك الأخـيـر ... .**

**✋🏻 إخـتـر سـبـب مـراسـلـتـك أو سـيـتـم حـظـرك.**
"""

    # --- التحذير الثاني ---
    elif warns == 2:
        WARNING_MSG = f"""
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**⚠️ تـنـبـيــه (2/4)**

**⤶ أرى أنـك مـازلـت تـكـرر الـرسـائـل !**
**⤶ يجـب عـلـيـك إختيـار سـبـب مـن الأزرار أولاً.**

**⏳ هـذا تـحـذيـر جــاد.**
"""

    # --- التحذير الأول (الترحيب الرسمي) ---
    else:
        WARNING_MSG = f"""
🖥┊**  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪 الـرد التلقـائي 〽️**
🧑🏻‍💻┊المستخـدم ↶ {my_mention}

**✋🏻 أهـلاً بـك فـي مـنـطـقـة {me.first_name} الخـاصـة.**

• حـالـة الـحـسـاب ↶ **( مـشـغـول حـالـيـاً )**
• وضـع الحـمـايـة ↶ **( مـفـعــل 🔒 )**
• عـداد تحذيـراتك ↶ **( {warns} / {MAX_FLOOD} )**

**👇🏻 مـن فـضـلـك .. حـدد سـبـب قـدومـك :**
"""

    # زيادة العداد
    PM_WARNS[str(chat.id)] = warns
    sql.add_collection("pmwarns", PM_WARNS, {})

    # إرسال الرسالة (بايروجرام للأولى فقط)
    try:
        if str(chat.id) in PMMESSAGE_CACHE:
            await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
            del PMMESSAGE_CACHE[str(chat.id)]
    except: pass

    try:
        if warns == 1:
            msg = await pm_guard.send_message(
                chat.id,
                WARNING_MSG,
                reply_markup=get_pm_keyboard(chat.id)
            )
            PMMESSAGE_CACHE[str(chat.id)] = msg.id
        else:
            # التحذيرات التالية نصية فقط لزيادة الجدية
            msg = await event.reply(WARNING_MSG)
            PMMESSAGE_CACHE[str(chat.id)] = msg.id
    except Exception as e:
        LOGS.error(str(e))
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
            await callback_query.answer("⚠️ هذا الخيار ليس لك !", show_alert=True)
            return
    except: pass

    # 1. الاستفسار
    if data.startswith("to_enquire"):
        text = """
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**

**📝 تـم تسجيـل إستفـسـارك بـنـجـاح.**

• سـيـقـوم المـالـك بـالـرد عـلـيـك قـريـبـاً.
• الـرجـاء عـدم تـكـرار الـرسـائـل.

**🤫 الـزم الـصـمـت.**
"""
        sqllist.add_to_list("pmenquire", user_id)
        reset_warns(user_id)
        await callback_query.edit_message_text(text)

    # 2. الطلب
    elif data.startswith("to_request"):
        text = """
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**

**📥 تـم رفـع طـلـبـك إلـى المـالـك.**

• رسـالـتـك فـي صـنـدوق الأولـويـات.
• الإنـتـظـار هـو الـحـل الـوحـيـد الآن.

**🛡 تـم الـحـفـظ.**
"""
        sqllist.add_to_list("pmrequest", user_id)
        reset_warns(user_id)
        await callback_query.edit_message_text(text)

    # 3. الدردشة
    elif data.startswith("to_chat"):
        text = """
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**

**🥀 الـمـالـك لـيـس فـي مـزاج للـدردشـة.**

• أترك رسـالـتـك (واحـدة فقـط) وإخـتـفِ.
• إذا كـان الأمـر مـهـمـاً .. سـيـتـم الـرد.

**⏳ إنـتـهـى.**
"""
        sqllist.add_to_list("pmchat", user_id)
        reset_warns(user_id)
        await callback_query.edit_message_text(text)

    # 4. الإزعاج
    elif data.startswith("to_spam"):
        text = """
🖥┊**نظــام الحـمـايـة  𓆩 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 𓆪**

**☠️ لـقـد إخـتـرت الـطـريـق الـخـطـأ !**

• هـذا الخـيـار للـمـتـطـفـلـيـن فـقـط.
• أي رسـالـة إضـافـيـة سـتـؤدي للـحـظـر.

**⚠️ تـم تـفـعـيـل الإنـذار الأحـمـر.**
"""
        sqllist.add_to_list("pmspam", user_id)
        set_warns_critical(user_id)
        await callback_query.edit_message_text(text)


# ====================================================================
# 🛠 دوال مساعدة (Utils)
# ====================================================================
def reset_warns(user_id):
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    if str(user_id) in PM_WARNS:
        del PM_WARNS[str(user_id)]
        sql.add_collection("pmwarns", PM_WARNS, {})

def set_warns_critical(user_id):
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    PM_WARNS[str(user_id)] = MAX_FLOOD - 1
    sql.add_collection("pmwarns", PM_WARNS, {})

def clean_db(user_id):
    try:
        for lst in ["pmspam", "pmchat", "pmrequest", "pmenquire", "pmoptions"]:
            sqllist.rm_from_list(lst, user_id)
        PM_WARNS = sql.get_collection("pmwarns").json
        if str(user_id) in PM_WARNS: del PM_WARNS[str(user_id)]
        sql.add_collection("pmwarns", PM_WARNS, {})
    except: pass

async def log_block(event, chat, reason):
    try:
        if BOTLOG_CHATID:
            the_message = f"#حمـايـة_الخـاص_القصـوى\n** 👤 العضـو** [{get_display_name(chat)}](tg://user?id={chat.id}) .\n** ☠️ الحـالـة:** تـم حظـره \n** 🏷 السـبب:** {reason}"
            await event.client.send_message(BOTLOG_CHATID, the_message)
    except: pass


# ====================================================================
# 📬 مراقب الرسائل الواردة (Incoming)
# ====================================================================
@zedub.zed_cmd(incoming=True, func=lambda e: e.is_private, edited=False, forword=None)
async def on_new_private_message(event):
    if gvarstatus("pmpermit") is None:
        return

    chat = await event.get_chat()
    # استثناء المطورين
    zel_dev = [8241311871, 5176749470, 5426390871, 925972505, 1895219306, 2095357462, 5280339206]

    if event.chat_id in zel_dev or chat.bot or chat.verified:
        return
    if pmpermit_sql.is_approved(chat.id):
        return

    # التوجيه للسيناريوهات الخاصة حسب الاختيار السابق
    if str(chat.id) in sqllist.get_collection_list("pmspam"):
        return await do_pm_spam_action(event, chat)
    if str(chat.id) in sqllist.get_collection_list("pmchat"):
        return await do_pm_chat_action(event, chat)
    if str(chat.id) in sqllist.get_collection_list("pmrequest"):
        return await do_pm_request_action(event, chat)
    if str(chat.id) in sqllist.get_collection_list("pmenquire"):
        return await do_pm_enquire_action(event, chat)

    # مستخدم جديد
    await do_pm_permit_action(event, chat)


# ====================================================================
# 📤 الرد اليدوي (Outgoing)
# ====================================================================
@zedub.zed_cmd(outgoing=True, func=lambda e: e.is_private, edited=False, forword=None)
async def you_dm_other(event):
    if gvarstatus("pmpermit") is None:
        return
    chat = await event.get_chat()
    if chat.bot or chat.verified: return
    if event.text and event.text.startswith(cmdhd): return

    if not pmpermit_sql.is_approved(chat.id):
        pmpermit_sql.approve(chat.id, get_display_name(chat), str(datetime.now().strftime("%B %d, %Y")), chat.username, "موافقة تلقائية (رد)")
        try:
            PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
            if str(chat.id) in PMMESSAGE_CACHE:
                try: await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
                except: pass
                del PMMESSAGE_CACHE[str(chat.id)]
            sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})
        except: pass


# ====================================================================
# ⚙️ أوامر التحكم (Commands)
# ====================================================================
@zedub.zed_cmd(pattern="الحمايه (تفعيل|تعطيل)$")
async def pmpermit_on(event):
    input_str = event.pattern_match.group(1)
    if input_str == "تفعيل":
        if gvarstatus("pmpermit") is None:
            addgvar("pmpermit", "true")
            await edit_delete(event, "**🖥┊نظــام الحـمـايـة 𝗭𝗧𝗵𝗼𝗻**\n\n**🔒 تـم تـشـغـيـل الـدروع .. الـخـاص مـغـلـق.**")
        else:
            await edit_delete(event, "**🖥┊نظــام الحـمـايـة 𝗭𝗧𝗵𝗼𝗻**\n\n**⚠️ الـحـمـايـة مـفـعـلـة بـالـفـعـل !**")
    else:
        if gvarstatus("pmpermit") is not None:
            delgvar("pmpermit")
            await edit_delete(event, "**🖥┊نظــام الحـمـايـة 𝗭𝗧𝗵𝗼𝗻**\n\n**🔓 تـم إيـقـاف الـدروع .. الـخـاص مـفـتـوح.**")
        else:
            await edit_delete(event, "**🖥┊نظــام الحـمـايـة 𝗭𝗧𝗵𝗼𝗻**\n\n**⚠️ الـحـمـايـة مـعـطـلـة بـالـفـعـل !**")

@zedub.zed_cmd(pattern="(قبول|سماح)(?:\s|$)([\s\S]*)")
async def approve_p_m(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, f"**⚠️ فعـل الحمايـة أولاً !**")

    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(2)
    else:
        user, reason = await get_user_from_event(event, secondgroup=True)
        if not user: return

    if not reason: reason = "**أمـر مـلـكـي 👑**"

    if not pmpermit_sql.is_approved(user.id):
        pmpermit_sql.approve(user.id, get_display_name(user), str(datetime.now().strftime("%B %d, %Y")), user.username, reason)
        clean_db(user.id)
        await edit_delete(event, f"**🖥┊نظــام الحـمـايـة 𝗭𝗧𝗵𝗼𝗻**\n\n**✅ تـم الـسـمـاح لـ** [{user.first_name}](tg://user?id={user.id})\n**🏷 السـبب:** {reason}")
    else:
        await edit_delete(event, f"**⚠️ هـذا الشخـص مـوافـق عليـه مسبقـاً !**")

@zedub.zed_cmd(pattern="(رف|رفض)(?:\s|$)([\s\S]*)")
async def disapprove_p_m(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, f"**⚠️ فعـل الحمايـة أولاً !**")

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
        return await edit_delete(event, "**☢️ تـم طـرد الجميـع مـن قـائمـة السمـاح !**")

    if not reason: reason = "**غـضـب مـلـكـي 😤**"

    if pmpermit_sql.is_approved(user.id):
        pmpermit_sql.disapprove(user.id)
        await edit_or_reply(event, f"**🖥┊نظــام الحـمـايـة 𝗭𝗧𝗵𝗼𝗻**\n\n**❌ تـم رفـض** [{user.first_name}](tg://user?id={user.id})\n**🏷 السـبب:** {reason}")
    else:
        await edit_delete(event, f"**⚠️ هـذا الشخـص غيـر مـوافـق عليـه أصـلاً !**")

@zedub.zed_cmd(pattern="بلوك(?:\s|$)([\s\S]*)")
async def block_p_m(event):
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user: return
    if not reason: reason = "**لا يوجـد سبـب 🖕**"

    if pmpermit_sql.is_approved(user.id): pmpermit_sql.disapprove(user.id)
    await event.client(functions.contacts.BlockRequest(user.id))
    await edit_or_reply(event, f"**🖥┊نظــام الحـمـايـة 𝗭𝗧𝗵𝗼𝗻**\n\n**⛔️ تـم حـظـر** [{user.first_name}](tg://user?id={user.id}) **بنجـاح.**\n**🏷 السـبب:** {reason}")

@zedub.zed_cmd(pattern="الغاء بلوك(?:\s|$)([\s\S]*)")
async def unblock_pm(event):
    if event.is_private:
        user = await event.get_chat()
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user: return
    if not reason: reason = "**عـفـو مـلـكـي 🏳️**"

    await event.client(functions.contacts.UnblockRequest(user.id))
    await edit_or_reply(event, f"**🖥┊نظــام الحـمـايـة 𝗭𝗧𝗵𝗼𝗻**\n\n**🔓 تـم الغـاء حـظـر** [{user.first_name}](tg://user?id={user.id})\n**🏷 السـبب:** {reason}")

@zedub.zed_cmd(pattern="المقبولين$")
async def show_approved(event):
    if gvarstatus("pmpermit") is None:
        return await edit_delete(event, f"**⚠️ فعـل الحمايـة أولاً !**")
    approved_users = pmpermit_sql.get_all_approved()
    APPROVED_PMs = "**- 📋 قائمـة النخبـة ( المقبـوليـن ) :**\n\n"
    if len(approved_users) > 0:
        for user in approved_users:
            APPROVED_PMs += f"**• 👤 الاسـم :** {_format.mentionuser(user.first_name , user.user_id)}\n**- الايـدي :** `{user.user_id}`\n**- المعـرف :** @{user.username}\n**- التـاريخ : **__{user.date}__\n**- السـبب : **__{user.reason}__\n\n"
    else:
        APPROVED_PMs = "**- لا يوجـد أحـد يستحـق الثقـة حتـى الآن 🤷🏻‍♂**"
    await edit_or_reply(event, APPROVED_PMs, file_name="قائمـة الحمايـة.txt", caption="**- 🛡 قائمـة المسمـوح لهـم ( المقبوليـن )**\n\n**- سـورس زدثــون** 𝙕𝙏𝙝𝙤𝙣 ")