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
import time
from bs4 import BeautifulSoup
from datetime import datetime
from telethon.tl.types import InputMediaPhoto

from . import zedub
from ..Config import Config

ZELZAL_APP_ID = "6e65179ed1d879f3d905e28ef8803625"


# ===================== أدوات البحث ===================== #

async def fetch_image(session, url):
    try:
        async with session.get(url, timeout=10) as r:
            if r.status == 200:
                return await r.read()
    except:
        return None
    return None


async def pinterest_search(session, query):
    try:
        url = f"https://www.pinterest.com/search/pins/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        async with session.get(url, headers=headers) as r:
            if r.status != 200:
                return None
            html = await r.text()
            soup = BeautifulSoup(html, "html.parser")
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                return img_tag.get("src")
    except:
        return None
    return None


async def google_api_search(session, query):
    try:
        url = "https://bots.shrimadhavuk.me/search/"
        params = {"q": query, "app_id": ZELZAL_APP_ID, "p": "GoogleImages"}
        async with session.get(url, params=params) as r:
            if r.status != 200:
                return None
            data = await r.json()
            results = [i.get("url") for i in data.get("results", []) if i.get("url")]
            return results[0] if results else None
    except:
        return None


async def duckduckgo_search(session, query):
    try:
        url = "https://duckduckgo.com/i.js"
        params = {"q": query, "o": "json"}
        async with session.get(url, params=params) as r:
            if r.status != 200:
                return None
            data = await r.json()
            results = [i.get("image") for i in data.get("results", []) if i.get("image")]
            return results[0] if results else None
    except:
        return None


async def bing_search(session, query):
    try:
        url = f"https://www.bing.com/images/search?q={query}&form=HDRSC2"
        async with session.get(url) as r:
            if r.status != 200:
                return None
            soup = BeautifulSoup(await r.text(), "html.parser")
            imgs = [i.get("src") for i in soup.find_all("img") if i.get("src")]
            return imgs[0] if imgs else None
    except:
        return None


# ===================== أمر الصور ===================== #

@zedub.zed_cmd(pattern="صور (.*)")
async def _(event):
    if event.fwd_from:
        return

    start = datetime.now()
    await event.edit("╮ ❐ جـاري البحث عن الصـورة  ...𓅫╰")

    query = event.pattern_match.group(1)

    async with aiohttp.ClientSession() as session:
        image_data = None

        # محركات البحث بالترتيب: Pinterest -> Google -> DuckDuckGo -> Bing
        search_order = [
            pinterest_search,
            google_api_search,
            duckduckgo_search,
            bing_search,
        ]

        for method in search_order:
            try:
                img_url = await method(session, query)
                if img_url:
                    image_data = await fetch_image(session, img_url)
                    if image_data:
                        break
            except:
                continue

    if not image_data:
        await event.edit(f"- اووبـس .. لم استطـع ايجـاد صـورة عـن {query} ؟!\n"
                         f"**- حـاول مجـدداً واكتـب الكلمـه بشكـل صحيح**")
        return

    await event.client.send_file(
        event.chat_id,
        file=image_data,
        caption=f"صورة عن: {query}"
    )

    end = datetime.now()
    ms = (end - start).seconds
    await event.edit(f"- اكتمـل البحث عـن {query} في {ms} ثانيـه ✓", link_preview=False)
    await asyncio.sleep(5)
    await event.delete()