"""Command: اوقات الصلاة لعواصم الدول باللغـة العربيـة
Credit: T.me/ZThon
@zzzzl1l - كتـابـة الملـف :  زلــزال الهيبــه"""

import json

import requests

from ..core.managers import edit_delete, edit_or_reply
from . import zedub

plugin_category = "البحث"


@zedub.zed_cmd(
    pattern="صلاة ([\s\S]*)",
    command=("صلاة", plugin_category),
    info={
        "header": "اوقـات الصـلاة لـ عواصـم الـدول العـربيـة",
        "الاستـخـدام": "{tr}صلاة + العاصمـة",
    },
)
async def get_adzan(adzan):
    ZELZAL = adzan.pattern_match.group(1)
    if ZELZAL == "صنعاء" or ZELZAL == "اليمن":
        url = f"https://api.pray.zone/v2/times/today.json?city=Sanaa"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>صنعـاء</b>\
	            \n<b>الـدولة  : <b>اليمـن</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "مصر" or ZELZAL == "القاهرة" or ZELZAL == "القاهره":
        url = f"https://api.pray.zone/v2/times/today.json?city=Cairo"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>القاهـرة</b>\
	            \n<b>الـدولة  : <b>مصـر</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "بغداد" or ZELZAL == "العراق":
        url = f"https://api.pray.zone/v2/times/today.json?city=Baghdad"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>بغـداد</b>\
	            \n<b>الـدولة  : <b>العـراق</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "دمشق" or ZELZAL == "سوريا":
        url = f"https://api.pray.zone/v2/times/today.json?city=Damascus"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>دمشـق</b>\
	            \n<b>الـدولة  : <b>سـوريا</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "الدوحه" or ZELZAL == "قطر":
        url = f"https://api.pray.zone/v2/times/today.json?city=Doha"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>الدوحـه</b>\
	            \n<b>الـدولة  : <b>قطـر</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "مسقط" or ZELZAL == "سلطنه عمان":
        url = f"https://api.pray.zone/v2/times/today.json?city=Muscat"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>مسقـط</b>\
	            \n<b>الـدولة  : <b>سلطنـة عمـان</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "مكه" or ZELZAL == "السعوديه":
        url = f"https://api.pray.zone/v2/times/today.json?city=Mecca"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>مكـه المكـرمـه</b>\
	            \n<b>الـدولة  : <b>المملكـة العربيـه السعـودية</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "بيروت" or ZELZAL == "لبنان":
        url = f"https://api.pray.zone/v2/times/today.json?city=Beirut"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>بيـروت</b>\
	            \n<b>الـدولة  : <b>لبنـان</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "عمان" or ZELZAL == "الاردن":
        url = f"https://api.pray.zone/v2/times/today.json?city=Amman"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>عَمـان</b>\
	            \n<b>الـدولة  : <b>الاردن</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "الرباط" or ZELZAL == "المغرب":
        url = f"https://api.pray.zone/v2/times/today.json?city=Rabat"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>الربـاط</b>\
	            \n<b>الـدولة  : <b>المغـرب</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "الخرطوم" or ZELZAL == "السودان":
        url = f"https://api.pray.zone/v2/times/today.json?city=Khartoum"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>الخرطـوم</b>\
	            \n<b>الـدولة  : <b>السـودان</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "بنغازي" or ZELZAL == "ليبيا":
        url = f"https://api.pray.zone/v2/times/today.json?city=Benghazi"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>بنغـازي</b>\
	            \n<b>الـدولة  : <b>ليبيـا</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif ZELZAL == "تونس":
        url = f"https://api.pray.zone/v2/times/today.json?city=Tunis"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>تونـس</b>\
	            \n<b>الـدولة  : <b>تونـس</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
    elif (
        ZELZAL == "ازمير"
        or ZELZAL == "اسطنبول"
        or ZELZAL == "انقره"
        or ZELZAL == "تركيا"
    ):
        url = f"https://api.pray.zone/v2/times/today.json?city=Izmir"
        request = requests.get(url)
        if request.status_code != 200:
            await edit_delete(
                adzan,
                f"** لم يـتم العثور على هـذه المدينه {ZELZAL}**\n**-يرجى كتابة اسم العاصمـه او الدولـة بشكـل صحيـح** ",
                5,
            )
            return
        result = json.loads(request.text)
        zedthonresult = f"<b>🕋╎اوقـات الصـلاة بالتـوقيت المحلـي لعواصـم الـدول <b>\
	            \n\n<b>المـدينة     : <b>اسطنبـول</b>\
	            \n<b>الـدولة  : <b>تركيـا</b>\
	            \n<b>التـاريخ     : <b>{result['results']['datetime'][0]['date']['gregorian']}</b>\
	            \n<b>الهـجري    : <b>{result['results']['datetime'][0]['date']['hijri']}</b>\
	            \n\n<b>الامـساك    : <b>{result['results']['datetime'][0]['times']['Imsak']}</b>\
	            \n<b>شـروق الشمس  : <b>{result['results']['datetime'][0]['times']['Sunrise']}</b>\
	            \n<b>الـفجر     : <b>{result['results']['datetime'][0]['times']['Fajr']}</b>\
	            \n<b>الضـهر    : <b>{result['results']['datetime'][0]['times']['Dhuhr']}</b>\
	            \n<b>العـصر      : <b>{result['results']['datetime'][0]['times']['Asr']}</b>\
	            \n<b>غـروب الشمس   : <b>{result['results']['datetime'][0]['times']['Sunset']}</b>\
	            \n<b>المـغرب  : <b>{result['results']['datetime'][0]['times']['Maghrib']}</b>\
	            \n<b>العشـاء     : <b>{result['results']['datetime'][0]['times']['Isha']}</b>\
	            \n<b>منتـصف الليل : <b>{result['results']['datetime'][0]['times']['Midnight']}</b>\
		        \n\nᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡╎@ZThon\
	    "
        await edit_or_reply(adzan, zedthonresult, "html")
