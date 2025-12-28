import asyncio
import os
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from .. import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id, progress
from ..Config import Config

# اسم البوت الوسيط
DL_BOT = "@yt_zthon_bot"
plugin_category = "البحث"

# دالة مساعدة للتحدث مع البوت وجلب الميديا
async def fetch_media_from_bot(event, link):
    async with event.client.conversation(DL_BOT) as conv:
        try:
            # إرسال الرابط للبوت
            msg = await conv.send_message(link)
            
            # انتظار الرد (نتوقع ملف ميديا)
            # ننتظر رد يحتوي على ميديا، البوت أحيانا يرسل رسالة "جاري المعالجة" ثم الملف
            response = await conv.get_response()
            
            # لو الرد الأول نص فقط (مثل جاري التحميل)، ننتظر الثاني
            if not response.media:
                response = await conv.get_response()
            
            # التأكد النهائي من وجود ميديا
            if not response.media:
                return None
                
            return response
        except YouBlockedUserError:
            return "BLOCKED"
        except Exception as e:
            return None

# =========================================================
# 1. التحميل العام (فيديو/صور) - تيك، انستا، يوتيوب، أو نقطة ورابط
# =========================================================
@zedub.zed_cmd(
    pattern=r"(\.(?:تيك|انستا|فيس|يوتيوب|تحميل|رابط|)(?:\s+)([\s\S]*))|(\.(https?://[\s\S]*))",
    command=("تحميل", plugin_category),
    info={
        "header": "تحميل من كافة المنصات (فيديو/صور) عبر البوت المساعد",
        "شرح": "يدعم تيك توك، انستقرام، يوتيوب، وغيرها. يسحب الملف ويرسله بدون تحويل.",
        "طرق الاستخدام": [
            "{tr}تحميل + رابط",
            "{tr}تيك + رابط",
            "{tr}.https://google.com (نقطة ثم الرابط مباشرة)",
            "{tr}تحميل (بالرد على رابط)"
        ],
    },
)
async def zed_universal_dl(event):
    # تحليل المدخلات (لدعم النقطة المباشرة والأوامر العادية)
    # Group 1: الأمر مع مسافة ورابط (.تيك رابط)
    # Group 2: الرابط من Group 1
    # Group 3: الأمر المختصر (.رابط_مباشرة)
    # Group 4: الرابط من Group 3
    
    msg_link = ""
    
    if event.pattern_match.group(3):
        # حالة .https://...
        msg_link = event.pattern_match.group(4) # الرابط فقط
    else:
        # حالة .تيك رابط
        msg_link = event.pattern_match.group(2)
        
    # حالة الرد
    if not msg_link and event.is_reply:
        reply_msg = await event.get_reply_message()
        msg_link = reply_msg.text
        
    msg_link = (msg_link or "").strip()
    
    if not msg_link:
         # نتجاهل الأمر إذا لم يكن هناك رابط (خاصة مع النقطة)
         if event.pattern_match.group(3): 
             return
         return await edit_delete(event, "**╮ أرسـل الرابـط مـع الأمـر أو بالـرد ... 𓅫╰**", 5)

    zedevent = await edit_or_reply(event, "**⎉╎جـارِ جلـب المقطـع انتظر قليلا ▬▭ ...**")

    # التعامل مع البوت
    response = await fetch_media_from_bot(event, msg_link)
    
    if response == "BLOCKED":
        return await edit_delete(zedevent, f"**⎉╎عليك إلغاء حظر البوت {DL_BOT} أولاً ⚠️**", 10)
    
    if not response or not response.media:
        return await edit_delete(zedevent, "**⎉╎فشل التحميل .. تأكد من صحة الرابط أو أن البوت لا يدعمه ⚠️**", 10)

    # الإرسال "الكلين" (بدون تحويل)
    try:
        # تنسيق الكليشة
        caption_text = (
            f"**⎉╎الرابـط :** `{msg_link}`\n"
            f"**⎉╎بواسطـة :** {event.client.me.first_name}"
        )
        
        # استخدام send_file مع ميديا الرسالة الأصلية = نسخ بدون تحويل
        await event.client.send_file(
            event.chat_id,
            response.media,
            caption=caption_text,
            reply_to=await reply_id(event)
        )
        await zedevent.delete()
        
    except Exception as e:
        await edit_delete(zedevent, f"**خطأ في الإرسال:** {e}", 5)

