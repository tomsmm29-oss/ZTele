import asyncio
from telethon.errors import FloodWaitError
from . import zedub
from ..core.managers import edit_or_reply

@zedub.zed_cmd(
    pattern="وحظر الكل$",
    command=("وحظر الكل", "العروض"),
    info={
        "header": "تفليش المجموعة عبر استغلال البوتات الإدارية",
        "الاستخدام": "{tr}وحظر الكل",
    },
)
async def w_ban_all(event):
    if event.is_private:
        return await edit_or_reply(event, "**- عذراً .. هذا الأمر يُستخدم في المجموعات فقط ؟!**")
    
    zed = await edit_or_reply(event, "<b>- جـاري بـدء عمليـة التفليـش عبـر البـوتـات 😈...</b>", parse_mode="html")
    
    try:
        me = await event.client.get_me()
        # سحب جميع أعضاء المجموعة
        participants = await event.client.get_participants(event.chat_id)
        
        count = 0
        for user in participants:
            # استثناء حسابك عشان ما تحظر نفسك
            if user.id == me.id:
                continue
            
            try:
                # إرسال رسالة الحظر للبوت
                await event.client.send_message(event.chat_id, f"حظر {user.id}")
                count += 1
                
                # تأخير بسيط جداً (جزء من الثانية) لحماية حسابك من حظر تيليجرام (Spam/FloodWait)
                await asyncio.sleep(0.1) 
                
            except FloodWaitError as e:
                # إذا تيليجرام طلب الانتظار بسبب السرعة الزائدة
                await asyncio.sleep(e.seconds)
            except Exception:
                pass

        await zed.edit(f"<b>- تـم الانتهـاء مـن إرسـال أوامـر الحظـر لـ {count} عضـو بنجـاح 🚷</b>", parse_mode="html")
        
    except Exception as e:
        await zed.edit(f"**- حـدث خـطأ أثنـاء التنفيـذ:**\n`{str(e)}`")