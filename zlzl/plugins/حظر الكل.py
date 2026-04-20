import asyncio
from telethon.errors import FloodWaitError
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest

from . import zedub
from ..core.managers import edit_or_reply

plugin_category = "الادمن"
zel_dev =[8241311871, 1111565135, 6114298715]

@zedub.zed_cmd(pattern="بلو$")
async def block_all_pm(event):
    if event.is_private:
        return await edit_or_reply(event, "**•❐• عـذراً .. هـذا الامـر يـستخـدم داخـل المجمـوعـات فقـط**")

    zed = await edit_or_reply(event, "**•❐• جـاري حـظـر جميـع اعضـاء المجمـوعـة مـن الخـاص ..**")
    
    me = await event.client.get_me()
    count = 0

    async for user in event.client.iter_participants(event.chat_id):
        if user.id == me.id or user.bot or user.id in zel_dev:
            continue
            
        try:
            await event.client(BlockRequest(id=user.id))
            count += 1
        except FloodWaitError as e:
            # انتظار اجباري من تيليجرام لتجنب طرد الحساب (لا يمكن حذفه)
            await asyncio.sleep(e.seconds)
        except Exception:
            continue

    await zed.edit(f"**•❐• تـم حـظـر ( {count} ) عضـو مـن الخـاص بـك بنجـاح**")


@zedub.zed_cmd(pattern="الغاء بلو$")
async def unblock_all_pm(event):
    if event.is_private:
        return await edit_or_reply(event, "**•❐• عـذراً .. هـذا الامـر يـستخـدم داخـل المجمـوعـات فقـط**")

    zed = await edit_or_reply(event, "**•❐• جـاري الغـاء حـظـر جميـع اعضـاء المجمـوعـة مـن الخـاص ..**")
    
    me = await event.client.get_me()
    count = 0

    async for user in event.client.iter_participants(event.chat_id):
        if user.id == me.id or user.bot or user.id in zel_dev:
            continue
            
        try:
            await event.client(UnblockRequest(id=user.id))
            count += 1
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except Exception:
            continue

    await zed.edit(f"**•❐• تـم الغـاء حـظـر ( {count} ) عضـو مـن الخـاص بـك بنجـاح**")