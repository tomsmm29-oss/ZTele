import asyncio
import time
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from .. import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import reply_id

MUSIC_BOT_USER = "@oldnotpt_bot"
plugin_category = "البحث"

@zedub.zed_cmd(
    pattern="(يوت|اغنية|اغنيه)(?:\s|$)([\s\S]*)",
    command=("يوت", plugin_category),
    info={
        "header": "بحث وتحميل الأغاني بسرعة صاروخية",
        "شرح": "يحدد رسالة الانتظار بدقة ويراقب تعديلها للأصل.",
        "مثــال": ["{tr}يوت اغنية"],
    },
)
async def zed_fast_song(event):
    cmd = event.pattern_match.group(1)
    query = event.pattern_match.group(2)

    if not query and event.is_reply:
        reply_msg = await event.get_reply_message()
        query = reply_msg.text

    query = (query or "").strip()
    if not query:
        return await edit_delete(event, f"**╮ بالـرد ﮼؏ كلمـٓھہ للبحث ... 𓅫╰**", 10)

    zedevent = await edit_or_reply(event, "**⎉╎جـارِ البحث والسحب ...**")

    try:
        # 1. البحث السري
        results = await event.client.inline_query(MUSIC_BOT_USER, query)

        if not results:
            return await edit_delete(zedevent, "**⎉╎لم يتم العثور على نتائج ⚠️**", 10)

        # 2. النقر (إرسال للمحفوظات سراً)
        await results[0].click(entity="me", hide_via=True)

        # 3. التقاط رسالة الانتظار (ID)
        # ننتظر قليلاً حتى تصل رسالة الانتظار (التي مدتها قصيرة)
        waiting_msg_id = None
        for _ in range(15): # محاولات لمدة 3 ثواني لالتقاط بداية الرسالة
            async for msg in event.client.iter_messages('me', limit=1):
                # نتأكد أن الرسالة من البوت وتحتوي على صوت
                if msg.via_bot_id and msg.media:
                    waiting_msg_id = msg.id
                    break
            if waiting_msg_id:
                break
            await asyncio.sleep(0.2)

        if not waiting_msg_id:
             return await edit_delete(zedevent, "**⎉╎تأخر البوت في الاستجابة (لم تصل رسالة الانتظار) ⚠️**", 10)

        # 4. مراقبة هذا الـ ID تحديداً حتى يتعدل
        final_msg = None
        start_time = time.time()
        
        while time.time() - start_time < 25: # انتظار 25 ثانية كحد أقصى للتعديل
            # نجلب الرسالة نفسها مرة أخرى من السيرفر للتأكد من التحديث
            try:
                check_msg = await event.client.get_messages('me', ids=waiting_msg_id)
                
                # التحقق: هل يوجد ملف صوتي وهل مدته أكبر من 5 ثواني؟
                if check_msg and check_msg.file and check_msg.file.duration:
                    if check_msg.file.duration > 5:
                        final_msg = check_msg
                        break
            except Exception:
                pass # في حال حدوث خطأ لحظي في الجلب نواصل المحاولة
            
            await asyncio.sleep(1.5) # نفحص كل ثانية ونصف لتخفيف الضغط

        if not final_msg:
            return await edit_delete(zedevent, "**⎉╎فشلت العملية: البوت لم يقم بتعديل الرسالة للملف الأصلي ⚠️**", 10)

        # 5. إرسال الملف للدردشة
        song_title = query
        try:
            if hasattr(results[0], 'title'):
                song_title = results[0].title
        except:
            pass

        caption_text = (
            f"**⎉╎المقطــع :** `{song_title}`\n"
            f"**⎉╎بواسطـة :** {event.client.me.first_name}" 
        )

        await event.client.send_file(
            event.chat_id,
            final_msg.media,
            caption=caption_text,
            reply_to=await reply_id(event)
        )

        # 6. تنظيف الآثار
        await final_msg.delete()
        await zedevent.delete()

    except YouBlockedUserError:
        return await edit_delete(zedevent, f"**⎉╎قم بإلغاء حظر {MUSIC_BOT_USER} أولاً ⚠️**", 10)
    except Exception as e:
        print(f"Error: {e}")
        await edit_delete(zedevent, "**⎉╎خطأ فني ⚠️**", 5)
