import asyncio
import time
import re
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import (
    UpdateUserStatus,
    UpdateReadHistoryOutbox,
    UpdateReadChannelOutbox,
    UpdateDraftMessage,
    UserStatusOnline
)

from . import zedub
from ..core.managers import edit_or_reply

# --- استدعاء قاعدة البيانات لكليشات زدثون ---
try:
    from ..sql_helper.globals import gvarstatus
except ImportError:
    def gvarstatus(val):
        return None

# --- نصوص الكليشة الفخمة ---
ZEDM = gvarstatus("CUSTOM_ALIVE_EMOJI") or "✦ "

# --- المتغيرات العالمية لنظام الرادار ---
RADAR_ENABLED = False
LAST_HUMAN_ACTION = time.time()
CURRENT_NAME_STATE = "offline"
RADAR_TASK = None

# حفظ بيانات المستخدم الأصلية
ORIGINAL_FIRST_NAME = ""
ORIGINAL_LAST_NAME = ""
MY_ID = 0

# =======================================================
# دالة لتنظيف الاسم الأخير من الحالات السابقة
# =======================================================
def clean_last_name(name):
    if not name:
        return ""
    name = re.sub(r'\(متصل\)', '', name)
    name = re.sub(r'\(غير متصل\)', '', name)
    return name.strip()

# =======================================================
# 1. نظام تغيير الأسماء (Anti-Flood Gate)
# =======================================================
async def update_profile_name(client, state):
    global CURRENT_NAME_STATE, ORIGINAL_FIRST_NAME, ORIGINAL_LAST_NAME
    
    # فلتر الحماية من الحظر: لا ترسل طلب إذا كانت الحالة لم تتغير
    if CURRENT_NAME_STATE == state:
        return
        
    try:
        if state == "online":
            new_last_name = f"{ORIGINAL_LAST_NAME} (متصل)".strip()
        elif state == "offline":
            new_last_name = f"{ORIGINAL_LAST_NAME} (غير متصل)".strip()
        else:
            new_last_name = ORIGINAL_LAST_NAME

        await client(UpdateProfileRequest(
            first_name=ORIGINAL_FIRST_NAME,
            last_name=new_last_name
        ))
        CURRENT_NAME_STATE = state
    except Exception:
        pass

# =======================================================
# 2. حلقة الموت الصامت (مؤقت الـ 20 ثانية في الخلفية)
# =======================================================
async def radar_background_worker(client):
    global RADAR_ENABLED, LAST_HUMAN_ACTION
    while RADAR_ENABLED:
        await asyncio.sleep(1)
        time_passed = time.time() - LAST_HUMAN_ACTION
        
        # طالما العداد أقل من 20، ستبقى متصلاً ولن يرسل طلبات متكررة بفضل فلتر الحماية
        if time_passed < 20:
            await update_profile_name(client, "online")
        # بمجرد أن تتعدى 20 ثانية، تتغير الحالة وتتوقف الطلبات
        elif time_passed >= 20:
            await update_profile_name(client, "offline")

# =======================================================
# 3. صائد الأحداث الخام (مستشعر نبضات التزامن البشري)
# =======================================================
@zedub.on(events.Raw)
async def session_sync_radar(event):
    global RADAR_ENABLED, LAST_HUMAN_ACTION, MY_ID
    if not RADAR_ENABLED or MY_ID == 0:
        return

    # التقاط الأونلاين الفعلي
    if isinstance(event, UpdateUserStatus):
        if getattr(event, 'user_id', 0) == MY_ID:
            if isinstance(event.status, UserStatusOnline):
                LAST_HUMAN_ACTION = time.time()
        return

    # التقاط القراءة والكتابة
    if isinstance(event, (UpdateReadHistoryOutbox, UpdateReadChannelOutbox, UpdateDraftMessage)):
        LAST_HUMAN_ACTION = time.time()

# =======================================================
# 4. أوامر التشغيل، الإيقاف، والاختبار
# =======================================================
@zedub.zed_cmd(
    pattern="تفعيل الكشف$",
    command=("تفعيل الكشف", "الادمن"),
    info={"header": "تفعيل نظام تغيير الاسم التلقائي بناءً على نشاطك الحقيقي."}
)
async def enable_radar(event):
    global RADAR_ENABLED, RADAR_TASK, LAST_HUMAN_ACTION
    global ORIGINAL_FIRST_NAME, ORIGINAL_LAST_NAME, MY_ID
    
    zed = await edit_or_reply(event, "<b>⎉╎جـاري الـتـفـعـيـل...</b>", parse_mode="html")
    
    if RADAR_ENABLED:
        return await zed.edit("<b>- نـظـام الـكـشـف مـفـعـل مـسـبـقـاً ✅</b>", parse_mode="html")
        
    me = await event.client.get_me()
    MY_ID = me.id
    ORIGINAL_FIRST_NAME = me.first_name or "مستخدم"
    ORIGINAL_LAST_NAME = clean_last_name(me.last_name)
    
    RADAR_ENABLED = True
    LAST_HUMAN_ACTION = time.time()
    
    if RADAR_TASK is None or RADAR_TASK.done():
        RADAR_TASK = event.client.loop.create_task(radar_background_worker(event.client))
        
    caption = f"<b>🛂┊نـظـام الـكـشـف - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉</b>\n\n"
    caption += f"⎉╎الـحـالـة ⩥ مـفـعـل ✅\n"
    caption += f"⎉╎الاسـم ⩥ {ORIGINAL_FIRST_NAME} {ORIGINAL_LAST_NAME}\n"
    caption += f"⎉╎الـرادار ⩥ 20 ثـانـيـة ⏱️\n\n"
    caption += f"ـ ━─━── 𝙕𝞝𝘿 ──━─━ ـ\n\n"
    caption += f"<b>{ZEDM}يـتـم الآن تـحـديـث حـالـتـك تـلـقـائـيـاً بـصـمـت...</b>"
    
    await zed.edit(caption, parse_mode="html")


@zedub.zed_cmd(
    pattern="تعطيل الكشف$",
    command=("تعطيل الكشف", "الادمن"),
    info={"header": "إيقاف نظام الكشف وإرجاع اسمك الطبيعي."}
)
async def disable_radar(event):
    global RADAR_ENABLED, RADAR_TASK, CURRENT_NAME_STATE
    
    zed = await edit_or_reply(event, "<b>⎉╎جـاري الـتـعـطـيـل...</b>", parse_mode="html")
    
    if not RADAR_ENABLED:
        return await zed.edit("<b>- نـظـام الـكـشـف مـعـطـل مـسـبـقـاً ❌</b>", parse_mode="html")
        
    RADAR_ENABLED = False
    CURRENT_NAME_STATE = "none"
    
    if RADAR_TASK and not RADAR_TASK.done():
        RADAR_TASK.cancel()
        
    try:
        await event.client(UpdateProfileRequest(
            first_name=ORIGINAL_FIRST_NAME, 
            last_name=ORIGINAL_LAST_NAME
        ))
    except:
        pass
        
    caption = f"<b>🛂┊نـظـام الـكـشـف - 𝙕𝞝𝘿𝙏𝙃𝙊𝙉</b>\n\n"
    caption += f"⎉╎الـحـالـة ⩥ مـعـطـل ❌\n"
    caption += f"⎉╎الـرادار ⩥ مـتـوقـف 🔕\n\n"
    caption += f"ـ ━─━── 𝙕𝞝𝘿 ──━─━ ـ\n\n"
    caption += f"<b>{ZEDM}تـم إرجـاع إسـمـك لـوضـعـه الـطـبـيـعـي بـنـجـاح.</b>"
    
    await zed.edit(caption, parse_mode="html")

# =======================================================
# 5. أمر الاختبار الفخم
# =======================================================
@zedub.zed_cmd(pattern="اختبار$")
async def test_cmd(event):
    # علامة تحميل سريعة
    zed = await edit_or_reply(event, "<b>⇆</b>", parse_mode="html")
    
    # كليشة V4
    caption = f"<b>{ZEDM} 𝙑4 𝙄𝙎 𝙇𝙄𝙑𝙀 ⚡</b>"
    
    # إرسال الكليشة
    await zed.edit(caption, parse_mode="html") 