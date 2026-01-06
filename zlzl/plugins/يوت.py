import asyncio
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
        "header": "بحث انلاين مباشر",
        "شرح": "يقوم بالبحث واختيار النتيجة الأولى وإرسالها مباشرة في الشات (مثل البحث اليدوي).",
        "مثــال": ["{tr}يوت اغنية"],
    },
)
async def zed_fast_song(event):
    cmd = event.pattern_match.group(1)
    query = event.pattern_match.group(2)

    # التحقق من وجود رد إذا لم يكن هناك نص
    if not query and event.is_reply:
        reply_msg = await event.get_reply_message()
        query = reply_msg.text

    query = (query or "").strip()
    if not query:
        return await edit_delete(event, f"**╮ بالـرد ﮼؏ كلمـٓھہ للبحث ... 𓅫╰**", 10)

    # رسالة مؤقتة تخبر المستخدم أن البحث جارٍ
    zedevent = await edit_or_reply(event, f"**⎉╎جـارِ البحث عن:** `{query}` ...")

    try:
        # 1. عمل بحث انلاين (مثل كتابة @bot query)
        # يقوم الكود بجلب النتائج في الخلفية بدون ما يظهر للمستخدم الكتابة
        results = await event.client.inline_query(MUSIC_BOT_USER, query)

        if not results:
            return await edit_delete(zedevent, "**⎉╎لم يتم العثور على نتائج ⚠️**", 10)

        # 2. النقر على النتيجة الأولى مباشرة في نفس الشات
        # هذا الأمر يعادل ضغطك على الأغنية لإرسالها
        await results[0].click(
            event.chat_id,            # الإرسال لنفس الشات الحالي
            reply_to=await reply_id(event), # الرد على الرسالة المطلوبة
            hide_via=True             # محاولة إخفاء "via @bot" إن أمكن
        )

        # 3. حذف رسالة "جارِ البحث" لأن الأغنية (أو رسالة الانتظار) وصلت
        await zedevent.delete()

    except YouBlockedUserError:
        return await edit_delete(zedevent, f"**⎉╎قم بإلغاء حظر {MUSIC_BOT_USER} أولاً ⚠️**", 10)
    except Exception as e:
        # في حال حدوث خطأ، نطبعه للتوضيح
        print(f"Error in zed_fast_song: {e}")
        await edit_delete(zedevent, "**⎉╎حدث خطأ أثناء البحث أو الإرسال ⚠️**", 5)
