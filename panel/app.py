import threading
import os
import json
import sys
from flask import Flask, request, session, redirect
import telebot
import time

TOKEN = "8961895801:AAHuSm3LrLVUlfWwCRHoPw8q3TxY4XWSAwg"

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

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect("/login")
@app.route("/", methods=["GET", "POST"])

def home():

    if not session.get("admin"):

        return redirect("/login")

    users = load_users()

    print("USERS:", users)
    print("COUNT:", len(users))

    top_users = []

    for user_id, data in users.items():

        total = sum(
            data.get("referrals", {}).values()
        )

        top_users.append((user_id, total))

    top_users = sorted(
        top_users,
        key=lambda x: x[1],
        reverse=True
    )

    total_users = len(users)

    total_referrals = sum(
        sum(user.get("referrals", {}).values())
        for user in users.values()
    )

    result = ""
    reset_user = None

    if request.method == "POST":

        sent = 0

        text = request.form.get("message", "")
        delay = int(request.form.get("delay", 0))
        reset_user = request.form.get("reset_user")
        delete_user = request.form.get("delete_user")
        grant_user = request.form.get("grant_user")
        grant_course = request.form.get("grant_course")
        search_user = request.form.get("search_user")

    # RESET
        if reset_user:

            if reset_user in users:

                users[reset_user]["autocad"] = 0
                users[reset_user]["photoshop"] = 0

                with open(
                    os.path.join(BASE_DIR, "users.json"),
                    "w"
                ) as f:

                    json.dump(users, f)

                result = f"✅ {reset_user} referrallari reset qilindi"

            else:

                result = "❌ User topilmadi"

        # DELETE USER
        elif delete_user:

            if delete_user in users:

                del users[delete_user]

                with open(
                    os.path.join(BASE_DIR, "users.json"),
                    "w"
                ) as f:

                    json.dump(users, f)

                result = f"🗑 {delete_user} o‘chirildi"

            else:

                result = "❌ User topilmadi"
    # GRANT COURSE
        elif grant_user:

            if grant_user in users:

                if grant_course == "autocad":

                    users[grant_user]["autocad"] = 10

                elif grant_course == "photoshop":

                    users[grant_user]["photoshop"] = 10

                with open(
                    os.path.join(BASE_DIR, "users.json"),
                    "w"
                ) as f:

                    json.dump(users, f)

                result = f"🎓 {grant_user} uchun {grant_course} kursi ochili"
            else:

                result = "❌ User topilmadi"

    # SEARCH USER
        elif search_user:

            if search_user in users:

                data = users[search_user]

                total = (
                    data.get("autocad", 0)
                    + data.get("photoshop", 0)
                )

                result = f"""
🔍 User: {search_user}

📘 AutoCAD: {data.get("autocad", 0)}
🎨 Photoshop: {data.get("photoshop", 0)}
🏆 Total: {total}
🎁 Offer sent: {data.get("offer_sent", False)}
⏰ Time: {data.get("time", 0)}
"""


            else:

                result = "❌ User topilmadi"
        else:

            photo = request.files.get("photo")

            photo_data = None

            if photo and photo.filename != "":

                photo_data = photo.read()

            def send_broadcast():

                nonlocal sent

                if delay > 0:

                    time.sleep(delay * 60)

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

                print(f"Broadcast sent: {sent}")

                history_path = os.path.join(
                    BASE_DIR,
                    "history.json"
                )

                with open(history_path, "r") as f:

                    history = json.load(f)

                history.append({

                    "time": time.time(),
                    "sent": sent,
                    "text": text,
                    "photo": bool(photo_data)

                })

                with open(history_path, "w") as f:

                    json.dump(history, f)

            threading.Thread(
                target=send_broadcast
            ).start()

            result = "✅ Xabar yuborish boshlandi"

    history_html = ""

    history_path = os.path.join(
        BASE_DIR,
        "history.json"
    )

    with open(history_path, "r") as f:

        history = json.load(f)

    for item in reversed(history[-10:]):

        history_html += f"""
<tr>
<td>{time.strftime('%d-%m-%Y %H:%M', time.localtime(item["time"]))}</td>
<td>{item["text"]}</td>
<td>{item["sent"]}</td>
<td>{item["photo"]}</td>
</tr>
"""

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

        total = sum(
            data.get("referrals", {}).values()
        )

        opened = len(
            data.get("opened_courses", [])
        )

        try:

            user = bot.get_chat(int(user_id))

            name = user.first_name

        except:

            name = "Noma'lum"

        users_html += f"""

<tr>

<td>{user_id}</td>

<td>{name}</td>

<td>{total}</td>

<td>{opened}</td>

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
    <a href="/logout">
<button>
🚪 Logout
</button>
</a>

<br><br>

    <div class="card">
    <h2>👥 Userlar: {total_users}</h2>
    <h3>🏆 Jami referral: {total_referrals}</h3>
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

    <input
    type="number"
    name="delay"
    placeholder="Necha daqiqadan keyin yuborilsin (0 = hozir)">

    <br><br>

    <button type="submit">
    📤 Yuborish
    </button>

    </form>

    <p>{result}</p>

    <hr>

<h2>🧹 Referral Reset</h2>

<form method="POST">

<input
type="text"
name="reset_user"
placeholder="User ID">

<br><br>

<button type="submit">
Reset Referral
</button>

</form>

<hr>

<h2>🗑 Delete User</h2>

<form method="POST">

<input
type="text"
name="delete_user"
placeholder="User ID">

<br><br>

<button type="submit">
Delete User
</button>

</form>
<hr>

<h2>🎓 Grant Course</h2>

<form method="POST">

<input
type="text"
name="grant_user"
placeholder="User ID">

<br><br>

<select name="grant_course">

<option value="autocad">
AutoCAD
</option>

<option value="photoshop">
Photoshop
</option>

</select>

<br><br>

<button type="submit">
Open Course
</button>

</form>

<hr>

<h2>🔍 Search User</h2>

<form method="POST">

<input
type="text"
name="search_user"
placeholder="User ID">

<br><br>

<button type="submit">
Search
</button>

</form>

<p>{result}</p>
<hr>

<h2>📜 Broadcast History</h2>

<table border="1" cellpadding="10">

<tr>
<th>Vaqt</th>
<th>Xabar</th>
<th>Sent</th>
<th>Photo</th>
</tr>

{history_html}

</table>
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
<th>Ism</th>
<th>Total Referral</th>
<th>Opened Courses</th>
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
