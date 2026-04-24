import random
import asyncio
from datetime import datetime
from telethon import events
from telethon.tl import functions
from . import zedub
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

plugin_category = "الادمن"

# الكليشات
FAV_RESPONSE = "**•❐• لا تـنـتظر رداً .. فـقـد طـويـت صـفحة هـذا الـحسـاب إلـى الأبـد**"
OTHER_RESPONSES = [
    "**•❐• عـذراً .. هـذا الـحساب خـارج الـخدمة بـسبب الاعـتزال الـنهـائي**",
    "**•❐• انـتهـى المـشوار .. صـاحب الـحساب غـادر ولـن يـعود**"
]

@zedub.zed_cmd(pattern="^[.,]الاعتزال$")
async def start_retirement(event):
    if gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• أنـت في وضـع الاعـتزال بـالـفـعـل**")

    # جلب معلومات الحساب
    me = await event.client.get_me()
    full_user_result = await event.client(functions.users.GetFullUserRequest(me.id))
    
    # تصحيح جلب البايو لتفادي AttributeError
    try:
        old_bio = full_user_result.full_user.about or ""
    except:
        old_bio = ""
        
    old_first_name = me.first_name
    old_last_name = me.last_name if me.last_name else ""
    
    # حفظ التاريخ والساعة
    now = datetime.now()
    ret_stamp = now.strftime("%Y/%m/%d | %I:%M %p")

    # تخزين في SQL
    addgvar("old_first_name", old_first_name)
    addgvar("old_last_name", old_last_name)
    addgvar("old_bio", old_bio)
    addgvar("zed_retired", "true")
    addgvar("ret_timestamp", ret_stamp)
    addgvar("ret_msg_count", "0") # تصغير العداد عند البدء

    # تنفيذ التغييرات
    new_name = f"{old_first_name} (معتزل)"
    new_bio = f"معتزل منذ : {ret_stamp}"
    
    try:
        await event.client(functions.account.UpdateProfileRequest(
            first_name=new_name,
            about=new_bio
        ))
    except Exception as e:
        return await edit_or_reply(event, f"**•❐• حـدث خـطأ أثـناء الـتحديث :** `{str(e)}`")

    await edit_or_reply(event, f"**• تـم حـفظ تـاريخ اعـتزالك ( {ret_stamp} ) وتـفعيل الـردود الـتلقائـية الـحزينة**")


@zedub.zed_cmd(pattern="^[.,]الغاء الاعتزال$")
async def stop_retirement(event):
    if not gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• أنـت لـست في وضـع الاعـتزال أصـلاً**")

    old_first = gvarstatus("old_first_name")
    old_last = gvarstatus("old_last_name") or ""
    old_bio = gvarstatus("old_bio") or ""

    try:
        await event.client(functions.account.UpdateProfileRequest(
            first_name=old_first,
            last_name=old_last,
            about=old_bio
        ))
        delgvar("old_first_name")
        delgvar("old_last_name")
        delgvar("old_bio")
        delgvar("zed_retired")
        delgvar("ret_timestamp")
        delgvar("ret_msg_count")
    except Exception as e:
        return await edit_or_reply(event, f"**•❐• حـدث خـطأ أثـناء اسـتعادة الـبيانات :** `{str(e)}`")

    await edit_or_reply(event, "**•❐• أهـلاً بـعودتـك .. تـم إلـغاء وضـع الاعـتزال واسـتعادة مـعلومـاتك بـنجـاح**")


# --- نظام الرد التلقائي ---
@zedub.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def retirement_auto_reply(event):
    if gvarstatus("zed_retired") and not event.out:
        sender = await event.get_sender()
        if not sender or sender.bot:
            return

        # جلب العداد وتحديثه
        count = int(gvarstatus("ret_msg_count") or 0)
        count += 1
        addgvar("ret_msg_count", str(count))

        try:
            if count <= 2:
                # أول مرتين تظهر الكليشة المفضلة
                await event.reply(FAV_RESPONSE)
            else:
                # بعد ذلك 50% للمفضلة و 50% للباقي
                if random.random() < 0.5:
                    await event.reply(FAV_RESPONSE)
                else:
                    await event.reply(random.choice(OTHER_RESPONSES))
        except:
            pass