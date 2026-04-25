import os
import random
import asyncio
import aiohttp
from datetime import datetime
from telethon import events, functions, types
from . import zedub
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

# جلب المفتاح مع تنظيفه من أي مسافات زائدة
AI_KEY = os.getenv("ai", "").strip()

plugin_category = "الادمن"
FAV_RESPONSE = "**•❐• لا تـنـتظر رداً .. فـقـد طـويـت صـفحة هـذا الـحسـاب إلـى الأبـد**"

async def get_llama_reply(user_msg, user_name, ret_stamp):
    if not AI_KEY:
        return "**•❐• تـنبيه : مـفتـاح (ai) غـيـر مـوجود فـي ريـندر .. ضـعه بـاسـم ai كـاملاً**"

    # برومبت مختصر جداً لضمان السرعة وعدم الرفض
    system_prompt = (
        f"أنت مساعد حساب لشخص اعتزل في {ret_stamp}. رد بحزن وفخر بمالك الحساب. "
        "اجعل الرد سطر واحد فقط باللغة العربية الفصحى. بدون إيموجي. خط عريض."
    )
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }
    
    # استخدام الموديل الأكثر استقراراً في 2026
    payload = {
        "model": "llama3-70b-8192", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers, timeout=10) as response:
                res_data = await response.json()
                if response.status == 200:
                    ai_text = res_data['choices'][0]['message']['content'].strip()
                    # تنسيق زدثون الفخم
                    return f"**•❐• مـسـاعـد الـحـسـاب (Llama 4) :**\n\n**- {ai_text}**"
                else:
                    # إظهار رسالة الخطأ القادمة من Groq مباشرة لتعرف السبب
                    error_msg = res_data.get('error', {}).get('message', 'Unknown Error')
                    return f"**•❐• عطل في الذكاء :** `{error_msg}`"
    except Exception as e:
        return f"**•❐• خـطأ فـي الاتـصـال :** `{str(e)}`"

@zedub.zed_cmd(pattern="^[.,]الاعتزال$")
async def start_retirement(event):
    if gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• وضـع الاعـتزال مـفـعـل بـالـفـعـل**")

    zed = await edit_or_reply(event, "**•❐• جـاري تـنفيـذ مـراسيـم الاعـتزال ..**")
    
    me = await event.client.get_me()
    
    # جلب البايو
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

    # إخفاء الصورة
    try:
        await event.client(functions.account.SetPrivacyRequest(
            key=types.InputPrivacyKeyProfilePhoto(),
            rules=[types.InputPrivacyValueDisallowAll()]
        ))
    except:
        pass

    # تحديث البروفايل
    try:
        await event.client(functions.account.UpdateProfileRequest(
            first_name=f"{me.first_name} (معتزل)",
            about=f"مغلق .. معتزل منذ : {ret_stamp}"
        ))
    except:
        pass

    await zed.edit(f"**• تـم الاعـتزال بـنجـاح ( {ret_stamp} )**\n**• تـم إخـفـاء الـصورة وتـفعيل الـمساعد الـوفـي (Llama)**")


@zedub.zed_cmd(pattern="^[.,]الغاء الاعتزال$")
async def stop_retirement(event):
    if not gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• أنـت لـست مـعتـزلاً**")

    try:
        # إظهار الصورة
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
        # تنظيف الداتابيز
        for key in ["old_first_name", "old_last_name", "old_bio", "zed_retired", "ret_timestamp"]:
            delgvar(key)
        
        await edit_or_reply(event, "**•❐• أهـلاً بـعودتـك .. تـم إلـغاء وضـع الاعـتزال**")
    except Exception as e:
        await edit_or_reply(event, f"**•❐• خـطأ فـي الاسـتعادة :** `{str(e)}`")


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

        user_key = f"ret_usr_{sender.id}"
        
        if gvarstatus(user_key) is None:
            # أول رسالة: الكليشة الملكية
            await event.reply(FAV_RESPONSE)
            addgvar(user_key, "done")
        else:
            # المرات القادمة: لاما يرد
            ret_stamp = gvarstatus("ret_timestamp") or "2026"
            ai_msg = await get_llama_reply(event.text, sender.first_name, ret_stamp)
            await event.reply(ai_msg)