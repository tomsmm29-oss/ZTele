# Zed-Thon - ZelZal (Clone Fixed for ZTele 2025 by Mikey)
# Fixed duplicated functions + Relative paths + Safe Defaults

import html
from telethon.tl import functions
from telethon.tl.functions.users import GetFullUserRequest

# --- تصحيح المسارات ---
from . import zedub
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import get_user_from_event

# محاولة استدعاء المتغيرات والـ SQL
try:
    from ..sql_helper.globals import gvarstatus
except ImportError:
    def gvarstatus(val): return None

try:
    from . import ALIVE_NAME, BOTLOG, BOTLOG_CHATID
except ImportError:
    ALIVE_NAME = "My Userbot"
    BOTLOG = False
    BOTLOG_CHATID = None

plugin_category = "العروض"
DEFAULTUSER = gvarstatus("FIRST_NAME") or ALIVE_NAME
# التأكد من وجود قيمة افتراضية للبايو
DEFAULTUSERBIO = getattr(Config, "DEFAULT_BIO", "- ‏وحدي أضيء، وحدي أنطفئ انا قمري و كُل نجومي..🤍")
ANTHAL = gvarstatus("ANTHAL") or "(اعادة الحساب|اعادة|اعاده)"


# دمجنا "نسخ" و "انتحال" في دالة واحدة لأنهم نفس الكود
@zedub.zed_cmd(pattern="(نسخ|انتحال)(?:\s|$)([\s\S]*)")
async def clone_profile(event):
    replied_user, error_i_a = await get_user_from_event(event)
    if replied_user is None:
        return await edit_delete(event, "**- يجب الرد على المستخدم لنسخ حسابه!**")
        
    user_id = replied_user.id
    try:
        # تحميل الصورة الشخصية
        profile_pic = await event.client.download_profile_photo(user_id, Config.TMP_DOWNLOAD_DIRECTORY)
    except Exception:
        profile_pic = None

    first_name = html.escape(replied_user.first_name or "")
    first_name = first_name.replace("\u2060", "")
    
    last_name = html.escape(replied_user.last_name or "")
    last_name = last_name.replace("\u2060", "")
    if not last_name:
        last_name = "" # جعلها فارغة بدل الرموز المخفية لتجنب المشاكل

    try:
        # جلب البايو
        full_user = (await event.client(GetFullUserRequest(replied_user.id))).full_user
        user_bio = full_user.about or ""
    except:
        user_bio = ""

    # تحديث البيانات
    await event.client(functions.account.UpdateProfileRequest(first_name=first_name))
    await event.client(functions.account.UpdateProfileRequest(last_name=last_name))
    await event.client(functions.account.UpdateProfileRequest(about=user_bio))
    
    # رفع الصورة
    if profile_pic:
        try:
            pfile = await event.client.upload_file(profile_pic)
            await event.client(functions.photos.UploadProfilePhotoRequest(pfile))
        except Exception as e:
            return await edit_delete(event, f"**اووبس خطـأ في انتحال الصورة:**\n__{e}__")
    
    await edit_delete(event, "**⎉╎تـم انتحـال الشخـص .. بنجـاح ༗**")
    
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            f"#الانتحـــال\n ⪼ تم انتحـال حسـاب الشخـص ↫ [{first_name}](tg://user?id={user_id}) بنجاح ✅",
        )


@zedub.zed_cmd(pattern=f"{ANTHAL}$")
async def revert(event):
    firstname = DEFAULTUSER
    lastname = gvarstatus("LAST_NAME") or ""
    bio = DEFAULTUSERBIO
    
    # حذف الصور
    try:
        await event.client(
            functions.photos.DeletePhotosRequest(
                await event.client.get_profile_photos("me", limit=1)
            )
        )
    except: pass # تجاهل الخطأ لو مفيش صور

    # استعادة البيانات
    await event.client(functions.account.UpdateProfileRequest(about=bio))
    await event.client(functions.account.UpdateProfileRequest(first_name=firstname))
    await event.client(functions.account.UpdateProfileRequest(last_name=lastname))
    
    await edit_delete(event, "**⎉╎تمت اعادة الحساب لوضعـه الاصلـي \n⎉╎والغـاء الانتحـال .. بنجـاح ✅**")
    
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID,
            "#الغـاء_الانتحـال\n**⪼ تم الغـاء الانتحـال .. بنجـاح ✅**\n**⪼ تم إعـاده معلـوماتك الى وضعـها الاصـلي**",
        )