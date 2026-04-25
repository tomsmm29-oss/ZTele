import random
import asyncio
import aiohttp
from datetime import datetime
from telethon import events, functions, types
from . import zedub
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

plugin_category = "الادمن"

# الكليشة الملكية (ترسل مرة واحدة فقط لكل مستخدم)
FAV_RESPONSE = "**•❐• لا تـنـتظر رداً .. فـقـد طـويـت صـفحة هـذا الـحسـاب إلـى الأبـد**"

# دالة استدعاء Llama 4 (سيرفر جديد ومستقر)
async def get_llama_assistant_reply(user_msg, user_name, ret_stamp):
    # برومبت المساعد الوفي بأسلوب زدثون
    system_prompt = (
        f"أنت 'مساعد الحساب' الوفي لشخص اعتزل في {ret_stamp}. "
        f"المستخدم اسمه {user_name}. "
        "رد بأسلوب حزين وفخم لأنك تشتاق لصاحب الحساب. "
        "أخبرهم أنك هنا لحماية ذكراه فقط. سطر واحد، فصحى، بدون إيموجي."
    )
    
    # سيرفر معالجة سريع جداً ومستقر
    url = "https://duckduckgo.com/duckduckgo-messaging-v1" # مثال لمحرك بحث يدعم الذكاء، لكن سنستخدم API عامل
    api_url = "https://api.pawan.krd/cosmosrp/v1/chat/completions" # API بديل مستقر
    
    # ملاحظة: سنستخدم الـ Worker البديل بطريقة POST لضمان الاستجابة
    worker_url = "https://darkness.ashlynn.workers.dev/chat/"
    
    try:
        async with aiohttp.ClientSession() as session:
            # طلب البيانات بطريقة POST لضمان وصول البرومبت كاملاً
            payload = {
                "model": "llama-4-70b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            }
            async with session.get(worker_url, params={"prompt": user_msg, "system": system_prompt}, timeout=7) as response:
                if response.status == 200:
                    res_json = await response.json()
                    ai_text = res_json.get("response", "")
                    if ai_text:
                        # تنسيق الخط بأسلوب زدثون الفخم
                        return f"**•❐• مـسـاعـد الـحـسـاب (Llama 4) :**\n\n**- {ai_text}**"
        return "**•❐• عـذراً .. المـساعد يـشعر بـالحـزن ولا يـستطيـع الـرد الآن**"
    except:
        return "**•❐• عـذراً .. المـساعد يـشعر بـالحـزن ولا يـستطيـع الـرد الآن**"

@zedub.zed_cmd(pattern="^[.,]الاعتزال$")
async def start_retirement(event):
    if gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• وضـع الاعـتزال مـفـعـل بـالـفـعـل**")

    zed = await edit_or_reply(event, "**•❐• جـاري تـنفيـذ مـراسيـم الاعـتزال وإغـلاق الـحساب ..**")
    
    me = await event.client.get_me()
    
    # جلب البايو بطريقة آمنة لتجاوز خطأ AttributeError
    old_bio = ""
    try:
        full = await event.client(functions.users.GetFullUserRequest(me.id))
        old_bio = getattr(full.full_user, 'about', "") or ""
    except:
        pass
    
    addgvar("old_first_name", me.first_name)
    addgvar("old_last_name", me.last_name or "")
    addgvar("old_bio", old_bio)
    addgvar("zed_retired", "true")
    
    now = datetime.now()
    ret_stamp = now.strftime("%Y/%m/%d | %I:%M %p")
    addgvar("ret_timestamp", ret_stamp)

    # 1. إخفاء الصورة عن الجميع
    try:
        await event.client(functions.account.SetPrivacyRequest(
            key=types.InputPrivacyKeyProfilePhoto(),
            rules=[types.InputPrivacyValueDisallowAll()]
        ))
    except:
        pass

    # 2. تغيير الاسم والوصف
    try:
        await event.client(functions.account.UpdateProfileRequest(
            first_name=f"{me.first_name} (معتزل)",
            about=f"مغلق .. معتزل منذ : {ret_stamp}"
        ))
    except:
        pass

    await zed.edit(f"**• تـم الاعـتزال بـنجـاح ( {ret_stamp} )**\n**• تـم إخـفـاء الـصورة وتـفعيل الـمساعد الـوفـي (Llama 4)**")


@zedub.zed_cmd(pattern="^[.,]الغاء الاعتزال$")
async def stop_retirement(event):
    if not gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• أنـت لـست مـعتـزلاً بـالأسـاس**")

    # 1. إظهار الصورة للجميع
    try:
        await event.client(functions.account.SetPrivacyRequest(
            key=types.InputPrivacyKeyProfilePhoto(),
            rules=[types.InputPrivacyValueAllowAll()]
        ))
    except:
        pass

    # 2. استعادة البيانات
    try:
        await event.client(functions.account.UpdateProfileRequest(
            first_name=gvarstatus("old_first_name"),
            last_name=gvarstatus("old_last_name") or "",
            about=gvarstatus("old_bio") or ""
        ))
        for key in ["old_first_name", "old_last_name", "old_bio", "zed_retired", "ret_timestamp"]:
            delgvar(key)
    except:
        pass

    await edit_or_reply(event, "**•❐• أهـلاً بـعودتـك .. تـم إلـغاء وضـع الاعـتزال وإعـادة كـافة الإعـدادات**")


# --- المراقب (الردود التلقائية) ---
@zedub.on(events.NewMessage(incoming=True))
async def retirement_ai_watcher(event):
    if not gvarstatus("zed_retired") or event.out:
        return

    me = await event.client.get_me()
    should_reply = False
    
    if event.is_private:
        should_reply = True
    elif event.is_group and event.reply_to:
        reply_msg = await event.get_reply_message()
        if reply_msg and reply_msg.sender_id == me.id:
            should_reply = True

    if should_reply:
        sender = await event.get_sender()
        if not sender or sender.bot:
            return

        # نستخدم مفتاح SQL قصير لضمان الحفظ
        user_key = f"r_{sender.id}"
        ret_stamp = gvarstatus("ret_timestamp") or "2026"
        user_name = sender.first_name

        if not gvarstatus(user_key):
            # أول مرة: الكليشة الملكية
            await event.reply(FAV_RESPONSE)
            addgvar(user_key, "y")
        else:
            # المرات القادمة: لاما يرد
            ai_msg = await get_llama_assistant_reply(event.text, user_name, ret_stamp)
            await event.reply(ai_msg)