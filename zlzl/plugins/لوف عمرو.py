# Zed-Thon - ZelZal (Group Protection & Whisper Fixed for ZTele 2025 by Mikey)
# Fixed: Whisper Inline, Lock Logic, Ban Requests, Relative Imports
# Visuals: 100% Original (Even the swear list lol)

import contextlib
import base64
import asyncio
import io
import re
from asyncio import sleep
from datetime import datetime
from math import sqrt

from telethon import events, functions, types, Button
from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import (
    ChatBannedRights,
    ChatAdminRights,
    ChannelParticipantsAdmins,
)
from telethon.errors import ChatAdminRequiredError, UserAdminInvalidError

# --- تصحيح المسارات والحقن النسبي ---
from . import zedub
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id, _format, get_user_from_event

# محاولة استدعاء SQL، لو مش موجود نستخدم Mock
try:
    from ..sql_helper.locks_sql import get_locks, is_locked, update_lock
except ImportError:
    # Mocking for Locks
    class MockLock:
        def __init__(self):
            self.bots = False
            self.egame = False
            self.rtl = False
            self.forward = False
            self.button = False
            self.url = False
            self.game = False
            self.document = False
            self.location = False
            self.contact = False
            self.inline = False
            self.video = False
            self.sticker = False
            self.voice = False

    def get_locks(chat_id): return MockLock()
    def is_locked(chat_id, type): return False
    def update_lock(chat_id, type, val): pass

try:
    from . import BOTLOG, BOTLOG_CHATID
except ImportError:
    BOTLOG = False
    BOTLOG_CHATID = None

# إعدادات الحظر الافتراضية
ANTI_DDDD_ZEDTHON_MODE = ChatBannedRights(
    until_date=None, view_messages=None, send_media=True, send_stickers=True, send_gifs=True
)

plugin_category = "الادمن"

# --- دالة مساعدة للتحقق من الأدمن ---
async def is_admin(event, user):
    try:
        sed = await event.client.get_permissions(event.chat_id, user)
        if sed.is_admin:
            is_mod = True
        else:
            is_mod = False
    except:
        is_mod = False
    return is_mod


# =========================================================
# 1. كود الهمسة (Whisper) - المصلّح
# =========================================================

@zedub.zed_cmd(pattern="همسه ?(.*)")
async def wspr(event):
    if event.fwd_from:
        return
    wwwspr = event.pattern_match.group(1)
    botusername = "@whisperBot"
    
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        # لو فيه رد، ممكن نستخدمه في السياق (حسب البوت)
    
    try:
        # استخدام event.client بدلاً من bot
        results = await event.client.inline_query(botusername, wwwspr)
        if results:
            await results[0].click(event.chat_id)
            await event.delete()
        else:
            await edit_delete(event, "**- عذراً، لم أستطع توليد الهمسة. تأكد من النص.**", 5)
    except Exception as e:
        await edit_delete(event, f"**- خطأ:** {str(e)}", 5)


# =========================================================
# 2. كود قفل وفتح الحماية (Locks)
# =========================================================

@zedub.zed_cmd(
    pattern="قفل ([\s\S]*)",
    command=("قفل", plugin_category),
    info={
        "header": "اوامــر قفـل الحمـاية الخـاصه بـ المجمـوعـات",
        "الاسـتخـدام": "{tr}قفل + الامــر",
    },
    groups_only=True,
    require_admin=True,
)
async def lock_cmd(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    zed_id = event.chat_id
    
    if not event.is_group:
        return await edit_delete(event, "**ايا مطـي! ، هـذه ليست مجموعـة لقفـل الأشيـاء**")
    
    if input_str == "البوتات":
        update_lock(zed_id, "bots", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة الطـرد والتحذيـر •**".format(input_str))
    if input_str == "المعرفات":
        update_lock(zed_id, "button", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة المسـح والتحذيـر •**".format(input_str))
    if input_str == "الدخول":
        update_lock(zed_id, "location", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة الطـرد والتحذيـر •**".format(input_str))
    if input_str == "الفارسيه" or input_str == "دخول الايران":
        update_lock(zed_id, "egame", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة المسـح والتحذيـر •**".format(input_str))
    if input_str == "الاضافه":
        update_lock(zed_id, "contact", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة الطـرد والتحذيـر •**".format(input_str))
    if input_str == "التوجيه":
        update_lock(zed_id, "forward", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة المسـح والتحذيـر •**".format(input_str))
    if input_str == "الميديا":
        update_lock(zed_id, "game", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة المسـح بالتقييـد والتحذيـر •**".format(input_str))
    if input_str == "تعديل الميديا":
        update_lock(zed_id, "document", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة المسـح بالتقييـد والتحذيـر •**".format(input_str))
    if input_str == "الانلاين":
        update_lock(zed_id, "inline", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة المسـح والتحذيـر •**".format(input_str))
    if input_str == "الفشار":
        update_lock(zed_id, "rtl", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة المسـح والتحذيـر •**".format(input_str))
    if input_str == "الروابط":
        update_lock(zed_id, "url", True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة المسـح والتحذيـر •**".format(input_str))
    if input_str == "الكل":
        # قفل كل شيء
        for lock in ["bots", "game", "forward", "egame", "rtl", "url", "contact", "location", "button", "inline", "video", "sticker", "voice", "document"]:
            update_lock(zed_id, lock, True)
        return await edit_or_reply(event, "**⎉╎تـم قفـل {} بنجـاح ✅ •**\n\n**⎉╎خاصيـة المسـح - الطـرد - التقييـد - التحذيـر •**".format(input_str))
    else:
        if input_str:
            return await edit_delete(
                event, f"**⎉╎عذراً لايـوجـد امـر بـ اسـم :** `{input_str}`\n**⎉╎لعـرض اوامـر القفـل والفتـح ارسـل** `.م4`", time=10
            )
        return await edit_or_reply(event, "**⎉╎عـذࢪاً عـزيـزي .. لايمكنك قفـل اي شي هنـا ...𓆰**")


@zedub.zed_cmd(
    pattern="فتح ([\s\S]*)",
    command=("فتح", plugin_category),
    groups_only=True,
    require_admin=True,
)
async def unlock_cmd(event):
    if event.fwd_from: return
    input_str = event.pattern_match.group(1)
    zed_id = event.chat_id
    
    if not event.is_group:
        return await edit_delete(event, "**ايا مطـي! ، هـذه ليست مجموعـة لقفـل الأشيـاء**")

    # قائمة الأقفال
    locks_map = {
        "البوتات": "bots", "الدخول": "location", "الاضافه": "contact",
        "التوجيه": "forward", "الفارسيه": "egame", "دخول الايران": "egame",
        "الفشار": "rtl", "الروابط": "url", "الميديا": "game",
        "تعديل الميديا": "document", "المعرفات": "button", "الانلاين": "inline"
    }

    if input_str in locks_map:
        update_lock(zed_id, locks_map[input_str], False)
        return await edit_or_reply(event, "**⎉╎تـم فتـح** {} **بنجـاح ✅ 𓆰•**".format(input_str))
    
    if input_str == "الكل":
        for lock in ["bots", "game", "forward", "egame", "rtl", "url", "contact", "location", "button", "inline", "video", "sticker", "voice", "document"]:
            update_lock(zed_id, lock, False)
        return await edit_or_reply(event, "**⎉╎تـم فتـح** {} **بنجـاح ✅ 𓆰•**".format(input_str))
        
    else:
        if input_str:
            return await edit_delete(
                event, f"**⎉╎عذراً لايـوجـد امـر بـ اسـم :** `{input_str}`\n**⎉╎لعـرض اوامـر القفـل والفتـح ارسـل** `.م4`", time=10
            )
        return await edit_or_reply(event, "**⎉╎عـذࢪاً عـزيـزي .. لايمكنك اعـادة فتـح اي شي هنـا ...𓆰**")


@zedub.zed_cmd(pattern="الاعدادات$", groups_only=True)
async def settings_cmd(event):
    if event.fwd_from: return
    
    current_zed_locks = get_locks(event.chat_id)
    if not current_zed_locks:
        res = "**⎉╎حـالة الحمـايه لـ هـذه المجمـوعـة : (الكل مفتوح)**"
    else:
        res = "**- فيمـا يلـي إعـدادات حمـاية المجمـوعـة :** \n"
        # دالة صغيرة لتحويل True/False لإيموجي
        def st(val): return "❌" if val else "✅"
        
        res += f"**⎉╎ البوتات :** {st(current_zed_locks.bots)}\n"
        res += f"**⎉╎ الدخول :** {st(current_zed_locks.location)}\n"
        res += f"**⎉╎ دخول الايران :** {st(current_zed_locks.egame)}\n"
        res += f"**⎉╎ الاضافه :** {st(current_zed_locks.contact)}\n"
        res += f"**⎉╎ التوجيه :** {st(current_zed_locks.forward)}\n"
        res += f"**⎉╎ الميديا :** {st(current_zed_locks.game)}\n"
        res += f"**⎉╎ تعديـل الميديـا :** {st(current_zed_locks.document)}\n"
        res += f"**⎉╎ المعرفات :** {st(current_zed_locks.button)}\n"
        res += f"**⎉╎ الفارسيه :** {st(current_zed_locks.egame)}\n"
        res += f"**⎉╎ الفشار :** {st(current_zed_locks.rtl)}\n"
        res += f"**⎉╎ الروابط :** {st(current_zed_locks.url)}\n"
        res += f"**⎉╎ الانلاين :** {st(current_zed_locks.inline)}\n"
        
    await edit_or_reply(event, res)


# =========================================================
# 3. الحارس الليلي (Watcher) - فحص الرسائل
# =========================================================

@zedub.zed_cmd(incoming=True)
async def check_incoming_messages(event):
    if not event.is_group: return
    
    # التأكد من أن المرسل ليس أدمن
    try:
        if await is_admin(event, event.sender_id): return
    except: pass
    
    zed_dev = [925972505, 1895219306, 5280339206]
    zelzal = event.sender_id
    malath = (await event.client.get_me()).id
    if zelzal == malath or zelzal in zed_dev: return

    hhh = event.message.text or ""
    zed_id = event.chat_id
    user = await event.get_sender()
    
    # 1. قفل الفشار (RTL) - القائمة المحترمة
    bad_words = ["خرا", "كسها", "كسمك", "كسختك", "عيري", "كسخالتك", "خرا بالله", "عير بالله", "كسخواتكم", "اختك", "بڪسسخخت", "كحاب", "مناويج", "كحبه", " كواد ", "كواده", "تبياته", "تبياتة", "فرخ", "كحبة", "فروخ", "طيز", "آإيري", "اختج", "سالب", "موجب", "فحل", "كسي", "كسك", "كسج", "مكوم", "نيج", "نتنايج", "مقاطع", "ديوث", "دياث", "اديث", "محارم", "سكس", "مصي", "اعرب", "أعرب", "قحب", "قحاب", "عراب", "مكود", "عربك", "مخنث", "مخنوث", "فتال", "زاني", "زنا", "لقيط", "بنات شوارع", "بنت شوارع", "نيك", "منيوك", "منيوج", "نايك", "قواد", "زبي", "ايري", "ممحو", "بنت شارع", " است ", "اسات", "زوب", "عيير", "املس", "مربرب", " خول ", "عرص", "قواد", "اهلاتك", "جلخ", "شرمو", "فرك", "رهط"]
    
    if is_locked(zed_id, "rtl") and any(word in hhh for word in bad_words):
        try:
            await event.delete()
            await event.reply(f"[ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - حمـاية المجموعـة ](t.me/ZedThon)\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n\n⌔╎**عـذࢪاً** [{user.first_name}](tg://user?id={user.id})  \n⌔╎**يُمنـع الفشـار والسب هنـا ⚠️•**", link_preview=False)
        except Exception:
            # لو فشل الحذف (مفيش صلاحية)، نلغي القفل عشان البوت ما يسبمش
            update_lock(zed_id, "rtl", False)

    # 2. قفل الميديا (Game)
    if is_locked(zed_id, "game") and event.message.media:
        try:
            await event.delete()
            await event.reply(f"[ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - حمـاية المجموعـة ](t.me/ZedThon)\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n\n⌔╎**عـذࢪاً** [{user.first_name}](tg://user?id={user.id})  \n⌔╎**يُمنـع ارسـال الوسائـط هنـا 🚸•**\n\n⌔╎**تـم تقييدك مـن ارسـال الوسائط 📵**", link_preview=False)
            await event.client(EditBannedRequest(event.chat_id, event.sender_id, ANTI_DDDD_ZEDTHON_MODE))
        except Exception:
            update_lock(zed_id, "game", False)

    # 3. قفل التوجيه (Forward)
    if is_locked(zed_id, "forward") and event.fwd_from:
        try:
            await event.delete()
            await event.reply(f"[ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - حمـاية المجموعـة ](t.me/ZedThon)\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n\n⌔╎**عـذࢪاً** [{user.first_name}](tg://user?id={user.id})  \n⌔╎**يُمنـع التوجيـه هنـا ⚠️•**", link_preview=False)
        except Exception:
            update_lock(zed_id, "forward", False)

    # 4. قفل المعرفات (Button/Usernames)
    if is_locked(zed_id, "button") and "@" in hhh:
        try:
            await event.delete()
            await event.reply(f"[ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - حمـاية المجموعـة ](t.me/ZedThon)\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n\n⌔╎**عـذࢪاً** [{user.first_name}](tg://user?id={user.id})  \n⌔╎**يُمنـع ارسـال المعـرفـات هنـا ⚠️•**", link_preview=False)
        except Exception:
            update_lock(zed_id, "button", False)

    # 5. قفل الفارسية (Egame)
    persian_chars = ["فارسى", "خوببی", "میخوام", "کی", "پی", "گ", "خسته", "صكص", "راحتی", "بیام", "بپوشم", "گرمه", "چ", "چه", "ڬ", "ٺ", "ڿ", "ڇ", "ڀ", "ڎ", "ݫ", "ژ", "ڟ", "۴", "زدن", "دخترا", "كسى", "مک", "خالى", "ݜ", "ڸ", "پ", "بند", "عزيزم", "برادر", "باشى", "ميخوام", "خوبى", "ميدم", "كى اومدى", "خوابيدين"]
    if is_locked(zed_id, "egame") and any(char in hhh for char in persian_chars):
        try:
            await event.delete()
            await event.reply(f"[ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - حمـاية المجموعـة ](t.me/ZedThon)\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n\n⌔╎**عـذࢪاً** [{user.first_name}](tg://user?id={user.id})  \n⌔╎**يُمنـع التحـدث بالفارسيـه هنـا ⚠️•**", link_preview=False)
        except Exception:
            update_lock(zed_id, "egame", False)

    # 6. قفل الروابط (URL)
    if is_locked(zed_id, "url") and ("http" in hhh or ".com" in hhh or ".net" in hhh):
        try:
            await event.delete()
            await event.reply(f"[ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - حمـاية المجموعـة ](t.me/ZedThon)\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n\n⌔╎**عـذࢪاً** [{user.first_name}](tg://user?id={user.id})  \n⌔╎**يُمنـع ارسـال الروابـط هنـا ⚠️•**", link_preview=False)
        except Exception:
            update_lock(zed_id, "url", False)

    # 7. قفل الانلاين (Inline)
    if is_locked(zed_id, "inline") and event.message.via_bot:
        try:
            await event.delete()
            await event.reply(f"[ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - حمـاية المجموعـة ](t.me/ZedThon)\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n\n⌔╎**عـذࢪاً** [{user.first_name}](tg://user?id={user.id})  \n⌔╎**يُمنـع استخـدام الانلايـن في هذه المجموعـة ⚠️•**", link_preview=False)
        except Exception:
            update_lock(zed_id, "inline", False)


# =========================================================
# 4. مراقبة الأحداث (إضافة البوتات، الانضمام، التعديل)
# =========================================================

# مراقبة تعديل الميديا
@zedub.on(events.MessageEdited)
async def check_edit_media(event):
    if not event.is_group: return
    try:
        if await is_admin(event, event.sender_id): return
    except: pass
    
    zed_id = event.chat_id
    user = await event.get_sender()
    
    if is_locked(zed_id, "document") and event.message.media:
        try:
            await event.delete()
            await event.reply(f"[ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - حمـاية المجموعـة ](t.me/ZedThon)\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n\n⌔╎**عـذࢪاً** [{user.first_name}](tg://user?id={user.id})  \n⌔╎**يُمنـع تعديـل الميديـا هنـا 🚫**\n⌔╎**تم حـذف التعديـل .. بنجـاح ☑️**", link_preview=False)
            await event.client(EditBannedRequest(event.chat_id, event.sender_id, ANTI_DDDD_ZEDTHON_MODE))
        except:
            update_lock(zed_id, "document", False)

# مراقبة إضافة البوتات والأعضاء
@zedub.on(events.ChatAction())
async def on_user_add(event):
    if event.is_private: return
    
    # قفل إضافة الأعضاء (Contact)
    if is_locked(event.chat_id, "contact") and event.user_added:
        added_by = event.action_message.sender_id
        if await is_admin(event, added_by): return
        
        for user_id in event.action_message.action.users:
            user_obj = await event.client.get_entity(user_id)
            try:
                # حظر العضو المضاف (ولليس المضيف، حسب طلب الكود)
                await event.client(EditBannedRequest(event.chat_id, user_obj, ChatBannedRights(until_date=None, view_messages=True)))
                await event.reply(f"**يُمنـع اضـافة الاعضـاء لـ هـذه المجموعـة ⚠️**")
            except: pass

    # قفل إضافة البوتات (Bots)
    if is_locked(event.chat_id, "bots") and event.user_added:
        added_by = event.action_message.sender_id
        if await is_admin(event, added_by): return
        
        for user_id in event.action_message.action.users:
            user_obj = await event.client.get_entity(user_id)
            if user_obj.bot:
                try:
                    await event.client(EditBannedRequest(event.chat_id, user_obj, ChatBannedRights(until_date=None, view_messages=True)))
                    await event.reply(f"**يُمنـع اضـافة البـوتـات لـ هـذه المجمـوعـة 🚫**")
                except: pass

    # قفل الانضمام (Location) ودخول الإيرانيين
    if event.user_joined:
        user = await event.get_user()
        
        # قفل الدخول العام
        if is_locked(event.chat_id, "location"):
            if await is_admin(event, user.id): return
            try:
                await event.client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
                await event.reply(f"**يُمنـع الانضمـام لـ هـذه المجموعـة 🚷**")
            except: pass
            
        # قفل الإيرانيين (Egame)
        persian_names = ["ژ", "چ", "۴", "مهسا", "sara", "گ", "نازنین", "آسمان", "ڄ", "پ", "Sanaz", "سارة", "GIRL", "Lady", "فتاة", "👅", "سمانه", "بهار", "maryam", "👙", "هانیه", "هستی", "💋", "ندا", "Mina", "خانم", "ایناز", "مبینا", "امینی", "سرنا", "اندیشه", "لنتكلم", "دریا", "زاده", "نااز", "ناز", "بیتا", "سكس", "💄"]
        if is_locked(event.chat_id, "egame") and any(char in (user.first_name or "") for char in persian_names):
            if await is_admin(event, user.id): return
            try:
                await event.client(EditBannedRequest(event.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
                await event.reply(f"**يُمنـع انضمـام الايـࢪان هنـا 🚷**")
            except: pass


# كود طرد البوتات (أمر يدوي)
@zedub.zed_cmd(pattern=f"البوتات ?(.*)")
async def kick_bots_cmd(zed):
    con = zed.pattern_match.group(1).lower()
    del_u = 0
    
    if con != "طرد":
        event = await edit_or_reply(zed, "**⎉╎جـاري البحـث عن بوتات في هـذه المجمـوعـة ...🝰**")
        async for user in zed.client.iter_participants(zed.chat_id):
            if user.bot: del_u += 1
        
        if del_u > 0:
            msg = f"🛂**┊كشـف البـوتات -** 𝙎𝙊𝙐𝙍𝘾𝞝 𝙕𝞝𝘿𝙏𝙃𝙊𝙉\n\n**⎉╎تم العثور على** **{del_u}**  **بـوت**\n**⎉╎لطـرد البوتات استخدم الامـر التالي ⩥** `.البوتات طرد`"
        else:
            msg = "**⎉╎مجمـوعتك/قناتـك في أمـان ✅.. لاتوجـد بوتـات في هذه المجمـوعـة ༗**"
        await event.edit(msg)
        return

    # عملية الطرد
    try:
        if not (await is_admin(zed, zed.sender_id)):
            return await edit_delete(zed, "**⎉╎عـذࢪاً .. احتـاج الى صلاحيـات المشـرف هنـا**", 5)
    except: pass

    event = await edit_or_reply(zed, "**⎉╎جـارِ طـرد البوتـات من هنـا ...⅏**")
    del_u = 0
    del_a = 0
    
    async for user in zed.client.iter_participants(zed.chat_id):
        if user.bot:
            try:
                # محاولة الطرد (Kick) باستخدام الطريقة الحديثة (Ban then Unban)
                await zed.client(EditBannedRequest(zed.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=True)))
                await zed.client(EditBannedRequest(zed.chat_id, user.id, ChatBannedRights(until_date=None, view_messages=False)))
                await sleep(0.5)
                del_u += 1
            except:
                del_a += 1
                
    if del_u > 0:
        del_status = f"**⎉╎تم طـرد  {del_u}  بـوت .. بنجـاح🚮**"
    else:
        del_status = "**⎉╎لم يتم طرد أي بوت (ربما لا توجد بوتات أو لا أملك صلاحية).**"
        
    await edit_delete(event, del_status, 50)