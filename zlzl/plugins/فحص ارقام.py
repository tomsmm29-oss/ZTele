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

# مخزن الجلسات في الذاكرة
ACCOUNT_CLIENTS = {}
CHECK_RESULTS = {}
IMPORTED_IDS = []

# ═══════════════════════════════
# إدارة البيانات
# ═══════════════════════════════

def get_accounts_data():
    raw = gvarstatus("ZED_ACCOUNTS")
    if not raw: return {}
    try:
        return json.loads(raw)
    except:
        return {}

def save_accounts_data(data):
    addgvar("ZED_ACCOUNTS", json.dumps(data, ensure_ascii=False))

# ═══════════════════════════════
# أمر إضافة حساب (سيشن أو رقم)
# ═══════════════════════════════

@zedub.zed_cmd(pattern="اضافه حساب$", command=("اضافه حساب", plugin_category))
async def add_account_pro(event):
    "إضافة حساب فحص (سيشن أو رقم هاتف)"
    zed = await edit_or_reply(event, "**📱 جاري تهيئة معالج الإضافة...**")
    
    try:
        async with event.client.conversation(event.chat_id, timeout=300) as conv:
            # الخطوة 1: طلب نوع الإضافة
            await conv.send_message(
                "**⎉╎مرحباً بك في معالج إضافة الحسابات**\n\n"
                "**1️⃣ أرسل كود (السيشن) مباشرة**\n"
                "**2️⃣ أو أرسل (رقم الهاتف) مع رمز الدولة (مثال: +964...)**\n\n"
                "**• للتراجع أرسل** `.الغاء`"
            )
            
            response = await conv.get_response()
            input_data = response.text.strip()
            
            if input_data.startswith('.'):
                return await conv.send_message("**✅ تم إلغاء العملية.**")

            # الحالة الأولى: إذا كان المدخل "سيشن" (طويل غالباً)
            if len(input_data) > 50:
                await zed.edit("**🔍 جاري التحقق من السيشن...**")
                new_client = TelegramClient(StringSession(input_data), APP_ID, API_HASH)
                try:
                    await new_client.connect()
                    if not await new_client.is_user_authorized():
                        return await conv.send_message("**❌ السيشن غير صالح أو منتهي الصلاحية.**")
                    
                    me = await new_client.get_me()
                    await save_new_acc(input_data, me)
                    return await conv.send_message(f"**✅ تمت إضافة الحساب بنجاح!**\n**👤 الاسم:** {me.first_name}\n**📱 الرقم:** `{me.phone}`")
                except Exception as e:
                    return await conv.send_message(f"**❌ خطأ في السيشن:** `{str(e)}` ")
                finally:
                    await new_client.disconnect()

            # الحالة الثانية: إذا كان المدخل "رقم هاتف"
            elif input_data.startswith('+'):
                phone = input_data
                await zed.edit(f"**📩 جاري إرسال الكود للرقم:** `{phone}`")
                
                # استخدام StringSession فارغ لبدء عملية تسجيل دخول جديدة
                new_client = TelegramClient(StringSession(), APP_ID, API_HASH)
                await new_client.connect()
                
                try:
                    send_code = await new_client.send_code_request(phone)
                except PhoneNumberInvalidError:
                    return await conv.send_message("**❌ رقم الهاتف غير صحيح.**")
                except Exception as e:
                    return await conv.send_message(f"**❌ حدث خطأ:** `{e}`")

                await conv.send_message("**⎉╎وصلك كود التحقق؟ أرسله الآن:**\n(ضع مسافة بين الأرقام إذا لم يصل الكود)")
                
                code_res = await conv.get_response()
                code = code_res.text.strip().replace(" ", "")
                
                try:
                    await new_client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    # معالجة التحقق بخطوتين (2FA)
                    await conv.send_message("**🔐 هذا الحساب محمي بالتحقق بخطوتين. أرسل كلمة المرور:**")
                    pwd_res = await conv.get_response()
                    try:
                        await new_client.sign_in(password=pwd_res.text.strip())
                    except Exception as e:
                        return await conv.send_message(f"**❌ كلمة المرور خاطئة:** `{e}`")
                except (PhoneCodeInvalidError, PhoneCodeExpiredError):
                    return await conv.send_message("**❌ الكود خاطئ أو منتهي الصلاحية.**")
                
                # نجاح الدخول
                me = await new_client.get_me()
                session_str = new_client.session.save()
                await save_new_acc(session_str, me)
                await conv.send_message(f"**✅ تم تسجيل الدخول وإضافة الحساب!**\n**👤 الاسم:** {me.first_name}\n**📱 الرقم:** `{me.phone}`")
                await new_client.disconnect()
            
            else:
                await conv.send_message("**❌ مدخلات غير معروفة. يرجى إرسال سيشن صحيح أو رقم هاتف يبدأ بـ +**")

    except Exception as e:
        LOGS.error(f"Error in add_account: {e}")
        await event.reply(f"**❌ حدث خطأ غير متوقع:** `{e}`")

# ═══════════════════════════════
# دوال مساعدة
# ═══════════════════════════════

async def save_new_acc(session, me):
    """حفظ الحساب في قاعدة البيانات"""
    data = get_accounts_data()
    # إيجاد رقم تسلسلي
    nums = [int(k) for k in data.keys() if k.isdigit()]
    new_idx = str(max(nums) + 1 if nums else 2)
    
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
    msg = f"**👥 حسابات الفحص المضافة:**\n\n**1 • الرئيسي** - {me.first_name} (`{me.phone}`)\n"
    for k, v in data.items():
        msg += f"**{k} • إضافي** - {v['name']} (`{v['phone']}`)\n"
    await edit_or_reply(event, msg)

@zedub.zed_cmd(pattern="جرب$", command=("جرب", plugin_category))
async def mass_check(event):
    "فحص الأرقام بالرد"
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await edit_or_reply(event, "**⎉╎يرجى الرد على قائمة أرقام.**")
    
    phones = list(dict.fromkeys(re.findall(r'\+\d{7,15}', reply.text)))
    if not phones:
        return await edit_or_reply(event, "**⎉╎لا توجد أرقام دولية في الرسالة.**")
    
    zed = await edit_or_reply(event, f"**🔍 جاري فحص {len(phones)} رقم...**")
    
    CHECK_RESULTS.clear()
    count = 0
    for ph in phones:
        try:
            # استخدام الحساب الرئيسي للفحص
            res = await zedub(ImportContactsRequest([InputPhoneContact(client_id=0, phone=ph, first_name="Z", last_name="C")]))
            if res.users:
                u = res.users[0]
                CHECK_RESULTS[ph] = {"id": u.id, "name": u.first_name, "prem": getattr(u, 'premium', False)}
                if u.id not in IMPORTED_IDS: IMPORTED_IDS.append(u.id)
        except: pass
        count += 1
        if count % 10 == 0: await zed.edit(f"**🔍 جاري الفحص... ({count}/{len(phones)})**")

    await zed.edit(f"**✅ انتهى الفحص.**\n**📱 الإجمالي:** {len(phones)}\n**✅ مسجل:** {len(CHECK_RESULTS)}\n**❌ غير مسجل:** {len(phones)-len(CHECK_RESULTS)}\n\nللعرض أرسل `.عرض الكل` وللتنظيف `.مسح` ")

@zedub.zed_cmd(pattern="عرض الكل$", command=("عرض الكل", plugin_category))
async def show_all(event):
    if not CHECK_RESULTS: return await edit_or_reply(event, "**❌ لا توجد نتائج.**")
    out = "**📋 قائمة الأرقام المسجلة:**\n\n"
    for p, v in CHECK_RESULTS.items():
        out += f"• `{p}` | {v['name']} {'⭐' if v['prem'] else ''}\n"
    await edit_or_reply(event, out)

@zedub.zed_cmd(pattern="مسح$", command=("مسح", plugin_category))
async def clear_it(event):
    if not IMPORTED_IDS: return await edit_or_reply(event, "**❌ القائمة فارغة.**")
    await zedub(DeleteContactsRequest(id=IMPORTED_IDS))
    IMPORTED_IDS.clear()
    await edit_or_reply(event, "**🗑️ تم مسح جهات الاتصال المستوردة بنجاح.**")