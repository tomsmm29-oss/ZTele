import os
import subprocess
import sys
from threading import Thread

from flask import Flask, jsonify, request

app = Flask("")


@app.route("/")
def home():
    return "Refz (Zedthon Edition) is High & Alive! 🚬"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"status": "no data"}), 400

    print("📡 استلمت إشارة تحديث... جاري المعالجة")

    try:
        # 1. استخراج رابط المستودع والفرع من بيانات جيتهاب
        repo_url = data.get("repository", {}).get("clone_url")
        ref = data.get("ref", "refs/heads/main")
        branch = ref.split("/")[-1]  # يستخرج main أو master

        if not repo_url:
            # رابط احتياطي في حال فشل الاستخراج
            repo_url = "https://github.com/tomsmm29/oss-ztele.git"

        print(f"📥 جاري سحب التحديث من {repo_url} (فرع: {branch})...")

        # 2. تنفيذ السحب المباشر بدون الحاجة لـ origin
        subprocess.run(["git", "reset", "--hard", "HEAD"], check=True)
        # جلب البيانات من الرابط مباشرة وضخها في الفرع الحالي
        subprocess.run(["git", "fetch", repo_url, branch], check=True)
        subprocess.run(["git", "reset", "--hard", "FETCH_HEAD"], check=True)

        print("✅ تم سحب الملفات وتحديث المستودع بنجاح!")
    except Exception as e:
        print(f"❌ فشل تحديث الملفات: {e}")
        return jsonify({"status": "git error", "details": str(e)}), 200

    # 3. تحديد الملفات المتأثرة لإعادة التشغيل
    modified_files = []
    if "commits" in data:
        for commit in data["commits"]:
            modified_files.extend(commit.get("modified", []))
            modified_files.extend(commit.get("added", []))

    core_modified = False
    plugins_modified = []

    if not modified_files:
        core_modified = True  # تحديث شامل إذا لم تصل قائمة ملفات
    else:
        for file in modified_files:
            if file == "requirements.txt":
                print("📦 تحديث مكتبات...")
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
                )
                core_modified = True
            elif file.startswith("zlzl/plugins/") and file.endswith(".py"):
                plugins_modified.append(file)
            else:
                core_modified = True

    # 4. إصدار أمر إعادة التشغيل للبوت
    if core_modified:
        print("🔄 تحديث نظامي: سيتم إعادة تشغيل البوت بالكامل")
        with open("reload_queue.txt", "w") as f:
            f.write("RESTART")
    elif plugins_modified:
        print(f"⚡ تحديث إضافات: {plugins_modified}")
        with open("reload_queue.txt", "a", encoding="utf-8") as f:
            for plugin in plugins_modified:
                plugin_name = os.path.basename(plugin).replace(".py", "")
                f.write(plugin_name + "\n")

    return jsonify({"status": "success"}), 200


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


if __name__ == "__main__":
    keep_alive()
