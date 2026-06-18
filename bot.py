import telebot
from telebot import types
import json
import os
import time
import threading

TOKEN = "8961895801:AAHuSm3LrLVUlfWwCRHoPw8q3TxY4XWSAwg"
ADMIN_ID = 1420365532
search_user_mode = set()
grant_mode = set()
grant_user = {}
delete_mode = set()
banned_users = set()
unban_mode = set()
reset_mode = set()
broadcast_mode = set()

bot = telebot.TeleBot(TOKEN)

# ---------- FILES ----------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USERS_FILE = os.path.join(BASE_DIR, "users.json")
COURSES_FILE = os.path.join(BASE_DIR, "courses.json")

# ---------- LOAD USERS ----------

def load_users():

    if not os.path.exists(USERS_FILE):

        with open(USERS_FILE, "w") as f:

            json.dump({}, f)

    with open(USERS_FILE, "r") as f:

        return json.load(f)

# ---------- SAVE USERS ----------

def save_users(users):

    with open(USERS_FILE, "w") as f:

        json.dump(users, f, ensure_ascii=False)

# ---------- LOAD COURSES ----------

def load_courses():

    with open(COURSES_FILE, "r") as f:

        return json.load(f)

# ---------- CREATE USER ----------

def create_user(user_id):

    users = load_users()

    if user_id not in users:

        courses = load_courses()

        users[user_id] = {

            "referrals": {},

            "opened_courses": [],

            "last_course": "",

            "time": time.time(),
            "inactive_reminder_sent": False,

            "offer_sent": False,
            "offer_sent_2": False

        }

        for course_key in courses:

            users[user_id]["referrals"][course_key] = 0

        save_users(users)

    return users

# ---------- MAIN MENU ----------

def main_menu():

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "💻 Dasturlash",
        "💼 Office dasturlari"
    )

    markup.row(
        "📒 1C Buxgalteriya",
        "🌍 Chet tillari"
    )

    markup.row(
        "📐 AutoCAD",
        "🏠 3Ds Max"
    )

    markup.row(
        "🎨 Photoshop",
        "🖌 Corel Draw"
    )

    markup.row(
        "🏗 Revit",
        "🎬 Videomontaj"
    )

    markup.row(
        "🤖 Telegram Bot yasash"
    )

    markup.row(
        "📊 Statistika",
        "🏆 TOP Referral"
    )

    return markup
# ---------- START ----------

@bot.message_handler(commands=['start'])
def start(message):

    user_id = str(message.from_user.id)

    if user_id in banned_users:
        bot.send_message(message.chat.id, "⛔ Bot vaqtincha ish faoliyatida emas.")
        return

    is_new_user = user_id not in load_users()
    users = create_user(user_id)

    courses = load_courses()

    args = message.text.split()

    # REFERRAL
    if len(args) > 1:

        ref = args[1]

        try:

            referrer_id, course_key = ref.split("_", 1)

            if (
                is_new_user
                and referrer_id != user_id
                and referrer_id in users
                and course_key in courses
            ):

                users[referrer_id]["referrals"][course_key] += 1

                current = users[referrer_id]["referrals"][course_key]

                required = courses[course_key]["required"]
                remaining = required - current

                if current < required:

                    bot.send_message(
                        int(referrer_id),
                        f"""
🎉 Tabriklaymiz!

Yangi do‘stingiz botga qo‘shildi.

{courses[course_key]['name']}

✅ {current}/{required} referral

👥 Maqsadgacha yana {remaining} ta do‘st qoldi.
"""
    )

# 5 taga yetganda
                if current == 5:

                    bot.send_message(
                        int(referrer_id),
        f"""
🚀 Zo‘r ketayapsiz!

{courses[course_key]['name']}

🔥 5/{required} referral

Yarim yo‘lni bosib o‘tdingiz.
"""
    )

# 9 taga yetganda
                if current == required - 1:

                    bot.send_message(
                        int(referrer_id),
        f"""
🔥 Oxirgi qadam!

{courses[course_key]['name']}

⚡ {current}/{required} referral

Kurs ochilishiga atigi 1 ta odam qoldi.
"""
    )

                # KURS OCHILISHI
                if (
                    current >= required
                    and course_key not in users[referrer_id]["opened_courses"]
                ):

                    users[referrer_id]["opened_courses"].append(course_key)

                    bot.send_message(
                        int(referrer_id),
                        f"""
🎉 Tabriklaymiz!

🔓 Siz {courses[course_key]['name']} kursini muvaffaqiyatli ochdingiz.

📚 Kurs kanali:

{courses[course_key]['link']}

━━━━━━━━━━

🎁 Endi boshqa premium kurslarni ham ochishingiz mumkin.

👥 Yana 10 ta do‘st taklif qiling va navbatdagi kursni bepul qo‘lga kiriting.

🚀 Asosiy menyudan yangi kurs tanlang.
"""
                    )

                save_users(users)

        except Exception as e:

            print(e)

    bot.send_message(
        message.chat.id,
        """
🔥 Premium kurslarni BEPUL o‘rganing!

📚 800+ videodars
🎓 11 ta premium kurs

🔓 Kursni ochish uchun atigi 10 ta do‘stingizga botga start bosdiring.

👇 Kurslardan birini tanlang:
""",
        reply_markup=main_menu()
    )
# ---------- COURSE BUTTONS ----------

COURSE_BUTTONS = {

    "💻 Dasturlash": "programming",
    "💼 Office dasturlari": "office",
    "📒 1C Buxgalteriya": "buxgalteriya",
    "🌍 Chet tillari": "languages",
    "📐 AutoCAD": "autocad",
    "🏠 3Ds Max": "max3d",
    "🎨 Photoshop": "photoshop",
    "🖌 Corel Draw": "coreldraw",
    "🏗 Revit": "revit",
    "🎬 Videomontaj": "video",
    "🤖 Telegram Bot yasash": "telegrambot"

}

@bot.message_handler(
    func=lambda m: m.text in COURSE_BUTTONS
)
def show_course(message):

    user_id = str(message.from_user.id)

    if user_id in banned_users:
        bot.send_message(message.chat.id, "⛔ Bot vaqtincha ish faoliyatida emas.")
        return

    users = create_user(user_id)

    courses = load_courses()

    course_key = COURSE_BUTTONS[message.text]

    users[user_id]["last_course"] = course_key

    save_users(users)

    course = courses[course_key]

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "🚀 Taklif qilish",
        "📊 Mening natijam"
    )

    markup.row(
        "🏆 TOP Referral",
        "⬅️ Asosiy menyu"
    )

    text = f"""
{course['name']}

📚 Darslar soni: {course['lessons']}

📖 Tarkibi:

{course['info']}

🔓 Kursni ochish uchun:

👥 {course['required']} ta do‘st taklif qiling.
"""

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup
    )
@bot.message_handler(
    func=lambda m: m.text == "⬅️ Asosiy menyu"
)
def back_to_menu(message):

    bot.send_message(
        message.chat.id,
        "🏠 Asosiy menyu",
        reply_markup=main_menu()
    )
@bot.message_handler(
    func=lambda m: m.text == "🚀 Taklif qilish"
)
def share_link(message):

    users = load_users()

    courses = load_courses()

    user_id = str(message.from_user.id)

    course_key = users[user_id]["last_course"]

    if not course_key:

        bot.send_message(
            message.chat.id,
            "❗ Avval kurs tanlang."
        )
        return

    course = courses[course_key]

    link = (
        f"https://t.me/master_darsbot"
        f"?start={user_id}_{course_key}"
    )

    text = f"""
🎁 Premium kurslarni bepul olayotgan edim.

📚 800+ videodars
🎓 11 ta premium kurs

💻 Dasturlash
📐 AutoCAD
🎨 Photoshop
🌍 Chet tillari
🎬 Videomontaj
va boshqalar.

🔥 Men aynan {course['name']} kursini ochyapman.

👇 Kirib START bosing:

{link}

⚡ Kurslar hozircha bepul.
"""

    bot.send_message(
        message.chat.id,
        text
    )
@bot.message_handler(
    func=lambda m: m.text == "📊 Mening natijam"
)
def my_result(message):

    users = load_users()

    courses = load_courses()

    user_id = str(message.from_user.id)

    course_key = users[user_id]["last_course"]

    if not course_key:

        bot.send_message(
            message.chat.id,
            "❗ Avval kurs tanlang."
        )
        return

    course = courses[course_key]

    current = users[user_id]["referrals"][course_key]

    required = course["required"]

    remaining = required - current

    blocks = 10

    filled = int((current / required) * blocks)

    progress = "█" * filled + "░" * (blocks - filled)

    text = f"""
{course['name']}

📊 Sizning natijangiz

{progress}

✅ {current}/{required} referral

👥 Yana {remaining} ta do‘st taklif qiling.

🎁 Kurs avtomatik ochiladi.
"""

    bot.send_message(
        message.chat.id,
        text
    )
@bot.message_handler(
    func=lambda m: m.text == "🏆 TOP Referral"
)
def top_referral(message):

    users = load_users()

    ranking = []

    for user_id, data in users.items():

        total = sum(
            data["referrals"].values()
        )

        ranking.append(
            (user_id, total)
        )

    ranking.sort(
        key=lambda x: x[1],
        reverse=True
    )

    text = "🏆 TOP Referralchilar\n\n"

    medals = [
        "🥇",
        "🥈",
        "🥉"
    ]

    for i, (uid, total) in enumerate(ranking[:10]):

        try:

            user = bot.get_chat(int(uid))

            name = user.first_name

        except:

            name = "User"

        if i < 3:

            text += (
                f"{medals[i]} "
                f"{name} — {total} ta\n"
            )

        else:

            text += (
                f"{i+1}. "
                f"{name} — {total} ta\n"
            )

    my_id = str(message.from_user.id)

    my_place = 0

    my_total = 0

    for i, (uid, total) in enumerate(ranking):

        if uid == my_id:

            my_place = i + 1

            my_total = total

            break

    text += f"""

━━━━━━━━━━

👤 Siz:

🏅 O‘rin: {my_place}

👥 Referral: {my_total}
"""

    bot.send_message(
        message.chat.id,
        text
    )
@bot.message_handler(
    func=lambda m: m.text == "👥 Userlar soni"
)
def admin_users_count(message):

    if message.from_user.id != ADMIN_ID:
        return

    users = load_users()

    bot.send_message(
        message.chat.id,
        f"👥 Jami userlar: {len(users)}"
    )
@bot.message_handler(
    func=lambda m: m.chat.id in search_user_mode
)
def search_user(message):

    if message.from_user.id != ADMIN_ID:
        return

    search_user_mode.discard(message.chat.id)

    user_id = message.text.strip()

    users = load_users()

    if user_id not in users:
        bot.send_message(
            message.chat.id,
            "❌ User topilmadi"
        )
        return

    data = users[user_id]

    total_referrals = sum(
        data.get("referrals", {}).values()
    )

    opened = len(
        data.get("opened_courses", [])
    )

    try:
        tg_user = bot.get_chat(int(user_id))
        name = tg_user.first_name
    except:
        name = "Noma'lum"

    bot.send_message(
        message.chat.id,
        f"""
👤 Ism: {name}

🆔 ID: {user_id}

🏆 Referral: {total_referrals}

📚 Ochilgan kurslar: {opened}

🕒 Oxirgi kurs: {data.get('last_course', '-')}
"""
    )
def check_users():

    users = load_users()

    now = time.time()

    for user_id, data in users.items():

        try:

            total = sum(
                data["referrals"].values()
            )

            passed = now - data["time"]

            # 24 soat
            if user_id == str(ADMIN_ID):
                continue
            # 24 soat
            # 24 soat - referral=0 bepul taklif
            if (
                total == 0
                and passed >= 86400
                and not data["inactive_reminder_sent"]
            ):
                bot.send_message(
                    int(user_id),
                    "🎓 Daromadli kasblarni o'rganishni boshlang.\n\nShunchaki 10 ta do'stingizga botga START bosishini so'rang.\n\n📚 Premium kurslar avtomatik ochiladi."
                )
                data["inactive_reminder_sent"] = True
            # 48 soat - hammaga pulli taklif
            if (
                0 <= total <= 9
                and passed >= 172800
                and not data.get("offer_sent", False)
            ):
                bot.send_message(
                    int(user_id),
                    "💎 Kursni hali ocholmadingizmi?\n\nHech qisi yo'q.\n\n💎 Atigi 59 000 so'm evaziga hohlagan kursingizni hoziroq ochishingiz mumkin.\n\n👨\u200d💻 Admin:\n@MasterdarsAdmin"
                )
                data["offer_sent"] = True
            # 120 soat - ikkinchi eslatma
            if (
                0 <= total <= 9
                and passed >= 432000
                and not data.get("offer_sent_2", False)
            ):
                bot.send_message(
                    int(user_id),
                    "🔥 Oxirgi eslatma!\n\nKurslarni bepul ochish imkoniyati hali bor.\n\n💎 Yoki atigi 59 000 so'm evaziga hoziroq oching.\n\n👨\u200d💻 Admin:\n@MasterdarsAdmin"
                )
                data["offer_sent_2"] = True

        except:
            pass

    save_users(users)
check_users()
def reminder_loop():

    while True:

        try:
            check_users()
        except Exception as e:
            print("Reminder error:", e)

        time.sleep(3600)  # har 1 soatda

@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("📊 Statistika")
    markup.row("👥 Userlar soni")

    markup.row("📢 Broadcast")
    markup.row("🎓 Kurs ochish")

    markup.row("🔍 User qidirish")
    markup.row("🏆 TOP Referral")

    markup.row("🧹 Referral reset")
    markup.row("🗑 Delete User")
    markup.row("✅ Unban User")
    bot.send_message(
        message.chat.id,
        "🛠 Admin Panel",
        reply_markup=markup
    )
@bot.message_handler(
    func=lambda m: m.text == "📊 Statistika"
)
def statistika(message):
    users = load_users()
    user_id = str(message.from_user.id)
    if message.from_user.id == ADMIN_ID:
        total_users = len(users)
        total_referrals = sum(
            sum(d.get("referrals", {}).values()) for d in users.values()
        )
        bot.send_message(
            message.chat.id,
            f"📊 Bot statistikasi\n\n👥 Userlar: {total_users}\n\n🏆 Jami referral: {total_referrals}"
        )
    else:
        total = sum(users[user_id]["referrals"].values())
        opened = len(users[user_id]["opened_courses"])
        faol = "🔥 Faol" if total > 0 else "😴 Hali boshlanmagan"
        bot.send_message(
            message.chat.id,
            f"📊 Sizning statistikangiz\n\n👥 Jami referral: {total}\n\n🎓 Ochilgan kurslar: {opened}\n\n🏆 Faollik holati:\n{faol}"
        )
@bot.message_handler(commands=['id'])
def my_id(message):
    bot.send_message(
        message.chat.id,
        str(message.from_user.id)
    )
@bot.message_handler(
    func=lambda m: m.text == "🔍 User qidirish"
)
def search_user_start(message):

    if message.from_user.id != ADMIN_ID:
        return

    search_user_mode.add(message.chat.id)

    bot.send_message(
        message.chat.id,
        "🔍 User ID yuboring"
    )
@bot.message_handler(
    func=lambda m: m.text == "🎓 Kurs ochish"
)
def grant_course_start(message):

    if message.from_user.id != ADMIN_ID:
        return

    grant_mode.add(message.chat.id)

    bot.send_message(
        message.chat.id,
        "🎓 Kurs beriladigan User ID ni yuboring"
    )
@bot.message_handler(
    func=lambda m: m.chat.id in grant_mode
)
def grant_course_user(message):

    if message.from_user.id != ADMIN_ID:
        return

    user_id = message.text.strip()

    users = load_users()

    if user_id not in users:
        bot.send_message(
            message.chat.id,
            "❌ User topilmadi"
        )
        return

    grant_mode.discard(message.chat.id)

    grant_user[message.chat.id] = user_id

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("1️⃣ Dasturlash")
    markup.row("2️⃣ Office")
    markup.row("3️⃣ Buxgalteriya")
    markup.row("4️⃣ Chet tillari")
    markup.row("5️⃣ AutoCAD")
    markup.row("6️⃣ 3Ds Max")
    markup.row("7️⃣ Photoshop")
    markup.row("8️⃣ Corel Draw")
    markup.row("9️⃣ Revit")
    markup.row("🔟 Videomontaj")
    markup.row("1️⃣1️⃣ Telegram Bot")

    bot.send_message(
        message.chat.id,
        "Kursni tanlang",
        reply_markup=markup
    )
threading.Thread(
    target=reminder_loop,
    daemon=True
).start()
print("Bot ishga tushdi...")
    
@bot.message_handler(
    func=lambda m: m.chat.id in grant_user and m.chat.id not in broadcast_mode and m.chat.id not in reset_mode and m.chat.id not in delete_mode
)
def grant_course_finish(message):

    if message.from_user.id != ADMIN_ID:
        return

    courses_map = {
        "1️⃣ Dasturlash": "programming",
        "2️⃣ Office": "office",
        "3️⃣ Buxgalteriya": "buxgalteriya",
        "4️⃣ Chet tillari": "languages",
        "5️⃣ AutoCAD": "autocad",
        "6️⃣ 3Ds Max": "max3d",
        "7️⃣ Photoshop": "photoshop",
        "8️⃣ Corel Draw": "coreldraw",
        "9️⃣ Revit": "revit",
        "🔟 Videomontaj": "video",
        "1️⃣1️⃣ Telegram Bot": "telegrambot"
    }

    if message.text not in courses_map:
        return

    target_user = str(grant_user[message.chat.id])

    users = load_users()

    course_key = courses_map[message.text]

    if course_key not in users[target_user]["opened_courses"]:
        users[target_user]["opened_courses"].append(course_key)

    save_users(users)

    courses = load_courses()
    course_name = courses[course_key]["name"]

    try:
        bot.send_message(
            int(target_user),
            f"🎉 Tabriklaymiz!\n\n🔓 Sizga {course_name} kursi ochildi.\n\n📚 Kurs kanali:\n{courses[course_key]['link']}\n\n━━━━━━━━━━\n🎁 Endi boshqa premium kurslarni ham ochishingiz mumkin."
        )
    except:
        pass

    bot.send_message(
        message.chat.id,
        f"✅ {target_user} uchun {course_name} kursi ochildi."
    )

    del grant_user[message.chat.id]
@bot.message_handler(func=lambda m: m.text == "🧹 Referral reset" and m.from_user.id == ADMIN_ID)
def referral_reset_start(message):
    reset_mode.add(message.chat.id)
    bot.send_message(message.chat.id, "🧹 Referali nolga tushuriladigan User ID ni yuboring")

@bot.message_handler(func=lambda m: m.chat.id in reset_mode)
def referral_reset_finish(message):
    if message.from_user.id != ADMIN_ID:
        return
    reset_mode.discard(message.chat.id)
    user_id = message.text.strip()
    users = load_users()
    if user_id not in users:
        bot.send_message(message.chat.id, "❌ User topilmadi")
        return
    courses = load_courses()
    for course_key in courses:
        users[user_id]["referrals"][course_key] = 0
    save_users(users)
    bot.send_message(message.chat.id, f"✅ {user_id} referallari nolga tushirildi.")

@bot.message_handler(func=lambda m: m.text == "🗑 Delete User" and m.from_user.id == ADMIN_ID)
def delete_user_start(message):
    delete_mode.add(message.chat.id)
    bot.send_message(message.chat.id, "🗑 O'chirilishi kerak bo'lgan User ID ni yuboring")

@bot.message_handler(func=lambda m: m.chat.id in delete_mode)
def delete_user_finish(message):
    if message.from_user.id != ADMIN_ID:
        return
    delete_mode.discard(message.chat.id)
    user_id = message.text.strip()
    users = load_users()
    if user_id not in users:
        bot.send_message(message.chat.id, "❌ User topilmadi")
    banned_users.add(user_id)
    del users[user_id]
    save_users(users)
    bot.send_message(message.chat.id, f"✅ {user_id} bloklandi va o'chirildi.")
    try:
        bot.send_message(int(user_id), "⛔ Bot vaqtincha ish faoliyatida emas.")
    except:
        pass
    bot.send_message(message.chat.id, f"✅ {user_id} o'chirildi.")
@bot.message_handler(func=lambda m: m.text == "📢 Broadcast" and m.from_user.id == ADMIN_ID)
def broadcast_start(message):
    broadcast_mode.add(message.chat.id)
    bot.send_message(message.chat.id, "📢 Yubormoqchi boqlgan xabarni yozing")

@bot.message_handler(content_types=["text","photo","video","document","audio","voice","sticker","animation"], func=lambda m: m.chat.id in broadcast_mode)
def broadcast_send(message):
    if message.from_user.id != ADMIN_ID:
        return
    broadcast_mode.discard(message.chat.id)
    users = load_users()
    success = 0
    fail = 0
    for user_id in users:
        try:
            bot.copy_message(int(user_id), message.chat.id, message.message_id)
            success += 1
        except:
            fail += 1
    bot.send_message(message.chat.id, f"✅ Yuborildi: {success}\n❌ Xato: {fail}")
@bot.message_handler(func=lambda m: m.text == "✅ Unban User" and m.from_user.id == ADMIN_ID)
def unban_start(message):
    unban_mode.add(message.chat.id)
    bot.send_message(message.chat.id, "✅ Unban qilinadigan User ID ni yuboring")

@bot.message_handler(func=lambda m: m.chat.id in unban_mode)
def unban_finish(message):
    if message.from_user.id != ADMIN_ID:
        return
    unban_mode.discard(message.chat.id)
    user_id = message.text.strip()
    if user_id in banned_users:
        banned_users.discard(user_id)
        bot.send_message(message.chat.id, f"✅ {user_id} unban qilindi.")
    else:
        bot.send_message(message.chat.id, "❌ Bu user banlarda topilmadi.")
bot.infinity_polling(
    timeout=10,
    long_polling_timeout=5
)
