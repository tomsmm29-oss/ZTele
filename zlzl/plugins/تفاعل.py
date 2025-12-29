import asyncio
import re
from telethon import events
from telethon.tl.functions.messages import SetTypingRequest
from telethon.tl.types import SendMessageEmojiInteraction

# ---------------------------------------------------------------------------------
#  🎭 ZEDTHON SUPER INTERACTIVE EMOJI
# ---------------------------------------------------------------------------------
# التحديث: إضافة وضع السرعة القصوى (Rage Mode)
# 1 Emoji = Normal | 2 Emojis = Infinite Normal
# 3 Emojis = Fast   | 4 Emojis = Infinite Fast
# ---------------------------------------------------------------------------------

running_interactions = {}

try:
    from . import zedub
    from ..core.managers import edit_or_reply
except ImportError:
    zedub = None

def parse_advanced_command(text):
    """
    تحليل النص لاستخراج:
    1. نوع الايموجي
    2. الوضع (عادي/سريع)
    3. المدة (ثواني/لانهائي)
    """
    if not text: return None, "normal", 30

    # استخراج الايموجي الأول لمعرفته
    first_char = text[0]
    
    # حساب عدد مرات تكرار الايموجي في البداية
    # مثال: "😭😭😭 60" -> count = 3
    count = 0
    for char in text:
        if char == first_char:
            count += 1
        else:
            break
            
    # استخراج الوقت المخصص (إن وجد)
    # نأخذ النص ما بعد الايموجيات
    remainder = text[count:].strip()
    custom_time = int(remainder) if remainder.isdigit() else None
    
    # --- [خوارزمية تحديد الوضع] ---
    
    mode = "normal"
    duration = 30 # الافتراضي
    
    if count == 1:
        # .😭 -> عادي، 30 ثانية
        mode = "normal"
        duration = custom_time if custom_time else 30
        
    elif count == 2:
        # .😭😭 -> عادي، لانهائي (إلا لو كتب وقت)
        mode = "normal"
        duration = custom_time if custom_time else "inf"
        
    elif count == 3:
        # .😭😭😭 -> سريع جداً، 30 ثانية
        mode = "fast"
        duration = custom_time if custom_time else 30
        
    elif count >= 4:
        # .😭😭😭😭 -> سريع جداً، لانهائي (إلا لو كتب وقت)
        mode = "fast"
        duration = custom_time if custom_time else "inf"
        
    return first_char, mode, duration

@zedub.zed_cmd(pattern="^\.([^0-9\s].*)")
async def super_emoji_handler(event):
    input_str = event.pattern_match.group(1)
    
    # تحليل الأمر
    emoji, mode, duration = parse_advanced_command(input_str)
    
    # إرسال الايموجي الأساسي
    # ملاحظة: نرسل الايموجي مرة واحدة فقط ليعمل التفاعل عليه
    msg = await edit_or_reply(event, emoji)
    
    chat_id = event.chat_id
    msg_id = msg.id
    task_name = f"{chat_id}_{msg_id}"
    
    # إعدادات الحلقة
    if duration == "inf":
        loop_limit = 99999999
        status_msg = "لانهائي ♾️"
    else:
        # في الوضع السريع نزيد عدد اللفات لأن اللفة قصيرة جداً
        factor = 10 if mode == "fast" else 0.4 
        loop_limit = int(duration * factor) if mode == "fast" else int(duration / 2.5)
        status_msg = f"{duration} ثانية ⏱️"

    # تحديد سرعة النوم (Sleep)
    if mode == "fast":
        sleep_time = 0.1  # ⚡ سرعة مرعبة (10 نقرات في الثانية)
        mode_name = "🚀 FAST"
    else:
        sleep_time = 2.5  # 🐢 سرعة الرسوم المتحركة الطبيعية
        mode_name = "🐢 Normal"

    # تسجيل العملية
    running_interactions[task_name] = True
    
    # (اختياري) طباعة في الكونسول للمطور
    # print(f"Starting: {emoji} | Mode: {mode} | Time: {duration}")

    try:
        # التكرار
        # ملاحظة: في الوضع السريع نستخدم تكرار مكثف
        # ولكن نراعي عدم تعليق السورس لذلك نستخدم await sleep
        
        current_loop = 0
        while current_loop < loop_limit:
            if task_name not in running_interactions:
                break
            
            try:
                await event.client(SetTypingRequest(
                    peer=event.chat_id,
                    action=SendMessageEmojiInteraction(
                        emoticon=emoji,
                        msg_id=msg_id,
                        interaction_data=None 
                    )
                ))
            except Exception:
                pass # تجاهل الأخطاء إذا الايموجي لا يدعم التفاعل
            
            await asyncio.sleep(sleep_time)
            
            # في الوضع اللانهائي لا نزيد العداد لكي لا يتوقف
            if duration != "inf":
                if mode == "fast":
                    # حساب الوقت يختلف في السرعة
                    # كل 10 لفات = ثانية واحدة تقريباً
                    current_loop += 1
                else:
                    current_loop += 1
            
    except Exception as e:
        print(f"Error: {e}")
        
    if task_name in running_interactions:
        del running_interactions[task_name]

@zedub.zed_cmd(pattern="ايقاف التفاعل$")
async def stop_interaction(event):
    count = 0
    keys_to_remove = []
    for key in running_interactions:
        if str(event.chat_id) in key:
            keys_to_remove.append(key)
            count += 1
            
    for key in keys_to_remove:
        del running_interactions[key]
        
    await edit_or_reply(event, f"**⎉╎تـم ايقـاف {count} تفاعـلات 🛑**")
