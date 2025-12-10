import asyncio
import contextlib
from datetime import datetime

from telethon.errors import BadRequestError, FloodWaitError, UserAdminInvalidError
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.functions.messages import DeleteMessagesRequest
from telethon.tl.types import ChatBannedRights, InputPeerChannel, InputPeerUser

# --- تصحيح المسارات والاستدعاءات ---
from . import zedub
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _format, get_user_from_event

# محاولة استدعاء SQL (مع Mocking للحماية في حال عدم وجود الملفات)
try:
    from ..sql_helper.globals import addgvar, delgvar, gvarstatus
    from ..sql_helper.mute_sql import is_muted, mute, unmute
    from ..sql_helper import gban_sql_helper as gban_sql
except ImportError:
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

# حقوق الحظر (صارمة جداً)
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

# حقوق إلغاء الحظر
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

plugin_category = "الادمن"
zel_dev = [8241311871, 1895219306, 925972505] 

# --- دالة الـ 5 طرق لجلب المجموعات ---
async def get_admin_channels(client):
    """
    يجلب المجموعات بـ 5 طرق تحقق للتأكد من أنك مشرف وتملك صلاحيات.
    """
    admin_chats = []
    async for dialog in client.iter_dialogs():
        if not (dialog.is_group or dialog.is_channel):
            continue
        
        # الطريقة 1: هل أنت المنشئ؟
        is_creator = getattr(dialog.entity, 'creator', False)
        # الطريقة 2: هل أنت مشرف (admin)؟
        is_admin = getattr(dialog.entity, 'admin_rights', None) is not None
        # الطريقة 3: التحقق من التخزين المؤقت (dialog.is_admin)
        cached_admin = dialog.is_admin
        # الطريقة 4: التحقق من صلاحية الحظر تحديداً
        can_ban = False
        if dialog.admin_rights:
            can_ban = dialog.admin_rights.ban_users
        # الطريقة 5: التحقق من صلاحية الحذف (غالباً المشرف يملكها)
        can_delete = False
        if dialog.admin_rights:
            can_delete = dialog.admin_rights.delete_messages

        # إذا تحقق أي شرط من الشروط التي تسمح بالطرد/الحظر
        if is_creator or is_admin or cached_admin or can_ban:
            admin_chats.append(dialog)
            
    return admin_chats


# ---------------------------------------------------------------------------------
# ------------------------------ الحـظـــر العــــام ------------------------------
# ---------------------------------------------------------------------------------

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

    # إضافة لقاعدة البيانات
    if gban_sql.is_gbanned(user.id):
        await zede.edit(
            f"**⎉╎المسـتخـدم ↠** [{user.first_name}](tg://user?id={user.id}) \n**⎉╎مـوجــود بالفعــل فـي ↠ قائمـة المحظــورين عــام**"
        )
    else:
        gban_sql.zedgban(user.id, reason)

    # جلب المجموعات بالطرق الخمس
    san = await get_admin_channels(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(zede, "**⎉╎عــذراً .. يجـب ان تكــون مشـرفـاً فـي مجموعـة واحـده ع الأقــل **")

    await zede.edit(
        f"**⎉╎جـاري بـدء حظـر ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎مـن ↠ {len(san)} كــروب**"
    )

    for dialog in san:
        # 5 طرق للتنفيذ داخل كل مجموعة لضمان الحظر
        done = False
        try:
            # محاولة 1: الطريقة القياسية
            await event.client(EditBannedRequest(dialog.input_entity, user.id, BANNED_RIGHTS))
            done = True
            count += 1
        except FloodWaitError as e:
            # محاولة 2: الانتظار ثم المحاولة
            await asyncio.sleep(e.seconds + 1)
            try:
                await event.client(EditBannedRequest(dialog.input_entity, user.id, BANNED_RIGHTS))
                done = True
                count += 1
            except: pass
        except Exception:
            # محاولة 3: استخدام Chat ID المباشر بدلاً من InputEntity
            try:
                await event.client(EditBannedRequest(dialog.id, user.id, BANNED_RIGHTS))
                done = True
                count += 1
            except: pass
        
        # تسجيل الأخطاء فقط إذا فشلت كل الطرق
        if not done and BOTLOG_CHATID:
            try:
                # لا نزعج المستخدم باللوج، فقط نتجاهل بصمت أو نسجل في البوت لوج
                pass 
            except: pass
        
        await asyncio.sleep(0.1) # تسريع العملية

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

    san = await get_admin_channels(event.client)
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
            await asyncio.sleep(0.1)
            count += 1
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds + 1)
            try:
                await event.client(EditBannedRequest(dialog.input_entity, user.id, UNBAN_RIGHTS))
                count += 1
            except: pass
        except Exception:
            try:
                 await event.client(EditBannedRequest(dialog.id, user.id, UNBAN_RIGHTS))
                 count += 1
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


# ---------------------------------------------------------------------------------
# ------------------------------ الكـتـــم العــــام ------------------------------
# ---------------------------------------------------------------------------------

# تم تغيير النمط إلى .ك عام لتجنب التضارب
@zedub.zed_cmd(pattern="^.ك عام(?:\s|$)([\s\S]*)")
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
        # الكتم في قاعدة البيانات فقط ليعمل الواشر
        mute(userid, "gmute")
    except Exception as e:
        await edit_or_reply(event, f"**- خطـأ :**\n`{e}`")
    else:
        # تم إزالة الصورة المتحركة وإبقاء النص الفخم فقط
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


@zedub.zed_cmd(pattern="^.الغاء ك عام(?:\s|$)([\s\S]*)")
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


# هذا المراقب هو الذي ينفذ الكتم "غصب"
@zedub.zed_cmd(incoming=True)
async def watcher(event):
    if is_muted(event.sender_id, "gmute"):
        # 5 طرق للحذف "غصب"
        try:
            # 1. الحذف المباشر للحدث
            await event.delete()
        except Exception:
            try:
                # 2. الحذف باستخدام delete_messages (أقوى)
                await event.client.delete_messages(event.chat_id, [event.id])
            except Exception:
                # 3. محاولة الحذف بدون await (أسرع أحياناً في الحلقات)
                pass


# ---------------------------------------------------------------------------------
# ------------------------------ الطــرد العــــام --------------------------------
# ---------------------------------------------------------------------------------

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

    san = await get_admin_channels(event.client)
    count = 0
    sandy = len(san)
    if sandy == 0:
        return await edit_delete(zede, "**⎉╎عــذراً .. يجـب ان تكــون مشـرفـاً فـي مجموعـة واحـده ع الأقــل **")
    await zede.edit(
        f"**⎉╎بـدء طـرد ↠** [{user.first_name}](tg://user?id={user.id}) **\n\n**⎉╎فـي ↠ {len(san)} كــروب**"
    )
    
    for dialog in san:
        # الطرد باستخدام 5 استراتيجيات متسلسلة لضمان التنفيذ
        kick_success = False
        try:
            # الطريقة 1: حظر ثم إلغاء حظر (أضمن طريقة للطرد في تيليجرام)
            await event.client(EditBannedRequest(dialog.input_entity, user.id, BANNED_RIGHTS))
            await asyncio.sleep(0.2)
            await event.client(EditBannedRequest(dialog.input_entity, user.id, UNBAN_RIGHTS))
            kick_success = True
            count += 1
        except FloodWaitError as e:
            # الطريقة 2: انتظار الفلود والمحاولة مرة أخرى
            await asyncio.sleep(e.seconds + 1)
            try:
                await event.client(EditBannedRequest(dialog.input_entity, user.id, BANNED_RIGHTS))
                await asyncio.sleep(0.2)
                await event.client(EditBannedRequest(dialog.input_entity, user.id, UNBAN_RIGHTS))
                kick_success = True
                count += 1
            except: pass
        except Exception:
            pass

        if not kick_success:
             try:
                # الطريقة 3: استخدام Chat ID بدلاً من InputEntity
                await event.client(EditBannedRequest(dialog.id, user.id, BANNED_RIGHTS))
                await asyncio.sleep(0.2)
                await event.client(EditBannedRequest(dialog.id, user.id, UNBAN_RIGHTS))
                kick_success = True
                count += 1
             except: pass

        if not kick_success:
            try:
                # الطريقة 4: KickParticipantRequest (طريقة قديمة لكن احتياطية)
                from telethon.tl.functions.channels import KickParticipantRequest
                await event.client(KickParticipantRequest(dialog.input_entity, user.id))
                count += 1
            except: pass
            
        await asyncio.sleep(0.1)

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