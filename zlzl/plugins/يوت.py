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
        "شرح": "يتصل بالبوت سراً ويسحب الملف الأصلي فقط (فوق 5 ثواني) ويتجاهل الملفات المؤقتة.",
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

        # 3. المراقبة والاقتناص (بحد أقصى 6 ثواني)
        start_time = time.time()
        final_msg = None

        while time.time() - start_time < 6:
            # فحص آخر رسالة وصلت للمحفوظات
            async for msg in event.client.iter_messages('me', limit=1):
                if msg.media and hasattr(msg, 'file'):
                    # شرط الفلترة: تجاهل أي شي 5 ثواني أو أقل
                    if msg.file.duration and msg.file.duration > 5:
                        final_msg = msg
                        break
            
            if final_msg:
                break
            
            # انتظار جزء من الثانية لإعادة الفحص بسرعة
            await asyncio.sleep(0.2)

        if not final_msg:
            return await edit_delete(zedevent, "**⎉╎فشلت العملية: البوت تأخر في إرسال الملف الأصلي ⚠️**", 10)

        # 4. إرسال الملف للدردشة
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

        # 5. تنظيف الآثار
        await final_msg.delete()
        await zedevent.delete()

    except YouBlockedUserError:
        return await edit_delete(zedevent, f"**⎉╎قم بإلغاء حظر {MUSIC_BOT_USER} أولاً ⚠️**", 10)
    except Exception as e:
        print(f"Error: {e}")
        await edit_delete(zedevent, "**⎉╎خطأ فني ⚠️**", 5)
