import asyncio
from telethon.tl.types import User
from . import zedub
from ..core.managers import edit_or_reply

plugin_category = "الادمن"

@zedub.zed_cmd(pattern="^[.,]عرض الحسابات$")
async def show_real_users(event):
    zed = await edit_or_reply(event, "**•❐• جـاري جـلـب قـائمـة الـحسـابـات الـحـقـيقيـة مـن الـخـاص ..**")
    
    me = await event.client.get_me()
    users_list =[]
    count = 0

    # فحص جميع المحادثات
    async for dialog in event.client.iter_dialogs():
        entity = dialog.entity
        # الشروط: محادثة فردية + ليس بوت + ليس حساب تليجرام الرسمي + ليس رسائلي المحفوظة
        if dialog.is_user and not entity.bot and entity.id not in[777000, me.id]:
            count += 1
            name = entity.first_name or "بدون اسم"
            # تنظيف الاسم من الأكواد لتجنب كسر التنسيق
            name = name.replace("[", "").replace("]", "").replace("*", "").replace("`", "")
            
            username = f" | @{entity.username}" if entity.username else ""
            user_link = f"[{name}](tg://user?id={entity.id})"
            
            users_list.append(f"**{count} •** {user_link}{username}")

    if count == 0:
        return await zed.edit("**•❐• لـم يـتـم الـعـثور عـلى أي مـحادثـات خـاصـة مـع أشـخـاص حـقـيقيـيـن**")

    # تجميع الكليشة الأساسية
    header = (
        "**🛂┊كشـف الحـسـابات - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**⎉╎تم العثور على {count}  حـسـاب**\n"
        "**⎉╎لـحذف الحـسـابات استخدم الامـر التالي ⩥** `.الحسابات حذف`\n\n"
        "**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**\n\n"
    )
    
    text = header
    messages =[]
    
    # تقسيم الرسالة برمجياً في حال كان العدد ضخماً وتجاوز حد التليجرام
    for user in users_list:
        if len(text) + len(user) + 2 > 4000:
            messages.append(text)
            text = user + "\n"
        else:
            text += user + "\n"
            
    if text:
        messages.append(text)

    # إرسال الدفعة الأولى كتعديل للرسالة
    await zed.edit(messages[0])
    
    # إرسال الباقي كرسائل تكميلية إذا كانت القائمة ضخمة
    if len(messages) > 1:
        for msg in messages[1:]:
            await event.reply(msg)


@zedub.zed_cmd(pattern="^[.,]الحسابات حذف$")
async def delete_real_users(event):
    zed = await edit_or_reply(event, "**•❐• جـاري حـذف شـات كـافـة الأشـخـاص مـن الـخـاص ..**\n**• قـد يـستـغرق الأمـر بـعض الـوقـت ..**")
    
    me = await event.client.get_me()
    count = 0

    async for dialog in event.client.iter_dialogs():
        entity = dialog.entity
        if dialog.is_user and not entity.bot and entity.id not in[777000, me.id]:
            try:
                await event.client.delete_dialog(dialog.id)
                count += 1
                await asyncio.sleep(0.2)
            except Exception:
                continue

    await zed.edit(f"**•❐• تـم تـطـهيـر الـخـاص بـنجـاح**\n**• تـم حـذف شـات ( {count} ) حـسـاب حـقـيقي**")