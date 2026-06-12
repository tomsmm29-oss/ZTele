# Zed-Thon
# Copyright (C) 2022 Zed-Thon . All Rights Reserved
#
# This file is a part of < https://github.com/Zed-Thon/ZelZal/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/Zed-Thon/ZelZal/blob/master/LICENSE/>.

"""وصـف الملـف : اوامـر اضـافة الفـارات باللغـة العربيـة كـاملة ولا حـرف انكلـش🤘 تخمـط اذكـر المصـدر يولـد
اضـافة فـارات صـورة ( الحمايـة - الفحـص - الوقتـي ) بـ امـر واحـد فقـط
حقـوق للتـاريخ : @ZThon
@zzzzl1l - كتـابـة الملـف :  زلــزال الهيبــه"""

# زلـزال_الهيبـه يولـد هههههههههههههههههههههههههه
import asyncio

import heroku3
import urllib3
from PIL import Image
from telegraph import Telegraph

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from urlextract import URLExtract

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from . import zedub

Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
heroku_api = "https://api.heroku.com"
HEROKU_APP_NAME = Config.HEROKU_APP_NAME
HEROKU_API_KEY = Config.HEROKU_API_KEY
from . import BOTLOG_CHATID

plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)

extractor = URLExtract()
telegraph = Telegraph()
r = telegraph.create_account(short_name=Config.TELEGRAPH_SHORT_NAME)
auth_url = r["auth_url"]


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")


ZelzalVP_cmd = (
    "𓆩 𝗭𝗧𝗵𝗼𝗻 𝗩𝗮𝗿𝘀 **🝢 اوامـر الفـارات** 𓆪\n"
    "**⋆┄─┄─┄─┄─┄─┄─┄─┄⋆**\n"
    "**✧ قائمـة اوامر تغييـر فـارات الصـور بأمـر واحـد فقـط - لـ اول مـره ع سـورس يـوزربـوت 🦾 :** \n\n"
    "⪼ `.اضف صورة الحماية` بالـرد ع صـورة او ميديـا\n\n"
    "⪼ `.اضف صورة الفحص` بالـرد ع صـورة او ميديـا\n"
    "⪼ قنـاة كلايـش الفحـص @zzclll\n\n"
    "⪼ `.اضف صورة الوقتي` بالـرد ع صـورة او ميديـا\n\n"
    "⪼ `.اضف صورة البوت` بالـرد ع صـورة او ميديـا لـ اضـافة صـورة ستـارت للبـوت\n\n"
    "⪼ `.اضف صورة الحظر` بالـرد ع صـورة او ميديـا لـ اضـافة صـورة لـ كليشـة الحظـر\n\n"
    "⪼ `.اضف صورة الكتم` بالـرد ع صـورة او ميديـا لـ اضـافة صـورة لـ كليشـة الكتـم\n\n"
    "⪼ `.اضف صورة البلوك` بالـرد ع صـورة او ميديـا لـ اضـافة صـورة لـ كليشـة حظـر الخـاص\n\n\n"
    "**✧ قائمـة اوامر تغييـر كليشـة الايـدي :** \n\n"
    "⪼ `.اضف كليشة الايدي` بالـرد ع الكليشـه مـن القنـاة @zziddd \n\n\n"
    "**✧ قائمـة اوامر تغييـر بقيـة الفـارات بأمـر واحـد فقـط :** \n\n"
    "⪼ `.اضف فار كليشة الحماية` بالـرد ع الكليشـة\n"
    "⪼ `.اضف فار كليشة البلوك` بالـرد ع الكليشـة لتغييـر كليشة الحظر خاص\n"
    "⪼ قنـاة كلايـش حمايـة الخـاص @zzkrr\n\n"
    "⪼ `.اضف فار كليشة الفحص` بالـرد ع الكليشـة\n"
    "⪼ قنـاة كلايـش الفحـص @zzclll\n\n"
    "⪼ `.اضف فار كليشة البوت` بالـرد ع الكليشـة لـ اضـافة كليشـة ستـارت\n\n"
    "⪼ `.اضف فار زر الستارت` بالـرد ع يوزرك او يوزر قناتك لـ اضـافة زر الستـارت\n\n"
    "⪼ `.اضف فار رمز الوقتي` بالـرد ع رمـز\n\n"
    "⪼ `.اضف فار زخرفة الوقتي` بالـرد ع ارقـام الزغـرفه\n\n"
    "⪼ `.اضف فار البايو الوقتي` بالـرد ع البـايـو\n\n"
    "⪼ `.اضف فار اسم المستخدم` بالـرد ع اسـم\n\n"
    "⪼ `.اضف فار كروب الرسائل` بالـرد ع ايدي الكـروب\n\n"
    "⪼ `.اضف فار كروب السجل` بالـرد ع ايدي الكـروب\n\n"
    "⪼ `.اضف فار ايديي` بالـرد ع ايدي حسـابك\n\n"
    "⪼ `.اضف فار نقطة الاوامر` بالـرد ع الـرمز الجديـد\n\n"
    "⪼ `.اضف فار نقطة المطور` بالـرد ع الـرمز الجديـد\n\n"
    "⪼ `.اضف فار كود تيرمكس` بالـرد ع الكـود الجديـد\n\n"
    "⪼ `.اضف فار توكن البوت` بالـرد ع التوكن الجديـد\n\n"
    "⪼ `.اضف فار كود تيرمكس` بالـرد ع الكـود الجديـد\n\n"
    "⪼ `.اضف فار توكن البوت` بالـرد ع التوكن الجديـد\n\n"
    "⪼ `.اضف فار مساعد الميوزك` بالـرد ع كـود تيليثون حساب مساعد الميوزك الجديـد\n\n"
    "⪼ `.اضف فار نوم الترحيب` بالـرد ع رقـم الساعة لبداية نوم الترحيب المؤقت\n\n"
    "⪼ `.اضف فار ثواني لانهائي` بالـرد ع رقـم لعـدد الثوانـي الفاصـله بيـن كل عمليـة تجميـع فـي الامـر لانهائـي\n\n"
    "⪼ `.اضف فار رسائل الحماية` بالـرد ع رقـم لعدد رسائل تحذيـرات حماية الخاص\n\n\n"
    "⪼ `.جلب فار` + اسـم الفـار\n\n"
    "⪼ `.حذف فار` + اسـم الفـار\n\n"
    "⪼ `.الوقت` لـ عـرض قائمـة اوامـر تغييـر الوقت حسب دولتك\n\n"
    "\n𓆩 [𝗭𝗧𝗵𝗼𝗻 𝗩𝗮𝗿𝘀 - قنـاة الفـارات](t.me/zzzvrr) 𓆪"
)


ZelzalTZ_cmd = (
    "𓆩 𝗭𝗧𝗵𝗼𝗻 𝗧𝗶𝗺𝗲 **🝢 المنطقة الزمنية** 𓆪\n"
    "**⋆┄─┄─┄─┄─┄─┄─┄─┄⋆**\n"
    "**✧ قائمـة اوامر تغييـر المنطقـة الزمنيـة لـ ضبط الوقت ع زدثــون حسب توقيت دولتك 🌐:** \n\n"
    "⪼ `.وقت فلسطين` \n"
    "⪼ `.وقت اليمن` \n"
    "⪼ `.وقت العراق` \n"
    "⪼ `.وقت السعودية` \n"
    "⪼ `.وقت سوريا` \n"
    "⪼ `.وقت الامارات` \n"
    "⪼ `.وقت قطر` \n"
    "⪼ `.وقت الكويت` \n"
    "⪼ `.وقت البحرين` \n"
    "⪼ `.وقت سلطنة عمان` \n"
    "⪼ `.وقت الاردن` \n"
    "⪼ `.وقت لبنان` \n"
    "⪼ `.وقت مصر` \n"
    "⪼ `.وقت السودان` \n"
    "⪼ `.وقت ليبيا` \n"
    "⪼ `.وقت الجزائر` \n"
    "⪼ `.وقت المغرب` \n"
    "⪼ `.وقت تونس` \n"
    "⪼ `.وقت موريتانيا` \n"
    "⪼ `.وقت ايران` \n"
    "⪼ `.وقت تركيا` \n"
    "⪼ `.وقت امريكا` \n"
    "⪼ `.وقت روسيا` \n"
    "⪼ `.وقت ايطاليا` \n"
    "⪼ `.وقت المانيا` \n"
    "⪼ `.وقت فرنسا` \n"
    "⪼ `.وقت اسبانيا` \n"
    "⪼ `.وقت بريطانيا` \n"
    "⪼ `.وقت بلجيكا` \n"
    "⪼ `.وقت النرويج` \n"
    "⪼ `.وقت الصين` \n"
    "⪼ `.وقت اليابان` \n"
    "⪼ `.وقت الهند` \n"
    "⪼ `.وقت اندنوسيا` \n"
    "⪼ `.وقت ماليزيا` \n\n"
    "**🛃 اذا لم تجد دولتك .. قم بالبحث عن اقرب دوله لها**\n"
    "𓆩 [𝗭𝗧𝗵𝗼𝗻 𝗩𝗮𝗿𝘀 - قنـاة الفـارات](t.me/zzzvrr) 𓆪"
)


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern=r"اضف فار (.*)")
async def variable(event):
    sender_id = event.sender_id
    if sender_id != Config.OWNER_ID:
        return await edit_or_reply(
            event,
            "**✧ عـذراً .. عـزيـزي ✕**\n**✧ اوامـر الفـارات خاصه بصاحب الحسـاب فقـط 👨🏻‍💻**",
        )
    input_str = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    vinfo = reply.text
    zed = await edit_or_reply(event, "**✧ جـاري اضـافة الفـار الـى بـوتك ...**")
    # All Rights Reserved for "Zed-Thon" "زلـزال الهيبـه"
    if input_str == "كليشة الفحص" or input_str == "كليشه الفحص":
        variable = "ALIVE_TEMPLATE"
        await asyncio.sleep(1.5)
        if gvarstatus("ALIVE_TEMPLATE") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ الكليشـة الجـديده** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.فحص` **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة {} بنجـاح ☑️**\n**✧ الكليشـة المضـافه** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.فحص` **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        addgvar("ALIVE_TEMPLATE", vinfo)
    elif (
        input_str == "كليشة الحماية"
        or input_str == "كليشه الحمايه"
        or input_str == "كليشه الحماية"
        or input_str == "كليشة الحمايه"
    ):
        variable = "pmpermit_txt"
        await asyncio.sleep(1.5)
        if gvarstatus("pmpermit_txt") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ الكليشـة الجـديده** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.الحمايه تفعيل` **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة {} بنجـاح ☑️**\n**✧ الكليشـة المضـافه** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.الحمايه تفعيل` **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        addgvar("pmpermit_txt", vinfo)
    elif input_str == "كليشة الايدي" or input_str == "كليشه الايدي":
        variable = "ZID_TEMPLATE"
        await asyncio.sleep(1.5)
        if gvarstatus("ZID_TEMPLATE") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ الكليشـة الجـديده** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.ايدي` **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة {} بنجـاح ☑️**\n**✧ الكليشـة المضـافه** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.ايدي` **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        addgvar("ZID_TEMPLATE", vinfo)
    elif (
        input_str == "كليشة البوت"
        or input_str == "كليشه البوت"
        or input_str == "ستارت البوت"
        or input_str == "كليشة الستارت"
        or input_str == "كليشه الستارت"
        or input_str == "كليشة البدء"
    ):
        variable = "START_TEXT"
        await asyncio.sleep(1.5)
        if gvarstatus("START_TEXT") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ الكليشـة الجـديده** \n {} \n\n**✧ الان قـم بـ الذهـاب لبوتك المسـاعد من حساب آخر ↶** ودز ستارت **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة {} بنجـاح ☑️**\n**✧ الكليشـة المضـافه** \n {} \n\n**✧ الان قـم بـ الذهـاب لبوتك المسـاعد من حساب آخر ↶** ودز ستارت **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        addgvar("START_TEXT", vinfo)
    elif (
        input_str == "زر البوت" or input_str == "زر الستارت" or input_str == "زر ستارت"
    ):
        variable = "START_BUTUN"
        await asyncio.sleep(1.5)
        if not vinfo.startswith("@"):
            return await zed.edit("**✧ خطـأ .. قم بالـرد ع يـوزر فقـط**")
        vinfo = vinfo.replace("@", "")
        if gvarstatus("START_TEXT") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ رابـط زر كليشـة الستـارت الجـديـد** \nhttps://t.me/{} \n\n**✧ الان قـم بـ الذهـاب لبوتك المسـاعد من حساب آخر ↶** ودز ستارت **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم إضـافـة {} بنجـاح ☑️**\n**✧ رابـط زر كليشـة الستـارت الجـديـد** \nhttps://t.me/{} \n\n**✧ الان قـم بـ الذهـاب لبوتك المسـاعد من حساب آخر ↶** ودز ستارت **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        addgvar("START_BUTUN", vinfo)
    elif (
        input_str == "كليشة التوديع"
        or input_str == "كليشه التوديع"
        or input_str == "كليشة البلوك"
        or input_str == "كليشه البلوك"
    ):
        variable = "pmblock"
        await asyncio.sleep(1.5)
        if gvarstatus("pmblock") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ الكليشـة الجـديده** \n {} \n\n**✧ الان قـم بـ تفعيـل حماية الخاص عبر الامر ↶** ( `الحماية تفعيل` ) **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ الكليشـة الجـديده** \n {} \n\n**✧ الان قـم بـ تفعيـل حماية الخاص عبر الامر ↶** ( `الحماية تفعيل` ) **لـ التحقـق مـن الكليشـة . .**".format(
                    input_str, vinfo
                )
            )
        addgvar("pmblock", vinfo)
    elif input_str == "رمز الوقتي" or input_str == "رمز الاسم الوقتي":
        variable = "CUSTOM_ALIVE_EMZED"
        await asyncio.sleep(1.5)
        if gvarstatus("CUSTOM_ALIVE_EMZED") is None:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ الـرمـز الجـديـد** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.الاسم تلقائي` **لـ التحقـق مـن الـرمز . .**".format(
                    input_str, vinfo
                )
            )
        else:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم اضـافـة {} بنجـاح ☑️**\n**✧ الـرمـز المضـاف** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.الاسم تلقائي` **لـ التحقـق مـن الـرمز . .**".format(
                    input_str, vinfo
                )
            )
    elif (
        input_str == "البايو"
        or input_str == "البايو الوقتي"
        or input_str == "النبذه"
        or input_str == "البايو تلقائي"
    ):
        variable = "DEFAULT_BIO"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_BIO") is None:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ البـايـو الجـديـد** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.البايو تلقائي` **لـ التحقـق مـن البايـو . .**".format(
                    input_str, vinfo
                )
            )
        else:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم اضـافه {} بنجـاح ☑️**\n**✧ البـايـو المضـاف** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.البايو تلقائي` **لـ التحقـق مـن البايـو . .**".format(
                    input_str, vinfo
                )
            )
    elif (
        input_str == "التحقق"
        or input_str == "كود التحقق"
        or input_str == "التحقق بخطوتين"
        or input_str == "تحقق"
    ):
        variable = "TG_2STEP_VERIFICATION_CODE"
        await asyncio.sleep(1.5)
        if gvarstatus("TG_2STEP_VERIFICATION_CODE") is None:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم إضافـة {} بنجـاح ☑️**\n**✧ كـود التحـقق بخطـوتيـن** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.تحويل ملكية` **ثم معـرف الشخـص داخـل الكـروب او القنـاة . .**".format(
                    input_str, vinfo
                )
            )
        else:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم إضافـة {} بنجـاح ☑️**\n**✧ كـود التحـقق بخطـوتيـن** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.تحويل ملكية` **ثم معـرف الشخـص داخـل الكـروب او القنـاة . .**".format(
                    input_str, vinfo
                )
            )
    elif input_str == "كاشف الاباحي" or input_str == "كشف الاباحي":
        variable = "DEEP_API"
        await asyncio.sleep(1.5)
        if gvarstatus("DEEP_API") is None:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم تغييـر توكـن {} بنجـاح ☑️**\n**✧ التوكـن الجـديـد** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.قفل الاباحي` **لـ تفعيـل كاشـف الاباحي . .**".format(
                    input_str, vinfo
                )
            )
        else:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم إضافـة توكـن {} بنجـاح ☑️**\n**✧ التوكـن المضـاف** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.قفل الاباحي` **لـ تفعيـل كاشـف الاباحي . .**".format(
                    input_str, vinfo
                )
            )
    elif (
        input_str == "ايموجي الايدي"
        or input_str == "ايموجي ايدي"
        or input_str == "رمز الايدي"
        or input_str == "رمز ايدي"
        or input_str == "الرمز ايدي"
    ):
        variable = "CUSTOM_ALIVE_EMOJI"
        await asyncio.sleep(1.5)
        if gvarstatus("CUSTOM_ALIVE_EMOJI") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.ايدي`".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.ايدي`".format(
                    input_str, vinfo
                )
            )
        addgvar("CUSTOM_ALIVE_EMOJI", vinfo)
    elif input_str == "عنوان الايدي" or input_str == "عنوان ايدي":
        variable = "CUSTOM_ALIVE_TEXT"
        await asyncio.sleep(1.5)
        if gvarstatus("CUSTOM_ALIVE_TEXT") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.ايدي`".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.ايدي`".format(
                    input_str, vinfo
                )
            )
        addgvar("CUSTOM_ALIVE_TEXT", vinfo)
    elif (
        input_str == "خط الايدي"
        or input_str == "خط ايدي"
        or input_str == "خطوط الايدي"
        or input_str == "خط ايدي"
    ):
        variable = "CUSTOM_ALIVE_FONT"
        await asyncio.sleep(1.5)
        if gvarstatus("CUSTOM_ALIVE_FONT") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.ايدي`".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.ايدي`".format(
                    input_str, vinfo
                )
            )
        addgvar("CUSTOM_ALIVE_FONT", vinfo)
    elif input_str == "اشتراك الخاص" or input_str == "اشتراك خاص":
        variable = "Custom_Pm_Channel"
        await asyncio.sleep(1.5)
        if gvarstatus("Custom_Pm_Channel") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.اشتراك خاص`".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.اشتراك خاص`".format(
                    input_str, vinfo
                )
            )
        delgvar("Custom_Pm_Channel")
        addgvar("Custom_Pm_Channel", vinfo)
        if BOTLOG_CHATID:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#قنـاة_الاشتـراك_الاجبـاري_للخـاص\
                        \n**- القنـاة {input_str} تم اضافتهـا في قاعده البيانات ..بنجـاح ✓**",
            )
    elif input_str == "اشتراك كروب" or input_str == "اشتراك الكروب":
        variable = "Custom_G_Channel"
        await asyncio.sleep(1.5)
        if gvarstatus("Custom_G_Channel") is None:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.اشتراك كروب`".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n\n**✧ المتغيـر : ↶**\n `{}`\n**✧ ارسـل الان** `.اشتراك كروب`".format(
                    input_str, vinfo
                )
            )
        delgvar("Custom_G_Channel")
        addgvar("Custom_G_Channel", vinfo)
        if BOTLOG_CHATID:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#قنـاة_الاشتـراك_الاجبـاري_للكـروب\
                        \n**- القنـاة {input_str} تم اضافتهـا في قاعده البيانات ..بنجـاح ✓**",
            )
    elif (
        input_str == "زاجل"
        or input_str == "قائمة زاجل"
        or input_str == "قائمه زاجل"
        or input_str == "يوزرات"
    ):
        variable = "ZAGL_Zed"
        await asyncio.sleep(1.5)
        if gvarstatus("ZAGL_Zed") is None:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️**\n**✧ اليـوزرات المضـافة** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.زاجل` **بالـرد ع نـص او ميديـا بنـص . .**".format(
                    input_str, vinfo
                )
            )
        else:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️**\n**✧ اليـوزرات المضـافة** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.زاجل` **بالـرد ع نـص او ميديـا بنـص . .**".format(
                    input_str, vinfo
                )
            )
    elif (
        input_str == "سوبر"
        or input_str == "قائمة السوبر"
        or input_str == "قائمه السوبر"
        or input_str == "السوبرات"
        or input_str == "السوبر"
    ):
        variable = "Super_Id"
        await asyncio.sleep(1.5)
        if not vinfo.startswith("-100"):
            return await zed.edit(
                "**✧ خطـأ .. قم بالـرد ع ارقـام ايديات المجموعات التي تبدأ ب 100- فقـط ؟!**\n**✧ قم بالذهاب لمجموعات السوبر التي تريد النشر فيها وكتابة الامر (.الايدي) ثم خذ ايدي المجموعة وهكذا لبقية المجموعات**"
            )
        if gvarstatus("Super_Id") is None:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️**\n**✧ الايديات المضـافة** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** (`.سوبر` + عدد الثواني + عدد مرات التكرار)**بالـرد ع نـص او ميديـا بنـص . .**".format(
                    input_str, vinfo
                )
            )
        else:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ الايديات المضـافة** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** (`.سوبر` + عدد الثواني + عدد مرات التكرار)**بالـرد ع نـص او ميديـا بنـص . .**".format(
                    input_str, vinfo
                )
            )
    elif (
        input_str == "بوت التجميع"
        or input_str == "بوت النقاط"
        or input_str == "النجميع"
        or input_str == "النقاط"
    ):
        variable = "Z_Point"
        await asyncio.sleep(1.5)
        if gvarstatus("Z_Point") is None:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ البـوت المضـاف** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.تجميع` **لـ البـدء بتجميـع النقـاط من البـوت الجـديـد . .**".format(
                    input_str, vinfo
                )
            )
        else:
            addgvar(variable, vinfo)
            await zed.edit(
                "**✧ تم اضـافه {} بنجـاح ☑️**\n**✧ البـوت المضـاف** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.تجميع` **لـ البـدء بتجميـع النقـاط من البـوت الجـديـد . .**".format(
                    input_str, vinfo
                )
            )
    elif input_str == "اسم المستخدم" or input_str == "الاسم":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "ALIVE_NAME"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo

    elif (
        input_str == "رسائل الحماية"
        or input_str == "رسائل الحمايه"
        or input_str == "رسائل الخاص"
        or input_str == "رسائل حماية الخاص"
        or input_str == "عدد التحذيرات"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✾╎اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "MAX_FLOOD_IN_PMS"
        await asyncio.sleep(1.5)
        if vinfo.isdigit():
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            return await zed.edit("**✧ خطـأ .. قم بالـرد ع رقـم فقـط ؟!**")
        heroku_var[variable] = vinfo

    elif (
        input_str == "كود تيرمكس"
        or input_str == "كود السيشن"
        or input_str == "كود سيشن"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "STRING_SESSION"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo

    elif (
        input_str == "جلسة المساعد"
        or input_str == "الحساب المساعد"
        or input_str == "مساعد الميوزك"
        or input_str == "كود الميوزك"
        or input_str == "جلسة الميوزك"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "VC_SESSION"
        await asyncio.sleep(1.5)
        if "=" not in vinfo:
            return await zed.edit(
                "**✧ خطـأ .. قم بالـرد ع كود تيليثون - Telethon فقـط ؟!**"
            )
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo

    elif (
        input_str == "كروب الرسائل"
        or input_str == "كروب التخزين"
        or input_str == "كروب الخاص"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "PM_LOGGER_GROUP_ID"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif input_str == "السجل" or input_str == "كروب السجل":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "PRIVATE_GROUP_BOT_API_ID"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif input_str == "السجل 2" or input_str == "كروب السجل 2":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "PRIVATE_GROUP_ID"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif input_str == "قناة السجل" or input_str == "قناة السجلات":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "PRIVATE_CHANNEL_BOT_API_ID"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif input_str == "قناة الملفات" or input_str == "قناة الاضافات":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "PLUGIN_CHANNEL"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif input_str == "ايديي" or input_str == "ايدي الحساب":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "OWNER_ID"
        await asyncio.sleep(1.5)
        if vinfo.isdigit():
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            return await zed.edit("**✧ خطـأ .. قم بالـرد ع رقـم فقـط ؟!**")
        heroku_var[variable] = vinfo
    elif input_str == "نقطة الاوامر" or input_str == "نقطه الاوامر":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "COMMAND_HAND_LER"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif input_str == "التوكن" or input_str == "توكن البوت":
        variable = "TG_BOT_TOKEN"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif input_str == "معرف البوت" or input_str == "معرف بوت":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "TG_BOT_USERNAME"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif input_str == "الريبو" or input_str == "السورس":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "UPSTREAM_REPO"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif (
        input_str == "توكن المكافح"
        or input_str == "كود المكافح"
        or input_str == "مكافح التخريب"
        or input_str == "مكافح التفليش"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )

        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "SPAMWATCH_API"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif (
        input_str == "توكن الذكاء"
        or input_str == "مفتاح الذكاء"
        or input_str == "الذكاء"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "OPENAI_API_KEY"
        await asyncio.sleep(1.5)
        if variable in heroku_var:
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️** \n**✧ المضاف اليه :**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        heroku_var[variable] = vinfo
    elif input_str == "ايقاف الترحيب" or input_str == "نوم الترحيب":
        variable = "TIME_STOP"
        await asyncio.sleep(1.5)
        if vinfo.isdigit():
            await zed.edit(
                "**✧ تم تغييـر {} بنجـاح ☑️**\n**✧ المتغيـر : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str, vinfo
                )
            )
        else:
            return await zed.edit("**✧ خطـأ .. قم بالـرد ع رقـم فقـط ؟!**")
        addgvar("TIME_STOP", vinfo)
        if BOTLOG_CHATID:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"#فتـرة_الايقـاف_المـؤقت_للترحيب\
                        \n**- تم اضافة الفتـرة من الساعة {vinfo} الى الساعة 6 صباحـاً .. بنجـاح ✓**",
            )
    elif (
        input_str == "ثواني لانهائي"
        or input_str == "ثواني التجميع"
        or input_str == "عدد لانهائي"
    ):
        variable = "SEC_LAN"
        await asyncio.sleep(1.5)
        if vinfo.isdigit():
            await zed.edit(
                "**✧ تم اضافـة {} بنجـاح ☑️**\n**✧ الثوانـي الجـديـدة** \n {} \n\n**✧ الان قـم بـ ارسـال الامـر ↶** `.لانهائي` **+ اسم بوت التجميـع لـ البـدء بالتجميـع اللانهائـي . .**".format(
                    input_str, vinfo
                )
            )
        else:
            return await zed.edit("**✧ خطـأ .. قم بالـرد ع رقـم فقـط ؟!**")
        addgvar(variable, vinfo)
    elif ("صورة" in input_str) or ("صوره" in input_str):
        return await zed.edit(
            "**✧ لـ إضافة صور الكلايش ..**\n**✧ استخدم الامر (اضف) مباشرة بدون كلمة فار**"
        )
    else:
        if input_str:
            return await zed.edit(
                "**✧ عـذࢪاً .. لايوجـد هنالك فـار بإسـم {} ؟!.. ارسـل (.اوامر الفارات) لـعرض قائمـة الفـارات**".format(
                    input_str
                )
            )
        return await edit_or_reply(
            event,
            "**✧ عـذࢪاً .. لايوجـد هنالك فـار بإسـم {} ؟!.. ارسـل (.اوامر الفارات) لـعرض قائمـة الفـارات**".format(
                input_str
            ),
        )


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="حذف فار(?:\s|$)([\s\S]*)")
async def variable(event):
    sender_id = event.sender_id
    if sender_id != Config.OWNER_ID:
        return await edit_or_reply(
            event,
            "**✧ عـذراً .. عـزيـزي ✕**\n**✧ اوامـر الفـارات خاصه بصاحب الحسـاب فقـط 👨🏻‍💻**",
        )
    input_str = event.text[9:]
    if (
        (input_str == "من" or input_str == "الى" or input_str == "الترحيب")
        or "رسائلي" in input_str
        or "رسائله" in input_str
    ):
        return
    if Config.HEROKU_API_KEY is None:
        return await ed(
            event,
            "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
        )
    if Config.HEROKU_APP_NAME is not None:
        app = Heroku.app(Config.HEROKU_APP_NAME)
    else:
        return await ed(
            event,
            "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
        )
    heroku_var = app.config()
    zed = await edit_or_reply(event, "**✧ جـاري حـذف الفـار مـن بـوتك 🚮...**")
    # All Rights Reserved for "Zed-Thon" "زلـزال الهيبـه"
    if input_str == "كليشة الفحص" or input_str == "كليشه الفحص":
        variable = gvarstatus("ALIVE_TEMPLATE")
        await asyncio.sleep(1.5)
        if gvarstatus("ALIVE_TEMPLATE") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, variable
            )
        )
        delgvar("ALIVE_TEMPLATE")

    elif (
        input_str == "كليشة الحماية"
        or input_str == "كليشه الحمايه"
        or input_str == "كليشه الحماية"
        or input_str == "كليشة الحمايه"
    ):
        variable = gvarstatus("pmpermit_txt")
        await asyncio.sleep(1.5)
        if gvarstatus("pmpermit_txt") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, variable
            )
        )
        delgvar("pmpermit_txt")

    elif input_str == "كليشة البوت" or input_str == "كليشه البوت":
        variable = gvarstatus("START_TEXT")
        await asyncio.sleep(1.5)
        if gvarstatus("START_TEXT") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, variable
            )
        )
        delgvar("START_TEXT")

    elif (
        input_str == "زر البوت" or input_str == "زر الستارت" or input_str == "زر ستارت"
    ):
        variable = gvarstatus("START_BUTUN")
        await asyncio.sleep(1.5)
        if gvarstatus("START_BUTUN") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, variable
            )
        )
        delgvar("START_BUTUN")

    elif (
        input_str == "كليشة التوديع"
        or input_str == "كليشه التوديع"
        or input_str == "كليشة البلوك"
        or input_str == "كليشه البلوك"
    ):
        variable = gvarstatus("pmblock")
        await asyncio.sleep(1.5)
        if gvarstatus("pmblock") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, variable
            )
        )
        delgvar("pmblock")

    elif input_str == "كليشة الايدي" or input_str == "كليشه الايدي":
        variable = "ZID_TEMPLATE"
        await asyncio.sleep(1.5)
        if gvarstatus("ZID_TEMPLATE") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
        delgvar("ZID_TEMPLATE")

    elif input_str == "صورة الفحص" or input_str == "صوره الفحص":
        variable = "ALIVE_PIC"
        await asyncio.sleep(1.5)
        if gvarstatus("ALIVE_PIC") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
        delgvar("ALIVE_PIC")

    elif input_str == "صورة الاوامر" or input_str == "صوره الاوامر":
        variable = "CMD_PIC"
        await asyncio.sleep(1.5)
        if gvarstatus("CMD_PIC") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
        delgvar("CMD_PIC")

    elif input_str == "صورة السورس" or input_str == "صوره السورس":
        variable = "ALIVE_PIC"
        await asyncio.sleep(1.5)
        if gvarstatus("ALIVE_PIC") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
        delgvar("ALIVE_PIC")

    elif input_str == "صورة الكتم" or input_str == "صوره الكتم":
        variable = "PC_MUTE"
        await asyncio.sleep(1.5)
        if gvarstatus("PC_MUTE") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
        delgvar("PC_MUTE")

    elif input_str == "صورة الحظر" or input_str == "صوره الحظر":
        variable = "PC_BANE"
        await asyncio.sleep(1.5)
        if gvarstatus("PC_BANE") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
        delgvar("PC_BANE")

    elif input_str == "صورة البلوك" or input_str == "صوره البلوك":
        variable = "PC_BLOCK"
        await asyncio.sleep(1.5)
        if gvarstatus("PC_BLOCK") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
        delgvar("PC_BLOCK")

    elif (
        input_str == "صورة البوت"
        or input_str == "صوره البوت"
        or input_str == "صورة الستارت"
        or input_str == "صوره الستارت"
        or input_str == "صورة ستارت"
        or input_str == "صوره ستارت"
    ):
        variable = "BOT_START_PIC"
        await asyncio.sleep(1.5)
        if gvarstatus("BOT_START_PIC") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
        delgvar("BOT_START_PIC")

    elif (
        input_str == "صورة الحماية"
        or input_str == "صوره الحمايه"
        or input_str == "صورة الحمايه"
        or input_str == "صوره الحماية"
    ):
        variable = "pmpermit_pic"
        await asyncio.sleep(1.5)
        if gvarstatus("pmpermit_pic") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        delgvar("pmpermit_pic")
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))

    elif input_str == "صورة الوقتي" or input_str == "صوره الوقتي":
        variable = gvarstatus("DIGITAL_PIC")
        await asyncio.sleep(1.5)
        if gvarstatus("DIGITAL_PIC") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, variable
            )
        )
        delgvar("DIGITAL_PIC")

    elif input_str == "رمز الوقتي" or input_str == "رمز الاسم الوقتي":
        variable = "CUSTOM_ALIVE_EMZED"
        await asyncio.sleep(1.5)
        if gvarstatus("CUSTOM_ALIVE_EMZED") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        delgvar("CUSTOM_ALIVE_EMZED")
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
    elif input_str == "زخرفه الوقتي" or input_str == "زخرفة الوقتي":
        variable = "ZI_FN"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]
    elif (
        input_str == "رسائل الحماية"
        or input_str == "رسائل الحمايه"
        or input_str == "رسائل الخاص"
        or input_str == "رسائل حماية الخاص"
        or input_str == "عدد التحذيرات"
    ):
        variable = "MAX_FLOOD_IN_PMS"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]
    elif (
        input_str == "البايو"
        or input_str == "البايو الوقتي"
        or input_str == "النبذه الوقتيه"
    ):
        variable = "DEFAULT_BIO"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_BIO") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        delgvar("DEFAULT_BIO")
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
    elif input_str == "اسم المستخدم" or input_str == "الاسم":
        variable = "ALIVE_NAME"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]
    elif (
        input_str == "كروب الرسائل"
        or input_str == "كروب التخزين"
        or input_str == "كروب الخاص"
    ):
        variable = "PM_LOGGER_GROUP_ID"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "السجل" or input_str == "كروب السجل":
        variable = "PRIVATE_GROUP_BOT_API_ID"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "السجل 2" or input_str == "كروب السجل 2":
        variable = "PRIVATE_GROUP_ID"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "قناة السجل" or input_str == "قناة السجلات":
        variable = "PRIVATE_CHANNEL_BOT_API_ID"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "قناة الملفات" or input_str == "قناة الاضافات":
        variable = "PLUGIN_CHANNEL"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "التحقق" or input_str == "كود التحقق":
        variable = "TG_2STEP_VERIFICATION_CODE"
        await asyncio.sleep(1.5)
        if gvarstatus("TG_2STEP_VERIFICATION_CODE") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        delgvar("TG_2STEP_VERIFICATION_CODE")
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))

    elif input_str == "ايديي" or input_str == "ايدي الحساب":
        variable = "OWNER_ID"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "نقطة الاوامر" or input_str == "نقطه الاوامر":
        variable = "COMMAND_HAND_LER"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "التوكن" or input_str == "توكن البوت":
        variable = "TG_BOT_TOKEN"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "معرف البوت" or input_str == "معرف بوت":
        variable = "TG_BOT_USERNAME"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "الريبو" or input_str == "السورس":
        variable = "UPSTREAM_REPO"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif input_str == "اسمي التلقائي" or input_str == "الاسم التلقاائي":
        variable = "AUTONAME"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str, heroku_var[variable]
            )
        )
        del heroku_var[variable]

    elif (
        input_str == "جلسة المساعد"
        or input_str == "الحساب المساعد"
        or input_str == "مساعد الميوزك"
        or input_str == "كود الميوزك"
        or input_str == "جلسة الميوزك"
    ):
        variable = "VC_SESSION"
        await asyncio.sleep(1.5)
        if variable not in heroku_var:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف الفـار .. بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶** `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                input_str
            )
        )
        del heroku_var[variable]

    elif (
        input_str == "ايموجي الايدي"
        or input_str == "ايموجي ايدي"
        or input_str == "رمز الايدي"
        or input_str == "رمز ايدي"
        or input_str == "الرمز ايدي"
    ):
        variable = gvarstatus("CUSTOM_ALIVE_EMOJI")
        await asyncio.sleep(1.5)
        if variable is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}`".format(
                input_str, variable
            )
        )
        delgvar("CUSTOM_ALIVE_EMOJI")
    elif input_str == "عنوان الايدي" or input_str == "عنوان ايدي":
        variable = gvarstatus("CUSTOM_ALIVE_TEXT")
        await asyncio.sleep(1.5)
        if variable is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}`".format(
                input_str, variable
            )
        )
        delgvar("CUSTOM_ALIVE_TEXT")
    elif (
        input_str == "خط الايدي"
        or input_str == "خط ايدي"
        or input_str == "خطوط الايدي"
        or input_str == "خط ايدي"
    ):
        variable = gvarstatus("CUSTOM_ALIVE_FONT")
        await asyncio.sleep(1.5)
        if variable is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}`".format(
                input_str, variable
            )
        )
        delgvar("CUSTOM_ALIVE_FONT")
    elif input_str == "كاشف الاباحي" or input_str == "كشف الاباحي":
        variable = gvarstatus("DEEP_API")
        await asyncio.sleep(1.5)
        if variable is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}`".format(
                input_str, variable
            )
        )
        delgvar("DEEP_API")
    elif input_str == "ايقاف الترحيب" or input_str == "نوم الترحيب":
        variable = "TIME_STOP"
        await asyncio.sleep(1.5)
        if variable is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit(
            "**✧ تم حـذف {} بنجـاح ☑️**\n**✧ المتغيـر المحـذوف : ↶**\n `{}`".format(
                input_str, variable
            )
        )
        delgvar("TIME_STOP")
    elif (
        input_str == "ثواني لانهائي"
        or input_str == "ثواني التجميع"
        or input_str == "عدد لانهائي"
    ):
        variable = "SEC_LAN"
        await asyncio.sleep(1.5)
        if gvarstatus("SEC_LAN") is None:
            return await zed.edit(
                "**✧ عـذࢪاً عـزيـزي .. انت لـم تقـم باضـافـة فـار {} اصـلاً...**".format(
                    input_str
                )
            )
        await zed.edit("**✧ تم حـذف فـار {} . . بنجـاح ☑️**".format(input_str))
        delgvar("SEC_LAN")
    else:
        if input_str:
            return await zed.edit(
                "**✧ عـذࢪاً .. لايوجـد هنالك فـار بإسـم {} ؟!.. ارسـل (.اوامر الفارات) لـعرض قائمـة الفـارات**".format(
                    input_str
                )
            )
        return await edit_or_reply(
            event,
            "**✧ عـذࢪاً .. لايوجـد هنالك فـار بإسـم {} ؟!.. ارسـل (.اوامر الفارات) لـعرض قائمـة الفـارات**".format(
                input_str
            ),
        )


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="جلب فار(?:\s|$)([\s\S]*)")
async def custom_zed(event):
    sender_id = event.sender_id
    if sender_id != Config.OWNER_ID:
        return await edit_or_reply(
            event,
            "**✧ عـذراً .. عـزيـزي ✕**\n**✧ اوامـر الفـارات خاصه بصاحب الحسـاب فقـط 👨🏻‍💻**",
        )
    input_str = event.text[9:]
    zed = await edit_or_reply(event, "**✧ جــاري جلـب معلـومـات الفــار 🛂. . .**")
    if (
        input_str == "كليشة الحماية"
        or input_str == "كليشة الحمايه"
        or input_str == "كليشه الحماية"
        or input_str == "كليشه الحمايه"
    ):
        variable = gvarstatus("pmpermit_txt")
        if variable is None:
            await zed.edit(
                "**✧ فـار كليشـة الحمايـة غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الكليشـة استخـدم الامـر : ↶**\n `.اضف فار كليشة الحماية` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "كليشة الفحص" or input_str == "كليشه الفحص":
        variable = gvarstatus("ALIVE_TEMPLATE")
        if variable is None:
            await zed.edit(
                "**✧ فـار كليشـة الفحص غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الكليشـة استخـدم الامـر : ↶**\n `.اضف فار كليشة الفحص` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "كليشة البوت" or input_str == "كليشه البوت":
        variable = gvarstatus("START_TEXT")
        if variable is None:
            await zed.edit(
                "**✧ فـار كليشـة البـوت غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الكليشـة استخـدم الامـر : ↶**\n `.اضف فار كليشة البوت` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "زر البوت" or input_str == "زر الستارت" or input_str == "زر ستارت"
    ):
        variable = gvarstatus("START_BUTUN")
        if variable is None:
            await zed.edit(
                "**✧ فـار زر كليشـة ستـارت البـوت غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع يـوزرك او يـوزر قناتـك استخـدم الامـر : ↶**\n `.اضف فار زر الستارت` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n https://t.me/{}\n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "كليشة التوديع"
        or input_str == "كليشه التوديع"
        or input_str == "كليشة البلوك"
        or input_str == "كليشه البلوك"
    ):
        variable = gvarstatus("pmblock")
        if variable is None:
            await zed.edit(
                "**✧ فـار كليشـة الحظـر غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الكليشـة استخـدم الامـر : ↶**\n `.اضف فار كليشة الحظر` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "رمز الوقتي" or input_str == "رمز الاسم الوقتي":
        variable = gvarstatus("CUSTOM_ALIVE_EMZED")
        if variable is None:
            await zed.edit(
                "**✧ فـار رمـز الوقتـي غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الرمـز استخـدم الامـر : ↶**\n `.اضف فار رمز الوقتي` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "التحقق" or input_str == "كود التحقق":
        variable = gvarstatus("TG_2STEP_VERIFICATION_CODE")
        if variable is None:
            await zed.edit(
                "**✧ فـار التحقق بخطوتين غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الرمـز استخـدم الامـر : ↶**\n `.اضف فار التحقق`  **بالـرد ع كـود التحـقق**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "كاشف الاباحي" or input_str == "كشف الاباحي":
        variable = gvarstatus("DEEP_API")
        if variable is None:
            await zed.edit(
                "**✧ فـار كشـف الاباحي غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الكـود استخـدم الامـر : ↶**\n `.اضف فار كاشف الاباحي` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "البايو"
        or input_str == "البايو الوقتي"
        or input_str == "النبذه"
        or input_str == "البايو تلقائي"
    ):
        variable = gvarstatus("DEFAULT_BIO")
        if variable is None:
            await zed.edit(
                "**✧ فـار البايـو الوقتـي غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع نـص استخـدم الامـر : ↶**\n `.اضف فار البايو` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "اسم المستخدم" or input_str == "الاسم":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "ALIVE_NAME"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار اسـم المستخـدم غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الاسم استخـدم الامـر : ↶**\n `.اضف فار اسم المستخدم` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "كود تيرمكس"
        or input_str == "كود السيشن"
        or input_str == "كود سيشن"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "STRING_SESSION"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار {} غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الاسم استخـدم الامـر : ↶**\n `.اضف فار {}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, input_str
                )
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "جلسة المساعد"
        or input_str == "الحساب المساعد"
        or input_str == "مساعد الميوزك"
        or input_str == "كود الميوزك"
        or input_str == "جلسة الميوزك"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "VC_SESSION"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار {} غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الاسم استخـدم الامـر : ↶**\n `.اضف فار {}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, input_str
                )
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "ايديي" or input_str == "ايدي الحساب":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "OWNER_ID"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار ايـدي الحسـاب غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الايـدي فقـط استخـدم الامـر : ↶**\n `.اضف فار ايدي الحساب` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "نقطة الاوامر" or input_str == "نقطه الاوامر":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "COMMAND_HAND_LER"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار نقطـة الاوامـر غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الرمـز فقـط استخـدم الامـر : ↶**\n `.اضف فار نقطة الاوامر` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "التوكن" or input_str == "توكن البوت":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "TG_BOT_TOKEN"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار توكـن البـوت غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع التوكـن فقـط استخـدم الامـر : ↶**\n `.اضف فار التوكن` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "معرف البوت" or input_str == "معرف بوت":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "TG_BOT_USERNAME"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار معرف البوت غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع المعرف استخـدم الامـر : ↶**\n `.اضف فار معرف البوت` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "الريبو" or input_str == "السورس":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "UPSTREAM_REPO"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار الريبـو غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع رابط السورس الرسمي استخـدم الامـر : ↶**\n `.اضف فار الريبو` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "اسمي التلقائي" or input_str == "الاسم التلقاائي":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "AUTONAME"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار الاسـم التلقائي غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الاسم استخـدم الامـر : ↶**\n `.اضف فار اسمي التلقائي` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "صورة الحماية"
        or input_str == "صوره الحمايه"
        or input_str == "صورة الحمايه"
        or input_str == "صوره الحماية"
    ):
        variable = gvarstatus("pmpermit_pic")
        if variable is None:
            await zed.edit(
                "**✧ فـار صـورة الحمايـة غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع صـورة فقـط استخـدم الامـر : ↶**\n `.اضف صورة الحماية` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "صورة الوقتي" or input_str == "صوره الوقتي":
        variable = gvarstatus("DIGITAL_PIC")
        if variable is None:
            await zed.edit(
                "**✧ فـار صـورة الوقتـي غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع صـورة فقـط استخـدم الامـر : ↶**\n `.اضف صورة الوقتي` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "صورة الفحص" or input_str == "صوره الفحص":
        variable = gvarstatus("ALIVE_PIC")
        if variable is None:
            await zed.edit(
                "**✧ فـار صـورة الفحص غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع صـورة فقـط استخـدم الامـر : ↶**\n `.اضف صورة الفحص` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "صورة البوت"
        or input_str == "صوره البوت"
        or input_str == "صورة الستارت"
        or input_str == "صوره الستارت"
        or input_str == "صورة ستارت"
        or input_str == "صوره ستارت"
    ):
        variable = gvarstatus("BOT_START_PIC")
        if variable is None:
            await zed.edit(
                "**✧ فـار صـورة ستـارت البـوت غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع صـورة فقـط استخـدم الامـر : ↶**\n `.اضف صورة البوت` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "صورة الاوامر" or input_str == "صوره الاوامر":
        variable = gvarstatus("CMD_PIC")
        if variable is None:
            await zed.edit(
                "**✧ فـار صـورة الاوامـر غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع صـورة فقـط استخـدم الامـر : ↶**\n `.اضف صورة الاوامر` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "صورة السورس" or input_str == "صوره السورس":
        variable = gvarstatus("ALIVE_PIC")
        if variable is None:
            await zed.edit(
                "**✧ فـار صـورة السـورس غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع صـورة فقـط استخـدم الامـر : ↶**\n `.اضف صورة السورس` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "صورة الكتم" or input_str == "صوره الكتم":
        variable = gvarstatus("PC_MUTE")
        if variable is None:
            await zed.edit(
                "**✧ فـار صـورة الكتم غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع صـورة فقـط استخـدم الامـر : ↶**\n `.اضف صورة الكتم` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "صورة الحظر" or input_str == "صوره الحظر":
        variable = gvarstatus("PC_BANE")
        if variable is None:
            await zed.edit(
                "**✧ فـار صـورة الحظر غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع صـورة فقـط استخـدم الامـر : ↶**\n `.اضف صورة الحظر` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "صورة البلوك" or input_str == "صوره البلوك":
        variable = gvarstatus("PC_BLOCK")
        if variable is None:
            await zed.edit(
                "**✧ فـار صـورة البلوك غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع صـورة فقـط استخـدم الامـر : ↶**\n `.اضف صورة البلوك` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "زخرفة الوقتي" or input_str == "زخرفه الوقتي":
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "ZI_FN"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار زخرفـة الاسـم الوقتي غيـر موجـود ❌**\n**✧ لـ اضـافته فقـط استخـدم الامـر : ↶**\n `.الوقتي 1` الـى `.الوقتي 14` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "رسائل الحماية"
        or input_str == "رسائل الحمايه"
        or input_str == "رسائل الخاص"
        or input_str == "رسائل حماية الخاص"
        or input_str == "عدد التحذيرات"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = Config.MAX_FLOOD_IN_PMS
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار رسـائل الحمايـة غيـر موجـود ❌**\n**✧ لـ اضـافته فقـط استخـدم الامـر : ↶**\n `.اضف فار رسائل الحماية` بالـرد ع عـدد فقـط \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "زخرفة الوقتية"
        or input_str == "زخرفه الوقتيه"
        or input_str == "زخرفة الوقتيه"
        or input_str == "زخرفه الوقتية"
    ):
        variable = gvarstatus("DEFAULT_PIC")
        if variable is None:
            await zed.edit(
                "**✧ فـار زخرفـة الصـورة الوقتيـة غيـر موجـود ❌**\n**✧ لـ اضـافته فقـط استخـدم الامـر : ↶**\n `.وقتي 1` الـى `.وقتي 17` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "الوقت" or input_str == "الساعه" or input_str == "المنطقه الزمنيه"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "TZ"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار المنطقـه الزمنيـه غيـر موجـود ❌**\n**✧ لـ اضـافته فقـط استخـدم الامـر : ↶**\n `.وقت` واسـم الدولـة \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "كليشة الايدي" or input_str == "كليشه الايدي":
        variable = gvarstatus("ZID_TEMPLATE")
        if variable is None:
            await zed.edit(
                "**✧ فـار ايموجي/رمز الايدي غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الكليشـة من هنا ( @zziddd ) استخـدم الامـر : ↶**\n `.اضف كليشة الايدي` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "ايموجي الايدي"
        or input_str == "ايموجي ايدي"
        or input_str == "رمز الايدي"
        or input_str == "رمز ايدي"
        or input_str == "الرمز ايدي"
    ):
        variable = gvarstatus("CUSTOM_ALIVE_EMOJI")
        if variable is None:
            await zed.edit(
                "**✧ فـار ايموجي/رمز الايدي غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الرمـز استخـدم الامـر : ↶**\n `.اضف فار رمز الايدي` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "عنوان الايدي" or input_str == "عنوان ايدي":
        variable = gvarstatus("CUSTOM_ALIVE_TEXT")
        if variable is None:
            await zed.edit(
                "**✧ فـار نص عنـوان كليشـة الايـدي غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الرمـز استخـدم الامـر : ↶**\n `.اضف فار عنوان الايدي` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "خط الايدي"
        or input_str == "خط ايدي"
        or input_str == "خطوط الايدي"
        or input_str == "خط ايدي"
    ):
        variable = gvarstatus("CUSTOM_ALIVE_FONT")
        if variable is None:
            await zed.edit(
                "**✧ فـار خطـوط كليشـة الايـدي غيـر موجـود ❌**\n**✧ لـ اضـافته بالـرد ع الرمـز استخـدم الامـر : ↶**\n `.اضف فار خطوط الايدي` \n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "لاعب 1":
        variable = gvarstatus("Z_AK")
        if gvarstatus("Z_AK") is None:
            await zed.edit(
                "**✧ المتغيـر غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ المتغيـر {} موجـود ☑️**\n**✧ قيمـة المتغيـر : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "لاعب 2":
        variable = gvarstatus("Z_A2K")
        if gvarstatus("Z_A2K") is None:
            await zed.edit(
                "**✧ المتغيـر غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ المتغيـر {} موجـود ☑️**\n**✧ قيمـة المتغيـر : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "لاعب 3":
        variable = gvarstatus("Z_A3K")
        if gvarstatus("Z_A3K") is None:
            await zed.edit(
                "**✧ المتغيـر غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ المتغيـر {} موجـود ☑️**\n**✧ قيمـة المتغيـر : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "لاعب 4":
        variable = gvarstatus("Z_A4K")
        if gvarstatus("Z_A4K") is None:
            await zed.edit(
                "**✧ المتغيـر غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ المتغيـر {} موجـود ☑️**\n**✧ قيمـة المتغيـر : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "لاعب 5":
        variable = gvarstatus("Z_A5K")
        if gvarstatus("Z_A5K") is None:
            await zed.edit(
                "**✧ المتغيـر غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ المتغيـر {} موجـود ☑️**\n**✧ قيمـة المتغيـر : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "توكن المكافح"
        or input_str == "كود المكافح"
        or input_str == "مكافح التخريب"
        or input_str == "مكافح التفليش"
    ):
        if Config.HEROKU_API_KEY is None:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_API_KEY` اذا كنت لاتعلم اين يوجد فقط اذهب الى حسابك في هيروكو ثم الى الاعدادات ستجده بالاسفل انسخه ودخله في الفار. ",
            )
        if Config.HEROKU_APP_NAME is not None:
            app = Heroku.app(Config.HEROKU_APP_NAME)
        else:
            return await ed(
                event,
                "✧ اضبط Var المطلوب في Heroku على وظيفة هذا بشكل طبيعي `HEROKU_APP_NAME` اسم التطبيق اذا كنت لاتعلم.",
            )
        heroku_var = app.config()
        variable = "SPAMWATCH_API"
        if variable not in heroku_var:
            await zed.edit(
                "**✧ فـار توكـن المكـافح غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ الفـار {} موجـود ☑️**\n**✧ قيمـة الفـار : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "اشتراك خاص"
        or input_str == "اشتراك الخاص"
        or input_str == "قناة الاشتراك"
        or input_str == "الاشتراك"
    ):
        variable = gvarstatus("Custom_Pm_Channel")
        if gvarstatus("Custom_Pm_Channel") is None:
            await zed.edit(
                "**✧ المتغيـر غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ المتغيـر {} موجـود ☑️**\n**✧ قيمـة المتغيـر : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "اشتراك كروب"
        or input_str == "اشتراك الكروب"
        or input_str == "قناة الاشتراك"
        or input_str == "الاشتراك"
    ):
        variable = gvarstatus("Custom_G_Channel")
        if gvarstatus("Custom_G_Channel") is None:
            await zed.edit(
                "**✧ المتغيـر غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ المتغيـر {} موجـود ☑️**\n**✧ قيمـة المتغيـر : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif input_str == "االهمسه":
        variable = gvarstatus("hmsa_id")
        if gvarstatus("hmsa_id") is None:
            await zed.edit(
                "**✧ المتغيـر غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ المتغيـر {} موجـود ☑️**\n**✧ قيمـة المتغيـر : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    elif (
        input_str == "ثواني لانهائي"
        or input_str == "ثواني التجميع"
        or input_str == "عدد لانهائي"
    ):
        variable = gvarstatus("SEC_LAN")
        if gvarstatus("SEC_LAN") is None:
            await zed.edit(
                "**✧ المتغيـر غيـر موجـود ❌**\n\n**✧ قنـاة السـورس : @ZThon**"
            )
        else:
            await zed.edit(
                "**✧ المتغيـر {} موجـود ☑️**\n**✧ قيمـة المتغيـر : ↶**\n `{}` \n\n**✧ قنـاة السـورس : @ZThon**".format(
                    input_str, variable
                )
            )

    else:
        if input_str:
            return await zed.edit(
                "**✧ عـذࢪاً .. لايوجـد هنالك فـار بإسـم {} ؟!.. ارسـل (.اوامر الفارات) لـعرض قائمـة الفـارات**".format(
                    input_str
                )
            )
        return await edit_or_reply(
            event,
            "**✧ عـذࢪاً .. لايوجـد هنالك فـار بإسـم {} ؟!.. ارسـل (.اوامر الفارات) لـعرض قائمـة الفـارات**".format(
                input_str
            ),
        )


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="وقت(?:\\s|$)([\\s\\S]*)")
async def variable(event):
    sender_id = event.sender_id
    if sender_id != Config.OWNER_ID:
        return await edit_or_reply(
            event,
            "**✧ عـذراً .. عـزيـزي ✕**\n**✧ اوامـر الفـارات خاصه بصاحب الحسـاب فقـط 👨🏻‍💻**",
        )
    input_str = event.text[5:]
    viraq = "Asia/Baghdad"
    vmsr = "Africa/Cairo"
    vdubai = "Asia/Dubai"
    vturk = "Europe/Istanbul"
    valgiers = "Africa/Algiers"
    vmoroco = "Africa/Casablanca"
    viran = "Asia/Tehran"
    zed = await edit_or_reply(
        event, "**✧ جـاري أعـداد المنطقـه الزمنيـه لـ زدثــون 🌐...**"
    )
    # All Rights Reserved for "Zed-Thon" "زلـزال الهيبـه"
    if (
        input_str == "العراق"
        or input_str == "اليمن"
        or input_str == "سوريا"
        or input_str == "السعودية"
        or input_str == "لبنان"
        or input_str == "الاردن"
        or input_str == "فلسطين"
        or input_str == "قطر"
        or input_str == "الكويت"
        or input_str == "البحرين"
    ):
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}` \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", viraq)
    elif input_str == "مصر" or input_str == "ليبيا" or input_str == "القاهرة":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", vmsr)
    elif (
        input_str == "دبي"
        or input_str == "الامارات"
        or input_str == "سلطنة عمان"
        or input_str == "مسقط"
    ):
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", vdubai)
    elif input_str == "تركيا" or input_str == "اسطنبول" or input_str == "انقرة":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", vturk)
    elif input_str == "تونس" or input_str == "الجزائر":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", valgiers)
    elif input_str == "المغرب" or input_str == "الدار البيضاء":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", vmoroco)
    elif input_str == "ايران" or input_str == "طهران":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", viran)
    elif input_str == "السودان":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Africa/Khartoum")
    elif input_str == "ايطاليا":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Europe/Rome")
    elif input_str == "روسيا":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Europe/Moscow")
    elif input_str == "امريكا":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "America/New_York")
    elif input_str == "ماليزيا":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Asia/Kuala_Lumpur")
        # addgvar("T_Z", "Asia/Kuching")
    elif input_str == "بريطانيا":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Europe/London")
    elif input_str == "شيكاغو":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "America/Chicago")
    elif input_str == "لوس انجلوس":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "America/Los_Angeles")
    elif (
        input_str == "المانيا"
        or input_str == "فرنسا"
        or input_str == "بلجيكا"
        or input_str == "النرويج"
        or input_str == "اسبانيا"
    ):
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Europe/Berlin")
    elif input_str == "الصين":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Asia/Shanghai")
    elif input_str == "اليابان":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Asia/Tokyo")
    elif input_str == "اندنوسيا":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Asia/Jakarta")
    elif input_str == "الهند":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Asia/Kolkata")
    elif input_str == "موريتانيا":
        await asyncio.sleep(1.5)
        if gvarstatus("T_Z") is not None:
            await zed.edit(
                "**✧ تم تغييـر المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المتغير : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✧ تم اضـافـة المنطقـه الزمنيـه .. بنجـاح ☑️**\n**✧ المضـاف اليـه : ↶**\n دولـة `{}`  \n**✧ يتم الان اعـادة تشغيـل بـوت زد ثـون يستغـرق الامر 2-1 دقيقـه ▬▭ ...**".format(
                    input_str
                )
            )
        addgvar("T_Z", "Africa/Nouakchott")


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="اوامر الفارات")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalVP_cmd)


@zedub.zed_cmd(pattern="الفارات")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalVP_cmd)


@zedub.zed_cmd(pattern="الوقت")
async def cmd(zelzallltm):
    await edit_or_reply(zelzallltm, ZelzalTZ_cmd)
