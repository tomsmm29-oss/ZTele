from flask import Flask, request, jsonify
from threading import Thread
import subprocess
import os
import sys

app = Flask('')

@app.route('/')
def home():
    return "Refz (Zedthon Edition) is High & Alive! 🚬"

@app.route('/webhook', methods=['POST'])
def webhook():
    """هذا المسار سيستقبل إشعار التحديث من جيتهاب"""
    data = request.json
    if not data:
        return jsonify({"status": "ignored", "message": "No JSON payload"}), 200

    try:
        # 1. سحب التحديثات فوراً من جيتهاب
        print("📥 جاري سحب التحديثات الجديدة من GitHub...")
        subprocess.run(["git", "pull"], check=True)
    except Exception as e:
        print(f"❌ خطأ في سحب التحديثات: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

    # 2. استخراج قائمة الملفات التي تم تعديلها أو إضافتها
    modified_files = []
    if 'commits' in data:
        for commit in data['commits']:
            modified_files.extend(commit.get('modified',[]))
            modified_files.extend(commit.get('added',[]))

    # 3. فلترة التعديلات لتحديد نوع التحديث
    plugins_modified =[]
    core_modified = False

    for file in modified_files:
        if file == "requirements.txt":
            print("📦 تم رصد تعديل في المكتبات! جاري التثبيت...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            core_modified = True
        elif file.startswith("zlzl/plugins/") and file.endswith(".py"):
            plugins_modified.append(file)
        else:
            # إذا التعديل في أي ملف أساسي آخر
            core_modified = True

    # 4. تنفيذ الأكشن المناسب
    if core_modified:
        # إعادة تشغيل السكربت بالكامل (Soft Restart)
        print("🔄 تحديثات أساسية تمت! جاري إعادة تشغيل السكربت...")
        os.execl(sys.executable, sys.executable, *sys.argv)
        
    elif plugins_modified:
        # التحديث الذكي: إرسال الملفات لكي يتم تحديثها بدون إطفاء البوت
        print(f"⚡ تعديلات في الإضافات: {plugins_modified}")
        with open("reload_queue.txt", "a", encoding="utf-8") as f:
            for plugin in plugins_modified:
                # نستخرج اسم الملف فقط (مثال: الادمن.py -> الادمن)
                plugin_name = os.path.basename(plugin).replace('.py', '')
                f.write(plugin_name + "\n")
                
    return jsonify({"status": "success", "message": "تم تطبيق التحديث بنجاح!"}), 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()