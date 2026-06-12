# @Zed-Thon - ZelZal (Updated for 2025 by Mikey)
# Copyright (C) 2022 ZedThon . All Rights Reserved
# < https://t.me/ZedThon >
# This file is a part of < https://github.com/Zed-Thon/ZelZal/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/Zed-Thon/ZelZal/blob/main/LICENSE/>.
# كـود الصورة الوقتيه كتـابتي وتعديلـي من زمان ومتعوب عليها
# + كـود زخـرفة الصورة الوقتيه
# + دددي لا ابلـع حســابك بـانـد بطـعـم الليمــون 🍋😹🤘
# زلــزال الهيبــه يـ ولــد - حقــوق لـ التــاريـخ ®
# هههههههههههههههههههههههههههههههههههههههههههههههههه

import asyncio
import os
import shutil
import time
from datetime import datetime

import requests
from PIL import Image, ImageDraw, ImageFont
from telethon.errors import FloodWaitError
from telethon.tl import functions

from ..Config import Config
from ..core.logger import logging

# --- منطقة الحقن النسبي (Relative Imports for ZTele) ---
from . import edit_delete, zedub

# محاولة استدعاء قاعدة البيانات
try:
    from ..sql_helper.globals import addgvar, delgvar, gvarstatus
except ImportError:
    # دوال وهمية في حال عدم وجود القاعدة لتجنب الكراش
    def gvarstatus(val):
        return None

    def addgvar(x, y):
        pass

    def delgvar(x):
        pass


plugin_category = "الادوات"
DEFAULTUSER = gvarstatus("ALIVE_NAME") or Config.ALIVE_NAME
LOGS = logging.getLogger(__name__)
CHANGE_TIME = int(gvarstatus("CHANGE_TIME")) if gvarstatus("CHANGE_TIME") else 60

# تحسين مسار الخط ليعمل على ريندر وسيرفرات لينكس الحديثة
FONT_FILE_TO_USE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

normzltext = "1234567890"

# تصحيح المسارات لتناسب هيكلة 2025 وتجنب أخطاء "File Not Found"
# نستخدم مجلد مؤقت آمن
if not os.path.exists("resources"):
    os.makedirs("resources")

autopic_path = os.path.join("resources", "original_pic.png")
digitalpic_path = os.path.join("resources", "digital_pic.png")
autophoto_path = os.path.join("resources", "photo_pfp.png")


NAUTO = gvarstatus("Z_NAUTO") or "(الاسم تلقائي|الاسم الوقتي|اسم وقتي|اسم تلقائي)"
PAUTO = (
    gvarstatus("Z_PAUTO")
    or "(البروفايل تلقائي|الصوره الوقتيه|الصورة الوقتية|صوره وقتيه|البروفايل)"
)
BAUTO = (
    gvarstatus("Z_BAUTO")
    or "(البايو تلقائي|البايو الوقتي|بايو وقتي|نبذه وقتيه|النبذه الوقتيه)"
)


async def digitalpicloop():
    DIGITALPICSTART = gvarstatus("digitalpic") == "true"
    i = 0
    while DIGITALPICSTART:
        # استبدال SmartDL بـ requests لضمان العمل في 2025
        if not os.path.exists(digitalpic_path):
            digitalpfp = gvarstatus("DIGITAL_PIC")
            if digitalpfp:
                try:
                    r = requests.get(digitalpfp, stream=True)
                    if r.status_code == 200:
                        with open(digitalpic_path, "wb") as f:
                            for chunk in r.iter_content(1024):
                                f.write(chunk)
                except Exception as e:
                    LOGS.error(f"Failed to download digital pic: {e}")

        zedfont = (
            gvarstatus("DEFAULT_PIC") or "resources/Papernotes.ttf"
        )  # تأكد من وجود الخط أو استخدم الافتراضي

        # التأكد من وجود الصورة قبل النسخ
        if os.path.exists(digitalpic_path):
            shutil.copy(digitalpic_path, autophoto_path)
        else:
            # لو مفيش صورة، ننتظر ونعيد المحاولة
            await asyncio.sleep(60)
            continue

        try:
            Image.open(autophoto_path)
            current_time = datetime.now().strftime("%I:%M")
            img = Image.open(autophoto_path)
            drawn_text = ImageDraw.Draw(img)

            # محاولة تحميل الخط، لو فشل نستخدم الافتراضي
            try:
                fnt = ImageFont.truetype(f"{zedfont}", 35)
            except:
                fnt = ImageFont.load_default()

            drawn_text.text((140, 70), current_time, font=fnt, fill=(280, 280, 280))
            img.save(autophoto_path)
            file = await zedub.upload_file(autophoto_path)

            if i > 0:
                # حذف الصورة القديمة لتجنب تكرار الصور في البروفايل
                await zedub(
                    functions.photos.DeletePhotosRequest(
                        await zedub.get_profile_photos("me", limit=1)
                    )
                )
            i += 1
            await zedub(functions.photos.UploadProfilePhotoRequest(file))
            if os.path.exists(autophoto_path):
                os.remove(autophoto_path)

            await asyncio.sleep(CHANGE_TIME)

        except FloodWaitError as ex:
            LOGS.warning(f"FloodWait: sleeping for {ex.seconds}")
            await asyncio.sleep(ex.seconds)
        except Exception as e:
            LOGS.error(f"Error in digitalpicloop: {e}")
            await asyncio.sleep(CHANGE_TIME)

        DIGITALPICSTART = gvarstatus("digitalpic") == "true"


async def autoname_loop():
    while AUTONAMESTART := gvarstatus("autoname") == "true":
        time.strftime("%d-%m-%y")
        HM = time.strftime("%I:%M")
        for normal in HM:
            if normal in normzltext:
                namerzfont = gvarstatus("ZI_FN") or "𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟬"
                try:
                    namefont = namerzfont[normzltext.index(normal)]
                    HM = HM.replace(normal, namefont)
                except IndexError:
                    pass  # تفادي الأخطاء لو النص المزخرف ناقص

        ZEDT = gvarstatus("CUSTOM_ALIVE_EMZED") or "⏐"
        name = f"{HM}{ZEDT}"
        # LOGS.info(name)
        try:
            await zedub(functions.account.UpdateProfileRequest(first_name=name))
        except FloodWaitError as ex:
            LOGS.warning(str(ex))
            await asyncio.sleep(ex.seconds)
        except Exception:
            # LOGS.error(str(e))
            pass
        await asyncio.sleep(CHANGE_TIME)
        AUTONAMESTART = gvarstatus("autoname") == "true"


async def autobio_loop():
    AUTOBIOSTART = gvarstatus("autobio") == "true"
    while AUTOBIOSTART:
        time.strftime("%d.%m.%Y")
        HM = time.strftime("%I:%M")
        for normal in HM:
            if normal in normzltext:
                namerzfont = gvarstatus("ZI_FN") or "𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟬"
                try:
                    namefont = namerzfont[normzltext.index(normal)]
                    HM = HM.replace(normal, namefont)
                except IndexError:
                    pass

        DEFAULTUSERBIO = gvarstatus("DEFAULT_BIO") or "الحمد الله على كل شئ - @ZedThon"
        bio = f"{DEFAULTUSERBIO} ⏐ {HM}"
        # LOGS.info(bio)
        try:
            await zedub(functions.account.UpdateProfileRequest(about=bio))
        except FloodWaitError as ex:
            LOGS.warning(str(ex))
            await asyncio.sleep(ex.seconds)
        except Exception:
            pass
        await asyncio.sleep(CHANGE_TIME)
        AUTOBIOSTART = gvarstatus("autobio") == "true"


@zedub.zed_cmd(pattern=f"{PAUTO}$")
async def _(event):
    digitalpfp = gvarstatus("DIGITAL_PIC")

    # استخدام requests بدلاً من SmartDL
    if digitalpfp:
        try:
            r = requests.get(digitalpfp, stream=True)
            with open(digitalpic_path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
        except:
            pass

    if gvarstatus("DIGITAL_PIC") is None:
        return await edit_delete(
            event,
            "**- فار الصـورة الوقتيـه غيـر موجـود ؟!**\n**- ارسـل صورة ثم قم بالـرد عليهـا بالامـر :**\n\n`.اضف صورة الوقتي`",
        )
    if gvarstatus("digitalpic") is not None and gvarstatus("digitalpic") == "true":
        return await edit_delete(
            event, "**⎉╎البروفـايل الوقتـي .. تم تفعيلهـا سابقـاً**"
        )
    addgvar("digitalpic", True)
    await edit_delete(event, "**⎉╎تـم بـدء البروفـايل الوقتـي .. بنجـاح ✓**")
    # استخدام create_task لعدم تجميد البوت
    zedub.loop.create_task(digitalpicloop())


@zedub.zed_cmd(pattern=f"{NAUTO}$")
async def _(event):
    if gvarstatus("autoname") is not None and gvarstatus("autoname") == "true":
        return await edit_delete(event, "**⎉╎الاسـم الوقتـي .. تم تفعيلـه سابقـاً**")
    addgvar("autoname", True)
    await edit_delete(event, "**⎉╎تـم بـدء الاسـم الوقتـي .. بنجـاح ✓**")
    zedub.loop.create_task(autoname_loop())


@zedub.zed_cmd(pattern=f"{BAUTO}$")
async def _(event):
    if gvarstatus("DEFAULT_BIO") is None:
        return await edit_delete(
            event,
            "**- فار النبـذة الوقتيـه غيـر موجـود ؟!**\n**- ارسـل نـص النبـذه ثم قم بالـرد عليهـا بالامـر :**\n\n`.اضف البايو`",
        )
    if gvarstatus("autobio") is not None and gvarstatus("autobio") == "true":
        return await edit_delete(event, "**⎉╎النبـذه الوقتـيه .. مفعلـه سابقـاً**")
    addgvar("autobio", True)
    await edit_delete(event, "**⎉╎تـم بـدء الـنبذة الوقتيـه .. بنجـاح ✓**")
    zedub.loop.create_task(autobio_loop())


@zedub.zed_cmd(
    pattern="الغاء ([\s\S]*)",
    command=("الغاء", plugin_category),
    info={
        "header": "To stop the functions of autoprofile",
        "description": "If you want to stop autoprofile functions then use this cmd.",
        "options": {
            "digitalpfp": "To stop difitalpfp",
            "autoname": "To stop autoname",
            "autobio": "To stop autobio",
        },
        "usage": "{tr}end <option>",
        "examples": ["{tr}end autopic"],
    },
)
async def _(event):  # sourcery no-metrics
    "To stop the functions of autoprofile plugin"
    input_str = event.pattern_match.group(1)
    if (
        input_str == "البروفايل تلقائي"
        or input_str == "البروفايل"
        or input_str == "البروفايل التلقائي"
        or input_str == "الصوره الوقتيه"
        or input_str == "الصورة الوقتية"
    ):
        if gvarstatus("digitalpic") is not None and gvarstatus("digitalpic") == "true":
            delgvar("digitalpic")
            # تنظيف الصور عند الإيقاف
            try:
                await event.client(
                    functions.photos.DeletePhotosRequest(
                        await event.client.get_profile_photos("me", limit=1)
                    )
                )
            except:
                pass
            return await edit_delete(
                event, "**⎉╎تم إيقـاف البروفـايل الوقتـي .. بنجـاح ✓**"
            )
        return await edit_delete(
            event, "**⎉╎البروفـايل الوقتـي .. غيـر مفعـل اصـلاً ؟!**"
        )
    if (
        input_str == "الاسم تلقائي"
        or input_str == "الاسم"
        or input_str == "الاسم التلقائي"
        or input_str == "الاسم الوقتي"
        or input_str == "اسم الوقتي"
    ):
        if gvarstatus("autoname") is not None and gvarstatus("autoname") == "true":
            delgvar("autoname")
            await event.client(
                functions.account.UpdateProfileRequest(first_name=DEFAULTUSER)
            )
            return await edit_delete(
                event, "**⎉╎تم إيقـاف الاسـم الوقتـي .. بنجـاح ✓**"
            )
        return await edit_delete(event, "**⎉╎الاسـم الوقتـي .. غيـر مفعـل اصـلاً ؟!**")
    if (
        input_str == "البايو تلقائي"
        or input_str == "البايو"
        or input_str == "البايو التلقائي"
        or input_str == "البايو الوقتي"
        or input_str == "النبذه الوقتيه"
        or input_str == "النبذة الوقتية"
        or input_str == "بايو الوقتي"
        or input_str == "نبذه الوقتي"
    ):
        if gvarstatus("autobio") is not None and gvarstatus("autobio") == "true":
            delgvar("autobio")
            DEFAULTUSERBIO = (
                gvarstatus("DEFAULT_BIO") or "الحمد الله على كل شئ - @ZedThon"
            )
            await event.client(
                functions.account.UpdateProfileRequest(about=DEFAULTUSERBIO)
            )
            return await edit_delete(
                event, "**⎉╎تم إيقـاف النبـذه الوقتيـه .. بنجـاح ✓**"
            )
        return await edit_delete(
            event, "**⎉╎النبـذه الوقتيـه .. غيـر مفعـله اصـلاً ؟!**"
        )


@zedub.zed_cmd(
    pattern="ايقاف ([\s\S]*)",
    command=("ايقاف", plugin_category),
    info={
        "header": "To stop the functions of autoprofile",
        "description": "If you want to stop autoprofile functions then use this cmd.",
        "options": {
            "digitalpfp": "To stop difitalpfp",
            "autoname": "To stop autoname",
            "autobio": "To stop autobio",
        },
        "usage": "{tr}end <option>",
        "examples": ["{tr}end autopic"],
    },
)
async def _(event):  # sourcery no-metrics
    "To stop the functions of autoprofile plugin"
    input_str = event.pattern_match.group(1)
    if (
        input_str == "البروفايل تلقائي"
        or input_str == "البروفايل"
        or input_str == "البروفايل التلقائي"
        or input_str == "الصوره الوقتيه"
        or input_str == "الصورة الوقتية"
    ):
        if gvarstatus("digitalpic") is not None and gvarstatus("digitalpic") == "true":
            delgvar("digitalpic")
            try:
                await event.client(
                    functions.photos.DeletePhotosRequest(
                        await event.client.get_profile_photos("me", limit=1)
                    )
                )
            except:
                pass
            return await edit_delete(
                event, "**⎉╎تم إيقـاف البروفـايل الوقتـي .. بنجـاح ✓**"
            )
        return await edit_delete(
            event, "**⎉╎البروفـايل الوقتـي .. غيـر مفعـل اصـلاً ؟!**"
        )
    if (
        input_str == "الاسم تلقائي"
        or input_str == "الاسم"
        or input_str == "الاسم التلقائي"
        or input_str == "الاسم الوقتي"
        or input_str == "اسم الوقتي"
        or input_str == "اسم وقتي"
        or input_str == "اسم تلقائي"
    ):
        if gvarstatus("autoname") is not None and gvarstatus("autoname") == "true":
            delgvar("autoname")
            await event.client(
                functions.account.UpdateProfileRequest(first_name=DEFAULTUSER)
            )
            return await edit_delete(
                event, "**⎉╎تم إيقـاف الاسـم الوقتـي .. بنجـاح ✓**"
            )
        return await edit_delete(event, "**⎉╎الاسـم الوقتـي .. غيـر مفعـل اصـلاً ؟!**")
    if (
        input_str == "البايو تلقائي"
        or input_str == "البايو"
        or input_str == "البايو التلقائي"
        or input_str == "البايو الوقتي"
        or input_str == "النبذه الوقتيه"
        or input_str == "النبذة الوقتية"
        or input_str == "بايو الوقتي"
        or input_str == "نبذه الوقتي"
    ):
        if gvarstatus("autobio") is not None and gvarstatus("autobio") == "true":
            delgvar("autobio")
            DEFAULTUSERBIO = (
                gvarstatus("DEFAULT_BIO") or "الحمد الله على كل شئ - @ZedThon"
            )
            await event.client(
                functions.account.UpdateProfileRequest(about=DEFAULTUSERBIO)
            )
            return await edit_delete(
                event, "**⎉╎تم إيقـاف النبـذه الوقتيـه .. بنجـاح ✓**"
            )
        return await edit_delete(
            event, "**⎉╎النبـذه الوقتيـه .. غيـر مفعـله اصـلاً ؟!**"
        )


@zedub.zed_cmd(
    pattern="انهاء ([\s\S]*)",
    command=("انهاء", plugin_category),
    info={
        "header": "To stop the functions of autoprofile",
        "description": "If you want to stop autoprofile functions then use this cmd.",
        "options": {
            "digitalpfp": "To stop difitalpfp",
            "autoname": "To stop autoname",
            "autobio": "To stop autobio",
        },
        "usage": "{tr}end <option>",
        "examples": ["{tr}end autopic"],
    },
)
async def _(event):  # sourcery no-metrics
    "To stop the functions of autoprofile plugin"
    input_str = event.pattern_match.group(1)
    if (
        input_str == "البروفايل تلقائي"
        or input_str == "البروفايل"
        or input_str == "البروفايل التلقائي"
        or input_str == "الصوره الوقتيه"
        or input_str == "الصورة الوقتية"
    ):
        if gvarstatus("digitalpic") is not None and gvarstatus("digitalpic") == "true":
            delgvar("digitalpic")
            try:
                await event.client(
                    functions.photos.DeletePhotosRequest(
                        await event.client.get_profile_photos("me", limit=1)
                    )
                )
            except:
                pass
            return await edit_delete(
                event, "**⎉╎تم إيقـاف البروفـايل الوقتـي .. بنجـاح ✓**"
            )
        return await edit_delete(
            event, "**⎉╎البروفـايل الوقتـي .. غيـر مفعـل اصـلاً ؟!**"
        )
    if (
        input_str == "الاسم تلقائي"
        or input_str == "الاسم"
        or input_str == "الاسم التلقائي"
        or input_str == "الاسم الوقتي"
        or input_str == "اسم الوقتي"
        or input_str == "اسم وقتي"
        or input_str == "اسم تلقائي"
    ):
        if gvarstatus("autoname") is not None and gvarstatus("autoname") == "true":
            delgvar("autoname")
            await event.client(
                functions.account.UpdateProfileRequest(first_name=DEFAULTUSER)
            )
            return await edit_delete(
                event, "**⎉╎تم إيقـاف الاسـم الوقتـي .. بنجـاح ✓**"
            )
        return await edit_delete(event, "**⎉╎الاسـم الوقتـي .. غيـر مفعـل اصـلاً ؟!**")
    if (
        input_str == "البايو تلقائي"
        or input_str == "البايو"
        or input_str == "البايو التلقائي"
        or input_str == "البايو الوقتي"
        or input_str == "النبذه الوقتيه"
        or input_str == "النبذة الوقتية"
        or input_str == "بايو الوقتي"
        or input_str == "نبذه الوقتي"
    ):
        if gvarstatus("autobio") is not None and gvarstatus("autobio") == "true":
            delgvar("autobio")
            DEFAULTUSERBIO = (
                gvarstatus("DEFAULT_BIO") or "الحمد الله على كل شئ - @ZedThon"
            )
            await event.client(
                functions.account.UpdateProfileRequest(about=DEFAULTUSERBIO)
            )
            return await edit_delete(
                event, "**⎉╎تم إيقـاف النبـذه الوقتيـه .. بنجـاح ✓**"
            )
        return await edit_delete(
            event, "**⎉╎النبـذه الوقتيـه .. غيـر مفعـله اصـلاً ؟!**"
        )
    END_CMDS = [
        "البروفايل تلقائي",
        "الصوره الوقتيه",
        "الاسم تلقائي",
        "الاسم الوقتي",
        "اسم تلقائي",
        "اسم وقتي",
        "البايو تلقائي",
        "البايو الوقتي",
        "النبذه الوقتيه",
        "البروفايل",
        "الاسم",
        "البايو",
    ]
    if input_str not in END_CMDS:
        await edit_delete(
            event,
            f"**{input_str} خيـار غيـر موجـود ؟!**",
        )


# إعادة تشغيل الحلقات عند تشغيل البوت إذا كانت مفعلة
if gvarstatus("digitalpic") == "true":
    zedub.loop.create_task(digitalpicloop())
if gvarstatus("autoname") == "true":
    zedub.loop.create_task(autoname_loop())
if gvarstatus("autobio") == "true":
    zedub.loop.create_task(autobio_loop())
