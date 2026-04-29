import asyncio
from telethon import functions, events
from telethon.tl.types import User

# --- منطقة الاستدعاءات (تطابق سورس زدثون 100%) ---
from . import zedub
from ..core.managers import edit_delete, edit_or_reply

# استدعاء قاعدة البيانات (PostgreSQL) لضمان حفظ الإعدادات في Render
try:
    from ..sql_helper.globals import addgvar, delgvar, gvarstatus
except ImportError:
    def gvarstatus(val): return None
    def addgvar(k, v): pass
    def delgvar(k): pass

plugin_category = "الحماية"

# --- كليشة زدثون الفخمة ---
Z_HEADER = "**🖥┊نظام الحماية - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"

# VIP🥀
VIP_USERS = [8569444589, 7668115898, 6184030144]

def get_whitelist():
    wl = gvarstatus("nuclear_whitelist")
    return [int(x) for x in str(wl).split()] if wl else []

def update_whitelist(wl_list):
    if not wl_list:
        delgvar("nuclear_whitelist")
    else:
        addgvar("nuclear_whitelist", " ".join(map(str, wl_list)))

@zedub.zed_cmd(
    pattern="^ق خاص$",
    command=("ق خاص", plugin_category),
    info={
        "header": "تفعيل وضع الإبادة الشامل (يغلق الخاص تماماً)",
        "الاستـخـدام": "{tr}ق خاص",
    },
)
async def strict_lock(event):
    if gvarstatus("strict_pm_lock"):
        return await edit_or_reply(event, Z_HEADER + "**⎉╎وضـع الإبـادة مـفعل مـسبقاً 🔒\n⎉╎لا أحـد يـستطيع المـرور ⩥**")
    
    addgvar("strict_pm_lock", "active")
    await edit_or_reply(event, Z_HEADER + "**⎉╎تم تـفـعيل وضـع الإبـادة الشـامـلة 🔒\n⎉╎الخـاص مـغلق بـالدروع الـنوويـة ⩥**")

@zedub.zed_cmd(
    pattern="^ف خاص$",
    command=("ف خاص", plugin_category),
    info={
        "header": "تعطيل وضع الإبادة الشامل (يفتح الخاص للجميع)",
        "الاستـخـدام": "{tr}ف خاص",
    },
)
async def strict_unlock(event):
    if not gvarstatus("strict_pm_lock"):
        return await edit_or_reply(event, Z_HEADER + "**⎉╎وضـع الإبـادة مـعطل بـالفعل 🔓\n⎉╎الخـاص مـفتوح للـجميع حـالياً ⩥**")
    
    delgvar("strict_pm_lock")
    await edit_or_reply(event, Z_HEADER + "**•❐• أهـلاً بـعودتـك .. تـم إيقـاف الدروع 🔓\n⎉╎تـم إلـغاء وضـع الإبـادة الشـاملـة ⩥**")

@zedub.zed_cmd(
    pattern="^فتح$",
    command=("فتح", plugin_category),
    info={
        "header": "استثناء المستخدم من الحظر",
        "الاستـخـدام": "{tr}فتح بالرد او في الخاص",
    },
)
async def allow_user_nuclear(event):
    if not event.is_private:
        return await edit_delete(event, "**⚠️╎هـذا الأمـر يـعمل فـي الخـاص فـقط ⩥**")

    chat_id = event.chat_id
    wl = get_whitelist()
    if chat_id not in wl:
        wl.append(chat_id)
        update_whitelist(wl)

    await edit_or_reply(event, Z_HEADER + "**⎉╎تـم مـنح الإذن لـهذا المـستخـدم 🔓\n⎉╎بـإمكـانه الـتحدث فـي الخـاص الآن ⩥**")

@zedub.zed_cmd(
    pattern="^قفل$",
    command=("قفل", plugin_category),
    info={
        "header": "إزالة العفو عن الشخص",
        "الاستـخـدام": "{tr}قفل بالرد او في الخاص",
    },
)
async def reset_user_nuclear(event):
    if not event.is_private:
        return await edit_delete(event, "**⚠️╎هـذا الأمـر يـعمل فـي الخـاص فـقط ⩥**")

    chat_id = event.chat_id
    wl = get_whitelist()
    if chat_id in wl:
        wl.remove(chat_id)
        update_whitelist(wl)

    await edit_or_reply(event, Z_HEADER + "**⎉╎تـم إلـغاء الاسـتثناء عـن هـذا الشـخص ⚠️\n⎉╎سـيتم حـظره فـور إرسـاله أي رسـالة ⩥**")

@zedub.zed_cmd(
    pattern="^صفرهم$",
    command=("صفرهم", plugin_category),
    info={
        "header": "تصفير ذاكرة المسموح لهم",
        "الاستـخـدام": "{tr}صفرهم",
    },
)
async def clear_whitelist_nuclear(event):
    delgvar("nuclear_whitelist")
    await edit_or_reply(event, Z_HEADER + "**⎉╎تـم تـصفيـر ذاكـرة المـستثنيين بـنجاح ♻️\n⎉╎تـم مـسح قـائمة السـماح بالـكامل ⩥**")

@zedub.zed_cmd(
    pattern="^المحظورين$",
    command=("المحظورين", plugin_category),
    info={
        "header": "عرض عدد المحظورين",
        "الاستـخـدام": "{tr}المحظورين",
    },
)
async def count_blocked(event):
    msg = await edit_or_reply(event, "**⎉╎جـارِ جـلب قـائمة الـضحايـا...**")
    try:
        result = await event.client(functions.contacts.GetBlockedRequest(offset=0, limit=1))
        await msg.edit(Z_HEADER + f"**⎉╎عـدد الـضحايا (المـحظورين) فـي حـسابك ⩥** `{result.count}` **☠️**")
    except Exception as e:
        await msg.edit(f"**خطأ:** {str(e)}")

@zedub.zed_cmd(
    pattern="^تصفير المحظورين$",
    command=("تصفير المحظورين", plugin_category),
    info={
        "header": "فك الحظر عن الجميع",
        "الاستـخـدام": "{tr}تصفير المحظورين",
    },
)
async def unblock_all_users(event):
    msg = await edit_or_reply(event, "**⚠️╎جـارِ بـدء عـملية العـفو العـام (فـك الحـظر)...**")
    try:
        blocked_users = await event.client(functions.contacts.GetBlockedRequest(offset=0, limit=10000))
        if not blocked_users.users:
            return await msg.edit(Z_HEADER + "**⎉╎الـقائمـة نـظيفـة ، لا يـوجـد مـحظوريـن ⩥**")

        done = 0
        for user in blocked_users.users:
            try:
                await event.client(functions.contacts.UnblockRequest(id=user.id))
                done += 1
                if done % 20 == 0:
                    await msg.edit(f"**⎉╎جـارِ تـنظيـف الـقائمـة.. ({done}/{len(blocked_users.users)}) ♻️**")
            except:
                continue

        await msg.edit(Z_HEADER + f"**⎉╎تـم تـصفيـر المـحظوريـن بـنجـاح ♻️**\n**⎉╎تـم فـك الحـظر عـن ⩥** `{done}` **مـستخـدم 🗑**")
    except Exception as e:
        await msg.edit(f"**حدث خطأ:** {str(e)}")

# =========================================================
# الرادار الصامت - إصلاح نهائي لتجنب خطأ incoming
# =========================================================

@zedub.on(events.NewMessage)
async def nuclear_block_action(event):
    # 1. التأكد أن الرسالة واردة (ليست صادرة منك) وفـي الخاص فقط
    if not event.incoming or not event.is_private:
        return

    # 2. التأكد من حالة القفل النووي
    if not gvarstatus("strict_pm_lock"):
        return

    # 3. جلب بيانات المرسل
    sender = await event.get_sender()

    # 4. الاستثناءات الأساسية (نفسك، البوتات، القنوات، الموثقين)
    if not sender or not isinstance(sender, User) or sender.bot or sender.verified or sender.is_self:
        return

    # 5. استثناء قائمة VIP والقائمة البيضاء المضافة يدوياً
    if event.chat_id in VIP_USERS or event.chat_id in get_whitelist():
        return

    # 6. كليشة الإعدام النهائية
    block_msg = (
        Z_HEADER +
        "**⎉╎عـذراً، الخـاص مـغلق حـالياً مـن قـبل الـمالك 🔒**\n"
        "**⎉╎تـم تـفـعيل الحـظـر الـتلقـائي لـلجمـيع ⩥**\n\n"
        "**•❐• 𝗕𝗹𝗼𝗰𝗸𝗲𝗱.**"
    )

    try:
        await event.reply(block_msg, link_preview=False)
        await asyncio.sleep(0.3)
    except:
        pass

    try:
        # تنفيذ الحظر
        await event.client(functions.contacts.BlockRequest(id=sender.id))
    except:
        pass
