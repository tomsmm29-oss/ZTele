# Zed-Thon - ZelZal (Tag/Mention Fixed for ZTele 2025 by Mikey)
# Removed Duplicates + Optimized Loops + Relative Paths

import asyncio
from telethon.tl.types import ChannelParticipantsAdmins

# --- تصحيح المسارات ---
from . import zedub
from ..core.logger import logging
from ..core.managers import edit_or_reply
from ..helpers.utils import get_user_from_event, reply_id

LOGS = logging.getLogger(__name__)
plugin_category = "الادمن"

# متغير عالمي للتحكم في التاك
moment_worker = []

@zedub.zed_cmd(pattern="ايقاف التاك?(.*)")
async def stop_tagall(event):
  global moment_worker
  if not event.chat_id in moment_worker:
    return await edit_or_reply(event, '**- عـذراً .. لا يوجـد هنـاك تـاك لـ إيقـافـه ؟!**')
  else:
    try:
      moment_worker.remove(event.chat_id)
    except:
      pass
    return await edit_or_reply(event, '**⎉╎تم إيقـاف التـاك .. بنجـاح ✓**')


@zedub.zed_cmd(pattern="(all|تاك)(?:\s|$)([\s\S]*)")
async def tagall(event):
  global moment_worker
  
  if event.is_private:
    return await edit_or_reply(event, "**- عـذراً ... هـذه ليـست مجمـوعـة ؟!**")
    
  # تحديد النمط (رسالة ولا رد)
  if event.pattern_match.group(2):
    mode = "by_cmd"
    msg = event.pattern_match.group(2)
  elif event.reply_to_msg_id:
    mode = "by_reply"
    msg = await event.get_reply_message() # جلب كائن الرسالة
    if msg == None:
        return await edit_or_reply(event, "**- عـذراً ... الرسـالة غيـر ظـاهـرة للأعضـاء الجـدد ؟!**")
  else:
    return await edit_or_reply(event, "**- بالـرد عـلى رسـالـه . . او باضـافة نـص مـع الامـر**")

  moment_worker.append(event.chat_id)
  usrnum = 0
  usrtxt = ""
  
  async for usr in event.client.iter_participants(event.chat_id):
      # التحقق من الإيقاف
      if event.chat_id not in moment_worker:
        return

      usrnum += 1
      usrtxt += f"- [{usr.first_name}](tg://user?id={usr.id}) "
      
      if usrnum == 5:
        if mode == "by_cmd":
            await event.client.send_message(event.chat_id, f"{usrtxt}\n\n- {msg}")
        else: # by_reply
            await event.client.send_message(event.chat_id, usrtxt, reply_to=msg)
            
        await asyncio.sleep(2)
        usrnum = 0
        usrtxt = ""
        
  # تنظيف القائمة بعد الانتهاء
  if event.chat_id in moment_worker:
      moment_worker.remove(event.chat_id)


@zedub.zed_cmd(pattern="تبليغ$")
async def tag_admins(event):
    mentions = "- انتباه الى المشرفين تم تبليغكم \n@admin"
    chat = await event.get_input_chat()
    reply_to_id = await reply_id(event)
    async for x in event.client.iter_participants(
        chat, filter=ChannelParticipantsAdmins
    ):
        if not x.bot:
            mentions += f"[\u2063](tg://user?id={x.id})"
    await event.client.send_message(event.chat_id, mentions, reply_to=reply_to_id)
    await event.delete()


@zedub.zed_cmd(pattern="منشن ([\s\S]*)")
async def mention_user(event):
    user, input_str = await get_user_from_event(event)
    if not user:
        return
    reply_to_id = await reply_id(event)
    await event.delete()
    await event.client.send_message(
        event.chat_id,
        f"<a href='tg://user?id={user.id}'>{input_str}</a>",
        parse_mode="HTML",
        reply_to=reply_to_id,
    )