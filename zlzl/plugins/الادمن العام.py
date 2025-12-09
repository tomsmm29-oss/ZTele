# Zed-Thon - ZelZal (Global Admin Fixed for ZTele 2025 by Mikey)
# Based on Reves/Zedthon logic, Refined for Modern Telethon
# Fixed: Kick logic, FloodWait, Imports, SQL Mocking
# Visuals: 100% Zedthon Fakhama

import asyncio
import contextlib
from datetime import datetime

from telethon.errors import BadRequestError, FloodWaitError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from telethon.utils import get_display_name

# --- تصحيح المسارات ---
from . import zedub
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format, get_user_from_event

# محاولة استدعاء SQL (مع Mocking للحماية)
try:
    from ..sql_helper.globals import addgvar, delgvar, gvarstatus
    from ..sql_helper.mute_sql import is_muted, mute, unmute
    from ..sql_helper import gban_sql_helper as gban_sql
except ImportError:
    # دوال وهمية
    def gvarstatus(val): return None
    def is_muted(id, t): return False
    def mute(id, t): pass
    def unmute(id, t): pass
    class MockGban:
        def is_gbanned(self, id): return False
        def zedgban(self, id, r): pass
        def catungban(self, id): pass
        def get_all_gbanned(self): return []
    gban_sql = MockGban()

try:
    from . import BOTLOG, BOTLOG_CHATID
except ImportError:
    BOTLOG = False
    BOTLOG_CHATID = None

# دالة لجلب المجموعات التي أنت مشرف فيها (بديلة لـ admin_groups المفقودة)
async def admin_groups(client):
    ag = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            if dialog.is_admin or dialog.is_creator:
                ag.append(dialog) # نحفظ الحوار كاملاً للاستخدام كـ InputEntity
    return ag

plugin_category = "الادمن"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

# قائمة المطورين (تم تحديثها بايديك)
zel_dev = [8241311871, 1895219306, 925972505]
KTMZ = gvarstatus("Z_KTM") or "كتم"


@zedub.zed_cmd(
    pattern="ح عام(?:\s|$)([\s\S]*)",
    command=("gban", plugin_category),
    info={
        "header": "To ban user in every group where you are admin.",
        "الـوصـف": "Will ban the person in every group where you are admin only.",
        "الاستخـدام": "{tr}gban <username/reply/userid> <reason (optional)>",
    },
)
async def zedgban(event):
    "To ban user in every group where you are admin."
    zede = await edit_or_reply(event, "**╮ ❐... جـاࢪِ حـظـࢪ الشخـص عـام**")
    start = datetime.now()
    user, reason = await get_user_from_event(event, zede)
    if not user:
        return
        
    me_id = (await event.client.get_me()).id
    if user.id == me_id:
        return await edit_delete(zede, "**⎉╎عـذراً ..لا استطيـع حظـࢪ نفسـي **")
    if user.id in zel_dev:
        return await edit_delete(zede, "**⎉╎عـذراً ..لا استطيـع حظـࢪ احـد المطـورين عـام **")

    if gban_sql.is_gbanned(user.id):
        await zede.edit(
            f"**⎉╎المسـتخـدم ↠** [{user.first_name}](tg://user?id={user.id}) \n**⎉╎مـوجــود بالفعــل فـي ↠ قائمـة المحظــورين عــام**"
        )
    else:
        gban_sql.zedgban(user.id, reason)
        
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(zede, "**⎉╎عــذراً .. يجـب ان تكــون مشـرفـاً فـي مجموعـة واحـده ع الأقــل **")
        
    await zede.edit(
        f"**⎉╎جـاري بـدء حظـر ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎مـن ↠ {len(san)} كــروب**"
    )
    
    for dialog in san:
        try:
            # استخدام input_entity لضمان التنفيذ
            await event.client(EditBannedRequest(dialog.input_entity, user.id, BANNED_RIGHTS))
            await asyncio.sleep(0.5)
            count += 1
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds + 1)
            try:
                await event.client(EditBannedRequest(dialog.input_entity, user.id, BANNED_RIGHTS))
                count += 1
            except: pass
        except BadRequestError:
            try:
                if BOTLOG_CHATID:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**⎉╎عــذراً .. لـيس لـديــك صـلاحيـات فـي ↠**\n**⎉╎كــروب :** {dialog.title}(`{dialog.id}`)",
                    )
            except: pass
        except Exception: pass
            
    end = datetime.now()
    zedtaken = (end - start).seconds
    if reason:
        await zede.edit(
            f"**⎉╎المستخـدم :** [{user.first_name}](tg://user?id={user.id})\n\n**⎉╎تم حـظـࢪه عـام مـن {count} كــࢪوب خـلال {zedtaken} ثـانيـه**\n**⎉╎السـبب :** {reason}"
        )
    else:
        await zede.edit(
            f"**╮ ❐... الشخـص :** [{user.first_name}](tg://user?id={user.id})\n\n**╮ ❐... تـم حـظـࢪه عـام مـن {count} كــࢪوب خـلال {zedtaken} ثـانيـه**"
        )
    
    if BOTLOG and count != 0:
        reply = await event.get_reply_message()
        msg_text = f"#الحظــࢪ_العـــام\n**المعلـومـات :-**\n**- الشخــص : **[{user.first_name}](tg://user?id={user.id})\n**- الايــدي : **`{user.id}`\n"
        if reason:
            msg_text += f"**- الســبب :** `{reason}`\n"
        msg_text += f"**- تـم حظـره مـن**  {count}  **كــروب**\n**- الــوقت المسـتغــࢪق :** {zedtaken} **ثــانيـه**"
        
        await event.client.send_message(BOTLOG_CHATID, msg_text)
        
        with contextlib.suppress(BadRequestError):
            if reply:
                await reply.forward_to(BOTLOG_CHATID)
                await reply.delete()


@zedub.zed_cmd(
    pattern="الغاء ح عام(?:\s|$)([\s\S]*)",
    command=("الغاء ح عام", plugin_category),
    info={
        "header": "To unban the person from every group where you are admin.",
        "الـوصـف": "will unban and also remove from your gbanned list.",
        "الاستخـدام": "{tr}ungban <username/reply/userid>",
    },
)
async def zedungban(event):
    "To unban the person from every group where you are admin."
    zede = await edit_or_reply(event, "**╮ ❐  جـاري الغــاء الحظـر العــام ❏╰**")
    start = datetime.now()
    user, reason = await get_user_from_event(event, zede)
    if not user:
        return
    if gban_sql.is_gbanned(user.id):
        gban_sql.catungban(user.id)
    else:
        return await edit_delete(
            zede,
            f"**⎉╎المسـتخـدم ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎ليـس مـوجــود فـي ↠ قائمـة المحظــورين عــام**",
        )
    
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(zede, "**⎉╎عــذراً .. يجـب ان تكــون مشـرفـاً فـي مجموعـة واحـده ع الأقــل **")
    
    await zede.edit(
        f"**⎉╎جـاري الغــاء حظـر ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎مـن ↠ {len(san)} كــروب**"
    )
    
    for dialog in san:
        try:
            await event.client(EditBannedRequest(dialog.input_entity, user.id, UNBAN_RIGHTS))
            await asyncio.sleep(0.5)
            count += 1
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds + 1)
            try:
                await event.client(EditBannedRequest(dialog.input_entity, user.id, UNBAN_RIGHTS))
                count += 1
            except: pass
        except BadRequestError:
            try:
                if BOTLOG_CHATID:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**⎉╎عــذراً .. لـيس لـديــك صـلاحيـات فـي ↠**\n**⎉╎كــروب :** {dialog.title}(`{dialog.id}`)",
                    )
            except: pass
            
    end = datetime.now()
    zedtaken = (end - start).seconds
    if reason:
        await zede.edit(
            f"**⎉╎المستخـدم :** [{user.first_name}](tg://user?id={user.id})\n\n**⎉╎تم الغــاء حـظـࢪه عـام مـن {count} كــࢪوب خـلال {zedtaken} ثـانيـه**\n**⎉╎السـبب :** {reason}"
        )
    else:
        await zede.edit(
            f"**⎉╎المستخـدم :** [{user.first_name}](tg://user?id={user.id})\n\n**⎉╎تم الغــاء حـظـࢪه عـام مـن {count} كــࢪوب خـلال {zedtaken} ثـانيـه**"
        )

    if BOTLOG and count != 0:
        msg_text = f"#الغـــاء_الحظــࢪ_العـــام\n**المعلـومـات :-**\n**- الشخــص : **[{user.first_name}](tg://user?id={user.id})\n**- الايــدي : **`{user.id}`\n"
        if reason:
            msg_text += f"**- الســبب :** `{reason}`\n"
        msg_text += f"**- تـم الغــاء حظـره مـن  {count} كــروب**\n**- الــوقت المسـتغــࢪق :** {zedtaken} **ثــانيـه**"
        
        await event.client.send_message(BOTLOG_CHATID, msg_text)


@zedub.zed_cmd(
    pattern="العام$",
    command=("العام", plugin_category),
    info={
        "header": "Shows you the list of all gbanned users by you.",
        "الاستخـدام": "{tr}listgban",
    },
)
async def gablist(event):
    "Shows you the list of all gbanned users by you."
    gbanned_users = gban_sql.get_all_gbanned()
    GBANNED_LIST = "- قائمـة المحظـورين عــام :\n\n"
    if len(gbanned_users) > 0:
        for a_user in gbanned_users:
            reason_txt = a_user.reason if hasattr(a_user, 'reason') and a_user.reason else "لا يـوجـد"
            chat_id_txt = a_user.chat_id if hasattr(a_user, 'chat_id') else "Unknown"
            GBANNED_LIST += f"**⎉╎المستخـدم :**  [{chat_id_txt}](tg://user?id={chat_id_txt}) \n**⎉╎سـبب الحظـر : {reason_txt} ** \n\n"
    else:
        GBANNED_LIST = "**- لايــوجـد محظــورين عــام بعــد**"
    await edit_or_reply(event, GBANNED_LIST)


@zedub.zed_cmd(pattern=f"{KTMZ}(?:\s|$)([\s\S]*)")
async def startgmute(event):
    if event.is_private:
        await asyncio.sleep(0.5)
        userid = event.chat_id
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user:
            return
        me_id = (await event.client.get_me()).id
        if user.id == me_id:
            return await edit_or_reply(event, "**- عــذࢪاً .. لايمكــنك كتــم نفســك ؟!**")
        if user.id in zel_dev:
            return await edit_or_reply(event, "**- عــذࢪاً .. لايمكــنك كتــم احـد المطـورين ؟!**")
        userid = user.id
        
    try:
        user = await event.client.get_entity(userid)
    except Exception:
        return await edit_or_reply(event, "**- عــذࢪاً .. لايمكــنني العثــوࢪ علـى المسـتخــدم ؟!**")
    if is_muted(userid, "gmute"):
        return await edit_or_reply(
            event,
            f"**⎉╎المستخـدم**  {_format.mentionuser(user.first_name ,user.id)} \n**⎉╎مڪتوم سابقـاً**",
        )
    try:
        mute(userid, "gmute")
    except Exception as e:
        await edit_or_reply(event, f"**- خطـأ :**\n`{e}`")
    else:
        if reason:
            await edit_or_reply(
                event,
                f"**⎉╎المستخـدم :** {_format.mentionuser(user.first_name ,user.id)}\n\n**⎉╎تم كتمــه .. بنجــاح ✓**\n**⎉╎السـبب :** {reason}",
            )
        else:
            await edit_or_reply(
                event,
                f"**⎉╎المستخـدم :** {_format.mentionuser(user.first_name ,user.id)}\n\n**⎉╎تم كتمــه .. بنجــاح ✓**",
            )
    if BOTLOG:
        reply = await event.get_reply_message()
        msg_text = "#الكتــم_العـــام\n" + f"**- الشخـص :** {_format.mentionuser(user.first_name ,user.id)} \n"
        if reason:
            msg_text += f"**- الســبب :** `{reason}`"
        await event.client.send_message(BOTLOG_CHATID, msg_text)
        if reply:
            await reply.forward_to(BOTLOG_CHATID)


@zedub.zed_cmd(pattern="الغاء كتم(?:\s|$)([\s\S]*)")
async def endgmute(event):
    if event.is_private:
        await asyncio.sleep(0.5)
        userid = event.chat_id
        reason = event.pattern_match.group(1)
    else:
        user, reason = await get_user_from_event(event)
        if not user:
            return
        me_id = (await event.client.get_me()).id
        if user.id == me_id:
            return await edit_or_reply(event, "**- عــذࢪاً .. انت غيـر مكتـوم يامطــي ؟!**")
        userid = user.id
    try:
        user = await event.client.get_entity(userid)
    except Exception:
        return await edit_or_reply(event, "**- عــذࢪاً .. لايمكــنني العثــوࢪ علـى المسـتخــدم ؟!**")
    if not is_muted(userid, "gmute"):
        return await edit_or_reply(
            event, f"**⎉╎المستخـدم :** {_format.mentionuser(user.first_name ,user.id)}\n\n**⎉╎غيـر مكتـوم عــام ✓**"
        )
    try:
        unmute(userid, "gmute")
    except Exception as e:
        await edit_or_reply(event, f"**- خطـأ :**\n`{e}`")
    else:
        if reason:
            await edit_or_reply(
                event,
                f"**⎉╎المستخـدم :** {_format.mentionuser(user.first_name ,user.id)}\n\n**⎉╎تم الغـاء كتمــه .. بنجــاح ✓**\n**⎉╎السـبب :** {reason}",
            )
        else:
            await edit_or_reply(
                event,
                f"**⎉╎المستخـدم :** {_format.mentionuser(user.first_name ,user.id)}\n\n**⎉╎تم الغـاء كتمــه .. بنجــاح ✓**",
            )
    if BOTLOG:
        msg_text = "#الغـــاء_الكتــم_العـــام\n" + f"**- الشخـص :** {_format.mentionuser(user.first_name ,user.id)} \n"
        if reason:
            msg_text += f"**- الســبب :** `{reason}`"
        await event.client.send_message(BOTLOG_CHATID, msg_text)


@zedub.zed_cmd(incoming=True)
async def watcher(event):
    if is_muted(event.sender_id, "gmute"):
        await event.delete()


@zedub.zed_cmd(
    pattern="ط عام(?:\s|$)([\s\S]*)",
    command=("ط عام", plugin_category),
    info={
        "header": "kicks the person in all groups where you are admin.",
        "الاستخـدام": "{tr}gkick <username/reply/userid> <reason (optional)>",
    },
)
async def catgkick(event):
    "kicks the person in all groups where you are admin"
    zede = await edit_or_reply(event, "**╮ ❐ ... جــاࢪِ طــرد الشخــص عــام ... ❏╰**")
    start = datetime.now()
    user, reason = await get_user_from_event(event, zede)
    if not user:
        return
    me_id = (await event.client.get_me()).id
    if user.id == me_id:
        return await edit_delete(zede, "**╮ ❐ ... عــذراً لا استطــيع طــرد نفســي ... ❏╰**")
    if user.id in zel_dev:
        return await edit_delete(zede, "**╮ ❐ ... عــذࢪاً .. لا استطــيع طــرد المطـورين ... ❏╰**")
    
    san = await admin_groups(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(zede, "**⎉╎عــذراً .. يجـب ان تكــون مشـرفـاً فـي مجموعـة واحـده ع الأقــل **")
    await zede.edit(
        f"**⎉╎بـدء طـرد ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎فـي ↠ {len(san)} كــروب**"
    )
    for dialog in san:
        try:
            # حيلة الطرد: حظر ثم إلغاء حظر فوراً (أضمن من kick_participant)
            await event.client(EditBannedRequest(dialog.input_entity, user.id, BANNED_RIGHTS))
            await asyncio.sleep(0.5)
            await event.client(EditBannedRequest(dialog.input_entity, user.id, UNBAN_RIGHTS))
            count += 1
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds + 1)
            try:
                await event.client(EditBannedRequest(dialog.input_entity, user.id, BANNED_RIGHTS))
                await asyncio.sleep(0.5)
                await event.client(EditBannedRequest(dialog.input_entity, user.id, UNBAN_RIGHTS))
                count += 1
            except: pass
        except BadRequestError:
            try:
                if BOTLOG_CHATID:
                    await event.client.send_message(
                        BOTLOG_CHATID,
                        f"**⎉╎عــذراً .. لـيس لـديــك صـلاحيـات فـي ↠**\n**⎉╎كــروب :** {dialog.title}(`{dialog.id}`)",
                    )
            except: pass
        except Exception: pass
            
    end = datetime.now()
    zedtaken = (end - start).seconds
    if reason:
        await zede.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `was gkicked in {count} groups in {zedtaken} seconds`!!\n**- الســبب :** `{reason}`"
        )
    else:
        await zede.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `was gkicked in {count} groups in {zedtaken} seconds`!!"
        )

    if BOTLOG and count != 0:
        reply = await event.get_reply_message()
        msg_text = f"#الطــࢪد_العـــام\n**المعلـومـات :-**\n**- الشخــص : **[{user.first_name}](tg://user?id={user.id})\n**- الايــدي : **`{user.id}`\n"
        if reason:
            msg_text += f"**- الســبب :** `{reason}`\n"
        msg_text += f"**- تـم طــرده مـن**  {count}  **كــروب**\n**- الــوقت المسـتغــࢪق :** {zedtaken} **ثــانيـه**"
        
        await event.client.send_message(BOTLOG_CHATID, msg_text)
        
        if reply:
            await reply.forward_to(BOTLOG_CHATID)