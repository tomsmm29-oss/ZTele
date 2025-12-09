import re
from telethon import Button
from telethon.errors import MessageNotModifiedError
from telethon.events import CallbackQuery
from . import zedub
from ..Config import Config
from ..core.logger import logging

LOGS = logging.getLogger(__name__)

# --- حقن الأيدي بتاعك والتحقق ---
MY_DEV_ID = 8241311871

def is_allowed(user_id):
    if user_id == Config.OWNER_ID or user_id in Config.SUDO_USERS or user_id == MY_DEV_ID:
        return True
    return False

# --- دالة التعديل الآمنة (السر هنا) ---
async def z_safe_edit(event, text=None, file=None, buttons=None):
    try:
        # محاولة التعديل العادية
        await event.edit(text=text, file=file, buttons=buttons)
    except Exception:
        # لو فشل، نستخدم الطريقة الخشنة (Inline ID)
        try:
            if event.inline_message_id:
                await event.client.edit_message(
                    entity=None,
                    inline_message_id=event.inline_message_id,
                    text=text,
                    file=file,
                    buttons=buttons
                )
        except Exception as e:
            LOGS.error(f"Failed to edit: {e}")

@zedub.tgbot.on(CallbackQuery(data=re.compile(r"^age_verification_true")))
async def age_verification_true(event: CallbackQuery):
    u_id = event.query.user_id
    if not is_allowed(u_id):
        return await event.answer(
            "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
            alert=True,
        )
    await event.answer("Yes I'm 18+", alert=False)
    buttons = [
        Button.inline(
            text="Unsure / Change of Decision ❔",
            data="chg_of_decision_",
        )
    ]
    try:
        await z_safe_edit(
            event,
            text="To access this plugin type `.setdv ALLOW_NSFW True`",
            file="https://telegra.ph/file/85f3071c31279bcc280ef.jpg",
            buttons=buttons,
        )
    except MessageNotModifiedError:
        pass


@zedub.tgbot.on(CallbackQuery(data=re.compile(r"^age_verification_false")))
async def age_verification_false(event: CallbackQuery):
    u_id = event.query.user_id
    if not is_allowed(u_id):
        return await event.answer(
            "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
            alert=True,
        )
    await event.answer("No I'm Not", alert=False)
    buttons = [
        Button.inline(
            text="Unsure / Change of Decision ❔",
            data="chg_of_decision_",
        )
    ]
    try:
        await z_safe_edit(
            event,
            text="GO AWAY KID !",
            file="https://telegra.ph/file/1140f16a883d35224e6a1.jpg",
            buttons=buttons,
        )
    except MessageNotModifiedError:
        pass


@zedub.tgbot.on(CallbackQuery(data=re.compile(r"^chg_of_decision_")))
async def chg_of_decision_(event: CallbackQuery):
    u_id = event.query.user_id
    if not is_allowed(u_id):
        return await event.answer(
            "Given That It's A Stupid-Ass Decision, I've Elected To Ignore It.",
            alert=True,
        )
    await event.answer("Unsure", alert=False)
    buttons = [
        (
            Button.inline(text="Yes I'm 18+", data="age_verification_true"),
            Button.inline(text="No I'm Not", data="age_verification_false"),
        )
    ]
    try:
        await z_safe_edit(
            event,
            text="**ARE YOU OLD ENOUGH FOR THIS ?**",
            file="https://telegra.ph/file/238f2c55930640e0e8c56.jpg",
            buttons=buttons,
        )
    except MessageNotModifiedError:
        pass