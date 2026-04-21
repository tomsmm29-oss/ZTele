import os
from telethon.tl import functions
from telethon.errors import UsernameOccupiedError
from zlzl.utils import admin_cmd
from zlzl.core.session import zedub

# 1. ميزة: ضع بروفايل (بالرد على صورة)
@zedub.on(admin_cmd(pattern="ضع بروفايل$"))
async def set_pfp(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await event.edit("⚠️ **بالرد على صورة أولاً!**")
    
    await event.edit("🔄 **جاري تغيير صورة البروفايل...**")
    photo = await event.client.download_media(reply)
    try:
        await event.client(functions.photos.UploadProfilePhotoRequest(
            file=await event.client.upload_file(photo)
        ))
        await event.edit("✅ **تم تغيير صورة البروفايل بنجاح!**")
    except Exception as e:
        await event.edit(f"❌ **فشل التغيير:** {str(e)}")
    finally:
        if os.path.exists(photo):
            os.remove(photo)

# 2. ميزة: ضع بايو (بالرد على نص)
@zedub.on(admin_cmd(pattern="ضع بايو$"))
async def set_bio(event):
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await event.edit("⚠️ **بالرد على نص لوضعه كـ بايو!**")
    
    await event.edit("🔄 **جاري تغيير البايو...**")
    try:
        await event.client(functions.account.UpdateProfileRequest(
            about=reply.text
        ))
        await event.edit("✅ **تم تحديث البايو بنجاح!**")
    except Exception as e:
        await event.edit(f"❌ **فشل التغيير:** {str(e)}")

# 3. ميزة: ضع اسم (بالرد على نص)
@zedub.on(admin_cmd(pattern="ضع اسم$"))
async def set_name(event):
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await event.edit("⚠️ **بالرد على نص لوضعه كاسم!**")
    
    await event.edit("🔄 **جاري تغيير الاسم...**")
    names = reply.text.split(maxsplit=1)
    first_name = names[0]
    last_name = names[1] if len(names) > 1 else ""
    
    try:
        await event.client(functions.account.UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name
        ))
        await event.edit(f"✅ **تم تغيير الاسم إلى: {reply.text}**")
    except Exception as e:
        await event.edit(f"❌ **فشل التغيير:** {str(e)}")

# 4. ميزة: ضع يوزر (بالرد على يوزر)
@zedub.on(admin_cmd(pattern="ضع يوزر$"))
async def set_username(event):
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await event.edit("⚠️ **بالرد على اليوزر المطلوب!**")
    
    new_username = reply.text.replace("@", "").strip()
    await event.edit(f"🔄 **جاري محاولة تغيير اليوزر إلى @{new_username}...**")
    
    try:
        await event.client(functions.account.UpdateUsernameRequest(
            username=new_username
        ))
        await event.edit(f"✅ **تم تغيير اليوزر بنجاح إلى @{new_username}**")
    except UsernameOccupiedError:
        await event.edit("❌ **اليوزر مستخدم بالفعل! اختر يوزراً آخر.**")
    except Exception as e:
        await event.edit(f"❌ **فشل التغيير:** {str(e)}")