import os
import requests
import asyncio
from zlzl.plugins import admin_cmd
from zlzl.core.managers import edit_or_reply

# استيراد دوال التحميل من ملف utils الخاص بسورس زدثون
try:
    from zlzl.utils import load_module, remove_plugin
except ImportError:
    from ..utils import load_module, remove_plugin 

# ==============================================
# إعدادات مستودع  جيتهوب
# ==============================================
USERNAME = "tomsmm29-oss"
REPO = "ZTele"
BRANCH = "master" 
# ==============================================

@admin_cmd(pattern=r"[.!+$](تحديث السورس|تحديث البوت|تحديث ملف)(?:\s+(.*))?")
async def smart_hot_update(event):
    cmd_type = event.pattern_match.group(1)
    plugin_name = event.pattern_match.group(2)
    
    # 1. بداية رسالة التحديث
    MSG = await edit_or_reply(
        event,
        "ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n"
        "**•─────────────────•**\n\n"
        "**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**"
    )
    
    # 2. عداد التحديث المتحرك (من 10% إلى 100%)
    animation_frames = [
        "%𝟷𝟶 ▬▭▭▭▭▭▭▭▭▭",
        "%𝟸𝟶 ▬▬▭▭▭▭▭▭▭▭",
        "%𝟹𝟶 ▬▬▬▭▭▭▭▭▭▭",
        "%𝟺𝟶 ▬▬▬▬▭▭▭▭▭▭",
        "%𝟻𝟶 ▬▬▬▬▬▭▭▭▭▭",
        "%𝟼𝟶 ▬▬▬▬▬▬▭▭▭▭",
        "%𝟽𝟶 ▬▬▬▬▬▬▬▭▭▭",
        "%𝟾𝟶 ▬▬▬▬▬▬▬▬▭▭",
        "%𝟿𝟶 ▬▬▬▬▬▬▬▬▬▭",
        "%𝟷𝟶𝟶 ▬▬▬▬▬▬▬▬▬▬💯"
    ]
    
    for frame in animation_frames:
        await asyncio.sleep(1)
        await MSG.edit(
            "ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n"
            "**•─────────────────•**\n\n"
            "**⇜ يتـم تحـديث بـوت زدثــون .. انتظـر . . .🌐**\n\n"
            f"{frame}"
        )

    # 3. سحب التحديثات وتطبيقها لحظياً
    if plugin_name:
        # إذا تم تحديد ملف معين
        plugin_name = plugin_name.strip()
        GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/{BRANCH}/zlzl/plugins/{plugin_name}.py"
        
        try:
            res = requests.get(GITHUB_RAW_URL)
            if res.status_code == 200:
                file_path = f"zlzl/plugins/{plugin_name}.py"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(res.text)
                    
                remove_plugin(plugin_name)
                load_module(plugin_name)
                
                await MSG.edit(
                    "ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n"
                    "**•─────────────────•**\n\n"
                    "**•⎆┊تم التحـديث ⎌ بنجـاح**\n"
                    f"**•⎆┊تم تحديث ملف `{plugin_name}` 🌐**"
                )
            elif res.status_code == 404:
                await MSG.edit(f"❌ **لم أجد ملفاً باسم `{plugin_name}`**")
        except Exception as e:
            await MSG.edit(f"❌ **خطأ:** `{str(e)}`")

    else:
        # إذا كان المطلوب تحديث السورس بالكامل ذكياً
        GITHUB_API_URL = f"https://api.github.com/repos/{USERNAME}/{REPO}/commits/{BRANCH}"
        
        try:
            res = requests.get(GITHUB_API_URL)
            if res.status_code == 200:
                commit_data = res.json()
                modified_files = commit_data.get("files", [])
                
                updated = False
                
                for f in modified_files:
                    filename = f.get("filename")
                    status = f.get("status")
                    
                    if filename.startswith("zlzl/plugins/") and filename.endswith(".py"):
                        p_name = filename.split("/")[-1].replace(".py", "")
                        
                        if status == "removed":
                            remove_plugin(p_name)
                            if os.path.exists(filename):
                                os.remove(filename)
                            updated = True
                            
                        elif status in ["modified", "added"]:
                            raw_url = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/{BRANCH}/{filename}"
                            raw_res = requests.get(raw_url)
                            
                            if raw_res.status_code == 200:
                                with open(filename, "w", encoding="utf-8") as file_obj:
                                    file_obj.write(raw_res.text)
                                    
                                remove_plugin(p_name)
                                load_module(p_name)
                                updated = True
                
                if updated:
                    await MSG.edit(
                        "ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n"
                        "**•─────────────────•**\n\n"
                        "**•⎆┊تم التحـديث ⎌ بنجـاح**\n"
                        "**•⎆┊تم تحديث السورس  🌐**"
                    )
                else:
                    await MSG.edit(
                        "ᯓ 𝗦𝗢𝗨𝗥𝗖𝗘 𝗭𝗧𝗛𝗢𝗡 - تحـديث زدثــون\n"
                        "**•─────────────────•**\n\n"
                        "**•⎆┊السـورس محـدث بالفعـل ⎌ **\n"
                        "**•⎆┊لا توجد تحديثات جديدة 🌐 **"
                    )
            
            else:
                await MSG.edit(f"❌ **فشل الاتصال بجيتهوب!**")
                
        except Exception as e:
            await MSG.edit(f"❌ **خطأ:**\n`{str(e)}`")