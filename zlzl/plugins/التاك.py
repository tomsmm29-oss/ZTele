import os
import time
import asyncio
from telethon.tl.types import ChannelParticipantsAdmins
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from . import zedub
from ..core.logger import logging
from ..core.managers import edit_or_reply
from ..helpers.utils import get_user_from_event, reply_id

LOGS = logging.getLogger(__name__)
plugin_category = "الادمن"

# ==========================================
# متغيرات التحكم وقاعدة البيانات المؤقتة
moment_worker = []
stop_search_worker =[]

# ==========================================
# إعداد بوت بايروجرام المساعد وسحب التوكن من Render
API_ID = int(os.environ.get("APP_ID", 6))
API_HASH = os.environ.get("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN") # سحب التوكن من الأسرار في ريندر

# تهيئة البوت فقط في حال وجود التوكن
if BOT_TOKEN:
    pyro_bot = Client(
        "ZThon_Helper_Bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        in_memory=True
    )
else:
    pyro_bot = None
    LOGS.info("⚠️ لم يتم العثور على TG_BOT_TOKEN في متغيرات البيئة.")

# تشغيل البوت المساعد في الخلفية عند تحميل الملف
async def start_helper_bot():
    if pyro_bot:
        try:
            if not pyro_bot.is_initialized:
                await pyro_bot.start()
        except Exception as e:
            LOGS.info(f"ملاحظة بخصوص البوت المساعد: {e}")

asyncio.create_task(start_helper_bot())

# ==========================================
# أزرار الانلاين (بايروجرام) لايقاف العمليات
if pyro_bot:
    @pyro_bot.on_callback_query(filters.regex(r"^stop_search_(.*)"))
    async def stop_search_callback(client, callback_query):
        chat_id = int(callback_query.matches[0].group(1))
        
        if chat_id not in stop_search_worker:
            stop_search_worker.append(chat_id)
            
        await callback_query.answer("⚠️ تم إيقاف الحفر والبحث بنجاح!", show_alert=True)
        await callback_query.message.edit_text(
            "**⪼ تـم إيقـاف عمليـة الحفـر 🛑\n⪼ سيتم البدء بمنشنة من تم جمعهم...**"
        )

    @pyro_bot.on_callback_query(filters.regex(r"^stop_tag_(.*)"))
    async def stop_tag_callback(client, callback_query):
        chat_id = int(callback_query.matches[0].group(1))
        
        if chat_id in moment_worker:
            moment_worker.remove(chat_id)
            
        await callback_query.answer("⚠️ تم تعطيل المنشن بالكامل!", show_alert=True)
        await callback_query.message.edit_text(
            "**⪼ تـم إيقـاف التـاك .. بنجـاح ☑️**"
        )

# ==========================================
# أوامر التليثون (سورس زدثون)

@zedub.zed_cmd(pattern="ايقاف التاك$")
async def stop_tagall(event):
    global moment_worker
    if event.chat_id not in moment_worker:
        return await edit_or_reply(event, '**- عـذراً .. لا يوجـد هنـاك تـاك لـ إيقـافـه ؟!**')

    moment_worker.remove(event.chat_id)
    return await edit_or_reply(event, '**⎉╎تم إيقـاف التـاك .. بنجـاح ✓**')


@zedub.zed_cmd(pattern="(all|تاك)(?: |$)(.*)")
async def tagall(event):
    global moment_worker, stop_search_worker

    if event.is_private:
        return await edit_or_reply(event, "**- عـذراً ... هـذه ليـست مجمـوعـة ؟!**")

    text = event.pattern_match.group(2).strip()
    reply_msg = None

    if text:
        mode = "cmd"
    elif event.reply_to_msg_id:
        mode = "reply"
        reply_msg = await event.get_reply_message()
        if reply_msg is None:
            return await edit_or_reply(event, "**- عـذراً ... الرسـالة غيـر ظـاهـرة للأعضـاء الجـدد ؟!**")
    else:
        return await edit_or_reply(event, "**- بالـرد عـلى رسـالـه . . او باضـافة نـص مـع الامـر**")

    chat = await event.get_chat()
    moment_worker.append(event.chat_id)
    if event.chat_id in stop_search_worker:
        stop_search_worker.remove(event.chat_id)

    # التحقق هل الأعضاء مخفيين؟
    try:
        participants = await event.client.get_participants(event.chat_id, limit=200)
        total_participants = chat.participants_count if hasattr(chat, 'participants_count') else len(participants)
    except:
        participants =[]
        total_participants = 0

    unique_users = {} # قاموس لمنع التكرار نهائياً

    # ==========================================
    # النضام الثاني: نظام الحفر العملاق والمخيف (V2)
    if len(participants) < 50 and total_participants > 50:
        await event.delete()
        
        klaisha = (
            "🖥┊لـوحـة اوامـر **𝗭𝗧𝗵𝗼𝗻** الشفـافـه\n"
            "🧑🏻‍💻┊المستخـدم ↶ 𝑉𝑋\n\n"
            "╮ ❐... جـاࢪِ حـفـࢪ المجمـوعـة ...❏╰\n"
            "⪼ حـالـة الاعضـاء : **مخفييـن** 🚷\n"
            "⪼ تـم إيجـاد : **{count}** عضـو 👤\n"
            "⪼ السـرعـة : **جنـونيـة** 🚀"
        )
        
        keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("إيقاف البحث 🛑", callback_data=f"stop_search_{event.chat_id}"),
                InlineKeyboardButton("إيقاف المنشن 🚫", callback_data=f"stop_tag_{event.chat_id}")
            ]
        ])

        bot_msg = None
        if pyro_bot:
            try:
                bot_msg = await pyro_bot.send_message(
                    event.chat_id, 
                    klaisha.format(count=0), 
                    reply_markup=keyboard
                )
            except Exception:
                await event.client.send_message(event.chat_id, "**⚠️ جاري الحفر الجبار... (يُرجى رفع البوت المساعد أدمن لظهور الأزرار)**")

        # 🚀 بدء الحفر بسرعة الضوء 🚀
        count = 0
        last_update_time = time.time() # نستخدم الوقت بدلاً من عدد الرسائل لتجنب البطء

        async for msg in event.client.iter_messages(event.chat_id, limit=None):
            if event.chat_id in stop_search_worker or event.chat_id not in moment_worker:
                break
                
            sender = msg.sender
            if sender and not sender.bot:
                if sender.id not in unique_users:
                    # حفظ البيانات: اليوزر إن وجد، وإلا الاسم
                    unique_users[sender.id] = {
                        "username": sender.username,
                        "name": sender.first_name or "مستخدم"
                    }
                    count += 1
                    
            # تحديث الكليشة كل ثانيتين فقط لتجنب إبطاء الحفر (سرعة مجنونة)
            current_time = time.time()
            if bot_msg and (current_time - last_update_time > 2.0):
                try:
                    await pyro_bot.edit_message_text(
                        event.chat_id, 
                        bot_msg.id, 
                        klaisha.format(count=count),
                        reply_markup=keyboard
                    )
                except:
                    pass
                last_update_time = current_time

        if bot_msg:
            try:
                await pyro_bot.edit_message_text(
                    event.chat_id, 
                    bot_msg.id, 
                    f"**⪼ تـم الانتهـاء مـن الحـفـر بنجـاح ☑️\n⪼ إجمـالي مـن تـم سحبهـم : {count} عضـو 👤\n⪼ جـاࢪِ بـدء المنشـن ...**",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("إيقاف المنشن 🚫", callback_data=f"stop_tag_{event.chat_id}")
                    ]])
                )
            except:
                pass

    # ==========================================
    # النظام الأول: طبيعي (أو إكمال المنشن بعد الحفر)
    else:
        for usr in participants:
            if not usr.bot:
                unique_users[usr.id] = {
                    "username": usr.username,
                    "name": usr.first_name or "مستخدم"
                }

    # ==========================================
    # بــــدء المـنشــــن (النظام الذكي)
    usrnum = 0
    usrtxt = ""

    for user_id, user_data in unique_users.items():
        if event.chat_id not in moment_worker:
            break

        # إذا كان لديه يوزر نمنشنه باليوزر، وإلا ماركداون بالاسم
        if user_data["username"]:
            usrtxt += f"- @{user_data['username']} \n"
        else:
            usrtxt += f"- [{user_data['name']}](tg://user?id={user_id}) \n"
            
        usrnum += 1

        if usrnum == 5:
            if mode == "cmd":
                await event.client.send_message(event.chat_id, f"{usrtxt}\n- {text}")
            else:
                await event.client.send_message(event.chat_id, usrtxt, reply_to=reply_msg.id)

            await asyncio.sleep(2) # حماية السورس من الباند أثناء الإرسال
            usrnum = 0
            usrtxt = ""

    if usrnum > 0 and event.chat_id in moment_worker:
        if mode == "cmd":
            await event.client.send_message(event.chat_id, f"{usrtxt}\n- {text}")
        else:
            await event.client.send_message(event.chat_id, usrtxt, reply_to=reply_msg.id)

    if event.chat_id in moment_worker:
        moment_worker.remove(event.chat_id)


@zedub.zed_cmd(pattern="تبليغ$")
async def tag_admins(event):
    mentions = "- انتباه الى المشرفين تم تبليغكم \n@admin"
    chat = await event.get_input_chat()
    reply_to_id = await reply_id(event)
    async for x in event.client.iter_participants(chat, filter=ChannelParticipantsAdmins):
        if not x.bot:
            mentions += f"[\u2063](tg://user?id={x.id})"
    await event.client.send_message(event.chat_id, mentions, reply_to=reply_to_id)
    await event.delete()


@zedub.zed_cmd(pattern="منشن ([\s\S]*)")
async def mention_user(event):
    user, input_str = await get_user_from_event(event)
    if not user:
        return
    reply_to_id = await reply_id(event)
    await event.delete()
    await event.client.send_message(
        event.chat_id,
        f"<a href='tg://user?id={user.id}'>{input_str}</a>",
        parse_mode="HTML",
        reply_to=reply_to_id,
    )