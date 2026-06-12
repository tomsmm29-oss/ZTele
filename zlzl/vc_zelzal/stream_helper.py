import glob
import os
import random
import re

try:
    pass
except ModuleNotFoundError:
    os.system("pip3 install enum")
from enum import Enum

from requests.exceptions import MissingSchema
from requests.models import PreparedRequest
from yt_dlp import YoutubeDL

from ..utils import runcmd


class Stream(Enum):
    audio = 1
    video = 2


def get_cookies_file():
    folder_path = f"{os.getcwd()}/zion"
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file


yt_regex_str = "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

yt_regex = re.compile(yt_regex_str)


def check_url(url):
    prepared_request = PreparedRequest()
    try:
        prepared_request.prepare_url(url, None)
        return prepared_request.url
    except MissingSchema:
        return False


async def get_yt_stream_link(url, audio_only=False):
    if audio_only:
        return (
            await runcmd(
                f"yt-dlp --cookies {get_cookies_file()} --geo-bypass -f bestaudio -g {url}"
            )
        )[0]
    return (
        await runcmd(
            f"yt-dlp --cookies {get_cookies_file()} --geo-bypass -f bestvideo -g {url}"
        )
    )[0]


async def video_dl(url, title):
    path = f"temp/{title.replace(' ', '_')}.mp4"
    video_opts = {
        "format": "(bestvideo[height<=?360][ext=mp4])+(bestaudio[ext=m4a])",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "writethumbnail": False,
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [
            {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
            {"key": "FFmpegMetadata"},
        ],
        "outtmpl": path,
        "logtostderr": False,
        "quiet": True,
        "no_warnings": True,
        "cookiefile": get_cookies_file(),
    }

    with YoutubeDL(video_opts) as ytdl:
        ytdl.extract_info(url)
    return path
