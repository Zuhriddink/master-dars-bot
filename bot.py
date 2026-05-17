import telebot
from telebot import types
import json
import os
import time

TOKEN = "8961895801:AAHWY3fv-DMcW-D1-THQtIliVeKSycWCTZg"
ADMIN_ID = 1420365532


bot = telebot.TeleBot(TOKEN)

# users.json yaratish
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

# userlarni o‘qish
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

# userlarni saqlash
def save_users(data):
    with open("users.json", "w") as f:
        json.dump(data, f)

# START
@bot.message_handler(commands=['start'])
def start(message):

    users = load_users()

    user_id = str(message.from_user.id)

    if user_id not in users:
        users[user_id] = {
    "autocad": 0,
    "photoshop": 0,
    "time": time.time(),
    "offer_sent": False
}

    # referral tekshirish
    args = message.text.split()

    if len(args) > 1:

        ref = args[1]

        if "_autocad" in ref:

            referrer_id = ref.replace("_autocad", "")

            if referrer_id != user_id:

                if referrer_id in users:

                    users[referrer_id]["autocad"] += 1

        elif "_photoshop" in ref:

            referrer_id = ref.replace("_photoshop", "")

            if referrer_id != user_id:

                if referrer_id in users:

                    users[referrer_id]["photoshop"] += 1
    total = (
        users[referrer_id]["autocad"] +
        users[referrer_id]["photoshop"]
    )

    if total == 25:

        bot.send_message(
            referrer_id,
            "🎉 Tabriklaymiz!\n\nSiz 25 ta referral yig‘dingiz va 4 ta bonus kursni qo‘lga kiritdingiz 🔥\n\n🎁 Bonusni olish uchun adminga murojaat qiling\n@Masterdarsadmin"
        )

    if total == 50:

        bot.send_message(
            referrer_id,
            "🏆 Tabriklaymiz!\n\nSiz 50 ta referral yig‘dingiz va 10 ta bonus kursni qo‘lga kiritdingiz 🚀\n\n🎁 Bonusni olish uchun adminga murojaat qiling:\n@Masterdarsadmin"
        )

    save_users(users)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn1 = types.KeyboardButton("📘 AutoCAD")
    btn2 = types.KeyboardButton("🎨 Photoshop")
    btn3 = types.KeyboardButton("📊 Statistika")
    btn4 = types.KeyboardButton("🏆 TOP Referral")

    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)

    bot.send_message(
        message.chat.id,
        "🎓 MasterDars ga xush kelibsiz!",
        reply_markup=markup
    )

# AUTOCAD
@bot.message_handler(func=lambda message: message.text == "📘 AutoCAD")
def autocad(message):

    users = load_users()

    user_id = str(message.from_user.id)

    count = users[user_id]["autocad"]

    # 10 ta bo‘lsa kurs ochiladi
    if count >= 10:

        bot.send_message(
            message.chat.id,
            "🎉 Tabriklaymiz!\n\n📘 Kurs ochildi 🔓\n\nhttps://t.me/+6i0sOENQzk8wZmUy"
        )

        return

    link = f"https://t.me/master_darsbot?start={user_id}_autocad"

    text = f"""
📘 AutoCAD Professional Kursi

✅ 101 ta videodars
✅ 20 soatlik material

👥 Kursni ochish uchun:
10 ta odam taklif qiling

📨 Sizning linkingiz:
{link}
"""

    bot.send_message(message.chat.id, text)

# PHOTOSHOP
@bot.message_handler(func=lambda message: message.text == "🎨 Photoshop")
def photoshop(message):

    users = load_users()

    user_id = str(message.from_user.id)

    count = users[user_id]["photoshop"]

    # 10 ta referral bo‘lsa
    if count >= 10:

        bot.send_message(
            message.chat.id,
            "🎉 Tabriklaymiz!\n\n🎨 Photoshop kursi siz uchun ochildi 🔓\n\n📚 Kanal linki:\nhttps://t.me/+-0nM3acocU1mY2Uy"
        )

        return

    link = f"https://t.me/master_darsbot?start={user_id}_photoshop"

    text = f"""
🎨 Photoshop Professional Kursi

✅ 25 ta videodars
✅ Amaliy darslar
✅ Dizayn uchun tayyor loyihalar

⏳ 7-10 kunda o‘rganishingiz mumkin.

👨‍🏫 Bepul yordam beriladi.

🔓 Kursni ochish uchun:
👥 10 ta odam taklif qiling

📨 Sizning linkingiz:
{link}
"""

    bot.send_message(message.chat.id, text)

# ADMIN PANEL
@bot.message_handler(commands=['admin'])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:
        return

    users = load_users()

    total_users = len(users)

    total_autocad = 0
    total_photoshop = 0

    for user in users.values():

        total_autocad += user["autocad"]
        total_photoshop += user["photoshop"]

    text = f"""
📊 ADMIN PANEL

👥 Foydalanuvchilar: {total_users}

📘 AutoCAD referral:
{total_autocad}

🎨 Photoshop referral:
{total_photoshop}
"""

    bot.send_message(message.chat.id, text)

# BROADCAST
@bot.message_handler(commands=['send'])
def broadcast(message):

    if message.from_user.id != ADMIN_ID:
        return

    users = load_users()

    text = message.text.replace("/send ", "")

    count = 0

    for user_id in users:

        try:

            bot.send_message(user_id, text)

            count += 1

        except:
            pass

    bot.send_message(
        message.chat.id,
        f"✅ Xabar yuborildi: {count} ta user"
    )

# TOP REFERRAL
@bot.message_handler(func=lambda message: message.text == "🏆 TOP Referral")
def top_ref(message):

    users = load_users()

    top_users = []

    for user_id, data in users.items():

        total = data["autocad"] + data["photoshop"]

        top_users.append((user_id, total))

    top_users.sort(key=lambda x: x[1], reverse=True)

    text = "🏆 TOP Referralchilar\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for i, (user_id, total) in enumerate(top_users[:5]):

        try:

            user = bot.get_chat(user_id)

            name = user.first_name

        except:

            name = "User"

        if i < 3:

            text += f"{medals[i]} {name} — {total} ta\n"

        else:

            text += f"{i+1}. {name} — {total} ta\n"

    your_id = str(message.from_user.id)

    your_place = 0

    your_total = 0

    for i, (user_id, total) in enumerate(top_users):

        if user_id == your_id:

            your_place = i + 1

            your_total = total

            break

    text += f"\n━━━━━━━━━━\n\n👤 Siz:\n{your_place}-o‘rin — {your_total} ta referral"

    bot.send_message(message.chat.id, text)

# STATISTIKA
@bot.message_handler(func=lambda message: message.text == "📊 Statistika")
def stats(message):

    users = load_users()

    user_id = str(message.from_user.id)

    count_a = users[user_id]["autocad"]
    count_p = users[user_id]["photoshop"]

    text = f"""
📊 Sizning statistikangiz

📘 AutoCAD: {count_a}/10
🎨 Photoshop: {count_p}/10
"""

    bot.send_message(message.chat.id, text)

print("Bot ishga tushdi...")

while True:

    users = load_users()

    for user_id in users:

        user = users[user_id]

        autocad = user["autocad"]
        photoshop = user["photoshop"]

        total = autocad + photoshop

        passed = time.time() - user["time"]

        if (
            total > 0
            and (autocad < 10 or photoshop < 10)
            and passed > 259200
            and user["offer_sent"] == False
        ):

            text = """
Assalomu alaykum 😊

Siz kursni olish uchun harakat qilib ko‘rdingiz, lekin hali barcha kurslarni ocholmadingiz.

Bugun siz uchun maxsus imkoniyat 🔥

📚 Istalgan kurs
atigi 59 000 so‘m

✅ Videodarslar
✅ Amaliy loyihalar
✅ Private kanal
✅ Bepul ustoz yordami

📩 To‘lov uchun admin bilan bog‘laning.
"""

            try:

                markup = types.InlineKeyboardMarkup()

                btn1 = types.InlineKeyboardButton(
                    "💳 To‘lov qilish",
                    url="https://t.me/MasterdarsAdmin"
                )

                btn2 = types.InlineKeyboardButton(
                    "👨‍💻 Admin bilan bog‘lanish",
                    url="https://t.me/MasterdarsAdmin"
                )

                markup.add(btn1)
                markup.add(btn2)

                bot.send_message(
                    user_id,
                    text,
                    reply_markup=markup
                )

                users[user_id]["offer_sent"] = True

                save_users(users)

            except:
                pass

    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)

    except Exception as e:
        print(e)
