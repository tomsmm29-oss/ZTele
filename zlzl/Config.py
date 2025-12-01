import os
from typing import Set
from telethon.tl.types import ChatBannedRights

class Config(object):
    LOGGER = True
    
    # ====================================================
    # 1. الأساسيات (من ريندر حصرياً)
    # ====================================================
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", None)
    APP_ID = int(os.environ.get("APP_ID", 6))
    API_HASH = os.environ.get("API_HASH", None)
    
    # الجلسة (أهم شي)
    STRING_SESSION = os.environ.get("STRING_SESSION", None)
    
    # قاعدة البيانات
    DB_URI = os.environ.get("DATABASE_URL", None) or os.environ.get("DB_URI", None)
    
    # ====================================================
    # 2. الهوية (يسحبها من ريندر، وإذا ما لقى، يحط 0)
    # ====================================================
    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    except:
        OWNER_ID = 0
        
    # السودو (اختياري)
    try:
        SUDO_USERS: Set[int] = set(map(int, os.environ.get("SUDO_USERS", "").split()))
    except:
        SUDO_USERS = set()
    
    # ====================================================
    # 3. التحكم (مثبت على النقطة للأمان)
    # ====================================================
    COMMAND_HAND_LER = os.environ.get("COMMAND_HAND_LER", ".")
    SUDO_COMMAND_HAND_LER = os.environ.get("SUDO_COMMAND_HAND_LER", ".")
    
    # ====================================================
    # 4. المجموعات (من ريندر)
    # ====================================================
    PRIVATE_GROUP_BOT_API_ID = int(os.environ.get("PRIVATE_GROUP_BOT_API_ID") or 0)
    PRIVATE_GROUP_ID = int(os.environ.get("PRIVATE_GROUP_ID") or 0)
    PM_LOGGER_GROUP_ID = int(os.environ.get("PM_LOGGER_GROUP_ID") or 0)
    FBAN_GROUP_ID = int(os.environ.get("FBAN_GROUP_ID") or 0)
    
    # ====================================================
    # 5. التخصيص (الاسم والصور)
    # ====================================================
    ALIVE_NAME = os.environ.get("ALIVE_NAME", "ZThon User")
    ALIVE_PIC = os.environ.get("ALIVE_PIC", None)
    BOT_PIC = os.environ.get("BOT_PIC", None)
    # ... (باقي المتغيرات الجمالية تسحب من ريندر)
    
    # ====================================================
    # 6. إعدادات النظام (افتراضية آمنة)
    # ====================================================
    TMP_DOWNLOAD_DIRECTORY = "downloads"
    TEMP_DIR = "./temp/"
    if not os.path.exists(TMP_DOWNLOAD_DIRECTORY):
        try:
            os.makedirs(TMP_DOWNLOAD_DIRECTORY)
        except:
            pass

    # APIs (نسحبها لو موجودة)
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", "https://github.com/ZThon-Bot/ZTele")
    
    # باقي المتغيرات كما هي (None افتراضياً)
    SCREEN_SHOT_LAYER_ACCESS_KEY = None
    # ... (كمل الباقي None عشان ما يطول الكود عليك)
    
    # ثوابت النظام
    MAX_MESSAGE_SIZE_LIMIT = 4095
    LOAD = []
    NO_LOAD = []
    ANTI_FLOOD_WARN_MODE = ChatBannedRights(until_date=None, view_messages=None, send_messages=True)
    CHROME_BIN = "/app/.apt/usr/bin/google-chrome"
    CHROME_DRIVER = "/app/.chromedriver/bin/chromedriver"
    GROUP_REG_SED_EX_BOT_S = r"(regex|moku|BananaButler_|rgx|l4mR)bot"
    COUNTRY = ""
    TZ_NUMBER = 1
    UPSTREAM_REPO_BRANCH = "master"
    ZEDUBLOGO = None
    BOTLOG = False
    BOTLOG_CHATID = 0
    EXTERNAL_REPO = None
    EXTERNAL_REPOBRANCH = "main"
    OLDZED_REPO = "https://github.com/ZThon-Bot/ZTele"
    OLDZED_REPOBRANCH = "oldzed"
    VC_REPO = "https://github.com/Zed-Thon/ZVCPlayer"
    VC_REPOBRANCH = "zvcplayer"
    VCMODE = False
    VC_SESSION = None
    OLDZED = False

class Production(Config):
    LOGGER = False

class Development(Config):
    LOGGER = True