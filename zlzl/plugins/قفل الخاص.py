import asyncio

from telethon import events, functions
from telethon.tl.types import User

from ..core.managers import edit_delete, edit_or_reply

# --- منطقة الاستدعاءات (تطابق سورس زدثون 100%) ---
from . import zedub

# استدعاء قاعدة البيانات (PostgreSQL) لضمان حفظ الإعدادات في Render والذاكرة الدائمة
try:
    from ..sql_helper.globals import addgvar, delgvar, gvarstatus
except ImportError:

    def gvarstatus(val):
        return None

    def addgvar(k, v):
        pass

    def delgvar(k):
        pass


plugin_category = "الحماية"

Z_LOGO = "𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉"
HEADER = f"**🖥┊نظام الحماية - {Z_LOGO}**"


VIP_USERS = [8569444589, 7668115898, 82725508]


def get_whitelist():
    """جلب قائمة السماح من قاعدة البيانات (الذاكرة)"""
    wl = gvarstatus("nuclear_whitelist")
    return [int(x) for x in str(wl).split()] if wl else []


def update_whitelist(wl_list):
    """تحديث قائمة السماح في قاعدة البيانات"""
    if not wl_list:
        delgvar("nuclear_whitelist")
    else:
        addgvar("nuclear_whitelist", " ".join(map(str, wl_list)))


@zedub.zed_cmd(
    pattern="ق خاص$",
    command=("ق خاص", plugin_category),
    info={
        "header": "تفعيل وضع الإبادة الشامل (يغلق الخاص تماماً)",
        "الاستـخـدام": "{tr}ق خاص",
    },
)
async def strict_lock(event):
    if gvarstatus("strict_pm_lock"):
        return await edit_or_reply(
            event,
            f"{HEADER}\n\n⎉╎الوضع النووي مفعل مسبقاً.\n⎉╎الخاص مغلق للجميع ولا أحد يمر.",
        )

    addgvar("strict_pm_lock", "active")
    await edit_or_reply(
        event,
        f"{HEADER}\n\n•❐• أهـلاً بـعودتـك .. تـم تفعيل الدروع\n⎉╎الخاص مغلق للجميع (باستثناء المسموح لهم).\n⩥ سيتم حظر أي شخص يرسل رسالة تلقائياً.",
    )


@zedub.zed_cmd(
    pattern="ف خاص$",
    command=("ف خاص", plugin_category),
    info={
        "header": "تعطيل وضع الإبادة الشامل (يفتح الخاص للجميع)",
        "الاستـخـدام": "{tr}ف خاص",
    },
)
async def strict_unlock(event):
    if not gvarstatus("strict_pm_lock"):
        return await edit_or_reply(
            event, f"{HEADER}\n\n⎉╎الدروع متوقفة بالفعل .. الخاص مفتوح."
        )

    delgvar("strict_pm_lock")
    await edit_or_reply(
        event,
        f"{HEADER}\n\n•❐• تـم إلـغاء وضـع الإبادة\n⎉╎تم إيقاف الدروع .. الخاص مفتوح للجميع.",
    )


@zedub.zed_cmd(
    pattern="فتح$",
    command=("فتح", plugin_category),
    info={
        "header": "استثناء المستخدم الحالي من الحظر (يسمح له بالتحدث)",
        "الاستـخـدام": "{tr}فتح بالرد او في خاص الشخص",
    },
)
async def allow_user_nuclear(event):
    if not event.is_private:
        return await edit_delete(event, "⚠️ هذا الأمر يعمل في الخاص فقط.")

    chat_id = event.chat_id
    wl = get_whitelist()
    if chat_id not in wl:
        wl.append(chat_id)
        update_whitelist(wl)

    await edit_or_reply(
        event,
        f"{HEADER}\n\n•❐• تـم منح العفو لهذا المستخدم بنجاح.\n⎉╎لن يتم حظره أثناء تفعيل قفل الخاص.",
    )


@zedub.zed_cmd(
    pattern="قفل$",
    command=("قفل", plugin_category),
    info={
        "header": "إزالة العفو عن الشخص (ليتم حظره فور إرساله رسالة)",
        "الاستـخـدام": "{tr}قفل بالرد او في خاص الشخص",
    },
)
async def reset_user_nuclear(event):
    if not event.is_private:
        return await edit_delete(event, "⚠️ هذا الأمر يعمل في الخاص فقط.")

    chat_id = event.chat_id
    wl = get_whitelist()
    if chat_id in wl:
        wl.remove(chat_id)
        update_whitelist(wl)

    await edit_or_reply(
        event,
        f"{HEADER}\n\n•❐• تـم إلغاء العفو وتصفير وضع المستخدم.\n⎉╎سيتم حظره فوراً عند إرسال أي رسالة.",
    )


@zedub.zed_cmd(
    pattern="صفرهم$",
    command=("صفرهم", plugin_category),
    info={
        "header": "تصفير قائمة المسموح لهم (الذاكرة) بالكامل",
        "الاستـخـدام": "{tr}صفرهم",
    },
)
async def clear_whitelist(event):
    delgvar("nuclear_whitelist")
    await edit_or_reply(
        event,
        f"{HEADER}\n\n•❐• تـم تصفير ذاكرة المسموح لهم بنجاح.\n⎉╎تم إزالة جميع من قمت بعمل (فتح) لهم سابقاً.\n⩥ الآن سيتعرض الجميع للحظر إذا كان الوضع مفعلاً.",
    )


@zedub.zed_cmd(
    pattern="المحظورين$",
    command=("المحظورين", plugin_category),
    info={
        "header": "عرض عدد الضحايا (المحظورين) في حسابك",
        "الاستـخـدام": "{tr}المحظورين",
    },
)
async def count_blocked(event):
    msg = await edit_or_reply(event, f"{HEADER}\n\n⎉╎جارِ جلب قائمة الضحايا ...")
    try:
        result = await event.client(
            functions.contacts.GetBlockedRequest(offset=0, limit=1)
        )
        await msg.edit(
            f"{HEADER}\n\n⎉╎تم العثور على {result.count} ضحية\n⎉╎لفك الحظر عنهم استخدم الامـر التالي\n⩥ `.تصفير المحظورين`"
        )
    except Exception as e:
        await msg.edit(f"خطأ: {str(e)}")


@zedub.zed_cmd(
    pattern="تصفير المحظورين$",
    command=("تصفير المحظورين", plugin_category),
    info={
        "header": "فك الحظر عن جميع المحظورين بحسابك دفعة واحدة",
        "الاستـخـدام": "{tr}تصفير المحظورين",
    },
)
async def unblock_all_users(event):
    msg = await edit_or_reply(
        event, f"{HEADER}\n\n⎉╎جارِ بدء عملية العفو العام (فك الحظر عن الجميع)..."
    )
    try:
        blocked_users = await event.client(
            functions.contacts.GetBlockedRequest(offset=0, limit=10000)
        )
        if not blocked_users.users:
            return await msg.edit(
                f"{HEADER}\n\n⎉╎القائمة نظيفة، لا يوجد محظورين في حسابك."
            )

        done = 0
        for user in blocked_users.users:
            try:
                await event.client(functions.contacts.UnblockRequest(id=user.id))
                done += 1
                if done % 20 == 0:
                    await msg.edit(
                        f"{HEADER}\n\n⎉╎جارِ تنظيف القائمة.. ({done}/{len(blocked_users.users)})"
                    )
            except:
                continue

        await msg.edit(
            f"{HEADER}\n\n•❐• تـم تصفير المحظورين بنجاح.\n⎉╎تم فك الحظر عن: `{done}` مستخدم."
        )
    except Exception as e:
        await msg.edit(f"**حدث خطأ:** {str(e)}")


# =========================================================
# الرادار الصامت (المراقب الذي يعمل بالخلفية بدون إيقاف السورس)
# =========================================================


@zedub.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def nuclear_block_action(event):
    """يعمل بتلقائية للقبض على أي شخص يرسل رسالة إذا كان القفل مفعلاً"""

    # 1. إذا الوضع معطل، اخرج فوراً
    if not gvarstatus("strict_pm_lock"):
        return

    sender = await event.get_sender()

    # 2. التأكد من أن المرسل شخص طبيعي (يتجاهل البوتات والقنوات ونفسك وموثقين تيليجرام)
    if (
        not sender
        or not isinstance(sender, User)
        or sender.bot
        or sender.verified
        or sender.is_self
    ):
        return

    # 3. التحقق مما إذا كان الشخص من الـ VIP أو في القائمة البيضاء المحفوظة بالذاكرة
    if event.chat_id in VIP_USERS or event.chat_id in get_whitelist():
        return

    # 4. رسالة الإعدام بفخامة زدثون
    block_msg = (
        f"{HEADER}\n\n"
        "•❐• **مـعذراً عـزيزي .. الخاص لدي مغلق**\n"
        "⎉╎**تم تفعيل وضع الإبادة والحظر التلقائي**\n"
        "⩥ **𝗕𝗹𝗼𝗰𝗸𝗲𝗱 🚫**"
    )

    try:
        # إرسال التحذير
        await event.reply(block_msg, link_preview=False)
        await asyncio.sleep(0.3)
    except:
        pass  # تجاهل الأخطاء إن لم يستطع الإرسال وأكمل لعملية الحظر

    try:
        # تنفيذ الحظر النهائي (حظر فقط بدون مسح المحادثة)
        await event.client(functions.contacts.BlockRequest(id=sender.id))
    except Exception:
        pass
