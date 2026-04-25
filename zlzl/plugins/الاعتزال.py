import os
import random
import asyncio
import aiohttp
from datetime import datetime
from telethon import events, functions, types
from . import zedub
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

# جلب مفتاح الـ API من متغيرات ريندر (Secrets)
AI_KEY = os.getenv("ai")

plugin_category = "الادمن"

# الكليشة الملكية (واجهة الاعتزال لأول مرة)
FAV_RESPONSE = "**•❐• لا تـنـتظر رداً .. فـقـد طـويـت صـفحة هـذا الـحسـاب إلـى الأبـد**"

# دالة استدعاء المساعد الوفي (Llama 3.1 عبر Groq)
async def get_llama_reply(user_msg, user_name, ret_stamp):
    if not AI_KEY:
        return "**•❐• خطأ : يرجى إضافة متغير 'ai' في إعدادات ريندر ووضع مفتاح Groq فيه**"

    system_prompt = (
        f"أنت 'مساعد الحساب' الوفي لشخص اعتزل في {ret_stamp}. "
        f"المستخدم اسمه {user_name}. رد بنبرة حزينة وفخمة تعبر عن وفائك للمالك الراحل. "
        "أخبرهم أنك هنا فقط لحماية حسابه وذكراه. الرحيل كان قراراً صعباً للمالك. "
        "ردك يجب أن يكون سطر واحد فقط، فخماً، لغة عربية فصحى، وبدون إيموجي نهائياً."
    )
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.6,
        "max_tokens": 150
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    ai_text = data['choices'][0]['message']['content'].strip()
                    # تنسيق الخط بأسلوب زدثون الفخم
                    return f"**•❐• مـسـاعـد الـحـسـاب (Llama 3.1) :**\n\n**- {ai_text}**"
        return "**•❐• المـساعد مـشغول بـحمايـة ذكـريـات الـمالك الآن ..**"
    except:
        return "**•❐• المـساعد يـشعر بـالأسى ولا يـستطيـع الـرد فـي هـذه اللـحظة ..**"

@zedub.zed_cmd(pattern="^[.,]الاعتزال$")
async def start_retirement(event):
    if gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• وضـع الاعـتزال مـفـعـل بـالـفـعـل**")

    zed = await edit_or_reply(event, "**•❐• جـاري تـنفيـذ مـراسيـم الاعـتزال وإغـلاق الـحساب ..**")
    
    me = await event.client.get_me()
    
    # جلب البايو بطريقة آمنة
    old_bio = ""
    try:
        full = await event.client(functions.users.GetFullUserRequest(me.id))
        old_bio = getattr(full.full_user, 'about', "") or ""
    except:
        pass
    
    # حفظ البيانات في SQL
    addgvar("old_first_name", me.first_name)
    addgvar("old_last_name", me.last_name or "")
    addgvar("old_bio", old_bio)
    addgvar("zed_retired", "true")
    
    now = datetime.now()
    ret_stamp = now.strftime("%Y/%m/%d | %I:%M %p")
    addgvar("ret_timestamp", ret_stamp)

    # 1. إخفاء الصورة عن الجميع فوراً
    try:
        await event.client(functions.account.SetPrivacyRequest(
            key=types.InputPrivacyKeyProfilePhoto(),
            rules=[types.InputPrivacyValueDisallowAll()]
        ))
    except:
        pass

    # 2. تغيير الاسم والنبذة (البايو)
    try:
        await event.client(functions.account.UpdateProfileRequest(
            first_name=f"{me.first_name} (معتزل)",
            about=f"هذا الحساب مغلق .. معتزل منذ : {ret_stamp}"
        ))
    except:
        pass

    await zed.edit(f"**• تـم الاعـتزال بـنجـاح ( {ret_stamp} )**\n**• تـم إخـفـاء الـصورة وتـفعيل الـمساعد الـوفـي (Llama)**")


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

    # 2. استعادة البيانات الأصلية
    try:
        await event.client(functions.account.UpdateProfileRequest(
            first_name=gvarstatus("old_first_name"),
            last_name=gvarstatus("old_last_name") or "",
            about=gvarstatus("old_bio") or ""
        ))
        # تنظيف قاعدة البيانات
        for key in ["old_first_name", "old_last_name", "old_bio", "zed_retired", "ret_timestamp"]:
            delgvar(key)
    except:
        pass

    await edit_or_reply(event, "**•❐• أهـلاً بـعودتـك .. تـم إلـغاء وضـع الاعـتزال وإعـادة كـافة الإعـدادات**")


# --- المراقب الذكي (الردود التلقائية) ---
@zedub.on(events.NewMessage(incoming=True))
async def retirement_ai_watcher(event):
    if not gvarstatus("zed_retired") or event.out:
        return

    me = await event.client.get_me()
    should_reply = False
    
    # الرد في الخاص أو الرد على رسائلك في المجموعات
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

        user_key = f"r_log_{sender.id}"
        ret_stamp = gvarstatus("ret_timestamp") or "2026"
        user_name = sender.first_name

        if not gvarstatus(user_key):
            # لأول مرة يراسلنا: يوصله رد الهيبة
            await event.reply(FAV_RESPONSE)
            addgvar(user_key, "y")
        else:
            # المرات القادمة: يتحدث معه مساعد Llama الوفي
            ai_msg = await get_llama_reply(event.text, user_name, ret_stamp)
            await event.reply(ai_msg)