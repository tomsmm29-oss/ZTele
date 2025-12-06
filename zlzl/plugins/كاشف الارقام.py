import asyncio
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

# --- تصحيح المسارات للمشروع الجديد ZTele ---
from . import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id, get_user_from_event, _format

plugin_category = "البحث"

# --- دالة مساعدة لفك رد بوت الأسماء (عشان لو مش موجودة في المساعدات) ---
async def sanga_seperator(responses):
    names = []
    usernames = []
    for response in responses:
        if "Name History" in response:
            names.append(response)
        elif "Username History" in response:
            usernames.append(response)
    return names, usernames

# ====================================================================
#                       كـاشـف الارقـام (زلزال)
# ====================================================================

ZelzalPH_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗭𝗘𝗗𝗧𝗵𝗼𝗻 𝗖𝗼𝗻𝗳𝗶𝗴 📲 - كـاشـف الارقـام العربيــة](t.me/ZEDthon) 𓆪\n\n"
    "**⪼ الامــر ↵**\n\n"
    "⪼ `.كاشف` + اسـم الدولـة + الـرقـم بـدون مفتـاح الـدولة\n\n"
    "**⪼ الوصـف :**\n"
    "**- لجـلب معلـومـات عـن رقـم هـاتف معيـن**\n\n"
    "**⪼ مثـال :**\n\n"
    "`.كاشف اليمن 777887798` \n\n"
    "`.كاشف السعوديه 555542317` \n\n"
    "`.كاشف الامارات 43171234` \n\n"
    "**الامـر يدعـم الـدول التـاليـة ↵** 🇾🇪🇸🇦🇦🇪🇰🇼🇶🇦🇧🇭🇴🇲 \n\n"
    "🛃 سيتـم اضـافة المزيـد من الدول قريبـاً\n\n"
    "\n𓆩 [𐇮 𝙕𝞝𝙇𝙕𝘼𝙇 الهہـيـٖ͡ـ͢ـبـه 𐇮](t.me/zzzzl1l) 𓆪"
)

@zedub.zed_cmd(
    pattern="كاشف ?(.*)",
    command=("كاشف", plugin_category),
    info={
        "header": "لـ جـلب معلـومـات عـن رقـم هـاتف معيـن .. الامـر يدعـم الـدول التـاليـة ↵ 🇾🇪🇸🇦🇦🇪🇰🇼🇶🇦🇧🇭🇴🇲 .. سيـتم اضـافـة بقيـة الـدول العـربيـة قريبـاً",
        "الاستـخـدام": "{tr}كاشف + اسـم الدولـة + الـرقـم بـدون مفتـاح الـدولة",
    },
)
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    # تصليح الـ reply_id عشان يشتغل مع الهيكلة الجديدة
    if event.reply_to_msg_id and not input_str:
        reply_msg = await event.get_reply_message()
        reply_to_id = str(reply_msg.message)
    else:
        reply_to_id = str(input_str)
    
    if not reply_to_id or not input_str:
        return await edit_or_reply(
            event, "**╮ . كـاشف الاࢪقـام الـ؏ـࢪبيـة 📲.. اࢪسـل** `.الكاشف` **للتعليـمات 𓅫╰**"
        )
    
    chat = "@jdjskzkk_bot"
    zzzzl1l = await edit_or_reply(event, "**╮•⎚ جـارِ الكـشف ؏ــن الـرقـم  📲 ⌭ . . .**")
    
    async with event.client.conversation(chat) as conv:
        try:
            # تم حذف ID البوت المحدد لضمان العمل مع أي تحديث، أو ممكن نرجعه لو البوت ده بس اللي شغال
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=chat)
            )
            await event.client.send_message(chat, "{}".format(input_str))
            response = await response
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await zzzzl1l.edit("**╮•⎚ تحـقق من انـك لم تقـم بحظر البوت @Zelzalybot .. ثم اعـد استخدام الامـر ...🤖♥️**")
            return
        
        if response.text.startswith("I can't find that"):
            await zzzzl1l.edit("**╮•⎚ عـذراً .. لـم استطـع ايجـاد المطلـوب ☹️💔**")
        else:
            await zzzzl1l.delete()
            await event.client.send_message(event.chat_id, response.message)

@zedub.zed_cmd(pattern="الكاشف")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalPH_cmd)


# ====================================================================
#                       كـاشـف الاسماء (سجل الأسماء)
# ====================================================================

@zedub.zed_cmd(
    pattern="(كشف|الاسماء)(المعرف)?(?:\s|$)([\s\S]*)",
    command=("الاسماء", plugin_category),
    info={
        "header": "To get name history of the user.",
        "flags": {
            "u": "That is sgu to get username history.",
        },
        "usage": [
            "{tr}كشف <username/userid/reply>",
            "{tr}كشف المعرف <username/userid/reply>",
        ],
        "examples": "{tr}sg @missrose_bot",
    },
)
async def _(event): 
    "To get name/username history."
    input_str = "".join(event.text.split(maxsplit=1)[1:])
    reply_message = await event.get_reply_message()
    
    if not input_str and not reply_message:
        return await edit_delete(
            event,
            "`reply to user's text message to get name/username history or give userid/username`",
        )
    
    user, rank = await get_user_from_event(event, secondgroup=True)
    if not user:
        return
    
    uid = user.id
    chat = "@SangMata_beta_bot"
    zedevent = await edit_or_reply(event, "**⎉╎جـارِ الكشـف ...**")
    
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message(f"{uid}")
        except YouBlockedUserError:
            await edit_delete(zedevent, "**- اضغط ستارت هنـا @SangMata_BOT ثم اعد ارسال الامر**")
            return
        
        responses = []
        while True:
            try:
                response = await conv.get_response(timeout=2)
            except asyncio.TimeoutError:
                break
            responses.append(response.text)
        await event.client.send_read_acknowledge(conv.chat_id)
    
    if not responses:
        await edit_delete(zedevent, "**- الامـر في وضع الصيانه حاليـاً ...**")
        return
        
    if "No data available" in responses:
        await edit_delete(zedevent, "**⎉╎المستخدم ليس لديه أي سجل اسمـاء بعـد ...**")
        return

    # استخدام الدالة المحلية اللي كتبناها فوق عشان ميعملش مشاكل
    names, usernames = await sanga_seperator(responses)
    
    cmd_trigger = event.pattern_match.group(2) # (المعرف)
    sandy = None
    check = usernames if cmd_trigger == "المعرف" else names
    
    for i in check:
        if sandy:
            await event.reply(i, parse_mode=_format.parse_pre)
        else:
            sandy = True
            await zedevent.edit(i, parse_mode=_format.parse_pre)