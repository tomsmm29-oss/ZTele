import asyncio

# import heroku3
import urllib3
from telegraph import Telegraph

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from ..Config import Config
from ..core.managers import edit_or_reply
from ..sql_helper.globals import addgvar, gvarstatus
from . import zedub

plugin_category = "الادوات"


telegraph = Telegraph()
r = telegraph.create_account(short_name=Config.TELEGRAPH_SHORT_NAME)
auth_url = r["auth_url"]


ZelzalVP_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗭𝗘𝗗𝗧𝗵𝗼𝗻 𝗖𝗼𝗻𝗳𝗶𝗴 𝗩𝗮𝗿𝘀 - اوامـر الفـارات](t.me/ZEDthon) 𓆪\n\n"
    "**✾╎قائـمه اوامـر تغييـر زخـارف البروفايـل + الاسـم الوقـتي بأمـر واحـد فقـط - حقـوق لـ التـاريـخ 🦾 :** \n\n"
    "⪼ `.وقتيه 1` / `.الوقتي 1`\n\n"
    "⪼ `.وقتيه 2` / `.الوقتي 2`\n\n"
    "⪼ `.وقتيه 3` / `.الوقتي 3`\n\n"
    "⪼ `.وقتيه 4` / `.الوقتي 4`\n\n"
    "⪼ `.وقتيه 5` / `.الوقتي 5`\n\n"
    "⪼ `.وقتيه 6` / `.الوقتي 6`\n\n"
    "⪼ `.وقتيه 7` / `.الوقتي 7`\n\n"
    "⪼ `.وقتيه 8` / `.الوقتي 8`\n\n"
    "⪼ `.وقتيه 9` / `.الوقتي 9`\n\n"
    "⪼ `.وقتيه 10` / `.الوقتي 10`\n\n"
    "⪼ `.وقتيه 11` / `.الوقتي 11`\n\n"
    "⪼ `.وقتيه 12` / `.الوقتي 12`\n\n"
    "⪼ `.وقتيه 13` / `.الوقتي 13`\n\n"
    "⪼ `.وقتيه 14` / `.الوقتي 14`\n\n"
    "⪼ `.وقتيه 15`\n\n"
    "⪼ `.وقتيه 16`\n\n"
    "⪼ `.وقتيه 17`\n\n\n"
    "**✾╎لـ رؤيـة زغـارف البروفايـل الوقتـي ↶**  [⦇  اضـغـط هنــا  ⦈](t.me/Zed_Thon) \n\n"
    "**✾╎لـ رؤيـة زغـارف الاســم الوقتـي ↶**  [⦇  اضـغـط هنــا  ⦈](t.me/Zed_Thon) \n\n\n"
    "🛃 سيتـم اضـافة المزيـد من الزغـارف بالتحديثـات الجـايـه\n\n"
    "\n𓆩 [𐇮 𝙕𝞝𝙇𝙕𝘼𝙇 الهہـيـٖ͡ـ͢ـبـه 𐇮](t.me/zzzzl1l) 𓆪"
)


# Copyright (C) 2022 @Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="وقتيه(?:\s|$)([\s\S]*)")
async def variable(event):
    input_str = event.pattern_match.group(1)
    zed = await edit_or_reply(
        event, "**✾╎جـاري اضـافة زخـرفـة الوقتيـه لـ بوتـك 💞🦾 . . .**"
    )
    # All Rights Reserved for "@Zed-Thon" "زلـزال الهيبـه"
    if input_str == "1":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/ZThon.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "2":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Starjedi.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "3":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Papernotes.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "4":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Terserah.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "5":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Photography Signature.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "6":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Austein.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "7":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Dream MMA.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "8":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/EASPORTS15.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "9":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/KGMissKindergarten.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "10":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/212 Orion Sans PERSONAL USE.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "11":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/PEPSI_pl.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "12":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Paskowy.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "13":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Cream Cake.otf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "14":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Hello Valentina.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "15":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Alien-Encounters-Regular.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "16":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/Linebeam.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "17":
        variable = "DEFAULT_PIC"
        zinfo = "resources/helpers/styles/EASPORTS15.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("DEFAULT_PIC") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة البروفـايل الوقـتي {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.البروفايل` **لـ بـدء البروفـايل الوقتـي . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)


# Copyright (C) 2022 @Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="الوقتي(?:\s|$)([\s\S]*)")
async def hhhzelzal(event):
    input_str = event.pattern_match.group(1)
    zed = await edit_or_reply(
        event, "**✾╎جـاري اضـافة زخـرفـة الوقتيـه لـ بوتـك 💞🦾 . . .**"
    )
    # All Rights Reserved for "@Zed-Thon" "زلـزال الهيبـه"
    if input_str == "1":
        zinfo = "𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟬"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟬")
    elif input_str == "2":
        zinfo = "𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗𝟎")
    elif input_str == "3":
        zinfo = "١٢٣٤٥٦٧٨٩٠"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "١٢٣٤٥٦٧٨٩٠")
    elif input_str == "4":
        zinfo = "₁₂₃₄₅₆₇₈₉₀"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "₁₂₃₄₅₆₇₈₉₀")
    elif input_str == "5":
        zinfo = "¹²³⁴⁵⁶⁷⁸⁹⁰"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "¹²³⁴⁵⁶⁷⁸⁹⁰")
    elif input_str == "6":
        zinfo = "➊➋➌➍➎➏➐➑➒✪"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "➊➋➌➍➎➏➐➑➒✪")
    elif input_str == "7":
        zinfo = "❶❷❸❹❺❻❼❽❾⓿"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "❶❷❸❹❺❻❼❽❾⓿")
    elif input_str == "8":
        zinfo = "➀➁➂➃➄➅➆➇➈⊙"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "➀➁➂➃➄➅➆➇➈⊙")
    elif input_str == "9":
        zinfo = "⓵⓶⓷⓸⓹⓺⓻⓼⓽⓪"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "⓵⓶⓷⓸⓹⓺⓻⓼⓽⓪")
    elif input_str == "10":
        zinfo = "①②③④⑤⑥⑦⑧⑨⓪"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "①②③④⑤⑥⑦⑧⑨⓪")
    elif input_str == "11":
        zinfo = "𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫𝟢")
    elif input_str == "12":
        zinfo = "𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿𝟶"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿𝟶")
    elif input_str == "13":
        zinfo = "𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟘"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡𝟘")
    elif input_str == "14":
        zinfo = "１２３４５６７８９０"
        await asyncio.sleep(1.5)
        if gvarstatus("ZI_FN") is not None:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎الان ارسـل ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        else:
            await zed.edit(
                "**✾╎تم إضـافة زغـرفة الاسـم الوقتـي .. بنجـاح✓**\n**✾╎نـوع الزخـرفـه {} **\n**✾╎ارسـل الان ↶** `.الاسم تلقائي`".format(
                    zinfo
                )
            )
        addgvar("ZI_FN", "１２３４５６７８９０")


# Copyright (C) 2022 @Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="اوامر الوقتي")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalVP_cmd)


# Copyright (C) 2022 @Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="الخط(?:\s|$)([\s\S]*)")
async def variable_2(event):
    input_str = event.pattern_match.group(1)
    zed = await edit_or_reply(
        event, "**✾╎جـاري اضـافة زخـرفـة خـط الحقـوق لـ بوتـك 💞🦾 . . .**"
    )
    # All Rights Reserved for "@Zed-Thon" "زلـزال الهيبـه"
    if input_str == "1":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/ZThon.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "2":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Starjedi.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "3":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Papernotes.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "4":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Terserah.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "5":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Photography Signature.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "6":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Austein.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "7":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Dream MMA.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "8":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/EASPORTS15.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "9":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/KGMissKindergarten.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "10":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/212 Orion Sans PERSONAL USE.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "11":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/PEPSI_pl.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "12":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Paskowy.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "13":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Cream Cake.otf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "14":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Hello Valentina.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "15":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Alien-Encounters-Regular.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "16":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/Linebeam.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
    elif input_str == "17":
        variable = "ZED_FONTS"
        zinfo = "resources/helpers/styles/EASPORTS15.ttf"
        await asyncio.sleep(1.5)
        if gvarstatus("ZED_FONTS") is None:
            await zed.edit(
                "**✾╎تم اضـافـة زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        else:
            await zed.edit(
                "**✾╎تم تغييـر زغـرفـة خـط الحقـوق {} بنجـاح ☑️**\n\n**✾╎الان قـم بـ ارسـال الامـر ↶** `.حقوق` **+ كلمـه بالـرد ع (صوره-ملصق-متحركه-فيديو) . .**".format(
                    input_str
                )
            )
        addgvar(variable, zinfo)
