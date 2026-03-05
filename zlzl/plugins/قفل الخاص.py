import asyncio
from telethon import functions
from telethon.tl.types import User, Chat, Channel
from zlzl import zedub
from zlzl.core.managers import edit_delete
from zlzl.sql_helper.globals import addgvar, delgvar, gvarstatus

# ----------------------------------------------------------------
# إعدادات الشعار الفخم
ZED_LINK = "https://t.me/ZThon"
Z_LOGO = f"[𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁]({ZED_LINK})"
# ----------------------------------------------------------------

def get_nuclear_whitelist():
    """جلب قائمة المسموح لهم من قاعدة البيانات"""
    wl = gvarstatus("nuclear_whitelist")
    if not wl:
        return []
    return [int(x) for x in wl.split()]

def add_to_whitelist(chat_id):
    """إضافة شخص للقائمة البيضاء"""
    wl = get_nuclear_whitelist()
    if chat_id not in wl:
        wl.append(chat_id)
        addgvar("nuclear_whitelist", " ".join(map(str, wl)))

def remove_from_whitelist(chat_id):
    """إزالة شخص من القائمة البيضاء"""
    wl = get_nuclear_whitelist()
    if chat_id in wl:
        wl.remove(chat_id)
        if len(wl) == 0:
            delgvar("nuclear_whitelist")
        else:
            addgvar("nuclear_whitelist", " ".join(map(str, wl)))

# ----------------------------------------------------------------

@zedub.zed_cmd(pattern="قفل الخاص$")
async def strict_lock(event):
    """تفعيل وضع الإبادة"""
    if gvarstatus("strict_pm_lock"):
        return await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔒 الوضع النووي مفعل مسبقاً .. لا أحد يمر.**")

    addgvar("strict_pm_lock", "active")
    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔒 تم تشغيل الدروع .. الخاص مغلق للجميع (باستثناء قائمة السماح).**")


@zedub.zed_cmd(pattern="فتح الخاص$")
async def strict_unlock(event):
    """تعطيل وضع الإبادة"""
    if not gvarstatus("strict_pm_lock"):
        return await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔓 الدروع متوقفة بالفعل .. الخاص مفتوح.**")

    delgvar("strict_pm_lock")
    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n🔓 تم إيقاف الدروع .. الخاص مفتوح.**")


@zedub.zed_cmd(pattern="فتح$")
async def allow_user_nuclear(event):
    """استثناء المستخدم الحالي من الحظر النووي (بدل كلمة سماح)"""
    if not event.is_private:
        return await edit_delete(event, "**⚠️ هذا الأمر يعمل في الخاص فقط.**")

    chat_id = event.chat_id
    add_to_whitelist(chat_id)

    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n✅ تم منح العفو لهذا المستخدم.\n لن يتم حظره أثناء قفل الخاص.**")


@zedub.zed_cmd(pattern="صفر$")
async def reset_user_nuclear(event):
    """إزالة الاستثناء (سيتم حظره في الرسالة القادمة)"""
    if not event.is_private:
        return await edit_delete(event, "**⚠️ هذا الأمر يعمل في الخاص فقط.**")

    chat_id = event.chat_id
    remove_from_whitelist(chat_id)

    await edit_delete(event, f"**🖥┊نظام الحماية {Z_LOGO}\n\n♻️ تم تصفير وضع المستخدم.\n🚫 سيتم حظره فوراً عند إرسال أي رسالة.**")


@zedub.zed_cmd(pattern="المحظورين$")
async def count_blocked(event):
    """عرض عدد الضحايا"""
    msg = await edit_delete(event, f"** جارِ جلب قائمة الضحايا...**")
    try:
        result = await event.client(functions.contacts.GetBlockedRequest(offset=0, limit=0))
        count = result.count
        await msg.edit(f"**🖥┊نظام الحماية {Z_LOGO}**\n\n**☠️ عدد المحظورين في حسابك:** `{count}`")
    except Exception as e:
        await msg.edit(f"**خطأ:** {str(e)}")


@zedub.zed_cmd(pattern="تصفير المحظورين$")
async def unblock_all_users(event):
    """فك الحظر عن الجميع"""
    msg = await edit_delete(event, f"**⚠️ جارِ بدء عملية العفو العام (فك الحظر عن الجميع)...**")
    try:
        blocked_users = await event.client(functions.contacts.GetBlockedRequest(offset=0, limit=10000))
        users_list = blocked_users.users

        if not users_list:
            return await msg.edit(f"**🖥┊نظام الحماية {Z_LOGO}**\n\n**✅ القائمة نظيفة، لا يوجد محظورين.**")

        done = 0
        for user in users_list:
            try:
                # استخدام id صريح للتوافق مع التحديثات الجديدة
                await event.client(functions.contacts.UnblockRequest(id=user.id))
                done += 1
                if done % 20 == 0:
                    await msg.edit(f"** جارِ تنظيف القائمة.. ({done}/{len(users_list)})**")
            except:
                pass

        await msg.edit(f"**🖥┊نظام الحماية {Z_LOGO}**\n\n**✅ تم تصفير المحظورين بنجاح.**\n**🗑 تم فك الحظر عن:** `{done}` **مستخدم.**")
    except Exception as e:
        await msg.edit(f"**حدث خطأ:** {str(e)}")


@zedub.zed_handler(incoming=True, func=lambda e: e.is_private)
async def nuclear_block_action(event):
    """
    المراقب النووي: يحظر الأشخاص فقط (بدون قنوات وبوتات) إلا المسموح لهم
    """
    # 1. الخروج فوراً إذا كان وضع قفل الخاص غير مفعل
    if not gvarstatus("strict_pm_lock"):
        return

    sender = await event.get_sender()

    # 2. التأكد من أن المرسل شخص حقيقي (ليس بوت ولا قناة ولا أنت ولا حساب تيليجرام الرسمي)
    if not sender or not isinstance(sender, User) or sender.bot or sender.verified or sender.is_self:
        return

    chat_id = event.chat_id

    # 3. التحقق من القائمة البيضاء (الاستثناءات التي تم كتابة "فتح" لها)
    whitelisted_ids = get_nuclear_whitelist()
    if chat_id in whitelisted_ids:
        return

    # 4. الرسالة الفخمة قبل الإعدام
    block_msg = (
        f"**🖥┊نظام الحماية {Z_LOGO}**\n\n"
        "**🔒 الخاص مقفل (Strict Lockdown)**\n"
        "**🚫 تم تفعيل الحظر التلقائي للجميع.**\n"
        "**⚠️ 𝗕𝗹𝗼𝗰𝗸𝗲𝗱.**"
    )

    try:
        # إرسال الرسالة أولاً
        await event.reply(block_msg, link_preview=False)
        # الانتظار قليلاً لضمان وصول الرسالة قبل الحظر
        await asyncio.sleep(0.5)
        # تنفيذ طلب الحظر (حظر فقط بدون حذف المحادثة باستخدام التعريف الحديث)
        await event.client(functions.contacts.BlockRequest(id=sender.id))
    except Exception as e:
        print(f"Error in Nuclear Block: {e}")