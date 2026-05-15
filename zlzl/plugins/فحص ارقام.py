import asyncio
import json
import os
import re

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError
)
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact

# استيرادات سورس زدثون الأساسية
from . import zedub
from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply

try:
    from ..sql_helper.globals import gvarstatus, addgvar
except ImportError:
    def gvarstatus(v): return None
    def addgvar(k, v): pass

LOGS = logging.getLogger(__name__)
plugin_category = "العروض"

# جلب الإعدادات من Config
APP_ID = getattr(Config, 'APP_ID', None) or 28797361
API_HASH = getattr(Config, 'API_HASH', None) or '771041b32e83ab232e066b7adeee700b'

# مخزن الجلسات في الذاكرة لعمليات الفحص
ACCOUNT_CLIENTS = {}
CHECK_RESULTS = {}
IMPORTED_IDS = []

# ═══════════════════════════════
# إدارة البيانات (SQL)
# ═══════════════════════════════

def get_accounts_data():
    raw = gvarstatus("ZED_ACCOUNTS")
    if raw is None or not str(raw).strip(): return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except:
        return {}

def save_accounts_data(data):
    addgvar("ZED_ACCOUNTS", json.dumps(data, ensure_ascii=False))

# ═══════════════════════════════
# أمر إضافة حساب (حل مشكلة Peer)
# ═══════════════════════════════

@zedub.zed_cmd(pattern="اضافه حساب$", command=("اضافه حساب", plugin_category))
async def add_account_final(event):
    "إضافة حساب فحص جديد (سيشن أو رقم)"
    zed = await edit_or_reply(event, "**📱 جاري تشغيل معالج الإضافة...**")
    
    chat_id = event.chat_id
    try:
        async with event.client.conversation(chat_id, timeout=300) as conv:
            await conv.send_message(
                "**⎉╎مرحباً بك في معالج إضافة الحسابات - زدثون**\n\n"
                "**1️⃣ أرسل كود السيشن (String Session)**\n"
                "**2️⃣ أو أرسل رقم الهاتف مع مفتاح الدولة (مثال: +964...)**\n\n"
                "**• للإلغاء أرسل** `.الغاء`"
            )
            
            response = await conv.get_response()
            input_text = response.text.strip()
            
            if input_text.startswith('.'):
                return await conv.send_message("**✅ تم إلغاء العملية.**")

            # --- الحالة 1: إضافة عبر سيشن جاهز ---
            if len(input_text) > 50:
                await zed.edit("**🔍 جاري فحص السيشن...**")
                # حل مشكلة InputPeer: نستخدم StringSession ونتصل فوراً
                new_client = TelegramClient(StringSession(input_text), APP_ID, API_HASH)
                try:
                    await new_client.connect()
                    # أهم خطوة لحل خطأ Peer:
                    me = await new_client.get_me() 
                    if me:
                        await save_new_acc(input_text, me)
                        return await conv.send_message(f"**✅ تمت الإضافة بنجاح!**\n**👤 الاسم:** {me.first_name}\n**📱 الرقم:** `{me.phone}`")
                    else:
                        return await conv.send_message("**❌ السيشن غير صالح.**")
                except Exception as e:
                    return await conv.send_message(f"**❌ خطأ:** `{e}`")
                finally:
                    await new_client.disconnect()

            # --- الحالة 2: إضافة عبر رقم الهاتف ---
            elif input_text.startswith('+'):
                phone = input_text
                await zed.edit(f"**📩 جاري طلب الكود للرقم:** `{phone}`")
                
                # إنشاء جلسة جديدة تماماً
                new_client = TelegramClient(StringSession(), APP_ID, API_HASH)
                await new_client.connect()
                
                try:
                    # طلب الكود
                    send_code = await new_client.send_code_request(phone)
                    phone_code_hash = send_code.phone_code_hash
                except Exception as e:
                    await new_client.disconnect()
                    return await conv.send_message(f"**❌ خطأ في إرسال الكود:** `{e}`")

                await conv.send_message("**⎉╎أرسل الكود الذي وصلك الآن:**\n(يفضل وضع مسافات بين الأرقام مثل: 1 2 3 4 5)")
                
                code_res = await conv.get_response()
                raw_code = code_res.text.strip().replace(" ", "")
                
                try:
                    # محاولة تسجيل الدخول
                    await new_client.sign_in(phone, raw_code, phone_code_hash=phone_code_hash)
                except SessionPasswordNeededError:
                    # معالجة التحقق بخطوتين
                    await conv.send_message("**🔐 الحساب محمي بكلمة سر (2FA)، أرسلها الآن:**")
                    pw_res = await conv.get_response()
                    try:
                        await new_client.sign_in(password=pw_res.text.strip())
                    except Exception as e:
                        return await conv.send_message(f"**❌ كلمة السر خاطئة:** `{e}`")
                except Exception as e:
                    return await conv.send_message(f"**❌ كود غير صحيح أو منتهي:** `{e}`")
                
                # نجاح العملية
                me = await new_client.get_me()
                session_str = new_client.session.save()
                await save_new_acc(session_str, me)
                await conv.send_message(f"**✅ تم تسجيل الدخول وحفظ الحساب!**\n**👤 الاسم:** {me.first_name}\n**📱 الرقم:** `{me.phone}`")
                await new_client.disconnect()
            
            else:
                await conv.send_message("**❌ يرجى إرسال رقم هاتف يبدأ بـ (+) أو سيشن صحيح.**")

    except Exception as e:
        LOGS.error(f"Error in add_account: {e}")
        await event.reply(f"**❌ حدث خطأ فني:** `{e}`\nجرب استخدام سيشن جاهز إذا استمر الخطأ.")

# ═══════════════════════════════
# دوال مساعدة وحفظ
# ═══════════════════════════════

async def save_new_acc(session, me):
    data = get_accounts_data()
    # الحصول على رقم الحساب القادم
    existing_nums = [int(k) for k in data.keys() if k.isdigit()]
    new_idx = str(max(existing_nums) + 1 if existing_nums else 2)
    
    data[new_idx] = {
        "session": session,
        "name": me.first_name,
        "phone": me.phone
    }
    save_accounts_data(data)

@zedub.zed_cmd(pattern="الحسابات$", command=("الحسابات", plugin_category))
async def list_accs(event):
    "عرض حسابات الفحص"
    data = get_accounts_data()
    me = await zedub.get_me()
    msg = f"**👥 حسابات الفحص المضافة - زدثون**\n\n**1 • الرئيسي** - {me.first_name} (`{me.phone}`)\n"
    for k, v in data.items():
        msg += f"**{k} • إضافي** - {v['name']} (`{v['phone']}`)\n"
    await edit_or_reply(event, msg)

@zedub.zed_cmd(pattern="جرب$", command=("جرب", plugin_category))
async def mass_check(event):
    "فحص الأرقام بالرد"
    reply = await event.get_reply_message()
    if not reply or not reply.text: return await edit_or_reply(event, "**⎉╎رد على قائمة أرقام.**")
    
    phones = list(dict.fromkeys(re.findall(r'\+\d{7,15}', reply.text)))
    if not phones: return await edit_or_reply(event, "**⎉╎لا توجد أرقام.**")
    
    zed = await edit_or_reply(event, f"**🔍 جاري فحص {len(phones)} رقم...**")
    CHECK_RESULTS.clear()
    
    for ph in phones:
        try:
            res = await zedub(ImportContactsRequest([InputPhoneContact(client_id=0, phone=ph, first_name="Z", last_name="C")]))
            if res.users:
                u = res.users[0]
                CHECK_RESULTS[ph] = {"id": u.id, "name": u.first_name, "prem": getattr(u, 'premium', False)}
                if u.id not in IMPORTED_IDS: IMPORTED_IDS.append(u.id)
        except: pass
    
    await zed.edit(f"**✅ انتهى الفحص.**\n**📱 الإجمالي:** {len(phones)}\n**✅ مسجل:** {len(CHECK_RESULTS)}\n**❌ غير مسجل:** {len(phones)-len(CHECK_RESULTS)}\n\nاستخدم `.عرض الكل` للمعاينة.")

@zedub.zed_cmd(pattern="عرض الكل$", command=("عرض الكل", plugin_category))
async def show_all(event):
    if not CHECK_RESULTS: return await edit_or_reply(event, "**❌ لا توجد نتائج.**")
    out = "**📋 قائمة الأرقام المسجلة:**\n\n"
    for p, v in CHECK_RESULTS.items():
        out += f"• `{p}` | {v['name']} {'⭐' if v['prem'] else ''}\n"
    await edit_or_reply(event, out)

@zedub.zed_cmd(pattern="مسح$", command=("مسح", plugin_category))
async def clear_contacts_pro(event):
    "حذف جهات الاتصال المستوردة"
    if not IMPORTED_IDS: return await edit_or_reply(event, "**❌ القائمة فارغة.**")
    await zedub(DeleteContactsRequest(id=IMPORTED_IDS))
    IMPORTED_IDS.clear()
    await edit_or_reply(event, "**🗑️ تم تنظيف جهات الاتصال بنجاح.**")