import threading
import os
import json
import sys
from flask import Flask, request, session, redirect
import telebot

TOKEN = "8961895801:AAGBJhkydB3ZtnkMjFQwJ7rak60mXeEUPg4"

bot = telebot.TeleBot(TOKEN)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


app = Flask(__name__)

app.secret_key = "masterdarssecret"


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_users():

    with open(os.path.join(BASE_DIR, "users.json"), "r") as file:

        return json.load(file)


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

    print("USERS:", users)
    print("COUNT:", len(users))

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

        photo = request.files.get("photo")

        photo_data = None

        if photo and photo.filename != "":

            photo_data = photo.read()

        for user_id in users:

            try:

                if photo_data:

                    bot.send_photo(
                        int(user_id),
                        photo_data,
                        caption=text
                    )

                else:

                    bot.send_message(
                        int(user_id),
                        text
                    )

                sent += 1

            except Exception as e:

                print(e)

        result = f"✅ {sent} ta userga yuborildi"


    top_html = ""

    medals = ["🥇", "🥈", "🥉"]

    for i, (user_id, total) in enumerate(top_users[:10]):

        try:

            user = bot.get_chat(int(user_id))

            name = user.first_name

        except:

            name = f"User {user_id}"

        if i < 3:

            medal = medals[i]

        else:

            medal = f"{i+1}."

        top_html += f"""
        <tr>
            <td>{medal}</td>
            <td>{name}</td>
            <td>{total}</td>
        </tr>
        """


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
    <html>

    <head>

    <title>MASTER DARS ADMIN</title>

    <style>

    body {{
        background:#111827;
        color:white;
        font-family:Arial;
        padding:20px;
    }}

    .card {{
        background:#1f2937;
        padding:20px;
        border-radius:15px;
        margin-bottom:20px;
    }}

    h1,h2,h3 {{
        margin:10px 0;
    }}

    textarea,input[type=file] {{
        width:100%;
        padding:12px;
        border-radius:10px;
        border:none;
        margin-top:10px;
    }}

    button {{
        background:#10b981;
        color:white;
        border:none;
        padding:12px 20px;
        border-radius:10px;
        font-size:16px;
        cursor:pointer;
    }}

    table {{
        width:100%;
        border-collapse:collapse;
        background:#1f2937;
        border-radius:10px;
        overflow:hidden;
    }}

    th {{
        background:#10b981;
        color:white;
        padding:12px;
    }}

    td {{
        padding:10px;
        border-bottom:1px solid #374151;
        text-align:center;
    }}

    </style>

    </head>

    <body>

    <h1>🔥 MASTER DARS ADMIN PANEL</h1>

    <div class="card">
    <h2>👥 Userlar: {total_users}</h2>
    <h3>📘 AutoCAD: {total_autocad}</h3>
    <h3>🎨 Photoshop: {total_photoshop}</h3>
    </div>

    <div class="card">
    <h2>📢 Broadcast</h2>

    <form method="POST" enctype="multipart/form-data">

    <textarea
    name="message"
    rows="5"
    placeholder="Xabar yozing"></textarea>

    <br><br>

    <input type="file" name="photo">

    <br><br>

    <button type="submit">
    📤 Yuborish
    </button>

    </form>

    <p>{result}</p>
    </div>

    <div class="card">
    <h2>🏆 TOP Referral</h2>

    <table>
    <tr>
    <th>O‘rin</th>
    <th>Ism</th>
    <th>Referral</th>
    </tr>

    {top_html}

    </table>
    </div>

    <div class="card">
    <h2>👥 User List</h2>

    <table>

    <tr>
    <th>User ID</th>
    <th>AutoCAD</th>
    <th>Photoshop</th>
    <th>Total</th>
    </tr>

    {users_html}

    </table>
    </div>

    </body>
    </html>
    """


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
