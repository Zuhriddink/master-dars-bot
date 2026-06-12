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

            "offer_sent": False

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

    users = load_users()

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
    func=lambda m: m.text == "📊 Statistika"
)
def statistics(message):

    users = load_users()

    user_id = str(message.from_user.id)

    total = sum(
        users[user_id]["referrals"].values()
    )

    opened = len(
        users[user_id]["opened_courses"]
    )

    text = f"""
📊 Sizning statistikangiz

👥 Jami referral: {total}

🎓 Ochilgan kurslar: {opened}

🏆 Faollik holati:
{"🔥 Faol" if total > 0 else "😴 Hali boshlanmagan"}
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
            if (
                total == 0
                and passed >= 86400
                and not data["inactive_reminder_sent"]
            ):

                bot.send_message(
                    int(user_id),
                    """
🎓 Daromadli kasblarni o‘rganishni boshlang.

Shunchaki 10 ta do‘stingizga botga START bosishini so‘rang.

📚 Premium kurslar avtomatik ochiladi.
"""
                )

                data["inactive_reminder_sent"] = True

            # 48 soat
            if (
                1 <= total <= 9
                and passed >= 172800
                and not data["offer_sent"]
            ):

                bot.send_message(
                    int(user_id),
                    """
🔥 Siz kursni ochishga harakat qildingiz, lekin hali yakunlay olmadingiz.

Hech qisi yo‘q.

💎 Atigi 59 000 so‘m evaziga hohlagan kursingizni hoziroq ochishingiz mumkin.

👨‍💻 Admin:
@MasterdarsAdmin
"""
                )

                data["offer_sent"] = True

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
@bot.message_handler(
    func=lambda m: m.chat.id in grant_user
)
def grant_course_finish(message):

    if message.from_user.id != ADMIN_ID:
        return

    courses_map = {
        "📐 AutoCAD": "autocad",
        "🎨 Photoshop": "photoshop",
        "🏠 3Ds Max": "max3d",
        "🏗 Revit": "revit"
    }

    if message.text not in courses_map:
        return

    target_user = grant_user[message.chat.id]

    users = load_users()

    course_key = courses_map[message.text]

    if course_key not in users[target_user]["opened_courses"]:
        users[target_user]["opened_courses"].append(course_key)

    save_users(users)

    try:
        bot.send_message(
            int(target_user),
            f"🎉 Tabriklaymiz!\n\nSizga {message.text} kursi ochildi."
        )
    except:
        pass

    bot.send_message(
        message.chat.id,
        f"✅ {target_user} uchun {message.text} kursi ochildi."
    )

    del grant_user[message.chat.id]

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
    bot.send_message(
        message.chat.id,
        "🛠 Admin Panel",
        reply_markup=markup
    )
@bot.message_handler(
    func=lambda m: m.text == "📊 Statistika"
)
def admin_stats(message):

    if message.from_user.id != ADMIN_ID:
        return

    users = load_users()

    total_users = len(users)

    total_referrals = 0

    for data in users.values():

        total_referrals += sum(
            data.get("referrals", {}).values()
        )

    bot.send_message(
        message.chat.id,
        f"""
📊 Bot statistikasi

👥 Userlar: {total_users}

🏆 Jami referral: {total_referrals}
"""
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

    markup.row("📐 AutoCAD")
    markup.row("🎨 Photoshop")
    markup.row("🏠 3Ds Max")
    markup.row("🏗 Revit")

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
    
bot.infinity_polling(
    timeout=10,
    long_polling_timeout=5
)
