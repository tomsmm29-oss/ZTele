import asyncio
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from .. import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id

# اسم البوت الوسيط المعتمد
MUSIC_BOT_USER = "@oldnotpt_bot"
plugin_category = "البحث"

@zedub.zed_cmd(
    pattern="(يوت|اغنية|اغنيه)(?:\s|$)([\s\S]*)",
    command=("يوت", plugin_category),
    info={
        "header": "بحث وتحميل الأغاني بسرعة عالية عبر البوت المساعد",
        "شرح": "يقوم السورس بالبحث في البوت، واختيار أول نتيجة، وسحبها للشات بدون توجيه.",
        "مثــال": [
            "{tr}يوت توكيو غول",
            "{tr}اغنية حلمي تحطم واختفى",
        ],
    },
)
async def zed_fast_song(event):
    """
    يقوم بالبحث في oldnotpt_bot وسحب النتيجة الأولى وإرسالها "كلين" (Clean Upload).
    """
    # 1. تحليل الأمر واستخراج النص
    cmd = event.pattern_match.group(1)
    query = event.pattern_match.group(2)
    
    # دعم الرد على رسالة
    if not query and event.is_reply:
        reply_msg = await event.get_reply_message()
        query = reply_msg.text
    
    query = (query or "").strip()
    
    # إذا لم يوجد نص للبحث
    if not query:
        return await edit_delete(
            event, 
            f"**╮ بالـرد ﮼؏ كلمـٓھہ للبحث أو ضعها مـع الأمـر ... 𓅫╰**\n**مثال:** `{cmd} اغنية البداية`", 
            10
        )

    # رسالة الانتظار (نفس فخامة زدثون)
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ التحميل انتظر قليلا ▬▭ ...**")
    
    try:
        # 2. البحث عبر الانلاين (Inline Query) باستخدام تليثون
        # السورس يتصرف وكأنه يكتب @oldnotpt_bot query
        results = await event.client.inline_query(MUSIC_BOT_USER, query)
        
        if not results:
            return await edit_delete(zedevent, "**⎉╎عذراً .. لم أجد نتائج لهذه الأغنية ⚠️**", 10)

        # 3. الخدعة (The Trick):
        # نرسل النتيجة الأولى إلى "الرسائل المحفوظة" (me)
        # هذا الإجراء ضروري لإزالة علامة "via @bot" ولإزالة التوجيه لاحقاً
        saved_msg = await results[0].click(entity="me", hide_via=True)
        
        # التأكد من وصول الرسالة
        if not saved_msg:
             # انتظار بسيط ومحاولة جلب آخر رسالة في المحفوظات احتياطاً
             await asyncio.sleep(0.5)
             async for msg in event.client.iter_messages('me', limit=1):
                 saved_msg = msg
                 break

        # التحقق من أن الرسالة تحتوي على ملف (صوت أو فيديو)
        if not saved_msg or not saved_msg.media:
            return await edit_delete(zedevent, "**⎉╎حدث خطأ أثناء جلب الملف من المصدر ⚠️**", 10)

        # 4. إعادة الإرسال (Send File)
        # نستخدم send_file بدلاً من forward_messages لإرسالها كملف جديد تماماً
        # نقوم بوضع تعليق بسيط (Caption) للحفاظ على التنسيق
        
        # نحاول جلب عنوان الأغنية لترتيب شكل الرسالة
        song_title = query
        try:
            # محاولة استخراج العنوان من نتيجة البحث
            if hasattr(results[0], 'title'):
                song_title = results[0].title
        except:
            pass

        # الكليشة (نص الرسالة)
        caption_text = (
            f"**⎉╎المقطــع :** `{song_title}`\n"
            f"**⎉╎بواسطـة :** {event.client.me.first_name}" 
        )

        await event.client.send_file(
            event.chat_id,
            saved_msg.media,
            caption=caption_text,
            reply_to=await reply_id(event)
        )

        # 5. التنظيف (Cleaning)
        # حذف الرسالة المؤقتة من المحفوظات
        await saved_msg.delete()
        # حذف رسالة "جاري التحميل"
        await zedevent.delete()

    except YouBlockedUserError:
        # تنبيه المستخدم إذا كان حاظراً للبوت
        return await edit_delete(zedevent, f"**⎉╎عليك إلغاء حظر البوت {MUSIC_BOT_USER} أولاً ⚠️**", 10)
    
    except Exception as e:
        # التعامل مع أي خطأ طارئ
        print(f"Error in zed_fast_song: {e}") # للمطور في التيرمنال
        await edit_delete(zedevent, f"**⎉╎خطـأ غير متوقع :** {str(e)}", 10)

