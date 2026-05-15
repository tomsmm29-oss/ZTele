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

# استيراد مستلزمات سورس زدثون
from . import zedub
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply

# محاولة استيراد قاعدة البيانات (Globals)
try:
    from ..sql_helper.globals import gvarstatus, addgvar, delgvar
except ImportError:
    def gvarstatus(v): return None
    def addgvar(k, v): pass
    def delgvar(k): pass

LOGS = logging.getLogger(__name__)
plugin_category = "العروض"

# الثوابت
OLD_ID_THRESHOLD = 6000000000
# جلب الـ API من الكوفنج الخاص باليوزرنيوت
APP_ID = getattr(Config, 'APP_ID', 28797361)
API_HASH = getattr(Config, 'API_HASH', '771041b32e83ab232e066b7adeee700b')

# الحالات المؤقتة (داخل الذاكرة)
ACCOUNT_CLIENTS = {}   # {رقم_الحساب: العميل}
CHECK_RESULTS = {}
IMPORTED_IDS = []

# ═══════════════════════════════
# الدوال المساعدة (Helper Functions)
# ═══════════════════════════════

def get_accounts_data():
    """جلب بيانات الحسابات من قاعدة البيانات مع فحص النوع لتجنب خطأ NoneType"""
    raw = gvarstatus("ZED_ACCOUNTS")
    if raw is None or raw == "":
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        LOGS.error(f"Error parsing ZED_ACCOUNTS: {e}")
        return {}

def save_accounts_data(data):
    """حفظ البيانات في قاعدة بيانات زدثون"""
    addgvar("ZED_ACCOUNTS", json.dumps(data, ensure_ascii=False))

def normalize_phone(phone):
    return phone.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

def extract_phones(text):
    if not text: return []
    return list(dict.fromkeys(re.findall(r'\+\d{7,15}', text)))

def get_country(phone):
    # قائمة مختصرة للدول (نفس نمطك السابق)
    codes = {'964': '🇮🇶 العراق', '966': '🇸🇦 السعودية', '20': '🇪🇬 مصر', '967': '🇾🇪 اليمن', '962': '🇯🇴 الأردن'}
    clean = phone.replace('+', '')
    for code, name in codes.items():
        if clean.startswith(code): return name
    return '🌍 دولي'

async def init_client(num, session_str):
    """تشغيل حساب إضافي"""
    try:
        client = TelegramClient(StringSession(session_str), APP_ID, API_HASH)
        await client.connect()
        if await client.is_user_authorized():
            ACCOUNT_CLIENTS[int(num)] = client
            return await client.get_me()
    except Exception as e:
        LOGS.error(f"Failed to init account {num}: {e}")
    return None

async def get_all_active_clients():
    """جلب كل الحسابات (الرئيسي + الإضافية)"""
    data = get_accounts_data()
    # إضافة الحساب الرئيسي دائماً
    all_clients = [(1, zedub)]
    for num_str, info in data.items():
        num = int(num_str)
        if num not in ACCOUNT_CLIENTS:
            me = await init_client(num, info.get('session', ''))
            if me: all_clients.append((num, ACCOUNT_CLIENTS[num]))
        else:
            all_clients.append((num, ACCOUNT_CLIENTS[num]))
    return all_clients

# ═══════════════════════════════
# الأوامر (Commands)
# ═══════════════════════════════

@zedub.zed_cmd(
    pattern="اضافه حساب$",
    command=("اضافه حساب", plugin_category),
    info={"header": "لإضافة حساب فحص جديد للسورس"},
)
async def add_acc(event):
    "إضافة حساب جديد (سيشن)"
    zed = await edit_or_reply(event, "**📱 جاري بدء إضافة حساب فحص جديد...**")
    try:
        async with event.client.conversation(event.chat_id, timeout=120) as conv:
            await conv.send_message("**⎉╎أرسل الآن كود السيشن (String Session) للحساب:**\nأو أرسل `.الغاء` للتراجع")
            res = await conv.get_response()
            session_str = res.text.strip()
            
            if session_str.startswith('.'):
                return await zed.edit("**⎉╎تم الإلغاء.**")

            temp_client = TelegramClient(StringSession(session_str), APP_ID, API_HASH)
            await temp_client.connect()
            
            if not await temp_client.is_user_authorized():
                return await zed.edit("**❌ السيشن غير صالح أو منتهي.**")
            
            me = await temp_client.get_me()
            data = get_accounts_data()
            
            # تحديد الرقم التالي
            nums = [int(k) for k in data.keys()]
            new_num = max(nums) + 1 if nums else 2
            
            data[str(new_num)] = {
                "session": session_str,
                "name": me.first_name,
                "phone": me.phone
            }
            save_accounts_data(data)
            ACCOUNT_CLIENTS[new_num] = temp_client
            
            await zed.edit(f"**✅ تمت إضافة الحساب #{new_num} بنجاح!**\n**👤 الاسم:** {me.first_name}\n**📱 الرقم:** `{me.phone}`")
    except Exception as e:
        await zed.edit(f"**❌ حدث خطأ:** `{e}`")

@zedub.zed_cmd(pattern="الحسابات$", command=("الحسابات", plugin_category))
async def list_accs(event):
    "عرض حسابات الفحص"
    me = await zedub.get_me()
    data = get_accounts_data()
    msg = f"**👥 حـسـابـات الـفـحـص - ZThon**\n\n**1 • الرئيسي** - {me.first_name} (`{me.phone}`)\n"
    for k, v in data.items():
        msg += f"**{k} • إضافي** - {v['name']} (`{v['phone']}`)\n"
    await edit_or_reply(event, msg)

@zedub.zed_cmd(pattern="جرب$", command=("جرب", plugin_category))
async def start_check(event):
    "الفحص الشامل بالرد"
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await edit_or_reply(event, "**⎉╎يجب الرد على رسالة تحتوي أرقام تبدأ بـ +**")
    
    phones = extract_phones(reply.text)
    if not phones:
        return await edit_or_reply(event, "**⎉╎لم يتم العثور على أرقام بصيغة دولية.**")
    
    zed = await edit_or_reply(event, f"**🔍 جاري فحص {len(phones)} رقم...**")
    
    clients = await get_all_active_clients()
    CHECK_RESULTS.clear()
    
    count = 0
    for ph in phones:
        # الفحص عبر الحساب الرئيسي (كمثال للتبسيط)
        try:
            contact = [InputPhoneContact(client_id=0, phone=ph, first_name="Z", last_name="Check")]
            res = await zedub(ImportContactsRequest(contact))
            if res.users:
                user = res.users[0]
                CHECK_RESULTS[ph] = {
                    "id": user.id,
                    "name": user.first_name,
                    "user": f"@{user.username}" if user.username else "لا يوجد",
                    "prem": getattr(user, 'premium', False),
                    "old": user.id < OLD_ID_THRESHOLD
                }
                if user.id not in IMPORTED_IDS: IMPORTED_IDS.append(user.id)
        except Exception:
            pass
        count += 1
        if count % 5 == 0:
            await zed.edit(f"**🔍 جاري الفحص... ({count}/{len(phones)})**")

    res_msg = f"**✅ انتهى الفحص لـ {len(phones)} رقم**\n"
    res_msg += f"**👥 المسجلة:** {len(CHECK_RESULTS)}\n"
    res_msg += f"**❌ غير المسجلة:** {len(phones) - len(CHECK_RESULTS)}\n\n"
    res_msg += "أرسل `.عرض الكل` لرؤية النتائج."
    await zed.edit(res_msg)

@zedub.zed_cmd(pattern="عرض الكل$", command=("عرض الكل", plugin_category))
async def show_res(event):
    if not CHECK_RESULTS:
        return await edit_or_reply(event, "**⎉╎لا توجد نتائج سابقة، استخدم .جرب أولاً**")
    
    output = "**📋 نتائج فحص الأرقام المسجلة:**\n\n"
    for ph, info in CHECK_RESULTS.items():
        status = "⭐" if info['prem'] else ""
        age = "📅" if info['old'] else ""
        output += f"• `{ph}` - {info['name']} ({info['user']}) {status}{age}\n"
    
    await edit_or_reply(event, output)

@zedub.zed_cmd(pattern="مسح$", command=("مسح", plugin_category))
async def clear_imported(event):
    "حذف جهات الاتصال المستوردة"
    if not IMPORTED_IDS:
        return await edit_or_reply(event, "**⎉╎لا توجد جهات اتصال لمسحها.**")
    
    await edit_or_reply(event, f"**🗑️ جاري حذف {len(IMPORTED_IDS)} جهة اتصال...**")
    try:
        await zedub(DeleteContactsRequest(id=IMPORTED_IDS))
        IMPORTED_IDS.clear()
        await edit_or_reply(event, "**✅ تم مسح جهات الاتصال بنجاح.**")
    except Exception as e:
        await edit_or_reply(event, f"**❌ خطأ أثناء المسح:** `{e}`")