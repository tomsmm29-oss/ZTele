import asyncio

from telethon.errors import FloodWaitError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest
from telethon.tl.functions.messages import AddChatUserRequest

from ..core.managers import edit_delete, edit_or_reply

# --- تصحيح المسارات لـ ZThon ---
from . import zedub


@zedub.zed_cmd(pattern="انضمام ([\s\S]*)")
async def lol(event):
    a = event.text
    bol = a[7:]  # ظبطت القص عشان كلمة "انضمام" 6 حروف + مسافة
    sweetie = "- جاري الانضمام الى المجموعة انتظر قليلا  ."
    await event.reply(sweetie, parse_mode=None, link_preview=None)
    try:
        await zedub(JoinChannelRequest(bol))
        await event.edit("**- تم الانضمام بنجاح  ✓**")
    except Exception as e:
        await event.edit(str(e))


@zedub.zed_cmd(pattern="اضافة ([\s\S]*)")
async def _(event):
    to_add_users = event.pattern_match.group(1)
    if not event.is_channel and event.is_group:
        for user_id in to_add_users.split(" "):
            try:
                await event.client(
                    AddChatUserRequest(
                        chat_id=event.chat_id, user_id=user_id, fwd_limit=1000000
                    )
                )
            except Exception as e:
                return await edit_delete(event, f"`{str(e)}`", 5)
    else:
        for user_id in to_add_users.split(" "):
            try:
                await event.client(
                    InviteToChannelRequest(channel=event.chat_id, users=[user_id])
                )
            except Exception as e:
                return await edit_delete(event, f"`{e}`", 5)

    await edit_or_reply(event, f"**{to_add_users} تم إضافته بنجاح ✓**")


@zedub.zed_cmd(pattern="ضيف ([\s\S]*)", groups_only=True)
async def get_users(event):
    # ظبطت القص هنا كمان عشان يظبط مع كلمة "ضيف"
    if event.text.startswith("."):
        legen_ = event.text[5:]
    else:
        legen_ = event.text[4:]  # لو مفيش نقطة (رغم ان النمط فيه نقطة بس للامان)

    input_str = event.pattern_match.group(1)
    # zedub_chat = legen_.lower() # دي ملهاش لازمة بس سيبتها عشان ماغيرش اللوجيك
    zedb = await edit_or_reply(event, f"**جارِ إضـافـة الاعضاء من  ** {legen_}")
    sender = await event.get_sender()
    me = await event.client.get_me()
    if not sender.id == me.id:
        await zedb.edit("**⎉╎ جـارِ إتمـام العمليـة انتظــر ⅏ . . .**")
    else:
        await zedb.edit("**⎉╎ جـارِ إتمـام العمليـة انتظــر ⅏ . . .**")
    if event.is_private:
        return await zedb.edit("**╮  لا استطـيع إضافـة الأعضـاء هـنا 𓅫╰**")
    s = 0
    f = 0
    error = "None"
    try:
        chat = await event.client.get_entity(input_str)
    except Exception as e:
        return await zedb.edit(f"**خطأ في جلب المجموعة:** `{str(e)}`")

    await zedb.edit("**⎉╎حالة الإضافة:**\n\n**⎉╎تتم جمع معلومات المستخدمين 🔄 ...⏣**")
    async for user in event.client.iter_participants(chat):
        if user.bot:
            continue  # تخطي البوتات عشان النضافة
        try:
            if error.startswith("Too"):
                return await zedb.edit(
                    f"**حالة الإضافة انتهت مع الأخطاء**\n- (**ربما هنالك ضغط على الأمر حاول مجددا لاحقا **) \n**الخطأ** : \n`{error}`\n\n• إضافة `{s}` \n• خطأ بإضافة `{f}`"
                )

            await zedub(InviteToChannelRequest(channel=event.chat_id, users=[user.id]))
            s = s + 1
            await zedb.edit(
                f"**⎉╎تتم الإضافة **\n\n• إضيف `{s}` \n•  خطأ بإضافة `{f}` \n\n**× اخر خطأ:** `{error}`"
            )
            await asyncio.sleep(0.5)  # فاصل زمني بسيط عشان الفلود
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds)
        except UserPrivacyRestrictedError:
            f = f + 1
        except Exception as e:
            error = str(e)
            f = f + 1
    return await zedb.edit(
        f"**⎉╎اڪتملت الإضافة ✅** \n\n• تم بنجاح إضافة `{s}` \n• خطأ بإضافة `{f}`"
    )
