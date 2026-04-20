import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# جلب متغيراتك من ريندر
APP_ID = int(os.environ.get("APP_ID", 6))
API_HASH = os.environ.get("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
STRING_SESSION = os.environ.get("STRING_SESSION", "")

print("🔍 جاري البحث عن قاعدة البيانات المحفوظة في التليجرام...")

with TelegramClient(StringSession(STRING_SESSION), APP_ID, API_HASH) as client:
    # البحث في الرسائل المحفوظة عن الهاشتاج الخاص بقاعدة البيانات
    messages = client.iter_messages("me", search="#ZTELE_DB_BACKUP", limit=1)
    found = False
    for msg in messages:
        if msg.document:
            print("✅ تم العثور على قاعدة البيانات! جاري التحميل...")
            client.download_media(msg.document, file="ztele.db")
            print("✅ تم التحميل بنجاح. يمكن للسورس الآن العمل!")
            found = True
            break
    if not found:
        print("⚠️ لم يتم العثور على قاعدة بيانات سابقة. سيتم إنشاء واحدة جديدة.")