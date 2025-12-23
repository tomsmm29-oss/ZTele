import asyncio import requests import logging

from telethon import events, Button from telethon.errors.rpcerrorlist import UserNotParticipantError from telethon.tl.functions.channels import EditBannedRequest, ExportChatInviteRequest from telethon.tl.types import ChatBannedRights

--- تصحيح المسارات والحقن النسبي ---

from . import zedub from ..core.logger import logging from ..core.managers import edit_delete, edit_or_reply

محاولة استدعاء Config و SQL و BOTLOG

try: from ..Config import Config cmdhd = Config.COMMAND_HAND_LER except ImportError: class Config: TG_BOT_TOKEN = None COMMAND_HAND_LER = "." cmdhd = "."

try: from ..sql_helper.globals import addgvar, delgvar, gvarstatus except ImportError: def addgvar(x, y): return None def delgvar(x): return None def gvarstatus(val): return None

try: from . import BOTLOG, BOTLOG_CHATID except ImportError: BOTLOG_CHATID = None

LOGS = logging.getLogger(name) plugin_category = "الادمن"

---------- مساعدة: فحص الاشتراك عن طريق بوت API ----------

def bot_api_check_member(bot_token: str, chat_id, user_id) -> (bool, dict): """ترجع tuple (is_member, raw_json)""" try: url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={chat_id}&user_id={user_id}" r = requests.get(url, timeout=10) data = r.json() if not data.get("ok"): return (False, data) status = data.get("result", {}).get("status", "") # حالات تعتبر مشترك/عضو if status in ("creator", "administrator", "member", "restricted"): return (True, data) return (False, data) except Exception as e: return (False, {"error": str(e)})

async def get_channel_link_or_username(client, ch): """يعطي رابط الاشتراك: username link أو رابط دعوة للقناة الخاصة""" try: # ch قد يكون str "-10012345" أو int أو "@username" try: ch_int = int(ch) except Exception: ch_int = ch

c = await client.get_entity(ch_int)
    if hasattr(c, 'username') and c.username:
        return f"https://t.me/{c.username}", c.username
    # قناة خاصة -> حاول جلب رابط دعوة عبر بوت
    try:
        if zedub.tgbot:
            ra = await zedub.tgbot(ExportChatInviteRequest(c))
            return ra.link, 'قناة خاصة'
    except Exception:
        return ("#", 'القناة')
except Exception as e:
    LOGS.info(f"get_channel_link error: {e}")
    return ("#", 'القناة')

---------- أوامر ضبط القناة/الكروب للـاشتراك ----------

@zedub.zed_cmd(pattern="(ضع الاشتراك خاص|وضع الاشتراك خاص)(?:\s|$)([\s\S]*)") async def set_pm_sub(event): if input_str := event.pattern_match.group(2): try: p = await event.client.get_entity(input_str) except Exception as e: return await edit_delete(event, f"{e}", 5) try: if hasattr(p, 'first_name') and p.first_name: await asyncio.sleep(1.5) delgvar("Custom_Pm_Channel") addgvar("Custom_Pm_Channel", f"-100{p.id}") return await edit_or_reply( event, f"⎉╎تم إضافة قناة الاشتراك الاجباري للخاص .. بنجـاح ☑️\n\n**⎉╎يوزر القناة : ↶** {input_str}\n**⎉╎ايدي القناة : ↶** {p.id}\n\n**⎉╎ارسـل الان** .اشتراك خاص") except Exception: try: if hasattr(p, 'title') and p.title: await asyncio.sleep(1.5) delgvar("Custom_Pm_Channel") addgvar("Custom_Pm_Channel", f"-100{p.id}") return await edit_or_reply( event, f"⎉╎تم إضافة قناة الاشتراك الاجباري للخاص .. بنجـاح ☑️\n\n**⎉╎اسم القناة : ↶** {p.title}\n**⎉╎ايدي القناة : ↶** {p.id}\n\n**⎉╎ارسـل الان** .اشتراك خاص") except Exception as e: LOGS.info(str(e)) await edit_or_reply(event, "⪼ أدخل معـرف القناة او قم باستخدام الامر داخل القناة") elif event.reply_to_msg_id: r_msg = await event.get_reply_message() await asyncio.sleep(1.5) delgvar("Custom_Pm_Channel") addgvar("Custom_Pm_Channel", event.chat_id) await edit_or_reply( event, f"⎉╎تم إضافة قناة الاشتراك الاجباري للخاص .. بنجـاح ☑️\n\n**⎉╎ايدي القناة : ↶** {event.chat_id}\n\n**⎉╎ارسـل الان** .اشتراك خاص", )

else:
    await asyncio.sleep(1.5)
    delgvar("Custom_Pm_Channel")
    addgvar("Custom_Pm_Channel", event.chat_id)
    await edit_or_reply(event, f"**⎉╎تم إضافة قناة الاشتراك الاجباري للخاص .. بنجـاح ☑️**\n\n**⎉╎ايدي القناة : ↶** `{event.chat_id}`\n\n**⎉╎ارسـل الان** `.اشتراك خاص`")

@zedub.zed_cmd(pattern="(ضع الاشتراك كروب|وضع الاشتراك كروب)(?:\s|$)([\s\S]*)") async def set_grp_sub(event): if input_str := event.pattern_match.group(2): try: p = await event.client.get_entity(input_str) except Exception as e: return await edit_delete(event, f"{e}", 5) try: if hasattr(p, 'first_name') and p.first_name: await asyncio.sleep(1.5) delgvar("Custom_G_Channel") addgvar("Custom_G_Channel", f"-100{p.id}") return await edit_or_reply( event, f"⎉╎تم إضافة قناة الاشتراك الاجباري للكروب .. بنجـاح ☑️\n\n**⎉╎يوزر القناة : ↶** {input_str}\n**⎉╎ايدي القناة : ↶** {p.id}\n\n**⎉╎ارسـل الان** .اشتراك كروب") except Exception: try: if hasattr(p, 'title') and p.title: await asyncio.sleep(1.5) delgvar("Custom_G_Channel") addgvar("Custom_G_Channel", f"-100{p.id}") return await edit_or_reply( event, f"⎉╎تم إضافة قناة الاشتراك الاجباري للكروب .. بنجـاح ☑️\n\n**⎉╎اسم القناة : ↶** {p.title}\n**⎉╎ايدي القناة : ↶** {p.id}\n\n**⎉╎ارسـل الان** .اشتراك كروب") except Exception as e: LOGS.info(str(e)) await edit_or_reply(event, "⪼ أدخل إما اسم مستخدم أو الرد على المستخدم") elif event.reply_to_msg_id: r_msg = await event.get_reply_message() await asyncio.sleep(1.5) delgvar("Custom_G_Channel") addgvar("Custom_G_Channel", event.chat_id) await edit_or_reply( event, f"⎉╎تم إضافة قناة الاشتراك الاجباري للكروب .. بنجـاح ☑️\n\n**⎉╎ايدي القناة : ↶** {event.chat_id}\n\n**⎉╎ارسـل الان** .اشتراك كروب", )

---------- تفعيل / تعطيل الاشتراك الاجباري ----------

@zedub.zed_cmd(pattern="^اشتراك(?:\s+|$)([\s\S]*)$") async def supc(event): ty = event.text ty = ty.replace(".اشتراك", "") ty = ty.replace(" ", "") if len(ty) < 2: return await edit_delete(event, "⎉╎اختـر نوع الاشتـراك الاجبـاري اولاً :\n\n.اشتراك كروب\n\n.اشتراك خاص") # كروب if ty in ("كروب", "جروب", "قروب", "مجموعة", "مجموعه"): if not event.is_group: return await edit_delete(event, "⎉╎عـذراً .. هذه ليست مجمـوعـة ؟!") if gvarstatus("sub_group") == str(event.chat_id): return await edit_delete(event, "⎉╎الاشتـراك الاجبـاري لـ هذه المجمـوعـة مفعـل مسبقـاً") if gvarstatus("sub_group"): return await edit_or_reply(event, "⎉╎الاشتـراك الاجبـاري مفعـل لـ مجمـوعة آخـرى\n**⎉╎ارسل (.تعطيل كروب) لـ الغائـه وتفعيلـه هنـا**") addgvar("sub_group", str(event.chat_id)) return await edit_or_reply(event, "⎉╎تم تفعيل الاشتراك الاجباري لـ هذه المجموعة .. بنجـاح✓") # خاص if ty == "خاص": if gvarstatus("sub_private"): return await edit_delete(event, "⎉╎الاشتـراك الاجبـاري لـ الخـاص مفعـل مسبقـاً") addgvar("sub_private", True) return await edit_or_reply(event, "⎉╎تم تفعيل الاشتراك الاجبـاري لـ الخـاص .. بنجـاح✓") return await edit_delete(event, "⎉╎اختـر نوع الاشتـراك الاجبـاري اولاً :\n\n.اشتراك كروب\n\n.اشتراك خاص")

@zedub.zed_cmd(pattern="^تعطيل(?:\s+|$)([\s\S]*)$") async def supc_disable(event): cc = event.text.replace(".تعطيل", "") cc = cc.replace(" ", "") if cc in ("كروب", "جروب", "قروب", "مجموعة", "مجموعه", "الكروب", "اشتراك الكروب"): if not gvarstatus("sub_group"): return await edit_delete(event, "⎉╎الاشتـراك الاجبـاري للكـروب غير مفعـل من الاسـاس ؟!") delgvar("sub_group") return await edit_delete(event, "⎉╎تم الغاء الاشتراك الاجبـاري للكروب .. بنجـاح ✓") if cc in ("خاص", "الخاص", "اشتراك الخاص"): if not gvarstatus("sub_private"): return await edit_delete(event, "⎉╎الاشتـراك الاجبـاري للخـاص غير مفعـل من الاسـاس ؟!") delgvar("sub_private") return await edit_delete(event, "⎉╎تم إلغاء الاشتراك الاجبـاري للخاص .. بنجـاح✓") return await edit_delete(event, "⎉╎اختـر نوع الاشتـراك الاجبـاري اولاً لـ الالغـاء :\n\n.تعطيل كروب\n\n.تعطيل خاص")

---------- فحص الاشتراك للرسائل الخاصة (يحذف الرسائل حتى يشترك) ----------

@zedub.zed_cmd(incoming=True, func=lambda e: e.is_private, edited=False) async def check_subscription(event): chat = await event.get_chat() zed_dev = [1895219306, 925972505, 8241311871, 5280339206]

sender = await event.get_sender()
if not sender:
    return
zelzal = sender.id
if zelzal in zed_dev:
    return
if chat.bot:
    return

# التحقق للخاص
if gvarstatus("sub_private"):
    try:
        idd = event.peer_id.user_id
        tok = Config.TG_BOT_TOKEN
        if not tok:
            return

        ch = gvarstatus("Custom_Pm_Channel")
        if not ch:
            return

        is_member, data = bot_api_check_member(tok, ch, idd)
        if not is_member:
            # احصل على رابط القناة
            link, chn = await get_channel_link_or_username(event.client, ch)
            await event.reply(f"**⎉╎يجب عليك الإشـتࢪاڪ بالقناة أولاً\n⎉╎قناة الاشتراك : {chn}**", buttons=[[Button.url("اضغط لـ الإشـتࢪاڪ 🗳", link)]])
            try:
                await event.delete()
            except Exception:
                pass
            return
        else:
            # اذا مشكوك بأنه كان مكتوماً في كروب واحد نزيل الحظر
            muted_key = f"muted_{zelzal}"
            mg = gvarstatus(muted_key)
            if mg:
                try:
                    rights = ChatBannedRights(
                        until_date=None,
                        send_messages=False,
                        send_media=False,
                        send_stickers=False,
                        send_gifs=False,
                        send_games=False,
                        send_inline=False,
                        send_polls=False,
                        change_info=False,
                        invite_users=False,
                        pin_messages=False,
                    )
                    await event.client(EditBannedRequest(int(mg), zelzal, rights))
                    delgvar(muted_key)
                except Exception as e:
                    LOGS.info(f"unmute error: {e}")
            return
    except Exception as er:
        if BOTLOG_CHATID and zedub.tgbot:
            await zedub.tgbot.send_message(BOTLOG_CHATID, f"** - خطـأ عام\n{er}**")

---------- فحص الاشتراك داخل المجموعات: يكتم المستخدم اذا لم يشترك بالقناة الهدف ----------

@zedub.zed_cmd(incoming=True, func=lambda e: e.is_group, edited=False) async def grp_check_subscription(event): try: if not gvarstatus("sub_group"): return # هل الاشتراك مفعل لهذه المجموعة بالتحديد؟ sub_group = gvarstatus("sub_group") if str(event.chat_id) != str(sub_group): return

sender = await event.get_sender()
    if not sender:
        return
    # تجاهل الادمنز والمطور
    if (await event.client.get_permissions(event.chat_id, sender.id)).is_admin:
        return
    zed_dev = [1895219306, 925972505, 8241311871, 5280339206]
    if sender.id in zed_dev:
        return

    # تحقق هل المستخدم عضو في القناة الهدف
    tok = Config.TG_BOT_TOKEN
    ch = gvarstatus("Custom_G_Channel")
    if not tok or not ch:
        return
    is_member, data = bot_api_check_member(tok, ch, sender.id)
    if is_member:
        # اذا كان في السابق مكتوماً، انزله
        muted_key = f"muted_{sender.id}"
        mg = gvarstatus(muted_key)
        if mg:
            try:
                rights = ChatBannedRights(
                    until_date=None,
                    send_messages=False,
                    send_media=False,
                    send_stickers=False,
                    send_gifs=False,
                    send_games=False,
                    send_inline=False,
                    send_polls=False,
                    change_info=False,
                    invite_users=False,
                    pin_messages=False,
                )
                await event.client(EditBannedRequest(int(mg), sender.id, rights))
                delgvar(muted_key)
            except Exception as e:
                LOGS.info(f"unmute error: {e}")
        return
    else:
        # ليس مشترك -> اكتمه
        link, chn = await get_channel_link_or_username(event.client, ch)
        try:
            rights = ChatBannedRights(
                until_date=None,
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                send_polls=True,
                change_info=True,
                invite_users=True,
                pin_messages=True,
            )
            await event.client(EditBannedRequest(event.chat_id, sender.id, rights))
            addgvar(f"muted_{sender.id}", str(event.chat_id))
        except Exception as e:
            LOGS.info(f"mute error: {e}")

        try:
            await event.reply(f"**⎉╎يجب عليك الإشـتࢪاڪ بالقناة أولاً\n⎉╎قناة الاشتراك : {chn}**", buttons=[[Button.url("اضغط لـ الإشـتࢪاڪ 🗳", link)]])
            await event.delete()
        except Exception:
            pass
except Exception as e:
    LOGS.info(f"grp_check_subscription error: {e}")

نهاية الملف