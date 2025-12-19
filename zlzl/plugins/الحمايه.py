# 🚬 ZThon PM Permit - Official Luxury Edition 2025
# By Mikey & Kalvari 🍁
# المسار: zlzl/plugins/الحمايه.py

import os
import asyncio
import random
from datetime import datetime

from telethon import functions
from telethon.utils import get_display_name

# 👇 استدعاءات السورس الصحيحة (zlzl)
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

# =========================
# 🏗 إعداد الحارس المستقل (Pyrogram)
# =========================
api_id = zedub.api_id
api_hash = zedub.api_hash
bot_token = os.environ.get("TG_BOT_TOKEN") or os.environ.get("BOT_TOKEN")

pm_guard = Client(
    name="zthon_pm_guard",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    in_memory=True
)

async def start_guard():
    if bot_token:
        try:
            await pm_guard.start()
            print("🚬 Mikey: تم تفعيل نظام الحماية (ZThon Guard) بنجاح!")
        except Exception as e:
            print(f"🚬 Mikey Error: {e}")

zedub.loop.create_task(start_guard())

# =========================
# ⚙️ إعدادات التحذيرات
# =========================
MAX_FLOOD = 4  # (1:قائمة، 2:تنبيه، 3:اخير، 4:بلوك)

# =========================
# 🎮 هندسة الزراير
# =========================
def get_pm_keyboard(user_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⤶ لـ إسـتـفـسـار مـعـيـن", callback_data=f"to_enquire|{user_id}")],
        [InlineKeyboardButton("⤶ لـ طـلـب مـعـيـن", callback_data=f"to_request|{user_id}")],
        [InlineKeyboardButton("⤶ لـ الـدردشــه فـقـط", callback_data=f"to_chat|{user_id}")],
        [InlineKeyboardButton("⤶ لـ إزعـاجـي فـقـط", callback_data=f"to_spam|{user_id}")],
    ])

# =========================
# 🔥 المنطق الرئيسي (The Core)
# =========================

async def do_pm_permit_action(event, chat):
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except AttributeError: PM_WARNS = {}
    
    try:
        PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
    except AttributeError: PMMESSAGE_CACHE = {}
        
    me = await event.client.get_me()
    mention = f"[{chat.first_name}](tg://user?id={chat.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    
    if str(chat.id) not in PM_WARNS:
        PM_WARNS[str(chat.id)] = 0
    
    warns = PM_WARNS[str(chat.id)] + 1

    # -----------------------------------------------------
    # ☠️ مرحلة الحظر (Strike 4)
    # -----------------------------------------------------
    if warns >= MAX_FLOOD:
        await block_user_final(event, chat, my_mention, "تجـاهـل التحذيـرات واستمـر بـالإزعـاج")
        return

    # -----------------------------------------------------
    # ⚠️ مراحل التحذير (1, 2, 3)
    # -----------------------------------------------------
    
    # التحذير الثالث (الأخير) - الجدية التامة
    if warns == 3:
        WARNING_MSG = f"""
**⛔️ لـسـت مـتـفـرغـاً لـتـراهـاتـك !**

**⤶ هـذا هـو تـحـذيـرك الأخيـر ..   🏴‍☠️**
**⤶ ❨ لـديـك {warns} مـن 3 تـحـذيـرات ⚠️❩**

**⤶ رسـالـة واحـدة أخـرى وسـيـتـم تـفـعـيـل الـحـظـر التلقـائـي 🚷**
"""
    
    # التحذير الثاني - تنبيه
    elif warns == 2:
        WARNING_MSG = f"""
**⚠️ تـنـبـيــه هــام !**

**⤶ لـقـد طـلـبـت مـنـك الانتـظـار .. التكـرار لـن يفيـدك.**
**⤶ ❨ لـديـك {warns} مـن 3 تـحـذيـرات ⚠️❩**

**⤶ الـرجـاء عـدم تـكـرار الـرسـائـل لـتجـنـب الـحـظـر.**
"""

    # التحذير الأول (الترحيب الرسمي الفخم)
    else:
        WARNING_MSG = f"""
ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 **- الـرد التلقـائي 〽️**
**•─────────────────•**

❞ **مـرحبـاً بـك عـزيـزي**  {mention} ❝

**⤶ قـد اكـون مشغـول او غيـر موجـود حـاليـاً ؟!**
**⤶ ❨ لـديـك {warns} مـن 3 تـحـذيـرات ⚠️❩**
**⤶ الـرجـاء عـدم الإزعـاج لـتجـنـب الـحـظـر التـلـقـائـي . . .**

**👇🏻 إخـتـر سـبـب مـراسـلـتـك مـن الأسـفـل :**
"""

    # زيادة العداد وحفظه
    PM_WARNS[str(chat.id)] = warns
    sql.del_collection("pmwarns")
    sql.add_collection("pmwarns", PM_WARNS, {})

    # إرسال الرسالة (بايروجرام للأولى، تليثون للباقي لضمان الوصول)
    try:
        if str(chat.id) in PMMESSAGE_CACHE:
            await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
            del PMMESSAGE_CACHE[str(chat.id)]
    except: pass

    try:
        if warns == 1: # الأولى بس هي اللي فيها زراير
            msg = await pm_guard.send_message(
                chat.id,
                WARNING_MSG,
                reply_markup=get_pm_keyboard(chat.id)
            )
            PMMESSAGE_CACHE[str(chat.id)] = msg.id
        else:
            msg = await event.reply(WARNING_MSG)
            PMMESSAGE_CACHE[str(chat.id)] = msg.id
    except Exception as e:
        LOGS.error(str(e))
        msg = await event.reply(WARNING_MSG)
        PMMESSAGE_CACHE[str(chat.id)] = msg.id

    sql.del_collection("pmmessagecache")
    sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})


# =========================
# 🚫 دالة البلوك النهائية (Execution)
# =========================
async def block_user_final(event, chat, my_mention, reason):
    try:
        PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    
    # رسالة البلوك الفخمة (بنفس ستايل زدثون)
    USER_BOT_WARN_ZERO = f"""
**⤶ لقـد حذرتـڪ مـسـبـقـاً مـن الـتـڪـرار 📵** 
**⤶ تـم حـظـرڪ تلقـائيـاً .. الان لا يـمـڪـنـڪ ازعـاجـي🔕**

**⤶ تحيـاتـي {my_mention} 🫡**
"""
    await event.reply(USER_BOT_WARN_ZERO)
    await event.client(functions.contacts.BlockRequest(chat.id))
    
    the_message = f"#حمـايـة_الخـاص\n** ⎉╎المستخـدم** [{get_display_name(chat)}](tg://user?id={chat.id}) .\n** ⎉╎تم حظـره .. تلقائيـاً**\n** ⎉╎السبب:** {reason}"
    
    if str(chat.id) in PM_WARNS: del PM_WARNS[str(chat.id)]
    sql.del_collection("pmwarns")
    sql.add_collection("pmwarns", PM_WARNS, {})
    
    try:
        if BOTLOG_CHATID:
            await event.client.send_message(BOTLOG_CHATID, the_message)
    except: pass


# =========================
# 🔥 معالجات الزراير (Pyrogram Callbacks)
# =========================

@pm_guard.on_callback_query()
async def pm_callbacks(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    try:
        target_id = int(data.split("|")[1])
        if user_id != target_id: return
    except: pass

    # 1. الاستفسار
    if data.startswith("to_enquire"):
        text = "**⤶ حـسـنـاً عـزيـزي ، تـم أرسـال إسـتـفـسـارك بـنـجـاح 📨 .\n⤶ الـرجـاء الإنـتـظـار وعـدم الـتـكـرار .🧸🤍**"
        sqllist.add_to_list("pmenquire", user_id)
        await callback_query.edit_message_text(text)

    # 2. الطلب
    elif data.startswith("to_request"):
        text = "**⤶ تـم رفـع طـلـبـك إلـى الـمـالـك 📥 .\n⤶ عـنـدمـا يـكـون مـتـاحـاً سـيـقـوم بـالـرد عـلـيـك .. إنـتـظـر ⏳**"
        sqllist.add_to_list("pmrequest", user_id)
        await callback_query.edit_message_text(text)

    # 3. الدردشة
    elif data.startswith("to_chat"):
        text = "**⤶ الـمـالـك لـيـس فـي مـزاج للـدردشـة الآن 🤷🏻‍♂ .\n⤶ أترك رسـالـتـك وسـيـتـم الـرد إذا كـان الأمـر مـهـمـاً .**"
        sqllist.add_to_list("pmchat", user_id)
        await callback_query.edit_message_text(text)

    # 4. الإزعاج
    elif data.startswith("to_spam"):
        text = "**⤶ لـقـد إخـتـرت الإزعـاج بـإرادتـك .\n⤶ وهـذا هـو تـحـذيـرك الأخـيـر .. الـحـظـر قـادم 🚷**"
        sqllist.add_to_list("pmspam", user_id)
        # نخلي العداد 3 عشان المرة الجاية بلوك علطول
        set_warns_limit(user_id, 3) 
        await callback_query.edit_message_text(text)

    # تصفير العداد مؤقتاً (إلا لو اختار ازعاج)
    if not data.startswith("to_spam"):
        reset_warns_safe(user_id)


# =========================
# 🛠 دوال مساعدة (Utils)
# =========================
def set_warns_limit(user_id, count):
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    PM_WARNS[str(user_id)] = count
    sql.del_collection("pmwarns")
    sql.add_collection("pmwarns", PM_WARNS, {})

def reset_warns_safe(user_id):
    try: PM_WARNS = sql.get_collection("pmwarns").json
    except: PM_WARNS = {}
    if str(user_id) in PM_WARNS:
        del PM_WARNS[str(user_id)]
        sql.del_collection("pmwarns")
        sql.add_collection("pmwarns", PM_WARNS, {})


# =========================
# 📬 مراقب الرسائل الواردة
# =========================
@zedub.zed_cmd(incoming=True, func=lambda e: e.is_private, edited=False, forword=None)
async def on_new_private_message(event):
    if gvarstatus("pmpermit") is None:
        return
    
    chat = await event.get_chat()
    # قائمة المطورين
    zel_dev = [8241311871, 5176749470, 5426390871, 925972505, 1895219306, 2095357462, 5280339206]
    
    if event.chat_id in zel_dev or chat.bot or chat.verified:
        return
    if pmpermit_sql.is_approved(chat.id):
        return

    # دوال العقاب لمن يخالف بعد الاختيار
    me = await event.client.get_me()
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"

    if str(chat.id) in sqllist.get_collection_list("pmspam"):
        await block_user_final(event, chat, my_mention, "إخـتـار خيـار الإزعـاج")
        return
    if str(chat.id) in sqllist.get_collection_list("pmchat"):
        await block_user_final(event, chat, my_mention, "إخـتـار الـدردشـة وإستـمـر بـالإزعـاج")
        return
    if str(chat.id) in sqllist.get_collection_list("pmrequest"):
        await block_user_final(event, chat, my_mention, "إخـتـار الطـلـب وإستـمـر بـالتكـرار")
        return
    if str(chat.id) in sqllist.get_collection_list("pmenquire"):
        await block_user_final(event, chat, my_mention, "إخـتـار الإستـفـسـار وإستـمـر بـالتكـرار")
        return
    
    # لو مستخدم جديد أو لسه مختارش
    await do_pm_permit_action(event, chat)


# =========================
# 📤 الموافقة التلقائية عند الرد
# =========================
@zedub.zed_cmd(outgoing=True, func=lambda e: e.is_private, edited=False, forword=None)
async def you_dm_other(event):
    if gvarstatus("pmpermit") is None:
        return
    chat = await event.get_chat()
    if chat.bot or chat.verified: return
    if event.text and event.text.startswith(cmdhd): return

    if not pmpermit_sql.is_approved(chat.id):
        start_date = str(datetime.now().strftime("%B %d, %Y"))
        pmpermit_sql.approve(chat.id, get_display_name(chat), start_date, chat.username, "موافقة تلقائية")
        try:
            # تنظيف
            PMMESSAGE_CACHE = sql.get_collection("pmmessagecache").json
            if str(chat.id) in PMMESSAGE_CACHE:
                try: await event.client.delete_messages(chat.id, PMMESSAGE_CACHE[str(chat.id)])
                except: pass
                del PMMESSAGE_CACHE[str(chat.id)]
            sql.del_collection("pmmessagecache")
            sql.add_collection("pmmessagecache", PMMESSAGE_CACHE, {})
        except: pass


# =========================
# ⚙️ أوامر التحكم
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
        # تنظيف القوائم
        try:
            for lst in ["pmspam", "pmchat", "pmrequest", "pmenquire", "pmoptions"]:
                sqllist.rm_from_list(lst, user.id)
            PM_WARNS = sql.get_collection("pmwarns").json
            if str(user.id) in PM_WARNS: del PM_WARNS[str(user.id)]
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
    if pmpermit_sql.is_approved(user.id): pmpermit_sql.disapprove(user.id)
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
    await edit_or_reply(event, APPROVED_PMs, file_name="قائمـة الحمايـة.txt", caption="**- 🛡 قائمـة المسمـوح لهـم ( المقبوليـن )**\n\n**- سـورس زدثــون** 𝙕𝙏𝙝𝙤𝙣 ")