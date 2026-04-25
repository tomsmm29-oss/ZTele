import random
import asyncio
import aiohttp
from datetime import datetime
from telethon import events, functions, types
from . import zedub
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

plugin_category = "الادمن"

# الكليشة الملكية (واجهة الاعتزال لأول مرة)
FAV_RESPONSE = "**•❐• لا تـنـتظر رداً .. فـقـد طـويـت صـفحة هـذا الـحسـاب إلـى الأبـد**"

# برومبت Llama 4 (المساعد الوفي الحزين)
async def get_llama_assistant_reply(user_msg, user_name, ret_stamp):
    system_prompt = (
        f"أنت 'مساعد الحساب' الوفي. اعتزل صاحب هذا الحساب في {ret_stamp}. "
        f"المستخدم الذي يراسلنا اسمه {user_name}. "
        "مهمتك: الرد بنبرة حزينة جداً لرحيل صاحب الحساب. أنت وفيّ ومهذب وتشتاق للمالك. "
        "أخبرهم أنك هنا فقط لحماية حسابه وذكراه وأن الرحيل كان قراراً صعباً. "
        "اجعل الردود فخمة، قصيرة جداً (سطر واحد)، وباللغة العربية الفصحى. "
        "ممنوع استخدام الإيموجي. ردك يجب أن يكون نصاً جاداً."
    )
    
    url = "https://darkness.ashlynn.workers.dev/chat/"
    params = {
        "prompt": user_msg,
        "model": "llama-4-70b",
        "system": system_prompt
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=4) as response:
                if response.status == 200:
                    data = await response.json()
                    ai_text = data.get("response", "")
                    # تنسيق الخط بأسلوب زدثون (عريض مع شرطة)
                    return f"**•❐• مـسـاعـد الـحـسـاب (llama ) :**\n\n**- {ai_text}**"
                return FAV_RESPONSE
    except:
        return FAV_RESPONSE

@zedub.zed_cmd(pattern="^[.,]الاعتزال$")
async def start_retirement(event):
    if gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• وضـع الاعـتزال مـفـعـل بـالـفـعـل**")

    zed = await edit_or_reply(event, "**•❐• جـاري تـنفيـذ مـراسيـم الاعـتزال وإغـلاق الـحساب ..**")
    
    me = await event.client.get_me()
    
    # جلب البايو بطريقة آمنة جداً لتفادي الخطأ AttributeError
    try:
        full = await event.client(functions.users.GetFullUserRequest(me.id))
        if hasattr(full, 'full_user'):
            old_bio = full.full_user.about or ""
        else:
            old_bio = getattr(full, 'about', "") or ""
    except:
        old_bio = ""
    
    addgvar("old_first_name", me.first_name)
    addgvar("old_last_name", me.last_name or "")
    addgvar("old_bio", old_bio)
    addgvar("zed_retired", "true")
    
    now = datetime.now()
    ret_stamp = now.strftime("%Y/%m/%d | %I:%M %p")
    addgvar("ret_timestamp", ret_stamp)

    # 1. إخفاء صورة البروفايل عن الجميع
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
            about=f"مغلق .. معتزل منذ : {ret_stamp}"
        ))
    except:
        pass

    await zed.edit(f"**• تـم الاعـتزال بـنجـاح ( {ret_stamp} )**\n**• تـم إخـفـاء الـصورة وتـفعيل الـمساعد الـوفـي (Llama 4)**")


@zedub.zed_cmd(pattern="^[.,]الغاء الاعتزال$")
async def stop_retirement(event):
    if not gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• أنـت لـست مـعتـزلاً بـالأسـاس**")

    # 1. استعادة خصوصية الصورة (للجميع)
    try:
        await event.client(functions.account.SetPrivacyRequest(
            key=types.InputPrivacyKeyProfilePhoto(),
            rules=[types.InputPrivacyValueAllowAll()]
        ))
    except:
        pass

    # 2. استعادة المعلومات الأصلية
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


# --- المحرك الذكي (الردود التلقائية) ---
@zedub.on(events.NewMessage(incoming=True))
async def retirement_ai_watcher(event):
    if not gvarstatus("zed_retired") or event.out:
        return

    me = await event.client.get_me()
    should_reply = False
    
    # التحقق من الخاص أو الرد على رسائلك في المجموعات
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

        user_replied_key = f"ret_log_{sender.id}"
        ret_stamp = gvarstatus("ret_timestamp") or "2026"
        user_name = sender.first_name

        if not gvarstatus(user_replied_key):
            # الرد الأول بالكليشة الملكية
            await event.reply(FAV_RESPONSE)
            addgvar(user_replied_key, "done")
        else:
            # الردود التالية بذكاء Llama 4 وبخط زدثون الفخم
            ai_msg = await get_llama_assistant_reply(event.text, user_name, ret_stamp)
            await event.reply(ai_msg)