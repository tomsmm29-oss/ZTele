import os
from typing import Set
from telethon.tl.types import ChatBannedRights

class Config(object):
    LOGGER = True
    
    # ====================================================
    # 1. الثوابت الأساسية (لازم تتأكد منها في ريندر)
    # ====================================================
    # جلب التوكن والآيديات، وإذا ما لقاها يحط بدالها None
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN") or None
    APP_ID = int(os.environ.get("APP_ID", 6))
    API_HASH = os.environ.get("API_HASH") or None
    
    # قاعدة البيانات (دعمنا الاسمين عشان ما نضيع)
    DB_URI = os.environ.get("DATABASE_URL", None) or os.environ.get("DB_URI", None)
    
    # الجلسة
    STRING_SESSION = os.environ.get("STRING_SESSION", None)
    
    # ====================================================
    # 2. الهوية والصلاحيات (الحقن المباشر)
    # ====================================================
    # هنا نحط الآيدي حقك، إذا ما لقاه في ريندر يحط 0 (بس الأفضل تحطه في ريندر)
    try:
        OWNER_ID = int(os.environ.get("OWNER_ID", 8241311871))
    except:
        OWNER_ID = 8241311871 
        
    # المطورين المساعدين (سودو)
    SUDO_USERS: Set[int] = set(8241311871)
    
    # الاسم
    ALIVE_NAME = os.environ.get("ALIVE_NAME", "ZThon User")
    
    # ====================================================
    # 3. مفاتيح التحكم (الحل الجذري للنقطة)
    # ====================================================
    # هنا ثبتنا النقطة غصب، حتى لو ما حطيتها في ريندر
    COMMAND_HAND_LER = os.environ.get("COMMAND_HAND_LER", ".")
    SUDO_COMMAND_HAND_LER = os.environ.get("SUDO_COMMAND_HAND_LER", ".")
    
    # ====================================================
    # 4. المجموعات والقنوات (مانع الانهيار)
    # ====================================================
    # نعرفها كلها كـ 0 عشان لو الكود طلبها يلقى رقم وما يضرب
    PRIVATE_GROUP_BOT_API_ID = int(os.environ.get("PRIVATE_GROUP_BOT_API_ID") or 0)
    PRIVATE_GROUP_ID = int(os.environ.get("PRIVATE_GROUP_ID") or 0)
    PM_LOGGER_GROUP_ID = int(os.environ.get("PM_LOGGER_GROUP_ID") or os.environ.get("PM_LOGGR_BOT_API_ID") or 0)
    FBAN_GROUP_ID = int(os.environ.get("FBAN_GROUP_ID") or 0)
    PRIVATE_CHANNEL_BOT_API_ID = int(os.environ.get("PRIVATE_CHANNEL_BOT_API_ID") or 0)
    PLUGIN_CHANNEL = int(os.environ.get("PLUGIN_CHANNEL") or 0)
    
    # ====================================================
    # 5. متغيرات زدثون الخاصة (عشان ما يصيح)
    # ====================================================
    ZELZAL_Z = int(1338009605)
    ZELZAL_A = int(os.environ.get("ZELZAL_A") or -1001338009605)
    ZI_FN = os.environ.get("ZI_FN", "𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟬")
    
    # صور وروابط (حطينا افتراضي عشان ما يطلع NoneType error)
    ALIVE_PIC = os.environ.get("ALIVE_PIC", None)
    BOT_PIC = os.environ.get("BOT_PIC", None)
    DIGITAL_PIC = os.environ.get("DIGITAL_PIC", None)
    DEFAULT_PIC = os.environ.get("DEFAULT_PIC", None)
    PMPERMIT_PIC = os.environ.get("PMPERMIT_PIC", None)
    THUMB_IMAGE = os.environ.get("THUMB_IMAGE", "https://telegra.ph/file/c91c09fb188f0f281e628.jpg")
    
    # نصوص
    CUSTOM_ALIVE_TEXT = os.environ.get("CUSTOM_ALIVE_TEXT", None)
    CUSTOM_ALIVE_EMOJI = os.environ.get("CUSTOM_ALIVE_EMOJI", None)
    CUSTOM_PMPERMIT_TEXT = os.environ.get("CUSTOM_PMPERMIT_TEXT", None)
    DEFAULT_BIO = os.environ.get("DEFAULT_BIO", None)
    DEFAULT_NAME = os.environ.get("DEFAULT_NAME", None)
    
    # ====================================================
    # 6. المجلدات والنظام (شبكة الأمان)
    # ====================================================
    TMP_DOWNLOAD_DIRECTORY = os.environ.get("TMP_DOWNLOAD_DIRECTORY", "downloads")
    TEMP_DIR = os.environ.get("TEMP_DIR", "./temp/")
    
    # نتأكد إن المجلدات موجودة
    if not os.path.exists(TMP_DOWNLOAD_DIRECTORY):
        try:
            os.makedirs(TMP_DOWNLOAD_DIRECTORY)
        except:
            pass

    # ====================================================
    # 7. مقبرة الـ APIs (كل شي None عشان السكوت)
    # ====================================================
    HEROKU_API_KEY = os.environ.get("HEROKU_API_KEY", None)
    HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME", None)
    UPSTREAM_REPO = os.environ.get("UPSTREAM_REPO", "https://github.com/ZThon-Bot/ZTele")
    
    # قائمة الـ "ما عندنا"
    SCREEN_SHOT_LAYER_ACCESS_KEY = None
    OPEN_WEATHER_MAP_APPID = None
    IBM_WATSON_CRED_URL = None
    IBM_WATSON_CRED_PASSWORD = None
    IPDATA_API = None
    OCR_SPACE_API_KEY = None
    GENIUS_API_TOKEN = None
    REM_BG_API_KEY = None
    CURRENCY_API = None
    G_DRIVE_CLIENT_ID = None
    G_DRIVE_CLIENT_SECRET = None
    G_DRIVE_FOLDER_ID = None
    G_DRIVE_DATA = None
    G_DRIVE_INDEX_LINK = None
    TG_2STEP_VERIFICATION_CODE = None
    WATCH_COUNTRY = "IQ"
    BIO_PREFIX = None
    LASTFM_API = None
    LASTFM_SECRET = None
    LASTFM_USERNAME = None
    LASTFM_PASSWORD_PLAIN = None
    SPOTIFY_CLIENT_ID = None
    SPOTIFY_CLIENT_SECRET = None
    SPAMWATCH_API = None
    RANDOM_STUFF_API_KEY = None
    GITHUB_ACCESS_TOKEN = None
    GIT_REPO_NAME = None
    DEEP_AI = None
    
    # ====================================================
    # 8. إعدادات النظام الداخلية (لا تلمسها)
    # ====================================================
    MAX_MESSAGE_SIZE_LIMIT = 4095
    LOAD = []
    NO_LOAD = []
    ANTI_FLOOD_WARN_MODE = ChatBannedRights(until_date=None, view_messages=None, send_messages=True)
    CHROME_BIN = os.environ.get("CHROME_BIN", "/app/.apt/usr/bin/google-chrome")
    CHROME_DRIVER = os.environ.get("CHROME_DRIVER", "/app/.chromedriver/bin/chromedriver")
    GROUP_REG_SED_EX_BOT_S = os.environ.get("GROUP_REG_SED_EX_BOT_S", r"(regex|moku|BananaButler_|rgx|l4mR)bot")
    COUNTRY = str(os.environ.get("COUNTRY", ""))
    TZ_NUMBER = int(os.environ.get("TZ_NUMBER", 1))
    UPSTREAM_REPO_BRANCH = os.environ.get("UPSTREAM_REPO_BRANCH", "master")
    ZEDUBLOGO = None
    BOTLOG = False
    BOTLOG_CHATID = 0
    
    # مستودعات خارجية
    EXTERNAL_REPO = os.environ.get("EXTERNAL_REPO", None)
    EXTERNAL_REPOBRANCH = os.environ.get("EXTERNAL_REPOBRANCH", "main")
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