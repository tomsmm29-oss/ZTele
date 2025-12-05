import random
import asyncio
import requests
from telethon import functions
from telethon.errors import FloodWaitError, UsernameInvalidError

# --- تصحيح المسارات والحقن النسبي ---
from . import zedub
from ..core.managers import edit_delete, edit_or_reply

# --- دالة User-Agent محلية (بدل المكتبة الخارجية) ---

def generate_user_agent():
    versions = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(versions)

# الحروف والأرقام المسموح بها
letters = "qwertyuiopassdfghjklzxcvbnm"
digits = "1234567890"
alnum = letters + digits

# عدادات وحالات
trys, trys2 = [0], [0]
isclaim = ["off"]
isauto = ["off"]

# ذاكرة بسيطة لتجنب فحص نفس اليوزر مرارا
_checked_cache = set()

# --------------------------------------------------
# تحسينات/تقنيات الصيد (مطبقة داخل الكود، غير ظاهرة للمستخدم)
# 1) قوالب توليد مرنة (templates) لأنماط مختلفة
# 2) توليد متغيرات ومُحولات (leet, تكرار حروف، تغيير مواضع) لزيادة فرص الصيد
# 3) ذاكرة مؤقتة للحيلولة دون فحص نفس اليوزر أكثر من مرة
# 4) تحقق مزدوج: API (telethon resolve) ثم fallback عبر HTTP
# 5) تأخير تكيفي مع backoff عند أخطاء/معدل (exponential backoff)
# 6) حد للتوازي إن احتجنا (Semaphore) لتقليل FloodWait
# 7) استراتيجيات أولوية/وزن لاختيار الأنماط النادرة أولاً
# --------------------------------------------------

# مساعدات توليد

def _rand_chars(pool, n):
    return ''.join(random.choice(pool) for _ in range(n))


def _mutate_variants(base):
    """انشئ مجموعة من المتغيرات من النص الأساس لزيادة الاحتمالات.
    لا نعرض هذه المتغيرات للمستخدم، بل نحاولها داخلياً قبل الانتقال.
    """
    variants = set()
    variants.add(base)
    # leet substitutions
    subs = {"o": "0", "i": "1", "l": "1", "e": "3", "a": "4"}
    for k, v in subs.items():
        if k in base:
            variants.add(base.replace(k, v))
    # add underscores in random positions
    if len(base) >= 4:
        for i in range(1, len(base) - 1):
            variants.add(base[:i] + "_" + base[i:])
    # double some characters
    for i in range(len(base)):
        variants.add(base[:i] + base[i] + base[i:])
    # reverse
    variants.add(base[::-1])
    # append a digit
    variants.add(base + random.choice(digits))
    return list(variants)


async def check_user(username, client=None, max_retries=2):
    """تحقق مما إذا كان اليوزر متاحاً.
    تحاول أولاً عبر Telethon (إذا تواجد client)، ثم fallback على طلب HTTP الى t.me
    تُعيد True إن كان اليوزر متاح (قابل للحجز)، False إن وجد بالفعل أو حصل خطأ واضح.
    """
    uname = str(username).replace("@", "").lower()
    if not uname or len(uname) < 3:
        return False

    # تجنب الفحص المكرر
    if uname in _checked_cache:
        return False

    # Retry/backoff helper
    backoff = 1
    # 1) حاول عبر Telethon (تكون النتيجة الأكثر دقة)
    if client is not None:
        for attempt in range(max_retries + 1):
            try:
                # contacts.ResolveUsernameRequest تُرجع نتيجة إن كان اليوزر موجود
                _ = await client(functions.contacts.ResolveUsernameRequest(username=uname))
                # إن نجح الاستدعاء يعني الاسم محجوز
                _checked_cache.add(uname)
                return False
            except Exception as e:
                text = str(e).lower()
                # إذا الرسالة تفيد أن الاسم غير مشغول
                if "not found" in text or "username not" in text or "occupied" in text or "could not" in text or "no" in text:
                    # هنا نعتبره متاحاً
                    # ملاحظة: بعض الأخطاء قد تكون من الشبكة لذا نعمل retry
                    if attempt < max_retries:
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue
                    _checked_cache.add(uname)
                    return True
                # FloodWait يرمز الى حظر مؤقت
                if "flood" in text or "floodwait" in text:
                    return False
                # حالات غير متوقعة -> نبدل الى الفحص بالـ HTTP
                break

    # 2) فحص HTTP كـ fallback
    headers = {
        "User-Agent": generate_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "ar,en-US;q=0.8,en;q=0.7",
    }
    url = f"https://t.me/{uname}"
    for attempt in range(max_retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=6)
            # 404 أو redirect إلى صفحة generic تعني غالبا أن اليوزر غير موجود
            if resp.status_code == 404:
                _checked_cache.add(uname)
                return True
            text = resp.text.lower()
            # إذا الصفحة تعرض "If you have Telegram, you can contact" فهذا يعني وجود حساب
            if "if you have <strong>telegram</strong>" in text or "tgme_username_link" in text or "telegram" in text:
                _checked_cache.add(uname)
                return False
            # بعض صفحات t.me تعرض رسالة أن اليوزر غير موجود، حاول اكتشافها
            if "username is available" in text or "this username is available" in text or "this channel is available" in text:
                _checked_cache.add(uname)
                return True
            # افتراض افتراضي: إن كانت الصفحة تحتوي على "join channel" غالباً موجود
            if "join" in text and "channel" in text:
                _checked_cache.add(uname)
                return False
            # لا استنتاج واضح -> retry مع backoff
        except requests.RequestException:
            pass
        await asyncio.sleep(backoff)
        backoff *= 2
    # إن تعذر الاستدلال بدقة نخمن أنه غير متاح لتقليل الأخطار
    return False


# قوالب وأنماط متقدمة للتوليد

def gen_user(choice):
    choice = choice.strip()
    # أنواع مدعومة بترتيب أفضلية (لتقوية الصيد)
    try_order = [
        "رباعي",
        "ثلاثيات",
        "خماسي حرفين",
        "خماسي",
        "خماسي DF",
        "سداسيات",
        "سداسي حرفين",
        "سداسي",
        "سباعيات",
        "سباعي حرفين",
        "سباعي",
        "بوتات",
        "تيست",
        "رباعي DF_KK",
        "رباعي_raw",
    ]

    # توليد حسب النوع
    if choice == "ثلاثيات":
        return _rand_chars(letters, 3)

    if choice == "خماسي":
        return _rand_chars(alnum, 5)

    if choice == "خماسي حرفين":
        # 2 أحرف + 3 أرقام/أحرف بمواقع عشوائية
        parts = [random.choice(letters), random.choice(letters), random.choice(alnum), random.choice(alnum), random.choice(alnum)]
        random.shuffle(parts)
        return ''.join(parts)

    if choice == "سداسيات":
        return _rand_chars(alnum, 6)

    if choice == "سداسي حرفين":
        # إجبار على احتواء حرفين على الأقل
        parts = [random.choice(letters) for _ in range(2)] + [random.choice(alnum) for _ in range(4)]
        random.shuffle(parts)
        return ''.join(parts)

    if choice == "سباعيات":
        return _rand_chars(alnum, 7)

    if choice == "سباعي حرفين":
        parts = [random.choice(letters) for _ in range(2)] + [random.choice(alnum) for _ in range(5)]
        random.shuffle(parts)
        return ''.join(parts)

    if choice == "بوتات":
        base = _rand_chars(letters, 3)
        return base + "bot"

    if choice == "تيست":
        parts = [random.choice(alnum) for _ in range(10)]
        random.shuffle(parts)
        return ''.join(parts)

    # طلب المستخدم: رباعي بالشكل DF_KK => شكل مثل AB_CD
    if choice == "رباعي" or choice == "رباعي DF_KK":
        part1 = _rand_chars(letters, 2)
        part2 = _rand_chars(letters, 2)
        return f"{part1}_{part2}"

    # بديل رباعي خام
    if choice == "رباعي_raw":
        return _rand_chars(alnum, 4)

    # خماسي DF كمثال لنسق أكثر ندرة: حرفين + '_' + حرف/رقمين
    if choice == "خماسي DF":
        return f"{_rand_chars(letters,2)}_{_rand_chars(alnum,2)}"

    # قيمة افتراضية لتجنب الكراش
    return "error"


# نص الأوامر (حافظ على الفخامة والواجهة كما هي)
ZelzalChecler_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗭𝗧𝗵𝗼𝗻 - اوامـر الصيـد والتشيكـر](t.me/ZEDthon) 𓆪\n\n"
    "**✾╎قـائمـة اوامـر تشيكـر صيـد معـرفات تيليجـرام :** \n\n"
    "**- النـوع :**\n"
    "**(** `سداسي حرفين`/`ثلاثيات`/`سداسيات`/`بوتات`/`خماسي حرفين`/`خماسي`/`سباعيات` **)**\n\n"
    "`.صيد` + النـوع\n"
    "**⪼ لـ صيـد يـوزرات عشوائيـه على حسب النـوع**\n\n"
    "`.تثبيت` + اليوزر\n"
    "**⪼ لـ تثبيت اليـوزر بقنـاة معينـه اذا اصبح متاحـاً يتم اخـذه**\n\n"
    "`.حالة الصيد`\n"
    "**⪼ لـ معرفـة حالـة تقـدم عمليـة الصيـد**\n\n"
    "`.حالة التثبيت`\n"
    "**⪼ لـ معرفـة حالـة تقـدم التثبيت التلقـائـي**\n\n"
    "`.ايقاف الصيد`\n"
    "**⪼ لـ إيقـاف عمليـة الصيـد الجاريـه**\n\n"
    "`.ايقاف التثبيت`\n"
    "**⪼ لـ إيقـاف عمليـة التثبيت التلقـائـي**\n\n"
)


@zedub.zed_cmd(pattern="الصيد")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalChecler_cmd)


@zedub.zed_cmd(pattern="صيد (.*)")
async def hunterusername(event):
    choice = str(event.pattern_match.group(1)).strip()
    await event.edit(f"**⎉╎تم بـدء الصيـد .. بنجـاح ☑️**\n**⎉╎لمعرفـة حالة تقـدم عمليـة الصيـد ارسـل (**`.حالة الصيد`**)**")

    try:
        ch = await zedub(
            functions.channels.CreateChannelRequest(
                title="⎉ صيـد زدثـــون 𝗭𝗧𝗵𝗼𝗻 ⎉",
                about="This channel to hunt username by - @ZedThon ",
            )
        )
        ch = ch.updates[1].channel_id
    except Exception as e:
        await zedub.send_message(
            event.chat_id, f"خطأ في انشاء القناة , الخطأ**-  : {str(e)}**"
        )
        sedmod = False
        return

    isclaim.clear()
    isclaim.append("on")
    sedmod = True

    # semaphore لتجنب التوازي الكبير
    sem = asyncio.Semaphore(2)

    while sedmod:
        await asyncio.sleep(0.4)  # نوم بسيط لتجنب الحظر

        if "off" in isclaim:
            break

        base = gen_user(choice)
        if base == "error":
            await event.edit("**- يـرجى وضـع النـوع بشكـل صحيـح ...!!**")
            isclaim.clear()
            isclaim.append("off")
            break

        # ننتج متغيرات من القاعدة لزيادة فرص الصيد
        candidates = _mutate_variants(base)

        found = False
        for username in candidates:
            # لا نعالج أسماء فحصناها من قبل
            if username in _checked_cache:
                continue

            # تحقق مزدوج (API -> HTTP)
            async with sem:
                isav = await check_user(username, client=zedub)

            if isav:
                try:
                    await zedub(
                        functions.channels.UpdateUsernameRequest(
                            channel=ch, username=username
                        )
                    )
                    # إرسال النتائج بنفس الأسلوب الفخم
                    msg_text = (
                        "ᯓ 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - صيـد زدثــون \U0001f4a1\n**•────────────────────•**\n"
                        f"- UserName: ❲ @{username} ❳\n- ClickS: ❲ {trys} ❳\n- Type: {choice}\n- Save: ❲ Channel ❳\n**•────────────────────•**\n- By ❲ @ZedThon ❳ "
                    )
                    await event.client.send_message(event.chat_id, msg_text)
                    await event.client.send_message(ch, msg_text)

                    sedmod = False
                    found = True
                    break
                except UsernameInvalidError:
                    # تجاهل
                    pass
                except FloodWaitError as e:
                    await zedub.send_message(
                        event.chat_id,
                        f"للاسف تبندت , مدة الباند**-  ({e.seconds}) ثانية .**",
                    )
                    sedmod = False
                    found = True
                    break
                except Exception as eee:
                    err = str(eee).lower()
                    if "the username is already" in err or "username_purchase_available" in err:
                        pass
                    else:
                        await zedub.send_message(
                            event.chat_id,
                            f"- خطأ مع @{username} , الخطأ :{str(eee)}",
                        )
                        sedmod = False
                        found = True
                        break
            # زيادة عداد المحاولات لكل فحص
            trys[0] += 1

        if found:
            break

    isclaim.clear()
    isclaim.append("off")


@zedub.zed_cmd(pattern="تثبيت (.*)")
async def _(event):
    msg = event.text.split()
    try:
        ch = str(msg[2])
        ch = ch.replace("@", "")
        await event.edit(f"حسناً سيتم بدء التثبيت في**-  @{ch} .**")
    except:
        try:
            ch = await zedub(
                functions.channels.CreateChannelRequest(
                    title="⎉ تثبيت زدثـــون 𝗭𝗧𝗵𝗼𝗻 ⎉",
                    about="This channel to hunt username by - @ZedThon ",
                )
            )
            ch = ch.updates[1].channel_id
            await event.edit(f"**- تم بـدء التثبيت .. بنجـاح ☑️**")
        except Exception as e:
            await zedub.send_message(
                event.chat_id, f"خطأ في انشاء القناة , الخطأ : {str(e)}"
            )
            return

    isauto.clear()
    isauto.append("on")
    username = str(msg[1])

    swapmod = True
    while swapmod:
        await asyncio.sleep(0.5)

        if "off" in isauto:
            break

        isav = await check_user(username, client=zedub)
        if isav:
            try:
                await zedub(
                    functions.channels.UpdateUsernameRequest(
                        channel=ch, username=username
                    )
                )
                msg_text = (
                    "ᯓ 𝗭𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - صيـد زدثــون \U0001f4a1\n**•────────────────────•**\n"
                    f"- UserName: ❲ @{username} ❳\n- ClickS: ❲ {trys2} ❳\n- Save: ❲ Channel ❳\n**•────────────────────•**\n- By ❲ @ZedThon ❳ "
                )
                await event.client.send_message(ch, msg_text)
                await event.client.send_message(event.chat_id, msg_text)
                swapmod = False
                break
            except UsernameInvalidError:
                await event.client.send_message(
                    event.chat_id, f"**المعرف @{username} غير صالح ؟!**"
                )
                swapmod = False
                break
            except FloodWaitError as e:
                await zedub.send_message(
                    event.chat_id, f"للاسف تبندت , مدة الباند ({e.seconds}) ثانية ."
                )
                swapmod = False
                break
            except Exception as eee:
                await zedub.send_message(
                    event.chat_id,
                    f"خطأ مع {username} , الخطأ :{str(eee)}",
                )
                swapmod = False
                break
        trys2[0] += 1

    isauto.clear()
    isauto.append("off")


@zedub.zed_cmd(pattern="حالة الصيد")
async def _(event):
    if "on" in isclaim:
        await event.edit(f"**- الصيد وصل لـ({trys[0]}) من المحـاولات**")
    elif "off" in isclaim:
        await event.edit("**- لا توجد عمليـة صيد جاريـه حاليـاً ؟!**")
    else:
        await event.edit("**- لقد حدث خطأ ما وتوقف الامر لديك**")


@zedub.zed_cmd(pattern="حالة التثبيت")
async def _(event):
    if "on" in isauto:
        await event.edit(f"**- التثبيت وصل لـ({trys2[0]}) من المحاولات**")
    elif "off" in isauto:
        await event.edit("**- لا توجد عمليـة تثبيث جاريـه حاليـاً ؟!**")
    else:
        await event.edit("-لقد حدث خطأ ما وتوقف الامر لديك")


# بدائل لأسماء الاوامر (حاله الصيد / حاله التثبيت)
@zedub.zed_cmd(pattern="حاله الصيد")
async def _(event):
    if "on" in isclaim:
        await event.edit(f"**- الصيد وصل لـ({trys[0]}) من المحـاولات**")
    elif "off" in isclaim:
        await event.edit("**- لا توجد عمليـة صيد جاريـه حاليـاً ؟!**")
    else:
        await event.edit("**- لقد حدث خطأ ما وتوقف الامر لديك**")


@zedub.zed_cmd(pattern="حاله التثبيت")
async def _(event):
    if "on" in isauto:
        await event.edit(f"**- التثبيت وصل لـ({trys2[0]}) من المحاولات**")
    elif "off" in isauto:
        await event.edit("**- لا توجد عمليـة تثبيث جاريـه حاليـاً ؟!**")
    else:
        await event.edit("-لقد حدث خطأ ما وتوقف الامر لديك")


@zedub.zed_cmd(pattern="ايقاف الصيد")
async def _(event):
    if "on" in isclaim:
        isclaim.clear()
        isclaim.append("off")
        return await event.edit("**- تم إيقـاف عمليـة الصيـد .. بنجـاح ✓**")
    elif "off" in isclaim:
        return await event.edit("**- لا توجد عمليـة صيد جاريـه حاليـاً ؟!**")
    else:
        return await event.edit("**- لقد حدث خطأ ما وتوقف الامر لديك**")


@zedub.zed_cmd(pattern="ايقاف التثبيت")
async def _(event):
    if "on" in isauto:
        isauto.clear()
        isauto.append("off")
        return await event.edit("**- تم إيقـاف عمليـة التثبيت .. بنجـاح ✓**")
    elif "off" in isauto:
        return await event.edit("**- لا توجد عمليـة تثبيث جاريـه حاليـاً ؟!**")
    else:
        return await event.edit("**-لقد حدث خطأ ما وتوقف الامر لديك**")


# أمر جديد لعرض الأنواع بنفس الفخامة (طلب المستخدم: .النوع)
@zedub.zed_cmd(pattern="النوع")
async def show_types(event):
    types_list = (
        "**- الأنـواع المتاحة للصيـد :**\n"
        "`ثلاثيات`, `خماسي`, `خماسي حرفين`, `خماسي DF`, `رباعي`, `سداسيات`, `سداسي حرفين`, `سباعيات`, `سباعي حرفين`, `بوتات`, `تيست`\n\n"
        "**⪼ لاستخدام:** `.صيد` + النـوع  (مثال: `.صيد خماسي حرفين`)"
    )
    await edit_or_reply(event, types_list)

# نهاية الملف
