# Zed-Thon - ZelZal
# Copyright (C) 2022 Zedthon . All Rights Reserved
#
# This file is a part of < https://github.com/Zed-Thon/ZelZal/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/Zed-Thon/ZelZal/blob/master/LICENSE/>.

# الملف محمي بحقوق الملكيـه الخـاصه بـ GNU Affero General Public License
# So تخمـط الملف ابلـع سـورسك بانـد

import asyncio
import aiohttp
import os
import shutil
import time
from bs4 import BeautifulSoup
from datetime import datetime
from telethon.utils import guess_extension

from . import zedub
from ..Config import Config

ZELZAL_APP_ID = "6e65179ed1d879f3d905e28ef8803625"


# ===================== أدوات البحث ===================== #

async def fetch_image(session, url, save_path):
    try:
        r = await session.get(url, timeout=10)
        if r.status == 200:
            with open(save_path, "wb") as f:
                f.write(await r.read())
            return True
    except:
        return False
    return False


async def google_api_search(session, query):
    url = "https://bots.shrimadhavuk.me/search/"
    params = {"q": query, "app_id": ZELZAL_APP_ID, "p": "GoogleImages"}
    r = await session.get(url)
    if r.status != 200:
        return []
    data = await r.json()
    return [i.get("url") for i in data.get("results", []) if i.get("url")]


async def duckduckgo_search(session, query):
    url = "https://duckduckgo.com/i.js"
    params = {"q": query, "o": "json"}
    r = await session.get(url, params=params)
    if r.status != 200:
        return []
    data = await r.json()
    return [i.get("image") for i in data.get("results", []) if i.get("image")]


async def bing_search(session, query):
    url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2"
    r = await session.get(url)
    if r.status != 200:
        return []
    soup = BeautifulSoup(await r.text(), "html.parser")
    imgs = soup.find_all("img")
    return [i.get("src") for i in imgs if i.get("src")]


def unsplash_fallback(query):
    return [f"https://source.unsplash.com/1600x900/?{query}"]


def lorem_fallback(query):
    return [f"https://loremflickr.com/1600/900/{query}"]


# ===================== أمر الصور ===================== #

@zedub.zed_cmd(pattern="صور (.*)")
async def _(event):
    if event.fwd_from:
        return

    start = datetime.now()
    await event.edit("╮ ❐ جـاري البحث عن الصـور  ...𓅫╰")

    zedthon = event.pattern_match.group(1)
    wzed_dir = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, zedthon)
    if not os.path.isdir(wzed_dir):
        os.makedirs(wzed_dir)

    url_lst = []

    search_methods = [
        google_api_search,
        duckduckgo_search,
        bing_search,
    ]

    async with aiohttp.ClientSession() as session:
        found_urls = []

        for method in search_methods:
            try:
                found_urls = await method(session, zedthon)
                if found_urls:
                    break
            except:
                continue

        if not found_urls:
            found_urls = unsplash_fallback(zedthon)

        if not found_urls:
            found_urls = lorem_fallback(zedthon)

        for img_url in found_urls:
            if len(url_lst) >= 10:
                break

            image_name = f"{time.time()}.jpg"
            image_path = os.path.join(wzed_dir, image_name)

            ok = await fetch_image(session, img_url, image_path)
            if ok:
                url_lst.append(image_path)

    if not url_lst:
        await event.edit(
            f"- اووبـس .. لم استطـع ايجـاد صـور عـن {zedthon} ؟!\n"
            f"**- حـاول مجـدداً واكتـب الكلمـه بشكـل صحيح**"
        )
        return

    await event.reply(file=url_lst, force_document=True)

    for each_file in url_lst:
        os.remove(each_file)
    shutil.rmtree(wzed_dir, ignore_errors=True)

    end = datetime.now()
    ms = (end - start).seconds
    await event.edit(f"- اكتمـل البحث عـن {zedthon} في {ms} ثانيـه ✓", link_preview=False)
    await asyncio.sleep(5)
    await event.delete()


# ===================== أمر الخلفيات ===================== #

@zedub.zed_cmd(pattern="خلفيات (.*)")
async def _(event):
    if event.fwd_from:
        return

    start = datetime.now()
    await event.edit("╮ ❐ جـاري البحث عن خلفيـات  ...𓅫╰")

    zedthon = event.pattern_match.group(1)
    wzed_dir = os.path.join(Config.TMP_DOWNLOAD_DIRECTORY, zedthon)
    if not os.path.isdir(wzed_dir):
        os.makedirs(wzed_dir)

    url_lst = []

    search_methods = [
        google_api_search,
        duckduckgo_search,
        bing_search,
    ]

    async with aiohttp.ClientSession() as session:
        found_urls = []

        for method in search_methods:
            try:
                found_urls = await method(session, zedthon + " wallpaper")
                if found_urls:
                    break
            except:
                continue

        if not found_urls:
            found_urls = unsplash_fallback(zedthon)

        if not found_urls:
            found_urls = lorem_fallback(zedthon)

        for img_url in found_urls:
            if len(url_lst) >= 10:
                break

            image_name = f"{time.time()}.jpg"
            image_path = os.path.join(wzed_dir, image_name)

            ok = await fetch_image(session, img_url, image_path)
            if ok:
                url_lst.append(image_path)

    if not url_lst:
        await event.edit(
            f"- اووبـس .. لم استطـع ايجـاد خلفيـات عـن {zedthon} ؟!\n"
            f"**- حـاول مجـدداً واكتـب الكلمـه بشكـل صحيح**"
        )
        return

    await event.reply(file=url_lst, force_document=True)

    for each_file in url_lst:
        os.remove(each_file)
    shutil.rmtree(wzed_dir, ignore_errors=True)

    end = datetime.now()
    ms = (end - start).seconds
    await event.edit(f"- اكتمـل البحث عـن {zedthon} في {ms} ثانيـه ✓", link_preview=False)
    await asyncio.sleep(5)
    await event.delete()