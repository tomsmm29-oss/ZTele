import random
import re
from uuid import uuid4

from telethon import Button, types
from telethon.events import InlineQuery
from youtubesearchpython import VideosSearch

from . import zedub
from ..Config import Config
from ..helpers.functions import rand_key
from ..helpers.functions.utube import (
    download_button,
    get_yt_video_id,
    get_ytthumb,
    result_formatter,
    ytsearch_data,
)
from ..sql_helper.globals import gvarstatus

# تنظيف شامل للمتغيرات اللي مالها داعي
LOGS = zedub.LOGS

@zedub.tgbot.on(InlineQuery)
async def inline_handler(event):
    builder = event.builder
    result = None
    query = event.text
    string = query.lower()
    
    # تقسيم النص بطريقة آمنة عشان ما يضرب الكود
    str_y = query.split(" ", 1)
    
    query_user_id = event.query.user_id
    
    # التحقق من المستخدم (المالك أو المطورين)
    if query_user_id == Config.OWNER_ID or query_user_id in Config.SUDO_USERS:
        
        # --- قسم اليوتيوب (YTDL) ---
        if str_y[0].lower() == "ytdl" and len(str_y) == 2:
            link = get_yt_video_id(str_y[1].strip())
            found_ = True
            
            if link is None:
                # بحث عن فيديو
                search = VideosSearch(str_y[1].strip(), limit=15)
                resp = (search.result()).get("result")
                
                if len(resp) == 0:
                    found_ = False
                else:
                    outdata = await result_formatter(resp)
                    key_ = rand_key()
                    ytsearch_data.store_(key_, outdata)
                    
                    buttons = [
                        Button.inline(f"1 / {len(outdata)}", data=f"ytdl_next_{key_}_1"),
                        Button.inline("القائمـة 📜", data=f"ytdl_listall_{key_}_1"),
                        Button.inline("⬇️  تحميـل", data=f'ytdl_download_{outdata[1]["video_id"]}_0'),
                    ]
                    caption = outdata[1]["message"]
                    photo = await get_ytthumb(outdata[1]["video_id"])
            else:
                # رابط مباشر
                caption, buttons = await download_button(link, body=True)
                photo = await get_ytthumb(link)
            
            if found_:
                markup = event.client.build_reply_markup(buttons)
                photo = types.InputWebDocument(url=photo, size=0, mime_type="image/jpeg", attributes=[])
                text, msg_entities = await event.client._parse_message_text(caption, "html")
                
                result = types.InputBotInlineResult(
                    id=str(uuid4()),
                    type="photo",
                    title=link,
                    description="⬇️ اضغـط للتحميـل",
                    thumb=photo,
                    content=photo,
                    send_message=types.InputBotInlineMessageMediaAuto(
                        reply_markup=markup, message=text, entities=msg_entities
                    ),
                )
            else:
                result = builder.article(
                    title="Not Found",
                    text=f"No Results found for `{str_y[1]}`",
                    description="INVALID",
                )

        # --- قسم الحماية (PmPermit) ---
        elif string == "pmpermit":
            controlpmch = gvarstatus("pmchannel") or None
            
            # الأزرار الافتراضية
            buttons = [[Button.url("𝗭𝗧𝗵𝗼𝗻", "https://t.me/ZThon")]]
            if controlpmch is not None:
                zchannel = controlpmch.replace("@", "")
                buttons = [[Button.url("⌔ قنـاتـي ⌔", f"https://t.me/{zchannel}")]]
            
            # الصورة
            PM_PIC = gvarstatus("pmpermit_pic")
            ZZZ_IMG = None
            if PM_PIC:
                PIC = list([x for x in PM_PIC.split()])
                ZZZ_IMG = random.choice(PIC)
            
            # النص
            query = gvarstatus("pmpermit_text") or "ZThon Userbot Security"
            
            if ZZZ_IMG and ZZZ_IMG.endswith((".jpg", ".jpeg", ".png")):
                result = builder.photo(ZZZ_IMG, text=query, buttons=buttons)
            elif ZZZ_IMG:
                result = builder.document(ZZZ_IMG, title="Alive", text=query, buttons=buttons)
            else:
                result = builder.article(title="Alive", text=query, buttons=buttons)

    # إرسال النتيجة النهائية
    try:
        await event.answer([result] if result else None)
    except Exception as e:
        LOGS.error(f"Error in Inline: {e}")