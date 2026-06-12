import os

from telethon.errors import UsernameOccupiedError
from telethon.tl import functions

from ..core.managers import edit_or_reply

# استدعاءات زدثون الرسمية
from . import zedub

plugin_category = "الادمن"

# =================  Z T H O N  S T Y L E  =================


@zedub.zed_cmd(pattern="^[.,]ضع بروفايل$")
async def set_pfp(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await edit_or_reply(
            event, "**•❐• عـذراً .. يجـب الـرد علـى صـورة أولاً**"
        )

    zed = await edit_or_reply(
        event, "**•❐• جـاري تعييـن صـورة البروفايـل الجـديدة ..**"
    )
    photo = await event.client.download_media(reply)
    try:
        await event.client(
            functions.photos.UploadProfilePhotoRequest(
                file=await event.client.upload_file(photo)
            )
        )
        await zed.edit("**•❐• تـم تغييـر صـورة البروفايـل بنجـاح**")
    except Exception as e:
        await zed.edit(f"**•❐• عـذراً .. حـدث خـطأ أثنـاء التغييـر :** `{str(e)}`")
    finally:
        if os.path.exists(photo):
            os.remove(photo)


@zedub.zed_cmd(pattern="^[.,]ضع بايو$")
async def set_bio(event):
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await edit_or_reply(
            event, "**•❐• عـذراً .. يجـب الـرد علـى نـص لتعيينـه بـايـو**"
        )

    zed = await edit_or_reply(event, "**•❐• جـاري تحديـث نـبذة الحسـاب (البيـو) ..**")
    try:
        await event.client(functions.account.UpdateProfileRequest(about=reply.text))
        await zed.edit("**•❐• تـم تحديـث نـبذة الحسـاب بنجـاح**")
    except Exception as e:
        await zed.edit(f"**•❐• عـذراً .. حـدث خـطأ أثنـاء التحديث :** `{str(e)}`")


@zedub.zed_cmd(pattern="^[.,]ضع اسم$")
async def set_name(event):
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await edit_or_reply(
            event, "**•❐• عـذراً .. يجـب الـرد علـى نـص لتعيينـه كاسـم**"
        )

    zed = await edit_or_reply(event, "**•❐• جـاري تغييـر اسـم الحسـاب الآن ..**")
    names = reply.text.split(maxsplit=1)
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else ""

    try:
        await event.client(
            functions.account.UpdateProfileRequest(
                first_name=first_name, last_name=last_name
            )
        )
        await zed.edit(f"**•❐• تـم تغييـر اسـم الحسـاب بـنجـاح الـى :** {reply.text}")
    except Exception as e:
        await zed.edit(f"**•❐• عـذراً .. حـدث خـطأ أثنـاء التغيير :** `{str(e)}`")


@zedub.zed_cmd(pattern="^[.,]ضع يوزر$")
async def set_username(event):
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await edit_or_reply(
            event, "**•❐• عـذراً .. يجـب الـرد علـى المعـرف المطلوب**"
        )

    new_username = reply.text.replace("@", "").strip()
    zed = await edit_or_reply(
        event, f"**•❐• جـاري محاولـة تغييـر اليـوزر إلـى @{new_username} ..**"
    )

    try:
        await event.client(
            functions.account.UpdateUsernameRequest(username=new_username)
        )
        await zed.edit(
            f"**•❐• تـم تغييـر معـرف الحسـاب بـنجـاح الـى :** @{new_username}"
        )
    except UsernameOccupiedError:
        await zed.edit("**•❐• عـذراً .. هـذا اليـوزر مـستخدم بالفعـل**")
    except Exception as e:
        await zed.edit(f"**•❐• عـذراً .. حـدث خـطأ أثنـاء التغييـر :** `{str(e)}`")


# ===========================================================
