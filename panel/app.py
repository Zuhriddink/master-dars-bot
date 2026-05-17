from flask import request
import telebot
import threading
import os
from flask import Flask
import json
TOKEN = "8961895801:AAHWY3fv-DMcW-D1-THQtIliVeKSycWCTZg"

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

def load_users():

    try:

        with open("users.json", "r") as file:

            return json.load(file)

    except:

        return {}

@app.route("/", methods=["GET", "POST"])
def home():

    users = load_users()

    result = ""

    if request.method == "POST":

        text = request.form["message"]

        sent = 0

        for user_id in users:

            try:

                bot.send_message(user_id, text)

                sent += 1

            except:
                pass

    result = f"✅ {sent} ta userga yuborildi"

    total_users = len(users)

    total_autocad = 0
    total_photoshop = 0

    for user in users.values():

        total_autocad += user["autocad"]

        total_photoshop += user["photoshop"]

    return f"""
    <h1>🔥 MASTER DARS ADMIN PANEL</h1>

    <h2>👥 Userlar: {total_users}</h2>

    <h3>📘 AutoCAD referral: {total_autocad}</h3>

    <h3>🎨 Photoshop referral: {total_photoshop}</h3>
    """
    <hr>

<h2>📢 Broadcast</h2>

<form method="POST">

<textarea name="message"
rows="5"
cols="40"
placeholder="Xabar yozing"></textarea>

<br><br>

<button type="submit">
Yuborish
</button>

</form>

<p>{result}</p>
import os
def run_bot():

    os.system("python bot.py")

threading.Thread(target=run_bot).start()

app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000))
)
