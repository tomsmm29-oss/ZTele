import asyncio
from telethon.tl.functions.messages import DeleteMessagesRequest
from . import zedub
from ..core.managers import edit_or_reply
from ..helpers.utils import get_user_from_event

plugin_category = "الادمن"

@zedub.zed_cmd(pattern="مسح رسائلي$")
async def delete_my_messages(event):
    if event.is_private:
        return await edit_or_reply(event, "**•❐• عـذراً .. هـذا الامـر يـستخـدم داخـل المجمـوعـات فقـط**")
    
    zed = await edit_or_reply(event, "**•❐• جـاري جـمـع رسـائـلك وحـذفـهـا ..**")
    
    me = await event.client.get_me()
    count = 0
    ids = []
    
    # جلب جميع رسائلي وحذفها
    async for msg in event.client.iter_messages(event.chat_id, from_user=me.id):
        ids.append(msg.id)
        count += 1
        # الحذف على دفعات (كل 100 رسالة) لتجنب أخطاء التليجرام
        if len(ids) == 100:
            await event.client.delete_messages(event.chat_id, ids)
            ids = []
    
    if ids:
        await event.client.delete_messages(event.chat_id, ids)
    
    await zed.edit(f"**•❐• تـم حـذف ( {count} ) مـن رسـائـلك بـنجـاح**")


@zedub.zed_cmd(pattern="مسح رسائله(?:\s|$)([\s\S]*)")
async def delete_user_messages(event):
    if event.is_private:
        return await edit_or_reply(event, "**•❐• عـذراً .. هـذا الامـر يـستخـدم داخـل المجمـوعـات فقـط**")
    
    # التأكد من وجود صلاحية الحذف
    chat = await event.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await edit_or_reply(event, "**•❐• عـذراً .. لـيس لـديـك صـلاحيـات الاشـراف لـحذف رسـائـل الغـير**")
    
    if admin and not admin.delete_messages:
        return await edit_or_reply(event, "**•❐• عـذراً .. لـيس لـديـك صـلاحيـة (حـذف الرسـائـل) هـنا**")

    # تحديد المستخدم (بالرد، باليوزر، أو بالأيدي)
    user, extra = await get_user_from_event(event)
    if not user:
        return await edit_or_reply(event, "**•❐• يـرجى الـرد عـلى المـستخـدم او وضـع يـوزره/ايـديـه**")
    
    zed = await edit_or_reply(event, "**•❐• جـاري حـذف جـميـع رسـائـل المـستخـدم ..**")
    
    count = 0
    ids = []
    
    async for msg in event.client.iter_messages(event.chat_id, from_user=user.id):
        ids.append(msg.id)
        count += 1
        if len(ids) == 100:
            await event.client.delete_messages(event.chat_id, ids)
            ids = []
            
    if ids:
        await event.client.delete_messages(event.chat_id, ids)
    
    await zed.edit(f"**•❐• تـم حـذف ( {count} ) مـن رسـائـل الـمـستخـدم بـنجـاح**")