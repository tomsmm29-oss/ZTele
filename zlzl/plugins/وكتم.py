from telethon import events

from ..core.managers import edit_or_reply
from . import zedub

# محاولة استدعاء قاعدة البيانات لتوحيد الخطوط والإيموجيات
try:
    from ..sql_helper.globals import gvarstatus
except ImportError:

    def gvarstatus(val):
        return None


# --- نصوص الكليشة الفخمة (تصميم زدثون) ---
ZEDM = gvarstatus("CUSTOM_ALIVE_EMOJI") or "✦ "
CUSTOM_FONT = gvarstatus("CUSTOM_ALIVE_FONT")
ZEDF_TOP = CUSTOM_FONT or "⋆─┄─┄─┄─ 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉─┄─┄─┄─⋆"
ZEDF_BOT = CUSTOM_FONT or "⋆─┄─┄─┄─   🛂 ─┄─┄─┄─⋆"

# قاموس لحفظ الأشخاص المكتومين بهذا النظام
WMUTED_USERS = {}


# دالة مستقلة لجلب المستخدم
async def get_target_user(event):
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        if not msg or not msg.sender_id:
            return None
        return await event.client.get_entity(msg.sender_id)
    else:
        input_str = event.pattern_match.group(1)
        if not input_str:
            return None
        try:
            if input_str.isnumeric():
                return await event.client.get_entity(int(input_str))
            else:
                return await event.client.get_entity(input_str)
        except:
            return None


@zedub.zed_cmd(
    pattern="وكتم(?: |$)(.*)",
    command=("وكتم", "العروض"),
    info={
        "header": "كتم لطيف للمستخدم عبر الرد بـ (مسح) ليقوم بوت آخر بالحذف",
        "الاستخدام": "{tr}وكتم بالرد او باليوزر/الايدي",
    },
)
async def cute_w_mute(event):
    zed = await edit_or_reply(event, "<b>⇆</b>", parse_mode="html")
    user = await get_target_user(event)

    if not user:
        return await zed.edit(
            "<b>- لـم استطـع العثــور ع الشخــص (تأكد من المعرف) ؟!</b>",
            parse_mode="html",
        )

    me = await event.client.get_me()
    if user.id == me.id:
        return await zed.edit(
            "<b>- عـذراً .. لا يـمكنـك كتـم نفسـك ؟!</b>", parse_mode="html"
        )

    chat_id = event.chat_id
    user_id = user.id

    if chat_id not in WMUTED_USERS:
        WMUTED_USERS[chat_id] = set()

    if user_id in WMUTED_USERS[chat_id]:
        return await zed.edit(
            "<b>- هـذا الشخـص مكتـوم ( وكـتم ) بالفعـل ؟!</b>", parse_mode="html"
        )

    WMUTED_USERS[chat_id].add(user_id)

    first_name = user.first_name or "بدون اسم"
    first_name = first_name.replace("\u2060", "")

    # --- كليشة التفعيل الرسمية ---
    caption = f"<b>•⎚• تـم تفعيـل نظـام ( وكـتم ) بنجـاح</b>\n"
    caption += f"ٴ<b>{ZEDF_TOP}</b>\n"
    caption += (
        f"<b>{ZEDM}الاسـم    ⇠ </b> <a href='tg://user?id={user_id}'>{first_name}</a>\n"
    )
    caption += f"<b>{ZEDM}الايـدي   ⇠ </b> <code>{user_id}</code>\n"
    caption += f"<b>{ZEDM}الحالـة    ⇠  مكتـوم ( مسـح )</b>\n"
    caption += f"ٴ<b>{ZEDF_BOT}</b>"

    await zed.edit(caption, parse_mode="html")


@zedub.zed_cmd(
    pattern="الغاء وكتم(?: |$)(.*)",
    command=("الغاء وكتم", "العروض"),
    info={
        "header": "إلغاء الكتم عن المستخدم",
        "الاستخدام": "{tr}الغاء وكتم بالرد او باليوزر/الايدي",
    },
)
async def cute_un_w_mute(event):
    zed = await edit_or_reply(event, "<b>⇆</b>", parse_mode="html")
    user = await get_target_user(event)

    if not user:
        return await zed.edit(
            "<b>- لـم استطـع العثــور ع الشخــص (تأكد من المعرف) ؟!</b>",
            parse_mode="html",
        )

    chat_id = event.chat_id
    user_id = user.id

    if chat_id in WMUTED_USERS and user_id in WMUTED_USERS[chat_id]:
        WMUTED_USERS[chat_id].remove(user_id)

        first_name = user.first_name or "بدون اسم"
        first_name = first_name.replace("\u2060", "")

        # --- كليشة الإلغاء الرسمية ---
        caption = f"<b>•⎚• تـم إلغـاء نظـام ( وكـتم ) بنجـاح</b>\n"
        caption += f"ٴ<b>{ZEDF_TOP}</b>\n"
        caption += f"<b>{ZEDM}الاسـم    ⇠ </b> <a href='tg://user?id={user_id}'>{first_name}</a>\n"
        caption += f"<b>{ZEDM}الايـدي   ⇠ </b> <code>{user_id}</code>\n"
        caption += f"<b>{ZEDM}الحالـة    ⇠  غيـر مكتـوم</b>\n"
        caption += f"ٴ<b>{ZEDF_BOT}</b>"

        await zed.edit(caption, parse_mode="html")
    else:
        await zed.edit(
            "<b>- هـذا الشخـص غيـر مكتـوم ( وكـتم ) هنـا ؟!</b>", parse_mode="html"
        )


# مراقب الرسائل للرد بـ (مسح)
@zedub.on(events.NewMessage())
async def w_mute_watcher(event):
    if not event.chat_id or not event.sender_id:
        return

    chat_id = event.chat_id
    user_id = event.sender_id

    # إذا الشات فيه ناس مكتومين، والمُرسل الحالي من ضمنهم
    if chat_id in WMUTED_USERS and user_id in WMUTED_USERS[chat_id]:
        try:
            # يرد على رسالة المكتوم بكلمة مسح بصمت تام
            await event.reply("مسح")
        except:
            pass
