import random
import asyncio
from telethon.tl.functions.account import UpdateProfileRequest
from . import zedub
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

plugin_category = "الادمن"

# الكليشة المفضلة (الأساسية)
FAV_RESPONSE = "**•❐• لا تـنـتظر رداً .. فـقـد طـويـت صـفحة هـذا الـحسـاب إلـى الأبـد**"

# كليشات إضافية جادة (بدون كرنج)
OTHER_RESPONSES = [
    "**•❐• عـذراً .. هـذا الـحساب خـارج الـخدمة بـسبب الاعـتزال الـنهـائي**",
    "**•❐• انـتهـى المـشوار .. صـاحب الـحساب غـادر ولـن يـعود**"
]

@zedub.zed_cmd(pattern="^[.,]الاعتزال$")
async def start_retirement(event):
    if gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• أنـت في وضـع الاعـتزال بـالـفـعـل**")

    me = await event.client.get_me()
    first_name = me.first_name
    last_name = me.last_name if me.last_name else ""
    
    # حفظ البيانات
    addgvar("old_first_name", first_name)
    addgvar("old_last_name", last_name)
    addgvar("zed_retired", "true")

    # تغيير الاسم
    new_first_name = f"{first_name} (معتزل)"
    try:
        await event.client(UpdateProfileRequest(first_name=new_first_name))
    except Exception as e:
        return await edit_or_reply(event, f"**•❐• حـدث خـطأ أثـناء تـغيير الاسـم :** `{str(e)}`")

    # كليشة التفعيل المطلوبة فقط
    await edit_or_reply(event, "**• تـم حـفظ تـاريخ اعـتزالك وتـفعيل الـردود التـلقائـية الـحزينة**")


@zedub.zed_cmd(pattern="^[.,]الغاء الاعتزال$")
async def stop_retirement(event):
    if not gvarstatus("zed_retired"):
        return await edit_or_reply(event, "**•❐• أنـت لـست في وضـع الاعـتزال أصـلاً**")

    old_first = gvarstatus("old_first_name")
    old_last = gvarstatus("old_last_name") or ""

    try:
        await event.client(UpdateProfileRequest(first_name=old_first, last_name=old_last))
        delgvar("old_first_name")
        delgvar("old_last_name")
        delgvar("zed_retired")
    except Exception as e:
        return await edit_or_reply(event, f"**•❐• حـدث خـطأ أثـناء اسـتعادة الاسـم :** `{str(e)}`")

    await edit_or_reply(event, "**•❐• أهـلاً بـعودتـك .. تـم إلـغاء وضـع الاعـتزال واسـتعادة اسـمك بـنجـاح**")


@zedub.on(incoming=True)
async def retirement_watcher(event):
    # الفحص: اعتزال مفعل + خاص + رسالة واردة
    if gvarstatus("zed_retired") and event.is_private and not event.out:
        sender = await event.get_sender()
        if sender and not sender.bot:
            
            # فحص هل هي أول رسالة من هذا الشخص منذ الاعتزال؟
            replied_key = f"ret_replied_{sender.id}"
            
            if not gvarstatus(replied_key):
                # أول مرة: نرسل الكليشة المفضلة دائماً
                await event.reply(FAV_RESPONSE)
                addgvar(replied_key, "true")
            else:
                # المرات التالية: 50% المفضلة، 50% الباقي
                if random.random() < 0.5:
                    response = FAV_RESPONSE
                else:
                    response = random.choice(OTHER_RESPONSES)
                await event.reply(response)