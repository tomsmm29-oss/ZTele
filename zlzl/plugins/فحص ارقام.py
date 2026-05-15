"""
╔══════════════════════════════════╗
║   🔍 سكريبت الفحص الشامل        ║
║   متوافق مع سورس زدثون يوزربوت   ║
╚══════════════════════════════════╝

الأوامر:
  .جرب              - فحص أرقام بالرد على رسالة
  .رفحص +الرقم N    - فحص رقم بحساب محدد
  .رفحص الكل +الرقم  - فحص رقم بكل الحسابات
  .اضافه حساب        - إضافة حساب (سيشن / ملف / رقم)
  .الحسابات          - عرض الحسابات
  .حذف حساب N       - حذف حساب برقمه
  .عرض المميز        - عرض المميزة
  .عرض القديمه       - عرض القديمة
  .عرض الكل          - عرض كل المسجلة
  .مسح               - حذف جهات الاتصال المستوردة
"""

import asyncio
import json
import os
import re
import time

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    FloodWaitError, SessionPasswordNeededError,
    PhoneNumberInvalidError
)
from telethon.tl.functions.contacts import (
    ImportContactsRequest, DeleteContactsRequest
)
from telethon.tl.types import InputPhoneContact

from . import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..core.logger import logging

try:
    from ..sql_helper.globals import gvarstatus, addgvar, delgvar
except ImportError:
    def gvarstatus(v): return None
    def addgvar(k, v): pass
    def delgvar(k): pass

try:
    from ..Config import Config
    API_ID = getattr(Config, 'APP_ID', None) or getattr(Config, 'api_id', None) or 28797361
    API_HASH = getattr(Config, 'API_HASH', None) or getattr(Config, 'api_hash', None) or '771041b32e83ab232e066b7adeee700b'
except ImportError:
    API_ID = 28797361
    API_HASH = '771041b32e83ab232e066b7adeee700b'

plugin_category = "العروض"
LOGS = logging.getLogger(__name__)

OLD_ID_THRESHOLD = 6000000000
BATCH_SIZE = 50

# ═══════════════════════════════
# حالة عامة
# ═══════════════════════════════
ACCOUNT_CLIENTS = {}   # {رقم: TelegramClient}
IMPORTED_IDS = []
CHECK_RESULTS = {}


# ═══════════════════════════════
# إدارة تخزين الحسابات
# ═══════════════════════════════
def get_accounts_data():
    """قراءة بيانات الحسابات من قاعدة البيانات"""
    raw = gvarstatus("ZED_ACCOUNTS") or ""
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except:
        return {}


def save_accounts_data(data):
    """حفظ بيانات الحسابات في قاعدة البيانات"""
    addgvar("ZED_ACCOUNTS", json.dumps(data, ensure_ascii=False))


def get_next_num():
    """الحصول على رقم الحساب التالي المتاح"""
    data = get_accounts_data()
    if not data:
        return 2
    nums = [int(k) for k in data.keys() if k.isdigit()]
    return max(nums) + 1 if nums else 2


# ═══════════════════════════════
# إدارة العملاء (Clients)
# ═══════════════════════════════
async def init_client(num, session_str):
    """تهيئة عميل من سيشن وتخزينه"""
    try:
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()
        me = await client.get_me()
        if me:
            ACCOUNT_CLIENTS[num] = client
            # تحديث الاسم والرقم في التخزين
            data = get_accounts_data()
            if str(num) in data:
                data[str(num)]['name'] = me.first_name or ''
                data[str(num)]['phone'] = me.phone or ''
                save_accounts_data(data)
            return me
        else:
            await client.disconnect()
            return None
    except Exception as e:
        LOGS.error(f"فشل تهيئة الحساب {num}: {e}")
        return None


async def load_all_accounts():
    """تحميل كل الحسابات المحفوظة"""
    data = get_accounts_data()
    for num_str, info in data.items():
        num = int(num_str)
        if num not in ACCOUNT_CLIENTS:
            me = await init_client(num, info.get('session', ''))
            if me:
                LOGS.info(f"✅ حساب #{num}: {me.first_name}")


def get_client(num):
    """الحصول على عميل برقم الحساب"""
    if num == 1:
        return zedub
    return ACCOUNT_CLIENTS.get(num)


async def get_all_clients():
    """الحصول على كل العملاء المتاحين مع أرقامهم"""
    await load_all_accounts()
    result = [(1, zedub)]
    for num in list(ACCOUNT_CLIENTS.keys()):
        client = ACCOUNT_CLIENTS[num]
        try:
            if not client.is_connected():
                await client.connect()
            me = await client.get_me()
            if me:
                result.append((num, client))
            else:
                ACCOUNT_CLIENTS.pop(num, None)
        except:
            ACCOUNT_CLIENTS.pop(num, None)
    return result


# ═══════════════════════════════
# فحص الرقم (طريقة واحدة سريعة)
# ═══════════════════════════════
async def check_phone(client, phone):
    """فحص رقم واحد - استيراد جهة اتصال ومعرفة الصاحب"""
    try:
        contacts = [InputPhoneContact(
            client_id=0, phone=phone,
            first_name='Z', last_name='C'
        )]
        result = await client(ImportContactsRequest(contacts))
        if result.users:
            user = result.users[0]
            IMPORTED_IDS.append(user.id)
            return {
                'found': True,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'username': user.username or 'لا يوجد',
                'id': user.id,
                'premium': getattr(user, 'premium', False),
                'old': user.id < OLD_ID_THRESHOLD,
                'verified': getattr(user, 'verified', False),
                'restricted': getattr(user, 'restricted', False),
                'bot': getattr(user, 'bot', False),
            }
        return {'found': False}
    except FloodWaitError as e:
        return {'found': False, 'error': f'حـظـر {e.seconds}s'}
    except Exception as e:
        err = str(e)
        if 'BANNED' in err.upper():
            return {'found': False, 'error': 'حـسـاب مـحـظـور مـن الـمـتـجـر'}
        return {'found': False, 'error': err[:50]}


# ═══════════════════════════════
# دوال مساعدة
# ═══════════════════════════════
def normalize_phone(phone):
    return phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')


def extract_phones(text):
    pattern = r'\+\d{7,15}'
    return list(dict.fromkeys(re.findall(pattern, text)))


def get_country(phone):
    codes = {
        '964': '🇮🇶 الـعـراق', '966': '🇸🇦 الـسـعـوديـة', '971': '🇦🇪 الـإمـارات',
        '965': '🇰🇼 الـكـويـت', '974': '🇶🇦 قـطـر', '968': '🇴🇲 عـمـان',
        '973': '🇧🇭 الـبـحـريـن', '20': '🇪🇬 مـصـر', '212': '🇲🇦 الـمـغـرب',
        '213': '🇩🇿 الـجـزائـر', '216': '🇹🇳 تـونـس', '218': '🇱🇾 لـيـبـيـا',
        '249': '🇸🇩 الـسـودان', '967': '🇾🇪 الـيـمـن', '962': '🇯🇴 الأردن',
        '961': '🇱🇧 لـبـنـان', '963': '🇸🇾 سـوريـا', '970': '🇵🇸 فـلسـطيـن',
        '90': '🇹🇷 تـركـيـا', '44': '🇬🇧 بـريـطـانـيـا', '1': '🇺🇸 أمـريـكـا',
        '49': '🇩🇪 ألـمـانـيـا', '33': '🇫🇷 فـرنـسـا', '7': '🇷🇺روسـيـا',
        '86': '🇨🇳 الـصيـن', '91': '🇮🇳 الـهـنـد', '55': '🇧🇷 الـبـرازيـل',
        '234': '🇳🇬 نـيـجـيـريـا', '254': '🇰🇪 كـيـنـيـا', '62': '🇮🇩 إندونيسيا',
        '81': '🇯🇵 الـيـابـان', '82': '🇰🇷 كـوريـا', '39': '🇮🇹 إيـطـالـيـا',
        '34': '🇪🇸 أسـبـانـيـا', '46': '🇸🇪 الـسـويـد', '31': '🇳🇱 هـولـنـدا',
    }
    clean = phone.replace('+', '')
    for code, name in sorted(codes.items(), key=lambda x: -len(x[0])):
        if clean.startswith(code):
            return name
    return '🌍 غـيـر مـعـروف'


def progress_bar(current, total, width=15):
    if total == 0:
        return "[███████████████] 100%"
    pct = int((current / total) * 100)
    filled = int((current / total) * width)
    return f"[{'█' * filled}{'░' * (width - filled)}] {pct}%"


async def save_new_account(session_str, me):
    """حفظ حساب جديد وإرجاع رقمه"""
    num = get_next_num()
    data = get_accounts_data()
    data[str(num)] = {
        'session': session_str,
        'name': me.first_name or '',
        'phone': me.phone or ''
    }
    save_accounts_data(data)
    return num


# ═══════════════════════════════
# إضافة حساب
# ═══════════════════════════════
@zedub.zed_cmd(pattern=r"^[.,]اضافه حساب$")
async def add_account(event):
    """إضافة حساب: سيشن نصي / ملف .session / رقم وكود"""
    await load_all_accounts()

    zed = await edit_or_reply(event,
        "**📱┊إضـافـة حـسـاب جـديـد - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        "**⎉╎أرسـل الآن أحـد الـخـيـارات:**\n\n"
        "**1️⃣ سيـشـن نـصـي (StringSession)**\n"
        "**2️⃣ مـلـف .session (أرسـل الـمـلـف)**\n"
        "**3️⃣ رقـم هـاتـف + كـود تـحـقـق**\n\n"
        "**⎉╎لـلإلـغـاء أرسـل** `.الغاء`\n\n"
        "**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )

    try:
        async with event.client.conversation(event.chat_id, timeout=180) as conv:
            response = await conv.get_response()
            text = (response.text or '').strip()

            # ── إلغاء ──
            if text.startswith('.'):
                return await event.reply("**⎉╎تـم الإلـغـاء ❌**")

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # خيار 2: ملف .session
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            if response.media and hasattr(response.media, 'document'):
                file_path = None
                try:
                    file_path = await event.client.download_media(
                        response, f'temp_session_{int(time.time())}.session'
                    )
                    if not file_path:
                        return await event.reply("**⎉╎فـشـل تـنـزيـل الـمـلـف ❌**")

                    new_client = TelegramClient(file_path, API_ID, API_HASH)
                    await new_client.connect()
                    me = await new_client.get_me()

                    if not me:
                        await new_client.disconnect()
                        return await event.reply("**⎉╎مـلـف الـسـيـشـن غـيـر مـعـروف أو مـنـتـهـي ❌**")

                    # تحويل إلى StringSession
                    session_str = StringSession(new_client.session).save()
                    num = await save_new_account(session_str, me)
                    ACCOUNT_CLIENTS[num] = new_client

                    await event.reply(
                        f"**✅┊تـمـت إضـافـة الـحـسـاب بـنـجـاح! - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
                        f"**⎉╎الـحـسـاب:** #{num}\n"
                        f"**⎉╎الاسـم:** {me.first_name}\n"
                        f"**⎉╎الـهـاتـف:** `{me.phone}`\n\n"
                        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
                    )
                    return

                except Exception as e:
                    LOGS.error(f"خطأ ملف السيشن: {e}")
                    return await event.reply(f"**⎉╎خـطـأ فـي الـمـلـف:** `{str(e)[:80]}`")
                finally:
                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # خيار 1: سيشن نصي
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            if len(text) > 50:
                try:
                    new_client = TelegramClient(StringSession(text), API_ID, API_HASH)
                    await new_client.connect()
                    me = await new_client.get_me()

                    if not me:
                        await new_client.disconnect()
                        return await event.reply("**⎉╎الـسـيـشـن غـيـر صـالـح أو مـنـتـهـيـة ❌**")

                    session_str = new_client.session.save()
                    num = await save_new_account(session_str, me)
                    ACCOUNT_CLIENTS[num] = new_client

                    await event.reply(
                        f"**✅┊تـمـت إضـافـة الـحـسـاب بـنـجـاح! - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
                        f"**⎉╎الـحـسـاب:** #{num}\n"
                        f"**⎉╎الاسـم:** {me.first_name}\n"
                        f"**⎉╎الـهـاتـف:** `{me.phone}`\n\n"
                        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
                    )
                    return

                except Exception as e:
                    LOGS.error(f"خطأ سيشن نصي: {e}")
                    # إذا السيشن غلط يمكن يكون رقم هاتف طويل
                    if not text.startswith('+'):
                        return await event.reply(
                            f"**⎉╎خـطـأ فـي الـسـيـشـن:** `{str(e)[:80]}`\n\n"
                            f"**⎉╎تـأكـد أنـه StringSession صـح ❌**"
                        )

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # خيار 3: رقم هاتف + كود
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            phone = text.strip()
            if not phone.startswith('+'):
                return await event.reply("**⎉╎الـرسـالـة لـيـسـت سيـشـن أو رقـم هـاتـف (يـبـدأ بـ +) ❌**")

            new_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await new_client.connect()

            try:
                await new_client.send_code_request(phone)
            except Exception as e:
                await new_client.disconnect()
                return await event.reply(f"**⎉╎خـطـأ بإرسـال الـكـود:** `{e}`")

            await event.reply("**📧┊أرسـل كـود الـتـحـقـق الآن:**")

            code_resp = await conv.get_response()
            code = (code_resp.text or '').strip()

            if code.startswith('.'):
                await new_client.disconnect()
                return await event.reply("**⎉╎تـم الإلـغـاء ❌**")

            try:
                await new_client.sign_in(phone, code)
            except SessionPasswordNeededError:
                await event.reply("**🔐┊أرسـل كـلـمـة الـمـرور الـثـنـائـيـة:**")

                pwd_resp = await conv.get_response()
                pwd = (pwd_resp.text or '').strip()

                if pwd.startswith('.'):
                    await new_client.disconnect()
                    return await event.reply("**⎉╎تـم الإلـغـاء ❌**")

                try:
                    await new_client.sign_in(password=pwd)
                except Exception as e:
                    await new_client.disconnect()
                    return await event.reply(f"**⎉╎خـطـأ بـكـلـمـة الـمـرور:** `{e}`")

            except Exception as e:
                await new_client.disconnect()
                return await event.reply(f"**⎉╎خـطـأ بـتـسـجـيـل الـدخـول:** `{e}`")

            # حفظ الحساب
            me = await new_client.get_me()
            session_str = new_client.session.save()
            num = await save_new_account(session_str, me)
            ACCOUNT_CLIENTS[num] = new_client

            await event.reply(
                f"**✅┊تـمـت إضـافـة الـحـسـاب بـنـجـاح! - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
                f"**⎉╎الـحـسـاب:** #{num}\n"
                f"**⎉╎الاسـم:** {me.first_name}\n"
                f"**⎉╎الـهـاتـف:** `{me.phone}`\n\n"
                f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
            )

    except asyncio.TimeoutError:
        await event.reply("**⎉╎انـتـهـت مـهـلـة الإضـافـة (180 ثـانـيـة) ⏰**")
    except Exception as e:
        LOGS.error(f"خطأ إضافة حساب: {e}")
        await event.reply(f"**⎉╎خـطـأ:** `{str(e)[:100]}`")


# ═══════════════════════════════
# عرض الحسابات
# ═══════════════════════════════
@zedub.zed_cmd(pattern=r"^[.,]الحسابات$")
async def list_accounts(event):
    await load_all_accounts()

    me = await zedub.get_me()
    text = (
        f"**👥┊حـسـابـات الـفـحـص - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**1 • 👤 {me.first_name} | 📱 `{me.phone}` | ✅ رئـيـسـي**\n"
    )

    data = get_accounts_data()
    if data:
        for num_str in sorted(data.keys(), key=lambda x: int(x)):
            info = data[num_str]
            num = int(num_str)
            client = ACCOUNT_CLIENTS.get(num)
            if client:
                try:
                    connected = client.is_connected()
                except:
                    connected = False
                status = '✅' if connected else '❌'
            else:
                status = '❌'
            name = info.get('name', 'غـيـر مـعـروف')
            phone = info.get('phone', 'غـيـر مـعـروف')
            text += f"**{num} • 👤 {name} | 📱 `{phone}` | {status}**\n"
    else:
        text += "\n**💡 أضـف حـسـاب بـ** `.اضافه حساب`"

    total = 1 + len(data)
    text += f"\n**{'━' * 25}**\n**⎉╎الـمـجـمـوع:** {total} حـسـاب\n\n**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    await edit_or_reply(event, text)


# ═══════════════════════════════
# حذف حساب
# ═══════════════════════════════
@zedub.zed_cmd(pattern=r"^[.,]حذف حساب(?:\s+(\d+))?$")
async def remove_account(event):
    await load_all_accounts()
    data = get_accounts_data()
    index = event.pattern_match.group(1)

    # بدون رقم = عرض القائمة
    if not index:
        me = await zedub.get_me()
        text = (
            "**👥┊أرسـل رقـم الـحـسـاب لـلـحـذف:**\n\n"
            f"**1 • 👤 {me.first_name} | 📱 `{me.phone}` | رئـيـسـي (لا يُحذف)**\n"
        )
        if data:
            for num_str in sorted(data.keys(), key=lambda x: int(x)):
                info = data[num_str]
                text += f"**{num_str} • 👤 {info.get('name', '')} | 📱 `{info.get('phone', '')}`**\n"
        text += "\n**⎉╎مـثـال:** `.حذف حساب 2`"
        return await edit_or_reply(event, text)

    num = int(index)

    # لا يمكن حذف الرئيسي
    if num == 1:
        return await edit_delete(event, "**⎉╎لا يـمـكـن حـذف الـحـسـاب الـرئـيـسـي ❌**", 8)

    # الحساب غير موجود
    if str(num) not in data:
        return await edit_delete(event, f"**⎉╎الـحـسـاب رقـم {num} غـيـر مـوجـود ❌**", 8)

    # قطع الاتصال
    client = ACCOUNT_CLIENTS.pop(num, None)
    if client:
        try:
            await client.disconnect()
        except:
            pass

    # حذف من التخزين
    del data[str(num)]
    save_accounts_data(data)

    await edit_or_reply(event,
        f"**✅┊تـم حـذف الـحـسـاب رقـم {num}**\n"
        f"**⎉╎الـمـتـبـقـي:** {1 + len(data)} حـسـاب\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )


# ═══════════════════════════════
# .رفحص +الرقم رقم_الحساب
# ═══════════════════════════════
@zedub.zed_cmd(pattern=r"^[.,]رفحص\s+\+\d{7,15}\s+\d+$")
async def rfahs_single(event):
    """فحص رقم بحساب محدد"""
    text = event.text.strip()

    # استخراج الرقم
    phone_match = re.search(r'\+\d{7,15}', text)
    if not phone_match:
        return await edit_delete(event, "**⎉╎لـم أجـد رقـم صـحـيـح ❌**", 8)
    phone = phone_match.group(0)

    # استخراج رقم الحساب (آخر رقم بالرسالة)
    parts = text.split()
    account_num = int(parts[-1])

    await load_all_accounts()

    client = get_client(account_num)
    if not client:
        return await edit_delete(event, f"**⎉╎الـحـسـاب رقـم {account_num} غـيـر مـوجـود ❌**\n\n**⎉╎أرسـل** `.الحسابات` **لـلـعـرض**", 12)

    country = get_country(phone)

    zed = await edit_or_reply(event,
        f"**🔍┊رفـحـص الـرقـم - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**⎉╎الـرقـم:** `{phone}`\n"
        f"**⎉╎الـدولـة:** {country}\n"
        f"**⎉╎بـواسـطـة الـحـسـاب:** #{account_num}\n"
        f"**⎉╎جـاري الـفـحـص ...**\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )

    result = await check_phone(client, phone)

    if result.get('found'):
        info = result
        badges = ''
        if info.get('premium'):  badges += ' ⭐'
        if info.get('old'):      badges += ' 📅'
        if info.get('verified'): badges += ' ✔️'

        await zed.edit(
            f"**🔍┊نـتـيـجـة الـرفـحـص - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
            f"**📱┊الـرقـم:** `{phone}`{badges}\n"
            f"**🌍┊الـدولـة:** {country}\n"
            f"**👥┊بـواسـطـة:** #{account_num}\n\n"
            f"**{'━' * 25}**\n\n"
            f"**✅┊الـرقـم مـسـجـل ومـفـعـل**\n\n"
            f"**👤┊الاسـم:** {info['first_name']} {info['last_name']}\n"
            f"**🆔┊الـمـعـرف:** @{info['username']}\n"
            f"**🔢┊الايـدي:** `{info['id']}`\n"
            f"**⭐┊مـمـيـز:** {'✅' if info.get('premium') else '❌'}\n"
            f"**📅┊قـديـم:** {'✅' if info.get('old') else '❌'}\n\n"
            f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
        )
    else:
        error_msg = result.get('error', '')
        err_text = f"\n**⚠️┊الـسـبـب:** {error_msg}" if error_msg else ""

        await zed.edit(
            f"**🔍┊نـتـيـجـة الـرفـحـص - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
            f"**📱┊الـرقـم:** `{phone}`\n"
            f"**🌍┊الـدولـة:** {country}\n"
            f"**👥┊بـواسـطـة:** #{account_num}\n\n"
            f"**{'━' * 25}**\n\n"
            f"**❌┊الـرقـم غـيـر مـسـجـل أو مـعـطـل**\n"
            f"**💡┊يـمـكـنـك حـذفـه مـن الـقـائـمـة**{err_text}\n\n"
            f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
        )


# ═══════════════════════════════
# .رفحص الكل +الرقم
# ═══════════════════════════════
@zedub.zed_cmd(pattern=r"^[.,]رفحص\s+الكل\s+\+\d{7,15}$")
async def rfahs_all(event):
    """فحص رقم بكل الحسابات"""
    text = event.text.strip()

    phone_match = re.search(r'\+\d{7,15}', text)
    if not phone_match:
        return await edit_delete(event, "**⎉╎لـم أجـد رقـم صـحـيـح ❌**", 8)
    phone = phone_match.group(0)

    country = get_country(phone)
    clients_with_nums = await get_all_clients()
    total_clients = len(clients_with_nums)

    zed = await edit_or_reply(event,
        f"**🔍┊رفـحـص الـرقـم بـجـمـيـع الـحـسـابـات - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**⎉╎الـرقـم:** `{phone}`\n"
        f"**⎉╎الـدولـة:** {country}\n"
        f"**⎉╎عـدد الـحـسـابـات:** {total_clients}\n"
        f"**⎉╎جـاري الـفـحـص ...**\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )

    results_text = ""
    found_count = 0

    for num, client in clients_with_nums:
        result = await check_phone(client, phone)

        if result.get('found'):
            found_count += 1
            info = result
            badges = ''
            if info.get('premium'):  badges += ' ⭐'
            if info.get('old'):      badges += ' 📅'
            if info.get('verified'): badges += ' ✔️'

            results_text += (
                f"\n**{num} • ✅ مـسـجـل ومـفـعـل**{badges}\n"
                f"   **⎉╎الاسـم:** {info['first_name']} {info['last_name']}\n"
                f"   **⎉╎الـمـعـرف:** @{info['username']}\n"
                f"   **⎉╎الايـدي:** `{info['id']}`\n"
            )
        else:
            error_msg = result.get('error', '')
            err_text = f" ({error_msg})" if error_msg else ""
            results_text += f"\n**{num} • ❌ غـيـر مـسـجـل أو مـعـطـل**{err_text}\n"

        await asyncio.sleep(0.5)

    # النتيجة النهائية
    if found_count == total_clients:
        final = f"**✅┊الـرقـم مـسـجـل ومـفـعـل (تـأكـد {found_count}/{total_clients})**"
    elif found_count > 0:
        final = f"**⚠️┊الـرقـم مـسـجـل لـكـن بـعـض الـحـسـابـات لـم تـجـده ({found_count}/{total_clients})**"
    else:
        final = f"**❌┊الـرقـم مـعـطـل أو غـيـر مـسـجـل بـتـاتـاً (0/{total_clients})**\n**💡┊يـمـكـنـك حـذفـه مـن الـقـائـمـة**"

    await zed.edit(
        f"**🔍┊نـتـيـجـة الـرفـحـص - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**📱┊الـرقـم:** `{phone}`\n"
        f"**🌍┊الـدولـة:** {country}\n\n"
        f"**{'━' * 25}**\n"
        f"{results_text}\n"
        f"**{'━' * 25}**\n\n"
        f"{final}\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )


# ═══════════════════════════════
# .جرب - فحص شامل بالرد
# ═══════════════════════════════
@zedub.zed_cmd(pattern=r"^[.,]جرب$")
async def handle_check(event):
    global CHECK_RESULTS, IMPORTED_IDS
    CHECK_RESULTS = {}
    IMPORTED_IDS = []

    if not event.reply_to_msg_id:
        return await edit_delete(event,
            "**⎉╎أرسـل `.جرب` بـالـرد عـلى رسـالـة فـيـهـا أرقـام**", 10
        )

    reply_msg = await event.get_reply_message()
    phones = extract_phones(reply_msg.text or '')

    if not phones:
        return await edit_delete(event,
            "**⎉╎لـم يـتـم الـعـثـور عـلى أرقـام تـبـدأ بـ + ❌**", 10
        )

    clients_with_nums = await get_all_clients()
    total = len(phones)

    zed = await edit_or_reply(event,
        f"**🔍┊فـحـص الـرقـام - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"`{progress_bar(0, total)}`\n"
        f"**⎉╎0/{total} | 👥 {len(clients_with_nums)} حـسـاب | ⏳ جـاري ...**\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )

    lock = asyncio.Lock()
    checked = [0]
    last_update = [0.0]

    async def process_batch(client, phone_batch, client_num):
        for i in range(0, len(phone_batch), BATCH_SIZE):
            batch = phone_batch[i:i + BATCH_SIZE]

            contacts = [
                InputPhoneContact(
                    client_id=j, phone=ph,
                    first_name=f'Z{j}', last_name=f'C{client_num}'
                )
                for j, ph in enumerate(batch)
            ]

            try:
                result = await client(ImportContactsRequest(contacts))
                if result and result.users:
                    for user in result.users:
                        IMPORTED_IDS.append(user.id)
                        user_phone_clean = normalize_phone(
                            user.phone if user.phone.startswith('+') else '+' + user.phone
                        )
                        matched = None
                        for p in batch:
                            if normalize_phone(p) == user_phone_clean:
                                matched = p
                                break
                        if not matched:
                            continue

                        async with lock:
                            CHECK_RESULTS[matched] = {
                                'phone': matched,
                                'country': get_country(matched),
                                'user_id': user.id,
                                'first_name': user.first_name or '',
                                'last_name': user.last_name or '',
                                'username': user.username or 'لا يوجد',
                                'premium': getattr(user, 'premium', False),
                                'old': user.id < OLD_ID_THRESHOLD,
                                'registered': True
                            }
            except FloodWaitError as e:
                LOGS.warning(f"FloodWait {e.seconds}s")
                await asyncio.sleep(min(e.seconds, 20))
            except Exception as e:
                LOGS.error(f"خطأ دفعة: {e}")

            async with lock:
                checked[0] += len(batch)

            now = time.time()
            if now - last_update[0] >= 1.5:
                last_update[0] = now
                try:
                    await zed.edit(
                        f"**🔍┊فـحـص الـرقـام - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
                        f"`{progress_bar(checked[0], total)}`\n"
                        f"**⎉╎{checked[0]}/{total} | ✅ {len(CHECK_RESULTS)} مـسـجـل | ⏳ جـاري ...**\n\n"
                        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
                    )
                except:
                    pass

            await asyncio.sleep(0.3)

    # توزيع العمل بالتوازي
    per_client = total // len(clients_with_nums)
    remainder = total % len(clients_with_nums)

    tasks = []
    idx = 0
    for ci, (num, cl) in enumerate(clients_with_nums):
        count = per_client + (1 if ci < remainder else 0)
        batch = phones[idx:idx + count]
        idx += count
        if batch:
            tasks.append(process_batch(cl, batch, num))

    await asyncio.gather(*tasks, return_exceptions=True)

    # الأرقام غير المسجلة
    for ph in phones:
        if ph not in CHECK_RESULTS:
            CHECK_RESULTS[ph] = {
                'phone': ph,
                'country': get_country(ph),
                'registered': False,
                'premium': False,
                'old': False
            }

    # إحصائيات
    reg_count = sum(1 for v in CHECK_RESULTS.values() if v.get('registered'))
    not_reg = total - reg_count
    prem_count = sum(1 for v in CHECK_RESULTS.values() if v.get('premium'))
    old_count = sum(1 for v in CHECK_RESULTS.values() if v.get('old'))
    prem_old = sum(1 for v in CHECK_RESULTS.values()
                   if v.get('premium') and v.get('old'))

    countries = {}
    for v in CHECK_RESULTS.values():
        c = v.get('country', 'غير معروف')
        countries[c] = countries.get(c, 0) + 1
    countries_text = '\n'.join(
        [f"   **⎉╎{n}:** {cnt}"
         for n, cnt in sorted(countries.items(), key=lambda x: -x[1])]
    )

    text = (
        f"**🛂┊فـحـص الـرقـام - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**⎉╎إجـمـالـي الـرقـام:** {total}\n"
        f"**⎉╎مـسـجـلـة:** {reg_count} ✅\n"
        f"**⎉╎غـيـر مـسـجـلـة:** {not_reg} ❌\n"
        f"**⎉╎مـمـيـزة:** {prem_count} ⭐\n"
        f"**⎉╎قـديـمـة:** {old_count} 📅\n"
        f"**⎉╎مـمـيـز + قـديـم:** {prem_old} ⭐📅\n"
        f"**⎉╎حـسـابـات الـفـحـص:** {len(clients_with_nums)} 👥\n\n"
        f"**🌍┊الـدول:**\n"
        f"{countries_text}\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**\n\n"
        f"**📋┊الأوامـر:**\n"
        f"**⎉╎لـلـمـمـيـزة ⩥** `.عرض المميز`\n"
        f"**⎉╎لـلـقـديـمـة ⩥** `.عرض القديمه`\n"
        f"**⎉╎لـلـكـل ⩥** `.عرض الكل`\n"
        f"**⎉╎حـذف الـجـهـات ⩥** `.مسح`\n"
        f"**⎉╎رفـحـص رقـم ⩥** `.رفحص +الرقم رقـم_حـسـاب`\n"
        f"**⎉╎رفـحـص بـالـكـل ⩥** `.رفحص الكل +الرقم`"
    )

    await zed.edit(text)


# ═══════════════════════════════
# أوامر العرض
# ═══════════════════════════════
async def display_numbers(event, phones, title_emoji, title_text):
    if not phones:
        return await edit_delete(event, f"**⎉╎لا تـوجـد أرقـام {title_text} ❌**", 8)

    total = len(phones)
    zed = await edit_or_reply(event,
        f"**{title_emoji}┊جـاري عـرض {total} رقـم {title_text} ...**\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )

    text = ""
    msg_count = 0

    for i, ph in enumerate(phones):
        info = CHECK_RESULTS[ph]
        badges = ''
        if info.get('premium'): badges += ' ⭐'
        if info.get('old'):     badges += ' 📅'

        entry = (
            f"**{i+1} •** `{ph}`{badges}\n"
            f"   **⎉╎الاسـم:** {info.get('first_name', '')} {info.get('last_name', '')}\n"
            f"   **⎉╎الـمـعـرف:** @{info.get('username', 'لا يوجد')}\n"
            f"   **⎉╎الايـدي:** `{info.get('user_id', '')}`\n"
            f"   **⎉╎الـدولـة:** {info.get('country', '')}\n\n"
        )

        if len(text) + len(entry) > 3800:
            msg_count += 1
            try:
                await event.reply(
                    f"**{title_emoji}┊{title_text} - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉** [{msg_count}]\n\n"
                    f"{text}"
                    f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
                )
            except:
                pass
            text = entry
        else:
            text += entry

    if text.strip():
        msg_count += 1
        try:
            await event.reply(
                f"**{title_emoji}┊{title_text} - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉** [{msg_count}]\n\n"
                f"{text}"
                f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
            )
        except:
            pass

    try:
        await zed.edit(
            f"**✅┊تـم الـعـرض! {total} رقـم {title_text}**\n\n"
            f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
        )
    except:
        pass


@zedub.zed_cmd(pattern=r"^[.,]عرض المميز$")
async def show_premium(event):
    phones = [p for p, info in CHECK_RESULTS.items() if info.get('premium')]
    await display_numbers(event, phones, '⭐', 'مـمـيـزة')


@zedub.zed_cmd(pattern=r"^[.,]عرض القديمه$")
async def show_old(event):
    phones = [p for p, info in CHECK_RESULTS.items() if info.get('old')]
    await display_numbers(event, phones, '📅', 'قـديـمـة')


@zedub.zed_cmd(pattern=r"^[.,]عرض الكل$")
async def show_all(event):
    phones = [p for p, info in CHECK_RESULTS.items() if info.get('registered')]
    await display_numbers(event, phones, '📋', 'مـسـجـلـة')


# ═══════════════════════════════
# حذف جهات الاتصال المستوردة
# ═══════════════════════════════
@zedub.zed_cmd(pattern=r"^[.,]مسح$")
async def clear_contacts(event):
    if not IMPORTED_IDS:
        return await edit_delete(event,
            "**⎉╎لا تـوجـد جـهـات اتـصـال مـسـتـوردة ❌**", 8
        )

    deleted = 0
    all_clients = [zedub] + list(ACCOUNT_CLIENTS.values())

    for cl in all_clients:
        try:
            input_users = []
            for uid in IMPORTED_IDS:
                try:
                    inp = await cl.get_input_entity(uid)
                    input_users.append(inp)
                except:
                    pass

            if input_users:
                for i in range(0, len(input_users), 50):
                    batch = input_users[i:i + 50]
                    try:
                        await cl(DeleteContactsRequest(id=batch))
                        deleted += len(batch)
                    except:
                        pass
        except:
            pass

    IMPORTED_IDS.clear()
    await edit_or_reply(event,
        f"**🗑️┊تـم حـذف {deleted} جـهـة اتـصـال مـسـتـوردة ✅**\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )