"""
╔══════════════════════════════════╗
║   🔍 سكريبت الفحص الشامل        ║
║   متوافق مع سورس زدثون يوزربوت   ║
╚══════════════════════════════════╝

الأوامر:
  .جرب           - فحص الأرقام (بالرد على رسالة)
  .عرض المميز    - عرض الأرقام المميزة بـ5 طرق
  .عرض القديمه   - عرض الأرقام القديمة بـ5 طرق
  .عرض الكل      - عرض جميع المسجلة بـ5 طرق
  .اضافه حساب    - إضافة حساب ثانوي للفحص المتوازي
  .الحسابات      - عرض الحسابات الإضافية
  .حذف حساب      - حذف حساب إضافي
  .مسح           - حذف جهات الاتصال المستوردة
"""

import asyncio
import re
import time

try:
    import phonenumbers
    from phonenumbers import geocoder
    HAS_PHONENUMBERS = True
except ImportError:
    HAS_PHONENUMBERS = False

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    FloodWaitError, SessionPasswordNeededError,
    PhoneNumberInvalidError, ChatAdminRequiredError,
    UserPrivacyRestrictedError
)
from telethon.tl.functions.contacts import (
    ImportContactsRequest, DeleteContactsRequest
)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetCommonChatsRequest
from telethon.tl.types import (
    InputPhoneContact,
    UserStatusOnline, UserStatusOffline,
    UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth
)

from . import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..core.logger import logging

try:
    from ..sql_helper.globals import gvarstatus, addgvar, delgvar
except ImportError:
    def gvarstatus(v): return None
    def addgvar(k, v): pass
    def delgvar(k): pass

plugin_category = "العروض"
LOGS = logging.getLogger(__name__)

# ═══════════════════════════════
# إعدادات API من الكونفق
# ═══════════════════════════════
API_ID = getattr(Config, 'APP_ID', None) or getattr(Config, 'api_id', None) or 28797361
API_HASH = getattr(Config, 'API_HASH', None) or getattr(Config, 'api_hash', None) or '771041b32e83ab232e066b7adeee700b'

try:
    from ..Config import Config
except ImportError:
    class Config:
        APP_ID = 28797361
        API_HASH = '771041b32e83ab232e066b7adeee700b'

# ═══════════════════════════════
# إعدادات الفحص
# ═══════════════════════════════
OLD_ID_THRESHOLD = 6000000000
BATCH_SIZE = 50
METHOD_DELAY = 0.3
NUMBER_DELAY = 0.8

# ═══════════════════════════════
# حالة عامة
# ═══════════════════════════════
CHECK_RESULTS = {}
EXTRA_CLIENTS = []
IMPORTED_IDS = []
_extra_initialized = False
_client_round = 0


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
        '234': '🇳🇬 نـيـجـيـريـا', '254': '🇰🇪 كـيـنـيـا',
    }
    if HAS_PHONENUMBERS:
        try:
            parsed = phonenumbers.parse(phone, None)
            country = geocoder.region_name_for_number(parsed, 'ar')
            if country:
                return f'🌍 {country}'
        except:
            pass
    clean = phone.replace('+', '')
    for code, name in sorted(codes.items(), key=lambda x: -len(x[0])):
        if clean.startswith(code):
            return name
    return '🌍 غـيـر مـعـروف'


def is_old(user_id):
    return user_id < OLD_ID_THRESHOLD


def get_status_text(status):
    if isinstance(status, UserStatusOnline):
        return '🟢 مـتـصـل الآن'
    elif isinstance(status, UserStatusOffline):
        return '🔴 غـيـر مـتـصـل'
    elif isinstance(status, UserStatusRecently):
        return '🟡 مـؤخـراً'
    elif isinstance(status, UserStatusLastWeek):
        return '🟠 مـنـذ أسـبـوع'
    elif isinstance(status, UserStatusLastMonth):
        return '🔵 مـنـذ شـهـر'
    return '⚪ غـيـر مـعـروف'


def progress_bar(current, total, width=15):
    if total == 0:
        return "[███████████████] 100%"
    percent = int((current / total) * 100)
    filled = int((current / total) * width)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percent}%"


def get_next_client():
    global _client_round
    clients = [zedub] + EXTRA_CLIENTS
    if not clients:
        return zedub
    c = clients[_client_round % len(clients)]
    _client_round += 1
    return c


async def safe_import(client, contacts, max_retries=2):
    for attempt in range(max_retries):
        try:
            result = await client(ImportContactsRequest(contacts))
            return result
        except FloodWaitError as e:
            wait = min(e.seconds, 30)
            LOGS.warning(f"FloodWait {wait}s - محاولة {attempt+1}")
            await asyncio.sleep(wait)
        except Exception as e:
            err = str(e)
            if 'BANNED' in err.upper() or 'PHONE_NUMBER_BANNED' in err.upper():
                LOGS.error(f"حساب محظور: {err[:60]}")
                return None
            LOGS.error(f"خطأ استيراد: {err[:60]}")
            await asyncio.sleep(1)
    return None


async def ensure_extra_clients():
    global _extra_initialized, EXTRA_CLIENTS
    if _extra_initialized:
        return
    _extra_initialized = True

    sessions_data = gvarstatus("EXTRA_ACCOUNTS") or ""
    if not sessions_data:
        return

    for session_str in sessions_data.split("|||"):
        session_str = session_str.strip()
        if not session_str:
            continue
        try:
            c = TelegramClient(StringSession(session_str), API_ID, API_HASH)
            await c.connect()
            me = await c.get_me()
            if me:
                EXTRA_CLIENTS.append(c)
                LOGS.info(f"✅ حساب إضافي: {me.first_name} ({me.phone})")
            else:
                await c.disconnect()
        except Exception as e:
            LOGS.error(f"❌ فشل تحميل حساب إضافي: {e}")


async def get_all_clients():
    await ensure_extra_clients()
    clients = [zedub]
    for c in EXTRA_CLIENTS[:]:
        try:
            if not c.is_connected():
                await c.connect()
            me = await c.get_me()
            if me:
                clients.append(c)
            else:
                EXTRA_CLIENTS.remove(c)
        except:
            try:
                EXTRA_CLIENTS.remove(c)
            except:
                pass
    return clients


# ═══════════════════════════════
# الطرق الخمس لفحص صاحب الحساب
# ═══════════════════════════════
async def check_5_methods(phone, info):
    if not info.get('registered'):
        return "**❌ غـيـر مـسـجـل فـي تـيـلـجـرام**"

    user_id = info['user_id']
    results = []

    # ━━━━━━ 1️⃣ من البيانات المحفوظة (فوري) ━━━━━━
    results.append(
        f"**1️⃣ اسـتـيـراد سـريـع:**\n"
        f"   **⎉╎الاسـم:** {info['first_name']} {info['last_name']}\n"
        f"   **⎉╎الـمـعـرف:** @{info['username']}\n"
        f"   **⎉╎الايـدي:** `{user_id}`\n"
        f"   **⎉╎مـمـيـز:** {'✅' if info['premium'] else '❌'}"
    )

    # ━━━━━━ 2️⃣ تحليل الكيان + 4️⃣ تركيبي (طلب واحد) ━━━━━━
    client = get_next_client()
    entity = None
    try:
        entity = await client.get_entity(phone)

        results.append(
            f"**2️⃣ تـحـلـيـل الـكـيـان:**\n"
            f"   **⎉╎الاسـم:** {entity.first_name or '-'} {entity.last_name or ''}\n"
            f"   **⎉╎الـمـعـرف:** @{entity.username or 'لا يـوجد'}\n"
            f"   **⎉╎الايـدي:** `{entity.id}`\n"
            f"   **⎉╎بـوت:** {'✅' if getattr(entity, 'bot', False) else '❌'} | "
            f"**مـقـيـد:** {'✅' if getattr(entity, 'restricted', False) else '❌'}"
        )

        flags = []
        if getattr(entity, 'premium', False):  flags.append('⭐ مـمـيـز')
        if getattr(entity, 'verified', False):  flags.append('✔️ مـوثـق')
        if is_old(entity.id):                    flags.append('📅 قـديـم')
        if getattr(entity, 'restricted', False): flags.append('🚫 مـقـيـد')
        if getattr(entity, 'scam', None):        flags.append('⚠️ احـتـيـال')
        if getattr(entity, 'fake', None):        flags.append('🎭 مـزيـف')
        if getattr(entity, 'support', False):    flags.append('🛟 رسـمـي')
        flags_t = ' | '.join(flags) if flags else 'لا عـلامـات'

        status = getattr(entity, 'status', None)
        results.append(
            f"**4️⃣ فـحـص تـركـيـبـي:**\n"
            f"   **⎉╎الـعـلامـات:** {flags_t}\n"
            f"   **⎉╎الـحـالـة:** {get_status_text(status)}\n"
            f"   **⎉╎الايـدي:** `{entity.id}`"
        )
    except FloodWaitError as e:
        results.append(f"**2️⃣ الـكـيـان:** ⏳ حـظـر {e.seconds}s")
        results.append(f"**4️⃣ الـتـركـيـبـي:** ⏳ حـظـر")
        await asyncio.sleep(min(e.seconds, 15))
    except Exception as e:
        results.append(f"**2️⃣ الـكـيـان:** ❌ {str(e)[:35]}")
        results.append(f"**4️⃣ الـتـركـيـبـي:** ❌")

    await asyncio.sleep(METHOD_DELAY)

    # ━━━━━━ 3️⃣ البصمة الرقمية بايو+صور ━━━━━━
    client2 = get_next_client()
    try:
        full = await client2(GetFullUserRequest(user_id))
        user = full.users[0]
        bio = full.full_user.about or 'لا يـوجـد'

        try:
            photos = await client2.get_profile_photos(user_id, limit=1)
            photo_count = photos.total if hasattr(photos, 'total') else len(list(photos))
        except:
            photo_count = '؟'

        results.append(
            f"**3️⃣ بـصـمـة رقـمـيـة:**\n"
            f"   **⎉╎الـبـايـو:** {bio}\n"
            f"   **⎉╎الـصـور:** {photo_count}\n"
            f"   **⎉╎الايـدي:** `{user.id}`"
        )
    except FloodWaitError as e:
        results.append(f"**3️⃣ الـبـصـمـة:** ⏳ حـظـر {e.seconds}s")
        await asyncio.sleep(min(e.seconds, 15))
    except Exception as e:
        results.append(f"**3️⃣ الـبـصـمـة:** ❌ {str(e)[:35]}")

    await asyncio.sleep(METHOD_DELAY)

    # ━━━━━━ 5️⃣ خريطة الشبكة الاجتماعية ━━━━━━
    client3 = get_next_client()
    try:
        common = await client3(GetCommonChatsRequest(
            user_id=user_id, max_id=0, limit=100
        ))
        groups_list = [f"▫️ {c.title}" for c in common.chats[:5]]
        groups_text = '\n   '.join(groups_list) if groups_list else 'لا يـوجـد'
        results.append(
            f"**5️⃣ خـريـطـة شـبـكـة:**\n"
            f"   **⎉╎الـمـجـمـوعـات:** {len(common.chats)} مـشـتـركـة\n"
            f"   {groups_text}"
        )
    except FloodWaitError as e:
        results.append(f"**5️⃣ الـشـبـكـة:** ⏳ حـظـر {e.seconds}s")
        await asyncio.sleep(min(e.seconds, 15))
    except Exception as e:
        results.append(f"**5️⃣ الـشـبـكـة:** ❌ {str(e)[:35]}")

    return '\n\n'.join(results)


# ═══════════════════════════════
# أمر الفحص الرئيسي
# ═══════════════════════════════
@zedub.zed_cmd(pattern="^[.,]جرب$")
async def handle_check(event):
    global CHECK_RESULTS, IMPORTED_IDS, _client_round
    CHECK_RESULTS = {}
    IMPORTED_IDS = []
    _client_round = 0

    if not event.reply_to_msg_id:
        return await edit_delete(event, "**⎉╎لـلـفـحـص أرسـل `.جرب` بـالـرد عـلى رسـالـة فـيـهـا أرقـام**", 10)

    reply_msg = await event.get_reply_message()
    phones = extract_phones(reply_msg.text or '')

    if not phones:
        return await edit_delete(event, "**⎉╎لـم يـتـم الـعـثـور عـلى أرقـام تـبـدأ بـ + بـالـرسـالـة**", 10)

    zed = await edit_or_reply(event,
        f"**🔍┊فـحـص الـرقـام - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**⎉╎تـم الـعـثـور عـلى {len(phones)} رقـم**\n"
        f"**⎉╎جـاري الـتـحـمـيـل ...**\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )

    clients = await get_all_clients()
    total = len(phones)

    await zed.edit(
        f"**🔍┊فـحـص الـرقـام - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"`{progress_bar(0, total)}`\n"
        f"**⎉╎0/{total} | 👥 {len(clients)} حـسـاب | ⏳ جـاري ...**\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )

    lock = asyncio.Lock()
    checked = [0]
    last_update = [0]

    async def process_batch(client, phone_batch, client_idx):
        for i in range(0, len(phone_batch), BATCH_SIZE):
            batch = phone_batch[i:i + BATCH_SIZE]

            contacts = [
                InputPhoneContact(
                    client_id=j, phone=ph,
                    first_name=f'Z{j}', last_name=f'C{client_idx}'
                )
                for j, ph in enumerate(batch)
            ]

            result = await safe_import(client, contacts)

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

                    country = get_country(matched)
                    premium = getattr(user, 'premium', False)
                    old = is_old(user.id)

                    async with lock:
                        CHECK_RESULTS[matched] = {
                            'phone': matched,
                            'country': country,
                            'user_id': user.id,
                            'first_name': user.first_name or '',
                            'last_name': user.last_name or '',
                            'username': user.username or 'لا يوجد',
                            'premium': premium,
                            'old': old,
                            'registered': True
                        }

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

    per_client = total // len(clients)
    remainder = total % len(clients)

    tasks = []
    idx = 0
    for ci, cl in enumerate(clients):
        count = per_client + (1 if ci < remainder else 0)
        batch = phones[idx:idx + count]
        idx += count
        if batch:
            tasks.append(process_batch(cl, batch, ci))

    await asyncio.gather(*tasks, return_exceptions=True)

    for ph in phones:
        if ph not in CHECK_RESULTS:
            CHECK_RESULTS[ph] = {
                'phone': ph,
                'country': get_country(ph),
                'registered': False,
                'premium': False,
                'old': False
            }

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
        [f"   **⎉╎{n}:** {cnt}" for n, cnt in sorted(countries.items(), key=lambda x: -x[1])]
    )

    text = (
        f"**🛂┊فـحـص الـرقـام - 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**⎉╎إجـمـالـي الـرقـام:** {total}\n"
        f"**⎉╎مـسـجـلـة تـيـلـجـرام:** {reg_count} ✅\n"
        f"**⎉╎غـيـر مـسـجـلـة:** {not_reg} ❌\n"
        f"**⎉╎مـمـيـزة (Premium):** {prem_count} ⭐\n"
        f"**⎉╎قـديـمـة (قـبـل 2024):** {old_count} 📅\n"
        f"**⎉╎مـمـيـز + قـديـم:** {prem_old} ⭐📅\n"
        f"**⎉╎حـسـابـات الـفـحـص:** {len(clients)} 👥\n\n"
        f"**🌍┊الـدول:**\n"
        f"{countries_text}\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**\n\n"
        f"**📋┊الأوامـر:**\n"
        f"**⎉╎لـلـمـمـيـزة ⩥** `.عرض المميز`\n"
        f"**⎉╎لـلـقـديـمـة ⩥** `.عرض القديمه`\n"
        f"**⎉╎لـلـكـل ⩥** `.عرض الكل`\n"
        f"**⎉╎حـذف الـجـهـات ⩥** `.مسح`"
    )

    await zed.edit(text)


# ═══════════════════════════════
# أوامر العرض بـ5 طرق
# ═══════════════════════════════

async def display_numbers(event, phones, title_emoji, title_text):
    if not phones:
        return await edit_delete(event, f"**⎉╎لا تـوجـد أرقـام {title_text}**", 8)

    total = len(phones)
    zed = await edit_or_reply(event,
        f"**{title_emoji}┊جـاري فـحـص {total} رقـم {title_text} بـ5 طـرق ...**\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )

    for i, ph in enumerate(phones):
        info = CHECK_RESULTS[ph]
        badges = ''
        if info.get('premium'): badges += ' ⭐'
        if info.get('old'):     badges += ' 📅'

        header = (
            f"**{'━' * 25}**\n"
            f"**📱┊الـرقـم:** `{ph}`{badges}\n"
            f"**🌍┊الـدولـة:** {info['country']}\n"
            f"**{'━' * 25}**"
        )

        methods = await check_5_methods(ph, info)

        try:
            await event.reply(f"{header}\n\n{methods}")
        except Exception as e:
            LOGS.error(f"خطأ إرسال: {e}")

        if (i + 1) % 3 == 0 or i == total - 1:
            try:
                await zed.edit(
                    f"**{title_emoji}┊{title_text}:** `{progress_bar(i+1, total)}`\n"
                    f"**⎉╎{i+1}/{total} | ⏳ جـاري ...**\n\n"
                    f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
                )
            except:
                pass

        await asyncio.sleep(NUMBER_DELAY)

    try:
        await zed.edit(
            f"**{title_emoji}┊تـم الـفـحـص! {total} رقـم {title_text} ✅**\n\n"
            f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
        )
    except:
        pass


@zedub.zed_cmd(pattern="^[.,]عرض المميز$")
async def show_premium(event):
    phones = [p for p, info in CHECK_RESULTS.items() if info.get('premium')]
    await display_numbers(event, phones, '⭐', 'مـمـيـزة')


@zedub.zed_cmd(pattern="^[.,]عرض القديمه$")
async def show_old(event):
    phones = [p for p, info in CHECK_RESULTS.items() if info.get('old')]
    await display_numbers(event, phones, '📅', 'قـديـمـة')


@zedub.zed_cmd(pattern="^[.,]عرض الكل$")
async def show_all(event):
    phones = [p for p, info in CHECK_RESULTS.items() if info.get('registered')]
    await display_numbers(event, phones, '📋', 'مـسـجـلـة')


# ═══════════════════════════════
# إدارة الحسابات الإضافية
# ═══════════════════════════════

@zedub.zed_cmd(pattern="^[.,]اضافه حساب$")
async def add_account(event):
    await ensure_extra_clients()

    zed = await edit_or_reply(event,
        "**📱┊إضـافـة حـسـاب جـديـد لـلـفـحـص - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        "**⎉╎أرسـل رقـم الـحـسـاب الآن** (مـثـال: `+9647701234567`)\n"
        "**⎉╎لـلإلـغـاء أرسـل** `.الغاء`\n\n"
        "**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )

    try:
        async with event.client.conversation(event.chat_id, timeout=120) as conv:

            phone_resp = await conv.get_response()
            if phone_resp.text.startswith('.'):
                return await event.reply("**⎉╎تـم الإلـغـاء ❌**")

            phone = phone_resp.text.strip()
            if not phone.startswith('+'):
                return await event.reply("**⎉╎الـرقـم يـجـب أن يـبـدأ بـ + ❌**")

            new_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await new_client.connect()

            try:
                await new_client.send_code_request(phone)
            except Exception as e:
                await new_client.disconnect()
                return await event.reply(f"**⎉╎خـطـأ بإرسـال الـكـود:** `{e}`")

            await event.reply("**📧┊أرسـل كـود الـتـحـقـق الآن**")

            code_resp = await conv.get_response()
            if code_resp.text.startswith('.'):
                await new_client.disconnect()
                return await event.reply("**⎉╎تـم الإلـغـاء ❌**")

            code = code_resp.text.strip()

            try:
                await new_client.sign_in(phone, code)
            except SessionPasswordNeededError:
                await event.reply("**🔐┊أرسـل كـلـمـة الـمـرور الـثـنـائـيـة:**")

                pwd_resp = await conv.get_response()
                if pwd_resp.text.startswith('.'):
                    await new_client.disconnect()
                    return await event.reply("**⎉╎تـم الإلـغـاء ❌**")

                try:
                    await new_client.sign_in(password=pwd_resp.text.strip())
                except Exception as e:
                    await new_client.disconnect()
                    return await event.reply(f"**⎉╎خـطـأ بـكـلـمـة الـمـرور:** `{e}`")

            except Exception as e:
                await new_client.disconnect()
                return await event.reply(f"**⎉╎خـطـأ بـتـسـجـيـل الـدخـول:** `{e}`")

            session_str = new_client.session.save()

            existing = gvarstatus("EXTRA_ACCOUNTS") or ""
            new_val = f"{existing}|||{session_str}" if existing else session_str
            addgvar("EXTRA_ACCOUNTS", new_val)

            EXTRA_CLIENTS.append(new_client)

            me = await new_client.get_me()
            await event.reply(
                f"**✅┊تـمـت إضـافـة الـحـسـاب بـنـجـاح! - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
                f"**⎉╎الاسـم:** {me.first_name}\n"
                f"**⎉╎الـرقـم:** `{me.phone}`\n"
                f"**⎉╎إجـمـالـي حـسـابـات الـفـحـص:** {1 + len(EXTRA_CLIENTS)} 👥\n\n"
                f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
            )

    except asyncio.TimeoutError:
        await event.reply("**⎉╎انـتـهـت مـهـلـة الإضـافـة (120 ثـانـيـة) ⏰**")
    except Exception as e:
        LOGS.error(f"خطأ إضافة حساب: {e}")
        await event.reply(f"**⎉╎خـطـأ:** `{str(e)[:100]}`")


@zedub.zed_cmd(pattern="^[.,]الحسابات$")
async def list_accounts(event):
    await ensure_extra_clients()

    me = await zedub.get_me()
    text = (
        f"**👥┊حـسـابـات الـفـحـص - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉**\n\n"
        f"**1️⃣ 👤 {me.first_name} | 📱 `{me.phone}` | الـرئـيـسـي ✅**\n"
    )

    if EXTRA_CLIENTS:
        for i, c in enumerate(EXTRA_CLIENTS):
            try:
                acc = await c.get_me()
                status = '✅' if c.is_connected() else '❌'
                text += (
                    f"**{i+2}️⃣ 👤 {acc.first_name} | "
                    f"📱 `{acc.phone}` | إضـافـي {status}**\n"
                )
            except:
                text += f"**{i+2}️⃣ ❌ غـيـر مـتـصـل**\n"
    else:
        text += "\n**💡 أضـف حـسـاب بـ `.اضافه حساب` لـتـسـريـع الـفـحـص**"

    text += f"\n**⎉╎الـمـجـمـوع:** {1 + len(EXTRA_CLIENTS)} حـسـاب\n\n**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    await edit_or_reply(event, text)


@zedub.zed_cmd(pattern=r"^[.,]حذف حساب(?:\s+(\d+))?$")
async def remove_account(event):
    await ensure_extra_clients()

    if not EXTRA_CLIENTS:
        return await edit_delete(event, "**⎉╎لا تـوجـد حـسـابـات إضـافـيـة ❌**", 8)

    index = event.pattern_match.group(1)

    if not index:
        text = "**👥┊أرسـل رقـم الـحـسـاب لـلـحـذف:**\n\n"
        for i, c in enumerate(EXTRA_CLIENTS):
            try:
                acc = await c.get_me()
                text += f"**{i+2}️⃣ 👤 {acc.first_name} | 📱 `{acc.phone}`**\n"
            except:
                text += f"**{i+2}️⃣ ❌ غـيـر مـتـصـل**\n"
        text += "\n**⎉╎مـثـال:** `.حذف حساب 2`"
        return await edit_or_reply(event, text)

    idx = int(index) - 2
    if idx < 0 or idx >= len(EXTRA_CLIENTS):
        return await edit_delete(event, "**⎉╎رقـم الـحـسـاب غـيـر صـحـيـح ❌**", 8)

    client = EXTRA_CLIENTS.pop(idx)
    try:
        await client.disconnect()
    except:
        pass

    remaining = []
    sessions_data = gvarstatus("EXTRA_ACCOUNTS") or ""
    for i, s in enumerate(sessions_data.split("|||")):
        if i != idx and s.strip():
            remaining.append(s.strip())
    addgvar("EXTRA_ACCOUNTS", "|||".join(remaining))

    await edit_or_reply(event,
        f"**✅┊تـم حـذف الـحـسـاب الإضـافـي**\n"
        f"**⎉╎الـمـتـبـقـي:** {1 + len(EXTRA_CLIENTS)} حـسـاب\n\n"
        f"**ـ ━─━──── 𝙕𝞝𝘿 ────━─━ ـ**"
    )


# ═══════════════════════════════
# حذف جهات الاتصال المستوردة
# ═══════════════════════════════
@zedub.zed_cmd(pattern="^[.,]مسح$")
async def clear_contacts(event):
    if not IMPORTED_IDS:
        return await edit_delete(event, "**⎉╎لا تـوجـد جـهـات اتـصـال مـسـتـوردة ❌**", 8)

    deleted = 0
    all_clients = [zedub] + EXTRA_CLIENTS

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
                    batch = input_users[i:i+50]
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