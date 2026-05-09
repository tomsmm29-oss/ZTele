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

from telethon import TelegramClient, events
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
from ..Config import Config
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

# ═══════════════════════════════
# إعدادات الفحص
# ═══════════════════════════════
OLD_ID_THRESHOLD = 6000000000  # ايدي قبل 2024 تقريباً
BATCH_SIZE = 50                # عدد الأرقام بكل دفعة
METHOD_DELAY = 0.3             # تأخير بين الطرق (ثانية)
NUMBER_DELAY = 0.8             # تأخير بين الأرقام (ثانية)

# ═══════════════════════════════
# حالة عامة
# ═══════════════════════════════
CHECK_RESULTS = {}
EXTRA_CLIENTS = []
IMPORTED_IDS = []       # user_id لكل الحسابات المستوردة
_extra_initialized = False
_client_round = 0       # round-robin counter


# ═══════════════════════════════
# دوال مساعدة
# ═══════════════════════════════
def normalize_phone(phone):
    """تطبيع الرقم للمقارنة"""
    return phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')


def extract_phones(text):
    """استخراج الأرقام التي تبدأ بـ +"""
    pattern = r'\+\d{7,15}'
    return list(dict.fromkeys(re.findall(pattern, text)))


def get_country(phone):
    """تحديد الدولة من الرقم"""
    if not HAS_PHONENUMBERS:
        # طريقة بديلة بدون phonenumbers
        codes = {
            '964': '🇮🇶 العراق', '966': '🇸🇦 السعودية', '971': '🇦🇪 الإمارات',
            '965': '🇰🇼 الكويت', '974': '🇶🇦 قطر', '968': '🇴🇲 عمان',
            '973': '🇧🇭 البحرين', '20': '🇪🇬 مصر', '212': '🇲🇦 المغرب',
            '213': '🇩🇿 الجزائر', '216': '🇹🇳 تونس', '218': '🇱🇾 ليبيا',
            '249': '🇸🇩 السودان', '967': '🇾🇪 اليمن', '962': '🇯🇴 الأردن',
            '961': '🇱🇧 لبنان', '963': '🇸🇾 سوريا', '970': '🇵🇸 فلسطين',
            '90': '🇹🇷 تركيا', '44': '🇬🇧 بريطانيا', '1': '🇺🇸 أمريكا',
            '49': '🇩🇪 ألمانيا', '33': '🇫🇷 فرنسا', '7': '🇷🇺 روسيا',
            '86': '🇨🇳 الصين', '91': '🇮🇳 الهند', '62': '🇮🇩 إندونيسيا',
            '55': '🇧🇷 البرازيل', '234': '🇳🇬 نيجيريا', '254': '🇰🇪 كينيا',
        }
        clean = phone.replace('+', '')
        for code, name in sorted(codes.items(), key=lambda x: -len(x[0])):
            if clean.startswith(code):
                return name
        return '🌍 غير معروف'
    try:
        parsed = phonenumbers.parse(phone, None)
        country = geocoder.region_name_for_number(parsed, 'ar')
        if country:
            return f'🌍 {country}'
        return '🌍 غير معروف'
    except:
        return '🌍 غير معروف'


def is_old(user_id):
    """هل الحساب قديم (قبل 2024)"""
    return user_id < OLD_ID_THRESHOLD


def get_status_text(status):
    """نص حالة الاتصال"""
    if isinstance(status, UserStatusOnline):
        return '🟢 متصل الآن'
    elif isinstance(status, UserStatusOffline):
        return '🔴 غير متصل'
    elif isinstance(status, UserStatusRecently):
        return '🟡 مؤخراً'
    elif isinstance(status, UserStatusLastWeek):
        return '🟠 منذ أسبوع'
    elif isinstance(status, UserStatusLastMonth):
        return '🔵 منذ شهر'
    return '⚪ غير معروف'


def progress_bar(current, total, width=15):
    """شريط تقدم بصري"""
    if total == 0:
        return "[███████████████] 100%"
    percent = int((current / total) * 100)
    filled = int((current / total) * width)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percent}%"


def get_next_client():
    """الحصول على العميل التالي بنظام round-robin"""
    global _client_round
    clients = [zedub] + EXTRA_CLIENTS
    if not clients:
        return zedub
    c = clients[_client_round % len(clients)]
    _client_round += 1
    return c


async def safe_import(client, contacts, max_retries=2):
    """استيراد جهات اتصال مع إدارة الحظر والخطأ"""
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
                LOGS.error(f"حساب محظور من استيراد جهات: {err[:60]}")
                return None
            LOGS.error(f"خطأ استيراد: {err[:60]}")
            await asyncio.sleep(1)
    return None


async def ensure_extra_clients():
    """تحميل الحسابات الإضافية المحفوظة"""
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
    """الحصول على جميع العملاء المتاحين"""
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
# (مرتبة من الأسرع للأبطأ + محسّنة)
# ═══════════════════════════════
async def check_5_methods(phone, info):
    """تنفيذ الطرق الخمس بتحسين السرعة - 3 طلبات API فقط بدل 5"""

    if not info.get('registered'):
        return "❌ غير مسجل في تيليجرام"

    user_id = info['user_id']
    client = get_next_client()
    results = []

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1️⃣ الطريقة الأسرع: من البيانات المحفوظة (فوري - بدون API)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    results.append(
        f"1️⃣ استيراد سريع:\n"
        f"   👤 {info['first_name']} {info['last_name']}\n"
        f"   🆔 @{info['username']}\n"
        f"   🔢 `{user_id}`\n"
        f"   ⭐ {'✅ مميز' if info['premium'] else '❌ عادي'}"
    )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2️⃣ تحليل الكيان المباشر (سريع - طلب واحد)
    # + 4️⃣ الفحص التركيبي (من نفس الكيان - بدون طلب إضافي)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    entity = None
    try:
        entity = await client.get_entity(phone)

        results.append(
            f"2️⃣ تحليل الكيان:\n"
            f"   👤 {entity.first_name or '-'} {entity.last_name or ''}\n"
            f"   🆔 @{entity.username or 'لا يوجد'}\n"
            f"   🔢 `{entity.id}`\n"
            f"   🤖 {'✅' if getattr(entity, 'bot', False) else '❌'} | "
            f"🚫 {'✅' if getattr(entity, 'restricted', False) else '❌'}"
        )

        # الطريقة 4 من نفس الكيان (مجاني - بدون طلب إضافي)
        flags = []
        if getattr(entity, 'premium', False):  flags.append('⭐ مميز')
        if getattr(entity, 'verified', False):  flags.append('✔️ موثق')
        if is_old(entity.id):                    flags.append('📅 قديم')
        if getattr(entity, 'restricted', False): flags.append('🚫 مقيد')
        if getattr(entity, 'scam', None):        flags.append('⚠️ احتيال')
        if getattr(entity, 'fake', None):        flags.append('🎭 مزيف')
        if getattr(entity, 'support', False):    flags.append('🛟 رسمي')
        flags_t = ' | '.join(flags) if flags else 'لا علامات'

        status = getattr(entity, 'status', None)
        results.append(
            f"4️⃣ فحص تركيبي:\n"
            f"   🏷️ {flags_t}\n"
            f"   🟢 {get_status_text(status)}\n"
            f"   🔢 `{entity.id}`"
        )
    except FloodWaitError as e:
        results.append(f"2️⃣ الكيان: ⏳ حظر {e.seconds}s")
        results.append(f"4️⃣ تركيبي: ⏳ حظر")
        await asyncio.sleep(min(e.seconds, 15))
    except Exception as e:
        results.append(f"2️⃣ الكيان: ❌ {str(e)[:35]}")
        results.append(f"4️⃣ تركيبي: ❌")

    await asyncio.sleep(METHOD_DELAY)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3️⃣ البصمة الرقمية بايو+صور (متوسط - طلب واحد)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    client2 = get_next_client()
    try:
        full = await client2(GetFullUserRequest(user_id))
        user = full.users[0]
        bio = full.full_user.about or 'لا يوجد'

        try:
            photos = await client2.get_profile_photos(user_id, limit=1)
            photo_count = photos.total if hasattr(photos, 'total') else len(list(photos))
        except:
            photo_count = '؟'

        results.append(
            f"3️⃣ بصمة رقمية:\n"
            f"   📝 {bio}\n"
            f"   📷 صور: {photo_count}\n"
            f"   🔢 `{user.id}`"
        )
    except FloodWaitError as e:
        results.append(f"3️⃣ بصمة: ⏳ حظر {e.seconds}s")
        await asyncio.sleep(min(e.seconds, 15))
    except Exception as e:
        results.append(f"3️⃣ بصمة: ❌ {str(e)[:35]}")

    await asyncio.sleep(METHOD_DELAY)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5️⃣ خريطة الشبكة الاجتماعية (الأبطأ - طلب واحد)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    client3 = get_next_client()
    try:
        common = await client3(GetCommonChatsRequest(
            user_id=user_id, max_id=0, limit=100
        ))
        groups_list = [f"▫️ {c.title}" for c in common.chats[:5]]
        groups_text = '\n   '.join(groups_list) if groups_list else 'لا يوجد'
        results.append(
            f"5️⃣ خريطة شبكة:\n"
            f"   👥 {len(common.chats)} مجموعة مشتركة\n"
            f"   {groups_text}"
        )
    except FloodWaitError as e:
        results.append(f"5️⃣ شبكة: ⏳ حظر {e.seconds}s")
        await asyncio.sleep(min(e.seconds, 15))
    except Exception as e:
        results.append(f"5️⃣ شبكة: ❌ {str(e)[:35]}")

    return '\n\n'.join(results)


# ═══════════════════════════════
# أمر الفحص الرئيسي
# ═══════════════════════════════
@zedub.on(zedub.cmd(pattern="جرب$", outgoing=True))
async def handle_check(event):
    global CHECK_RESULTS, IMPORTED_IDS, _client_round
    CHECK_RESULTS = {}
    IMPORTED_IDS = []
    _client_round = 0

    if not event.reply_to_msg_id:
        return await edit_delete(event, "**❌ يجب الرد على رسالة فيها أرقام**", 10)

    reply_msg = await event.get_reply_message()
    phones = extract_phones(reply_msg.text or '')

    if not phones:
        return await edit_delete(event, "**❌ ما فيه أرقام تبدأ بـ + بالرسالة**", 10)

    status_msg = await edit_or_reply(event,
        f"**🔍 {len(phones)} رقم**\n**⏳ جاري تحميل الحسابات...**"
    )

    clients = await get_all_clients()
    total = len(phones)

    await status_msg.edit(
        f"**🔍 الفحص الشامل**\n"
        f"`{progress_bar(0, total)}`\n"
        f"**📊 0/{total} | 👥 {len(clients)} حساب | ⏳ جاري...**"
    )

    # ── قفل للعداد المشترك ──
    lock = asyncio.Lock()
    checked = [0]
    last_update = [0]

    async def process_batch(client, phone_batch, client_idx):
        """معالجة دفعة أرقام بحساب واحد"""
        registered = set()

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
                        registered.add(matched)

            # ── تحديث العداد والرسالة ──
            async with lock:
                checked[0] += len(batch)

            now = time.time()
            if now - last_update[0] >= 1.5:  # تحديث كل 1.5 ثانية
                last_update[0] = now
                try:
                    await status_msg.edit(
                        f"**🔍 الفحص الشامل**\n"
                        f"`{progress_bar(checked[0], total)}`\n"
                        f"**📊 {checked[0]}/{total} | ✅ {len(CHECK_RESULTS)} مسجل | ⏳ جاري...**"
                    )
                except:
                    pass

            await asyncio.sleep(0.3)

        return registered

    # ── توزيع الأرقام على الحسابات بالتوازي ──
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

    all_registered = set()
    task_results = await asyncio.gather(*tasks, return_exceptions=True)

    for r in task_results:
        if isinstance(r, set):
            all_registered.update(r)
        elif isinstance(r, Exception):
            LOGS.error(f"خطأ في مهمة: {r}")

    # ── الأرقام غير المسجلة ──
    for ph in phones:
        if ph not in CHECK_RESULTS:
            CHECK_RESULTS[ph] = {
                'phone': ph,
                'country': get_country(ph),
                'registered': False,
                'premium': False,
                'old': False
            }

    # ── حساب الإحصائيات ──
    reg_count = len(all_registered)
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
        [f"   {n}: {cnt}" for n, cnt in sorted(countries.items(), key=lambda x: -x[1])]
    )

    text = (
        f"**╔══════════════════════════╗**\n"
        f"**║  🔍 نتائج الفحص الشامل   ║**\n"
        f"**╚══════════════════════════╝**\n\n"
        f"**📊 ║ الإحصائيات:**\n"
        f"**━━━━━━━━━━━━━━━━━━━━━━━━**\n"
        f"📱 الإجمالي: **{total}**\n"
        f"✅ مسجلة: **{reg_count}**\n"
        f"❌ غير مسجلة: **{not_reg}**\n"
        f"⭐ مميزة (Premium): **{prem_count}**\n"
        f"📅 قديمة (قبل 2024): **{old_count}**\n"
        f"⭐📅 مميزة + قديمة: **{prem_old}**\n"
        f"👥 حسابات الفحص: **{len(clients)}**\n\n"
        f"**🌍 ║ الدول:**\n"
        f"**━━━━━━━━━━━━━━━━━━━━━━━━**\n"
        f"{countries_text}\n\n"
        f"**📋 ║ الأوامر:**\n"
        f"**━━━━━━━━━━━━━━━━━━━━━━━━**\n"
        f"📤 `.عرض المميز`\n"
        f"📤 `.عرض القديمه`\n"
        f"📤 `.عرض الكل`\n"
        f"🗑️ `.مسح` - حذف الجهات"
    )

    await status_msg.edit(text)


# ═══════════════════════════════
# أوامر العرض بـ5 طرق
# ═══════════════════════════════

async def display_numbers(event, phones, title_emoji, title_text):
    """دالة عرض موحدة للطرق الخمس"""
    if not phones:
        return await edit_delete(event, f"**❌ لا توجد أرقام {title_text}**", 8)

    total = len(phones)
    status_msg = await edit_or_reply(event,
        f"**{title_emoji} جاري فحص {total} رقم {title_text} بـ5 طرق...**"
    )

    for i, ph in enumerate(phones):
        info = CHECK_RESULTS[ph]
        badges = ''
        if info.get('premium'): badges += '⭐'
        if info.get('old'):     badges += '📅'

        header = (
            f"**{'═' * 28}**\n"
            f"📱 `{ph}` {badges}\n"
            f"🌍 {info['country']}\n"
            f"**{'═' * 28}**"
        )

        methods = await check_5_methods(ph, info)

        try:
            await event.reply(f"{header}\n\n{methods}")
        except Exception as e:
            LOGS.error(f"خطأ إرسال: {e}")

        # ── تحديث حالة التقدم ──
        if (i + 1) % 3 == 0 or i == total - 1:
            try:
                await status_msg.edit(
                    f"**{title_emoji} {title_text}: `{progress_bar(i+1, total)}`\n"
                    f"📊 {i+1}/{total} | ⏳ جاري...**"
                )
            except:
                pass

        await asyncio.sleep(NUMBER_DELAY)

    try:
        await status_msg.edit(f"**✅ تم الفحص! {total} رقم {title_text}**")
    except:
        pass


@zedub.on(zedub.cmd(pattern="عرض المميز$", outgoing=True))
async def show_premium(event):
    phones = [p for p, info in CHECK_RESULTS.items() if info.get('premium')]
    await display_numbers(event, phones, '⭐', 'مميزة')


@zedub.on(zedub.cmd(pattern="عرض القديمه$", outgoing=True))
async def show_old(event):
    phones = [p for p, info in CHECK_RESULTS.items() if info.get('old')]
    await display_numbers(event, phones, '📅', 'قديمة')


@zedub.on(zedub.cmd(pattern="عرض الكل$", outgoing=True))
async def show_all(event):
    phones = [p for p, info in CHECK_RESULTS.items() if info.get('registered')]
    await display_numbers(event, phones, '📋', 'مسجلة')


# ═══════════════════════════════
# إدارة الحسابات الإضافية
# ═══════════════════════════════

@zedub.on(zedub.cmd(pattern="اضافه حساب$", outgoing=True))
async def add_account(event):
    """إضافة حساب ثانوي للفحص المتوازي"""
    await ensure_extra_clients()

    await edit_or_reply(event,
        "**📱 إضافة حساب جديد للفحص**\n"
        "**━━━━━━━━━━━━━━━━━━━━━━━━**\n"
        "**أرسل رقم الحساب الآن** (مثال: `+9647701234567`)\n"
        "**💡 أرسل `.الغاء` للإلغاء**"
    )

    try:
        async with event.client.conversation(event.chat_id, timeout=120) as conv:

            # ── استقبال الرقم ──
            phone_resp = await conv.get_response()
            if phone_resp.text.startswith('.'):
                return await event.reply("**❌ تم الإلغاء**")

            phone = phone_resp.text.strip()
            if not phone.startswith('+'):
                return await event.reply("**❌ الرقم يجب أن يبدأ بـ +**")

            # ── إنشاء عميل جديد ──
            new_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await new_client.connect()

            try:
                await new_client.send_code_request(phone)
            except Exception as e:
                await new_client.disconnect()
                return await event.reply(f"**❌ خطأ بإرسال الكود:** `{e}`")

            await event.reply("**📧 أرسل كود التحقق الآن**")

            # ── استقبال الكود ──
            code_resp = await conv.get_response()
            if code_resp.text.startswith('.'):
                await new_client.disconnect()
                return await event.reply("**❌ تم الإلغاء**")

            code = code_resp.text.strip()

            try:
                await new_client.sign_in(phone, code)
            except SessionPasswordNeededError:
                await event.reply("**🔐 أرسل كلمة المرور الثنائية:**")

                pwd_resp = await conv.get_response()
                if pwd_resp.text.startswith('.'):
                    await new_client.disconnect()
                    return await event.reply("**❌ تم الإلغاء**")

                try:
                    await new_client.sign_in(password=pwd_resp.text.strip())
                except Exception as e:
                    await new_client.disconnect()
                    return await event.reply(f"**❌ خطأ بكلمة المرور:** `{e}`")

            except Exception as e:
                await new_client.disconnect()
                return await event.reply(f"**❌ خطأ بتسجيل الدخول:** `{e}`")

            # ── حفظ الجلسة ──
            session_str = new_client.session.save()

            existing = gvarstatus("EXTRA_ACCOUNTS") or ""
            new_val = f"{existing}|||{session_str}" if existing else session_str
            addgvar("EXTRA_ACCOUNTS", new_val)

            EXTRA_CLIENTS.append(new_client)

            me = await new_client.get_me()
            await event.reply(
                f"**✅ تمت إضافة الحساب بنجاح!**\n"
                f"**━━━━━━━━━━━━━━━━━━━━━━━━**\n"
                f"👤 **{me.first_name}**\n"
                f"📱 `{me.phone}`\n"
                f"👥 إجمالي حسابات الفحص: **{1 + len(EXTRA_CLIENTS)}**"
            )

    except asyncio.TimeoutError:
        await event.reply("**⏰ انتهت مهلة الإضافة (120 ثانية)**")
    except Exception as e:
        LOGS.error(f"خطأ إضافة حساب: {e}")
        await event.reply(f"**❌ خطأ:** `{str(e)[:100]}`")


@zedub.on(zedub.cmd(pattern="الحسابات$", outgoing=True))
async def list_accounts(event):
    """عرض الحسابات الإضافية"""
    await ensure_extra_clients()

    me = await zedub.get_me()
    text = (
        f"**👥 حسابات الفحص:**\n"
        f"**━━━━━━━━━━━━━━━━━━━━━━━━**\n"
        f"1️⃣ 👤 **{me.first_name}** | 📱 `{me.phone}` | **الرئيسي ✅**\n"
    )

    if EXTRA_CLIENTS:
        for i, c in enumerate(EXTRA_CLIENTS):
            try:
                acc = await c.get_me()
                status = '✅' if c.is_connected() else '❌'
                text += (
                    f"{i+2}️⃣ 👤 **{acc.first_name}** | "
                    f"📱 `{acc.phone}` | **إضافي {status}**\n"
                )
            except:
                text += f"{i+2}️⃣ ❌ **غير متصل**\n"
    else:
        text += "\n**💡 أضف حساب بـ `.اضافه حساب` لتسريع الفحص**"

    text += f"\n**📊 المجموع: {1 + len(EXTRA_CLIENTS)} حساب**"
    await edit_or_reply(event, text)


@zedub.on(zedub.cmd(pattern="حذف حساب(?:\s+(\d+))?$", outgoing=True))
async def remove_account(event):
    """حذف حساب إضافي"""
    await ensure_extra_clients()

    if not EXTRA_CLIENTS:
        return await edit_delete(event, "**❌ لا توجد حسابات إضافية**", 8)

    index = event.pattern_match.group(1)

    if not index:
        text = "**أرسل رقم الحساب للحذف:**\n**━━━━━━━━━━━━━━━━━━━━━━━━**\n"
        for i, c in enumerate(EXTRA_CLIENTS):
            try:
                acc = await c.get_me()
                text += f"**{i+2}️⃣** 👤 {acc.first_name} | 📱 `{acc.phone}`\n"
            except:
                text += f"**{i+2}️⃣** ❌ غير متصل\n"
        text += "\n**مثال:** `.حذف حساب 2`"
        return await edit_or_reply(event, text)

    idx = int(index) - 2  # الرئيسي = 1، الإضافي يبدأ من 2
    if idx < 0 or idx >= len(EXTRA_CLIENTS):
        return await edit_delete(event, "**❌ رقم الحساب غير صحيح**", 8)

    client = EXTRA_CLIENTS.pop(idx)
    try:
        await client.disconnect()
    except:
        pass

    # تحديث gvar
    remaining = []
    sessions_data = gvarstatus("EXTRA_ACCOUNTS") or ""
    for i, s in enumerate(sessions_data.split("|||")):
        if i != idx and s.strip():
            remaining.append(s.strip())
    addgvar("EXTRA_ACCOUNTS", "|||".join(remaining))

    await edit_or_reply(event,
        f"**✅ تم حذف الحساب الإضافي**\n"
        f"**👥 المتبقي: {1 + len(EXTRA_CLIENTS)} حساب**"
    )


# ═══════════════════════════════
# حذف جهات الاتصال المستوردة
# ═══════════════════════════════
@zedub.on(zedub.cmd(pattern="مسح$", outgoing=True))
async def clear_contacts(event):
    """حذف جهات الاتصال المستوردة من جميع الحسابات"""
    if not IMPORTED_IDS:
        return await edit_delete(event, "**❌ لا توجد جهات اتصال مستوردة**", 8)

    deleted = 0
    all_clients = [zedub] + EXTRA_CLIENTS

    for client in all_clients:
        try:
            input_users = []
            for uid in IMPORTED_IDS:
                try:
                    inp = await client.get_input_entity(uid)
                    input_users.append(inp)
                except:
                    pass

            if input_users:
                # تقسيم إلى دفعات
                for i in range(0, len(input_users), 50):
                    batch = input_users[i:i+50]
                    try:
                        await client(DeleteContactsRequest(id=batch))
                        deleted += len(batch)
                    except:
                        pass
        except:
            pass

    IMPORTED_IDS.clear()
    await edit_or_reply(event, f"**🗑️ تم حذف {deleted} جهة اتصال مستوردة ✅**")