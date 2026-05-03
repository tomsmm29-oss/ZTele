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
    """استقبال التحديث الفوري من جيتهاب"""
    data = request.json
    print("📡 استلمت إشارة تحديث من GitHub...")

    try:
        # 1. تنظيف أي تغييرات محلية قد تعيق السحب
        subprocess.run(["git", "reset", "--hard", "HEAD"], check=True)
        
        # 2. محاولة السحب من main أو master بشكل صريح
        # سنحاول سحب التحديث من الريموت origin
        try:
            print("📥 جاري محاولة السحب من main...")
            subprocess.run(["git", "pull", "origin", "main"], check=True)
        except:
            print("📥 فشل main، جاري محاولة السحب من master...")
            subprocess.run(["git", "pull", "origin", "master"], check=True)
            
        print("✅ تم سحب الملفات بنجاح!")
    except Exception as e:
        print(f"❌ خطأ في جيت: {e}")
        return jsonify({"status": "error", "message": str(e)}), 200 # نرجع 200 عشان جيتهاب ما يعيد المحاولة

    # استخراج الملفات المعدلة
    modified_files = []
    if data and 'commits' in data:
        for commit in data['commits']:
            modified_files.extend(commit.get('modified', []))
            modified_files.extend(commit.get('added', []))

    plugins_modified = []
    core_modified = False

    # إذا لم تصلنا قائمة ملفات (إشارة يدوية)، سنعتبره تحديث شامل
    if not modified_files:
        core_modified = True
    else:
        for file in modified_files:
            if file == "requirements.txt":
                print("📦 تحديث مكتبات...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
                core_modified = True
            elif file.startswith("zlzl/plugins/") and file.endswith(".py"):
                plugins_modified.append(file)
            else:
                core_modified = True

    # التنفيذ
    if core_modified:
        print("🔄 تحديث ملفات النظام.. إعادة تشغيل...")
        with open("reload_queue.txt", "w") as f: f.write("RESTART")
    elif plugins_modified:
        print(f"⚡ تحديث إضافات: {plugins_modified}")
        with open("reload_queue.txt", "a", encoding="utf-8") as f:
            for plugin in plugins_modified:
                plugin_name = os.path.basename(plugin).replace('.py', '')
                f.write(plugin_name + "\n")
                
    return jsonify({"status": "success"}), 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()