import os
import time
import json
import threading
import telebot
from telebot import types
from pymongo import MongoClient

# Railway Variables
TOKEN = os.getenv("BOT_TOKEN")
MONGO_URL = os.getenv("MONGO_URL")

ADMIN_ID = 1420365532

# Database connection
client = MongoClient(MONGO_URL)
db = client["master_dars"]
users_col = db["users"]
banned_col = db["banned"]

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

# Banned users
banned_users = set()
for doc in banned_col.find():
    banned_users.add(str(doc["_id"]))

user_states = {}
grant_user = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COURSES_FILE = os.path.join(BASE_DIR, "courses.json")

# ---------- HELPER FUNCTIONS ----------

def load_courses():
    with open(COURSES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_user(user_id):
    return users_col.find_one({"_id": str(user_id)})

def create_user_if_not_exists(user_id):
    user_id = str(user_id)
    user = get_user(user_id)
    if not user:
        courses = load_courses()
        referrals = {course_key: 0 for course_key in courses}
        new_data = {
            "_id": user_id,
            "referrals": referrals,
            "opened_courses": [],
            "last_course": "",
            "time": time.time(),
            "quiz_score": 0,           # Test ballari
            "solved_quizzes": [],      # Yechilgan testlar ID ro'yxati
            "reward_50_notified": False, # 50 ball xabari yuborilganlik bayrog'i
            "inactive_reminder_sent": False,
            "offer_sent": False,
            "offer_sent_2": False
        }
        users_col.insert_one(new_data)
        return new_data
    return user

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💻 Dasturlash", "💼 Office dasturlari")
    markup.row("📒 1C Buxgalteriya", "🌍 Chet tillari")
    markup.row("📐 AutoCAD", "🏠 3Ds Max")
    markup.row("🎨 Photoshop", "🖌 Corel Draw")
    markup.row("🏗 Revit", "🎬 Videomontaj")
    markup.row("🤖 Telegram Bot yasash")
    markup.row("🧠 Mini-Test (Natijam)", "📊 Statistika")
    markup.row("🏆 TOP Referral")
    return markup

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

# ---------- START HANDLER ----------

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)

    if user_id in banned_users:
        bot.send_message(message.chat.id, "⛔ Bot vaqtincha ish faoliyatida emas.")
        return

    is_new_user = get_user(user_id) is None
    user = create_user_if_not_exists(user_id)
    courses = load_courses()
    args = message.text.split()

    if len(args) > 1 and is_new_user:
        try:
            referrer_id, course_key = args[1].split("_", 1)
            referrer = get_user(referrer_id)

            if referrer and referrer_id != user_id and course_key in courses:
                users_col.update_one(
                    {"_id": referrer_id},
                    {"$inc": {f"referrals.{course_key}": 1}}
                )
                
                updated_referrer = get_user(referrer_id)
                current = updated_referrer["referrals"][course_key]
                required = courses[course_key]["required"]
                remaining = required - current

                if current < required:
                    bot.send_message(
                        int(referrer_id),
                        f"🎉 Tabriklaymiz!\n\nYangi do‘stingiz botga qo‘shildi.\n\n{courses[course_key]['name']}\n\n✅ {current}/{required} referral\n\n👥 Maqsadgacha yana {remaining} ta do‘st qoldi."
                    )
                elif current == 5:
                    bot.send_message(
                        int(referrer_id),
                        f"🚀 Zo‘r ketayapsiz!\n\n{courses[course_key]['name']}\n\n🔥 5/{required} referral\n\nYarim yo‘lni bosib o‘tdingiz."
                    )
                elif current == required - 1:
                    bot.send_message(
                        int(referrer_id),
                        f"🔥 Oxirgi qadam!\n\n{courses[course_key]['name']}\n\n⚡ {current}/{required} referral\n\nKurs ochilishiga atigi 1 ta odam qoldi."
                    )

                if current >= required and course_key not in updated_referrer["opened_courses"]:
                    users_col.update_one(
                        {"_id": referrer_id},
                        {"$push": {"opened_courses": course_key}}
                    )
                    bot.send_message(
                        int(referrer_id),
                        f"🎉 Tabriklaymiz!\n\n🔓 Siz {courses[course_key]['name']} kursini muvaffaqiyatli ochdingiz.\n\n📚 Kurs kanali:\n{courses[course_key]['link']}\n\n━━━━━━━━━━\n🎁 Endi boshqa premium kurslarni ham ochishingiz mumkin."
                    )
        except Exception as e:
            print("Referral error:", e)

    bot.send_message(
        message.chat.id,
        "🔥 Premium kurslarni BEPUL o‘rganing!\n\n📚 800+ videodars\n🎓 11 ta premium kurs\n\n🔓 Kursni ochish uchun atigi 10 ta do‘stingizga botga start bosdiring.\n\n👇 Kurslardan birini tanlang:",
        reply_markup=main_menu()
    )

# ---------- COURSE HANDLERS ----------

@bot.message_handler(func=lambda m: m.text in COURSE_BUTTONS)
def show_course(message):
    user_id = str(message.from_user.id)
    if user_id in banned_users:
        bot.send_message(message.chat.id, "⛔ Bot vaqtincha ish faoliyatida emas.")
        return

    course_key = COURSE_BUTTONS[message.text]
    create_user_if_not_exists(user_id)
    users_col.update_one({"_id": user_id}, {"$set": {"last_course": course_key}})

    course = load_courses()[course_key]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚀 Taklif qilish", "📊 Mening natijam")
    markup.row("🏆 TOP Referral", "⬅️ Asosiy menyu")

    text = f"{course['name']}\n\n📚 Darslar soni: {course['lessons']}\n\n📖 Tarkibi:\n{course['info']}\n\n🔓 Kursni ochish uchun:\n👥 {course['required']} ta do‘st taklif qiling."
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⬅️ Asosiy menyu")
def back_to_menu(message):
    bot.send_message(message.chat.id, "🏠 Asosiy menyu", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🚀 Taklif qilish")
def share_link(message):
    user_id = str(message.from_user.id)
    user = get_user(user_id)
    course_key = user.get("last_course") if user else None

    if not course_key:
        bot.send_message(message.chat.id, "❗ Avval kurs tanlang.")
        return

    course = load_courses()[course_key]
    link = f"https://t.me/master_darsbot?start={user_id}_{course_key}"
    text = f"🎁 Premium kurslarni bepul olayotgan edim.\n\n📚 800+ videodars\n🎓 11 ta premium kurs\n\n🔥 Men aynan {course['name']} kursini ochyapman.\n\n👇 Kirib START bosing:\n{link}\n\n⚡ Kurslar hozircha bepul."
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "📊 Mening natijam")
def my_result(message):
    user_id = str(message.from_user.id)
    if user_id in banned_users:
        return

    user = get_user(user_id)
    course_key = user.get("last_course") if user else None

    if not course_key:
        bot.send_message(message.chat.id, "❗ Avval kurs tanlang.")
        return

    course = load_courses()[course_key]
    current = user.get("referrals", {}).get(course_key, 0)
    required = course["required"]
    remaining = max(0, required - current)

    blocks = 10
    filled = int((current / required) * blocks) if required > 0 else 0
    filled = min(filled, blocks)
    progress = "█" * filled + "░" * (blocks - filled)

    text = f"{course['name']}\n\n📊 Sizning natijangiz\n\n{progress}\n\n✅ {current}/{required} referral\n\n👥 Yana {remaining} ta do‘st taklif qiling.\n\n🎁 Kurs avtomatik ochiladi."
    bot.send_message(message.chat.id, text)

# ---------- MINI-TEST STATS BUTTON ----------

@bot.message_handler(func=lambda m: m.text == "🧠 Mini-Test (Natijam)")
def show_quiz_stats(message):
    user_id = str(message.from_user.id)
    if user_id in banned_users:
        return

    user = create_user_if_not_exists(user_id)
    score = user.get("quiz_score", 0)
    
    # Maqsad ma'lumotlari
    if score < 50:
        target = 50
        remaining = target - score
        goal_text = f"🎯 Bepul kurs olish uchun yana <b>{remaining} ball</b> to'plashingiz kerak!"
    else:
        target = 200
        remaining = max(0, target - score)
        goal_text = f"🎯 Keyingi 2-bepul kurs uchun yana <b>{remaining} ball</b> to'plashingiz kerak!"

    blocks = 10
    filled = int((score / target) * blocks) if target > 0 else 0
    filled = min(filled, blocks)
    progress = "█" * filled + "░" * (blocks - filled)

    text = (
        f"🧠 <b>Sizning Test Natijangiz</b>\n\n"
        f"📊 Jamlangan ball: <b>{score} / {target}</b>\n"
        f" Progress: [{progress}]\n\n"
        f"{goal_text}\n\n"
        f"⏳ <i>Eslatib o'tamiz: Har bir mini-test yuborilgandan so'ng faqat 12 soat davomida faol bo'ladi. Keyingi testlarni o'tkazib yubormang!</i>"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "🏆 TOP Referral")
def top_referral(message):
    user_id = str(message.from_user.id)
    if user_id in banned_users:
        return

    ranking = []
    for user in users_col.find():
        uid = user["_id"]
        total = sum(user.get("referrals", {}).values())
        ranking.append((uid, total))

    ranking.sort(key=lambda x: x[1], reverse=True)
    text = "🏆 TOP Referralchilar\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, (uid, total) in enumerate(ranking[:10]):
        try:
            tg_user = bot.get_chat(int(uid))
            name = tg_user.first_name
        except Exception:
            name = "User"

        if i < 3:
            text += f"{medals[i]} {name} — {total} ta\n"
        else:
            text += f"{i+1}. {name} — {total} ta\n"

    my_place = 0
    my_total = 0
    for i, (uid, total) in enumerate(ranking):
        if uid == user_id:
            my_place = i + 1
            my_total = total
            break

    text += f"\n━━━━━━━━━━\n\n👤 Siz:\n🏅 O‘rin: {my_place}\n👥 Referral: {my_total}"
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['id'])
def my_id(message):
    bot.send_message(message.chat.id, str(message.from_user.id))

# ---------- ADMIN PANEL ----------

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📊 Statistika", "👥 Userlar soni")
    markup.row("📢 Broadcast", "📝 Aralash Test Yuborish")
    markup.row("🎓 Kurs ochish", "🔍 User qidirish")
    markup.row("🏆 TOP Referral", "🧹 Referral reset")
    markup.row("🗑 Delete User", "✅ Unban User")
    bot.send_message(message.chat.id, "🛠 Admin Panel", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📊 Statistika")
def statistika(message):
    user_id = str(message.from_user.id)
    if user_id in banned_users:
        return

    if message.from_user.id == ADMIN_ID:
        total_users = users_col.count_documents({})
        total_referrals = 0
        for user in users_col.find():
            total_referrals += sum(user.get("referrals", {}).values())
        bot.send_message(
            message.chat.id,
            f"📊 Bot statistikasi\n\n👥 Userlar: {total_users}\n\n🏆 Jami referral: {total_referrals}"
        )
    else:
        user = get_user(user_id)
        total = sum(user.get("referrals", {}).values()) if user else 0
        opened = len(user.get("opened_courses", [])) if user else 0
        faol = "🔥 Faol" if total > 0 else "😴 Hali boshlanmagan"
        bot.send_message(
            message.chat.id,
            f"📊 Sizning statistikangiz\n\n👥 Jami referral: {total}\n\n🎓 Ochilgan kurslar: {opened}\n\n🏆 Faollik holati:\n{faol}"
        )

@bot.message_handler(func=lambda m: m.text == "👥 Userlar soni" and m.from_user.id == ADMIN_ID)
def admin_users_count(message):
    total = users_col.count_documents({})
    bot.send_message(message.chat.id, f"👥 Jami userlar: {total}")

@bot.message_handler(func=lambda m: m.text == "🔍 User qidirish" and m.from_user.id == ADMIN_ID)
def search_user_start(message):
    user_states[message.chat.id] = "search_user"
    bot.send_message(message.chat.id, "🔍 User ID yuboring")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "search_user" and m.from_user.id == ADMIN_ID)
def search_user_finish(message):
    user_states.pop(message.chat.id, None)
    target_id = message.text.strip()
    data = get_user(target_id)

    if not data:
        bot.send_message(message.chat.id, "❌ User topilmadi")
        return

    total_referrals = sum(data.get("referrals", {}).values())
    opened = len(data.get("opened_courses", []))
    quiz_score = data.get("quiz_score", 0)

    try:
        tg_user = bot.get_chat(int(target_id))
        name = tg_user.first_name
    except Exception:
        name = "Noma'lum"

    bot.send_message(
        message.chat.id,
        f"👤 Ism: {name}\n🆔 ID: {target_id}\n🏆 Referral: {total_referrals}\n🧠 Test Ballari: {quiz_score}\n📚 Ochilgan kurslar: {opened}\n🕒 Oxirgi kurs: {data.get('last_course', '-')}"
    )

@bot.message_handler(func=lambda m: m.text == "🎓 Kurs ochish" and m.from_user.id == ADMIN_ID)
def grant_course_start(message):
    user_states[message.chat.id] = "grant_user_id"
    bot.send_message(message.chat.id, "🎓 Kurs beriladigan User ID ni yuboring")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "grant_user_id" and m.from_user.id == ADMIN_ID)
def grant_course_user(message):
    target_id = message.text.strip()
    if not get_user(target_id):
        bot.send_message(message.chat.id, "❌ User topilmadi")
        user_states.pop(message.chat.id, None)
        return

    grant_user[message.chat.id] = target_id
    user_states[message.chat.id] = "grant_course_select"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("1️⃣ Dasturlash", "2️⃣ Office")
    markup.row("3️⃣ Buxgalteriya", "4️⃣ Chet tillari")
    markup.row("5️⃣ AutoCAD", "6️⃣ 3Ds Max")
    markup.row("7️⃣ Photoshop", "8️⃣ Corel Draw")
    markup.row("9️⃣ Revit", "🔟 Videomontaj")
    markup.row("1️⃣1️⃣ Telegram Bot")
    bot.send_message(message.chat.id, "Kursni tanlang", reply_markup=markup)

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "grant_course_select" and m.from_user.id == ADMIN_ID)
def grant_course_finish(message):
    user_states.pop(message.chat.id, None)
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
        bot.send_message(message.chat.id, "❌ Noto'g'ri kurs tanlandi.")
        return

    target_user = grant_user.pop(message.chat.id, None)
    if not target_user:
        return

    course_key = courses_map[message.text]
    users_col.update_one({"_id": target_user}, {"$addToSet": {"opened_courses": course_key}})

    courses = load_courses()
    course_name = courses[course_key]["name"]

    try:
        bot.send_message(
            int(target_user),
            f"🎉 Tabriklaymiz!\n\n🔓 Sizga {course_name} kursi ochildi.\n\n📚 Kurs kanali:\n{courses[course_key]['link']}\n\n━━━━━━━━━━\n🎁 Endi boshqa premium kurslarni ham ochishingiz mumkin."
        )
    except Exception:
        pass

    bot.send_message(message.chat.id, f"✅ {target_user} uchun {course_name} kursi ochildi.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "🧹 Referral reset" and m.from_user.id == ADMIN_ID)
def referral_reset_start(message):
    user_states[message.chat.id] = "reset_user"
    bot.send_message(message.chat.id, "🧹 Referali nolga tushuriladigan User ID ni yuboring")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "reset_user" and m.from_user.id == ADMIN_ID)
def referral_reset_finish(message):
    user_states.pop(message.chat.id, None)
    target_id = message.text.strip()
    if not get_user(target_id):
        bot.send_message(message.chat.id, "❌ User topilmadi")
        return

    courses = load_courses()
    reset_dict = {f"referrals.{ck}": 0 for ck in courses}
    users_col.update_one({"_id": target_id}, {"$set": reset_dict})
    bot.send_message(message.chat.id, f"✅ {target_id} referallari nolga tushirildi.")

@bot.message_handler(func=lambda m: m.text == "🗑 Delete User" and m.from_user.id == ADMIN_ID)
def delete_user_start(message):
    user_states[message.chat.id] = "delete_user"
    bot.send_message(message.chat.id, "🗑 O'chirilishi kerak bo'lgan User ID ni yuboring")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "delete_user" and m.from_user.id == ADMIN_ID)
def delete_user_finish(message):
    user_states.pop(message.chat.id, None)
    target_id = message.text.strip()

    if not get_user(target_id):
        bot.send_message(message.chat.id, "❌ User topilmadi")
        return

    banned_users.add(target_id)
    banned_col.update_one({"_id": target_id}, {"$set": {"_id": target_id}}, upsert=True)
    users_col.delete_one({"_id": target_id})

    bot.send_message(message.chat.id, f"✅ {target_id} bloklandi va bazadan o'chirildi.")
    try:
        bot.send_message(int(target_id), "⛔ Bot vaqtincha ish faoliyatida emas.")
    except Exception:
        pass

@bot.message_handler(func=lambda m: m.text == "✅ Unban User" and m.from_user.id == ADMIN_ID)
def unban_start(message):
    user_states[message.chat.id] = "unban_user"
    bot.send_message(message.chat.id, "✅ Unban qilinadigan User ID ni yuboring")

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "unban_user" and m.from_user.id == ADMIN_ID)
def unban_finish(message):
    user_states.pop(message.chat.id, None)
    target_id = message.text.strip()

    if target_id in banned_users:
        banned_users.discard(target_id)
        banned_col.delete_one({"_id": target_id})
        bot.send_message(message.chat.id, f"✅ {target_id} unban qilindi.")
    else:
        bot.send_message(message.chat.id, "❌ Bu user banlarda topilmadi.")

@bot.message_handler(func=lambda m: m.text == "📢 Broadcast" and m.from_user.id == ADMIN_ID)
def broadcast_start(message):
    user_states[message.chat.id] = "broadcast"
    bot.send_message(message.chat.id, "📢 Yubormoqchi bo'lgan xabarni yozing")

@bot.message_handler(content_types=["text","photo","video","document","audio","voice","sticker","animation"], func=lambda m: user_states.get(m.chat.id) == "broadcast" and m.from_user.id == ADMIN_ID)
def broadcast_send(message):
    user_states.pop(message.chat.id, None)
    success = 0
    fail = 0

    for user in users_col.find():
        uid = user["_id"]
        try:
            bot.copy_message(int(uid), message.chat.id, message.message_id)
            success += 1
        except Exception:
            fail += 1

    bot.send_message(message.chat.id, f"✅ Yuborildi: {success}\n❌ Xato: {fail}")

# ---------- MINI-TEST SYSTEM ----------

@bot.message_handler(func=lambda m: m.text == "📝 Aralash Test Yuborish" and m.from_user.id == ADMIN_ID)
def quiz_start(message):
    user_states[message.chat.id] = "send_quiz_json"
    bot.send_message(
        message.chat.id, 
        "📝 Men bergan Tayyor Aralash Test JSON matnini nusxalab shu yerga yuboring:"
    )

@bot.message_handler(func=lambda m: user_states.get(m.chat.id) == "send_quiz_json" and m.from_user.id == ADMIN_ID)
def quiz_broadcast(message):
    user_states.pop(message.chat.id, None)
    try:
        quiz_data = json.loads(message.text.strip())
        
        # Test yaratilgan vaqtini belgilash
        current_time = time.time()
        quiz_id = str(int(current_time))
        quiz_data["quiz_id"] = quiz_id
        quiz_data["created_at"] = current_time

        # Bazaga joriy test sifatida saqlash
        db["quiz"].delete_many({}) 
        db["quiz"].insert_one(quiz_data)

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("▶️ Testni boshlash", callback_data=f"start_quiz_{quiz_id}_0_0"))

        success = 0
        for user in users_col.find():
            try:
                bot.send_message(
                    int(user["_id"]),
                    f"🧠 <b>Bugungi Bilim Sinovi (Mini-Test)!</b>\n\n📌 <b>Mavzu:</b> {quiz_data.get('title', 'Aralash Test')}\n❓ <b>Savollar soni:</b> {len(quiz_data['questions'])} ta (Juda oson!)\n🎁 <b>Har bir to'g'ri javob: +1 ball</b>\n\n⏳ <i>Diqqat: Test yechish uchun atigi 12 soat vaqtingiz bor!</i>\n\n👇 Bilimingizni sinash va ball to'plash uchun bosing:",
                    reply_markup=markup,
                    parse_mode="HTML"
                )
                success += 1
            except Exception:
                pass

        bot.send_message(message.chat.id, f"✅ Test {success} ta foydalanuvchiga yuborildi!", reply_markup=main_menu())
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ JSON formatda xatolik bor: {e}", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith("start_quiz_") or call.data.startswith("ans_"))
def handle_quiz_step(call):
    try:
        bot.answer_callback_query(call.id)

        user_id = str(call.from_user.id)
        user_data = create_user_if_not_exists(user_id)

        quiz = db["quiz"].find_one()
        if not quiz:
            bot.send_message(call.message.chat.id, "❌ Test topilmadi yoki yangi test yuborilgan.")
            return

        # 12 SOATLIK MUDDATNI TEKSHIRISH (12 soat = 43200 sek)
        created_at = quiz.get("created_at", 0)
        if time.time() - created_at > 43200:
            bot.send_message(call.message.chat.id, "⏰ <b>Afsuski, ushbu testning 12 soatlik vaqti tugagan!</b>\n\nO'tkazib yubormaslik uchun keyingi testlarni tezroq yechishga harakat qiling.", parse_mode="HTML")
            return

        quiz_id = quiz.get("quiz_id", "default")

        # BIR MARTA YECHISH CHEKLOVI
        solved_list = user_data.get("solved_quizzes", [])
        if quiz_id in solved_list:
            bot.send_message(call.message.chat.id, "⚠️ <b>Siz ushbu testni topshirib bo'lgansiz!</b>\n\nYangi test yuborilishini kuting. Jamlangan ballaringizni <b>🧠 Mini-Test (Natijam)</b> bo'limida ko'rishingiz mumkin.", parse_mode="HTML")
            return

        questions = quiz["questions"]
        parts = call.data.split("_")
        
        if call.data.startswith("start_quiz_"):
            q_idx = int(parts[3])
            score = int(parts[4])
        else:
            q_idx = int(parts[1])
            score = int(parts[2])
            chosen = int(parts[3])
            
            if chosen == questions[q_idx]["correct"]:
                score += 1
            q_idx += 1

        # Test yakunlanganda
        if q_idx >= len(questions):
            # Ballni oshirish hamda yechilganlar ro'yxatiga qo'shish
            users_col.update_one(
                {"_id": user_id},
                {
                    "$inc": {"quiz_score": score},
                    "$push": {"solved_quizzes": quiz_id}
                }
            )

            updated_user = get_user(user_id)
            total_score = updated_user.get("quiz_score", 0)

            # TEST TUGAGANDAGI BATAFSIL TUSHUNTIRISH
            text = (
                f"🎉 <b>Ajoyib natija!</b>\n\n"
                f"📊 Siz bu testdan <b>{score} ball</b> to'pladingiz!\n"
                f"🏆 Barcha testlardan to'plagan umumiy ballaringiz: <b>{total_score} ball</b>\n\n"
                f"💡 <i>Ballaringiz sizning hisobingizga muvaffaqiyatli qo'shildi! Asosiy menyudagi <b>🧠 Mini-Test (Natijam)</b> tugmasini bosib o'z progress panelingizni va maqsadgacha qancha qolganini kuzatib borishingiz mumkin.</i>"
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🏠 Asosiy Menyuga o'tish", callback_data="back_to_main"))
            
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

            # 50 BALLGA YETGANDA USERGA VA ADMINGA XABAR YUBORISH
            if total_score >= 50 and not updated_user.get("reward_50_notified", False):
                users_col.update_one({"_id": user_id}, {"$set": {"reward_50_notified": True}})

                # 1. Userga xabar
                user_msg = (
                    f"🎉 <b>TABRIKLAYMIZ! Siz 50 ball to'pladingiz!</b>\n\n"
                    f"⚡ Tez orada admin siz bilan shaxsan bog'lanadi va o'zingiz tanlagan 1 ta premium kursni BEPUL ochib beradi!\n\n"
                    f"🎁 <b>YANA BIR IMKONIYAT:</b> Agarda testlarda faol bo'lib umumiy ballaringizni <b>200 ball</b>ga yetkazsangiz, sizga YANA BIR kurs xuddi shunday BEPUL ochib beriladi!\n\n"
                    f"🚀 Testlarni o'tkazib yubormasdan ishtirok etishda davom eting!"
                )
                try:
                    bot.send_message(int(user_id), user_msg, parse_mode="HTML")
                except Exception:
                    pass

                # 2. Adminga xabar
                try:
                    tg_user = bot.get_chat(int(user_id))
                    user_name = tg_user.first_name
                except Exception:
                    user_name = "User"

                admin_msg = (
                    f"🚨 <b>YANGI G'OLIB! (50 BALL TO'PLANDI)</b>\n\n"
                    f"👤 <b>Ism:</b> {user_name}\n"
                    f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
                    f"🏆 <b>Jamlangan ball:</b> {total_score} ball\n\n"
                    f"💬 <i>Foydalanuvchi bilan bog'laning, hol-ahvol so'rang, bepul kursini ochib berib, keyingi bosqich va pullik taklifingizni bildiring!</i>"
                )
                bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")

            return

        # Navbatdagi savolni chiqarish
        q = questions[q_idx]
        markup = types.InlineKeyboardMarkup()
        for opt_idx, option in enumerate(q["options"]):
            markup.add(types.InlineKeyboardButton(option, callback_data=f"ans_{q_idx}_{score}_{opt_idx}"))

        cat = q.get('category', 'Umumiy')
        question_text = q['q']

        bot.edit_message_text(
            f"❓ <b>Savol {q_idx + 1}/{len(questions)}</b> ({cat})\n\n{question_text}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Quiz Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "back_to_main")
def back_to_main_callback(call):
    bot.send_message(call.message.chat.id, "🏠 Asosiy menyu", reply_markup=main_menu())

# ---------- BACKGROUND REMINDER THREAD ----------

def check_users():
    now = time.time()
    for user in users_col.find():
        user_id = user["_id"]
        if user_id == str(ADMIN_ID) or user_id in banned_users:
            continue

        try:
            total = sum(user.get("referrals", {}).values())
            passed = now - user.get("time", now)

            # 24 hours
            if total == 0 and passed >= 86400 and not user.get("inactive_reminder_sent"):
                bot.send_message(
                    int(user_id),
                    "🎓 Daromadli kasblarni o'rganishni boshlang.\n\nShunchaki 10 ta do'stingizga botga START bosishini so'rang.\n\n📚 Premium kurslar avtomatik ochiladi."
                )
                users_col.update_one({"_id": user_id}, {"$set": {"inactive_reminder_sent": True}})

            # 48 hours
            if 0 <= total <= 9 and passed >= 172800 and not user.get("offer_sent"):
                bot.send_message(
                    int(user_id),
                    "💎 Kursni hali ocholmadingizmi?\n\nHech qisi yo'q.\n\n💎 Atigi 59 000 so'm evaziga hohlagan kursingizni hoziroq ochishingiz mumkin.\n\n👨‍💻 Admin:\n@MasterdarsAdmin"
                )
                users_col.update_one({"_id": user_id}, {"$set": {"offer_sent": True}})

            # 120 hours
            if 0 <= total <= 9 and passed >= 432000 and not user.get("offer_sent_2"):
                bot.send_message(
                    int(user_id),
                    "🔥 Oxirgi eslatma!\n\nKurslarni bepul ochish imkoniyati hali bor.\n\n💎 Yoki atigi 59 000 so'm evaziga hoziroq oching.\n\n👨‍💻 Admin:\n@MasterdarsAdmin"
                )
                users_col.update_one({"_id": user_id}, {"$set": {"offer_sent_2": True}})

        except Exception:
            pass

def reminder_loop():
    while True:
        try:
            check_users()
        except Exception as e:
            print("Reminder error:", e)
        time.sleep(3600)

threading.Thread(target=reminder_loop, daemon=True).start()

print("Bot ishga tushdi...")
try:
    bot.send_message(ADMIN_ID, "✅ Bot ishga tushdi!")
except Exception:
    pass

bot.infinity_polling(timeout=10, long_polling_timeout=5)
