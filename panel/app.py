import telebot
import threading
import os
import json

from flask import Flask, request, session, redirect

TOKEN = "8961895801:AAHWY3fv-DMcW-D1-THQtIliVeKSycWCTZg"

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

app.secret_key = "masterdarssecret"


def load_users():

    with open("users.json", "r") as file:

        return json.load(file)


def run_bot():

    os.system("python ../bot.py")


bot_thread = threading.Thread(target=run_bot)

bot_thread.daemon = True

bot_thread.start()


@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        password = request.form["password"]

        if password == "9287870k":

            session["admin"] = True

            return redirect("/")

    return """

    <h2>🔐 Admin Login</h2>

    <form method="POST">

    <input
    type="password"
    name="password"
    placeholder="Parol">

    <button type="submit">
    Kirish
    </button>

    </form>

    """


@app.route("/", methods=["GET", "POST"])

def home():

    if not session.get("admin"):

        return redirect("/login")

    users = load_users()

    top_users = []

    for user_id, data in users.items():

        total = data.get("autocad", 0) + data.get("photoshop", 0)

        top_users.append((user_id, total))

    top_users = sorted(
        top_users,
        key=lambda x: x[1],
        reverse=True
    )
    total_users = len(users)

    total_autocad = sum(
        user.get("autocad", 0)
        for user in users.values()
    )

    total_photoshop = sum(
        user.get("photoshop", 0)
        for user in users.values()
    )

    result = ""

    sent = 0

    if request.method == "POST":

        text = request.form["message"]

        for user_id in users:

            try:

                bot.send_message(int(user_id), text)

                sent += 1

            except:
                pass

        result = f"✅ {sent} ta userga yuborildi"

    top_html = ""

    for user_id, total in top_users[:10]:

        top_html += f"<li>{user_id} — {total} ta referral</li>"


    users_html = ""

    for user_id, data in users.items():

        total = data.get("autocad", 0) + data.get("photoshop", 0)

        users_html += f"""

    <tr>

    <td>{user_id}</td>

    <td>{data.get("autocad", 0)}</td>

    <td>{data.get("photoshop", 0)}</td>

    <td>{total}</td>

    </tr>

    """
    return f"""

    <h1>🔥 MASTER DARS ADMIN PANEL</h1>

    <h2>👥 Userlar: {total_users}</h2>

    <h3>📘 AutoCAD referral: {total_autocad}</h3>

    <h3>🎨 Photoshop referral: {total_photoshop}</h3>

    <hr>

    <h2>📢 Broadcast</h2>

    <form method="POST">

    <textarea
    name="message"
    rows="5"
    cols="40"
    placeholder="Xabar yozing"></textarea>

    <br><br>

    <button type="submit">
    Yuborish
    </button>

    </form>

    <p>{result}</p>

    <hr>

    <h2>🏆 TOP Referral</h2>

    <p>TOP referral list</p>

    <hr>

    <h2>👥 User List</h2>

    <table border="1" cellpadding="10">

    <tr>

    <th>User ID</th>

    <th>AutoCAD</th>

    <th>Photoshop</th>

    <th>Total</th>

    </tr>

    {top_html}

    {users_html}

    </table>

    """


app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000))
)

