import os
import random
import asyncio
import aiohttp
from datetime import datetime
from telethon import events, functions, types
from . import zedub
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

# جلب المفتاح من متغيرات ريندر (ai)
AI_KEY = os.getenv("ai", "").strip()

plugin_category = "الادمن"

# الكليشة الملكية (واجهة الاعتزال لأول مرة)
FAV_RESPONSE = "**•❐• لا تـنـتظر رداً .. فـقـد طـويـت صـفحة هـذا الـحسـاب إلـى الأبـد**"

# دالة استدعاء المساعد الوفي (Llama 4 Ultra Speed)
async def get_llama_reply(user_msg, user_name, ret_stamp):
    if not AI_KEY:
        return "**•❐• تـنبيه : مـفتـاح (ai) غـيـر مـوجود فـي ريـندر**"

    # برومبت مكثف لزيادة سرعة المعالجة وتقليل "التفكير"
    system_prompt = (
        f"أنت مساعد وفـي لحساب معتزل منذ {ret_stamp}. "
        f"المراسل: {user_name}. رد بحزن وفخامة وهيبة. "
        "الرد سطر واحد فقط. لغة عربية فصحى عريقة. ممنوع الإيموجي."
    )
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    
    # استخدام موديل الـ Instant للسرعة القصوى
    payload = {
        "model": "llama-3.1-8b-instant", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.5,
        "max_tokens": 100,
        "top_p": 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=5) as response:
                if response.status == 200:
                    res_data = await response.json()
                    ai_text = res_data['choices'][0]['message']['content'].strip()
                    # تنسيق الخط العريض المسحوب (Zedthon Style)
                    return f"**•❐• مـسـاعـد الـحـسـاب (Llama 4-Ultra) :**\n\n**- {ai_text}**"
                else:
                    err = await response.json()
                    return f"**•❐• عطل فني :** `{err.get('error', {}).get('message', 'Unknown')}`"
    except Exception as e:
        return f"**•❐• خـطأ فـي الاتـصـال :** `{str(e)}`"

@zedub.zed_cmd(pattern="^[.,]الاعتزال$")
async def start_retirement(event):
    if gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• وضـع الاعـتزال مـفـعـل بـالـفـعـل**")

    zed = await edit_or_reply(event, "**•❐• جـاري تـنفيـذ مـراسيـم الاعـتزال الـمهيـبـة ..**")
    
    me = await event.client.get_me()
    
    # جلب البايو بطريقة آمنة جداً (إصلاح AttributeError)
    old_bio = ""
    try:
        full = await event.client(functions.users.GetFullUserRequest(me.id))
        old_bio = getattr(full.full_user, 'about', "") or ""
    except:
        pass
    
    # حفظ في SQL
    addgvar("old_first_name", str(me.first_name))
    addgvar("old_last_name", str(me.last_name or ""))
    addgvar("old_bio", str(old_bio))
    addgvar("zed_retired", "true")
    
    now = datetime.now()
    ret_stamp = now.strftime("%Y/%m/%d | %I:%M %p")
    addgvar("ret_timestamp", ret_stamp)

    # 1. إخفاء الصورة عن الجميع (Privacy Mode)
    try:
        await event.client(functions.account.SetPrivacyRequest(
            key=types.InputPrivacyKeyProfilePhoto(),
            rules=[types.InputPrivacyValueDisallowAll()]
        ))
    except:
        pass

    # 2. تغيير الاسم والبايو
    try:
        await event.client(functions.account.UpdateProfileRequest(
            first_name=f"{me.first_name} (معتزل)",
            about=f"هذا الحساب مغلق .. معتزل منذ : {ret_stamp}"
        ))
    except:
        pass

    await zed.edit(f"**• تـم الاعـتزال بـنجـاح ( {ret_stamp} )**\n**• تـم إخـفـاء الـصورة وتـفعيل الـمساعد الـفـوري (Llama 4)**")


@zedub.zed_cmd(pattern="^[.,]الغاء الاعتزال$")
async def stop_retirement(event):
    if not gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• أنـت لـست مـعتـزلاً بـالأسـاس**")

    try:
        # إظهار الصورة للجميع
        await event.client(functions.account.SetPrivacyRequest(
            key=types.InputPrivacyKeyProfilePhoto(),
            rules=[types.InputPrivacyValueAllowAll()]
        ))
        # استعادة الاسم والبايو
        await event.client(functions.account.UpdateProfileRequest(
            first_name=gvarstatus("old_first_name"),
            last_name=gvarstatus("old_last_name") or "",
            about=gvarstatus("old_bio") or ""
        ))
        # تنظيف البيانات
        for key in ["old_first_name", "old_last_name", "old_bio", "zed_retired", "ret_timestamp"]:
            delgvar(key)
        
        await edit_or_reply(event, "**•❐• أهـلاً بـعودتـك .. تـم إلـغاء وضـع الاعـتزال**")
    except Exception as e:
        await edit_or_reply(event, f"**•❐• خـطأ فـي الاسـتعادة :** `{str(e)}`")


# --- المحرك الذكي (Instant Auto-Reply) ---
@zedub.on(events.NewMessage(incoming=True))
async def retirement_ai_watcher(event):
    if not gvarstatus("zed_retired") or event.out:
        return

    me = await event.client.get_me()
    should_reply = False
    
    # يعمل في الخاص وفي الردود داخل المجموعات
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

        # مفتاح الحفظ في SQL
        user_key = f"rl4_{sender.id}"
        
        if gvarstatus(user_key) is None:
            # أول مرة: الهيبة الملكية
            await event.reply(FAV_RESPONSE)
            addgvar(user_key, "y")
        else:
            # المرات القادمة: الرد الفوري من لاما
            ret_stamp = gvarstatus("ret_timestamp") or "2026"
            ai_msg = await get_llama_reply(event.text, sender.first_name, ret_stamp)
            await event.reply(ai_msg)