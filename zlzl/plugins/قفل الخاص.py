import asyncio
from telethon import functions, events
from telethon.tl.types import User

# --- الاستدعاءات الصحيحة حسب مسارات سورس زدثون ---
from . import zedub
from ..core.managers import edit_delete
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

# ----------------------------------------------------------------
# إعدادات الشعار الفخم
ZED_LINK = "https://t.me/ZThon"
Z_LOGO = f"[𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁]({ZED_LINK})"
# ----------------------------------------------------------------

# دوال مبسطة للتعامل مع قاعدة البيانات
def get_whitelist():
    wl = gvarstatus("nuclear_whitelist")
    return [int(x) for x in wl.split()] if wl else []

def update_whitelist(wl_list):
    if not wl_list:
        delgvar("nuclear_whitelist")
    else:
        addgvar("nuclear_whitelist", " ".join(map(str, wl_list)))

# ----------------------------------------------------------------

@zedub.zed_cmd(pattern="ق خاص")
async def strict_lock(event):
    """تفعيل وضع الإبادة الشامل"""
    if gvarstatus("strict_pm_lock"):
        return await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔒 الوضع النووي مفعل مسبقاً .. لا أحد يمر.**")

    addgvar("strict_pm_lock", "active")
    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔒 تم تشغيل الدروع .. الخاص مغلق للجميع (باستثناء قائمة السماح).**")


@zedub.zed_cmd(pattern="ف خاص")
async def strict_unlock(event):
    """تعطيل وضع الإبادة الشامل"""
    if not gvarstatus("strict_pm_lock"):
        return await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔓 الدروع متوقفة بالفعل .. الخاص مفتوح.**")

    delgvar("strict_pm_lock")
    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔓 تم إيقاف الدروع .. الخاص مفتوح.**")


@zedub.zed_cmd(pattern="فتح")
async def allow_user_nuclear(event):
    """استثناء المستخدم الحالي من الحظر"""
    if not event.is_private:
        return await edit_delete(event, "**⚠️ هذا الأمر يعمل في الخاص فقط.**")

    chat_id = event.chat_id
    wl = get_whitelist()
    if chat_id not in wl:
        wl.append(chat_id)
        update_whitelist(wl)

    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n✅ تم منح العفو لهذا المستخدم.\n لن يتم حظره أثناء قفل الخاص.**")


@zedub.zed_cmd(pattern="قفل")
async def reset_user_nuclear(event):
    """إزالة الاستثناء (تصفير الذاكرة ليتم حظره)"""
    if not event.is_private:
        return await edit_delete(event, "**⚠️ هذا الأمر يعمل في الخاص فقط.**")

    chat_id = event.chat_id
    wl = get_whitelist()
    if chat_id in wl:
        wl.remove(chat_id)
        update_whitelist(wl)

    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n♻️ تم تصفير وضع المستخدم.\n🚫 سيتم حظره فوراً عند إرسال أي رسالة.**")


@zedub.zed_cmd(pattern="المحظورين")
async def count_blocked(event):
    """عرض عدد المحظورين"""
    msg = await edit_delete(event, "** جارِ جلب قائمة الضحايا...**")
    try:
        result = await event.client(functions.contacts.GetBlockedRequest(offset=0, limit=1))
        await msg.edit(f"**🖥┊نظام الحماية {Z_LOGO}**\n\n**☠️ عدد المحظورين في حسابك:** `{result.count}`")
    except Exception as e:
        await msg.edit(f"**خطأ:** {str(e)}")


@zedub.zed_cmd(pattern="تصفير المحظورين")
async def unblock_all_users(event):
    """فك الحظر عن الجميع"""
    msg = await edit_delete(event, "**⚠️ جارِ بدء عملية العفو العام (فك الحظر عن الجميع)...**")
    try:
        blocked_users = await event.client(functions.contacts.GetBlockedRequest(offset=0, limit=10000))
        if not blocked_users.users:
            return await msg.edit(f"**🖥┊نظام الحماية {Z_LOGO}**\n\n**✅ القائمة نظيفة، لا يوجد محظورين.**")

        done = 0
        for user in blocked_users.users:
            try:
                await event.client(functions.contacts.UnblockRequest(id=user.id))
                done += 1
                if done % 20 == 0:
                    await msg.edit(f"** جارِ تنظيف القائمة.. ({done}/{len(blocked_users.users)})**")
            except:
                continue

        await msg.edit(f"**🖥┊نظام الحماية {Z_LOGO}**\n\n**✅ تم تصفير المحظورين بنجاح.**\n**🗑 تم فك الحظر عن:** `{done}` **مستخدم.**")
    except Exception as e:
        await msg.edit(f"**حدث خطأ:** {str(e)}")


# استخدمنا events.NewMessage لأنها الطريقة الأقوى والأكثر توافقاً لصيد الرسائل الواردة في تيليجرام
@zedub.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def nuclear_block_action(event):
    """
    الرادار النووي: يعمل بتلقائية وسرعة
    """
    # 1. إذا الوضع معطل، اخرج فوراً لتوفير الموارد
    if not gvarstatus("strict_pm_lock"):
        return

    sender = await event.get_sender()

    # 2. التأكد من أن المرسل شخص طبيعي (تجاهل البوتات والقنوات ونفسك وموثقين تيليجرام)
    if not sender or not isinstance(sender, User) or sender.bot or sender.verified or sender.is_self:
        return

    # 3. التحقق مما إذا كان الشخص مسموح له (مكتوب له "فتح")
    if event.chat_id in get_whitelist():
        return

    # 4. الكليشة
    block_msg = (
        f"**🖥┊نظام الحماية {Z_LOGO}**\n\n"
        "**🔒 الخاص مقفل (Strict Lockdown)**\n"
        "**🚫 تم تفعيل الحظر التلقائي للجميع.**\n"
        "**⚠️ 𝗕𝗹𝗼𝗰𝗸𝗲𝗱.**"
    )

    try:
        # إرسال التحذير
        await event.reply(block_msg, link_preview=False)
        await asyncio.sleep(0.3)
    except:
        pass # تجاهل الأخطاء إن لم يستطع الإرسال وأكمل لعملية الحظر

    try:
        # تنفيذ الحظر النهائي بدون مسح المحادثة
        await event.client(functions.contacts.BlockRequest(id=sender.id))
    except Exception as e:
        print(f"Error Blocking: {e}")