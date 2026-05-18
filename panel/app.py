ghp_XrxpHveSo5CWN6j6H2mtCzRLUxnf1C1NkfTfrom flask import Flask, request, session, redirect
import telebot
import threading
import os
from flask import Flask, request, session, redirect
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

    if not session.get("admin"):

        return redirect("/login")

    users = load_users()

    result = ""

    sent = 0

    top_users = []

    for user_id, data in users.items():

        total = data.get("autocad", 0) + data.get("photoshop", 0)

        top_users.append((user_id, total))

    top_users = sorted(
        top_users,
        key=lambda x: x[1],
        reverse=True
    )

    result = ""
    sent = 0

    if request.method == "POST":

        text = request.form["message"]

        sent = 0

        for user_id in users:

            try:

                bot.send_message(int(user_id), text)

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
    <hr>

<h2>🏆 TOP Referral</h2>

<hr>

<h2>👥 User List</h2>

<table border="1" cellpadding="10">

<tr>

<th>User ID</th>

<th>AutoCAD</th>

<th>Photoshop</th>

<th>Total</th>

</tr>

{
''.join(

f"""

<tr>

<td>{user_id}</td>

<td>{data.get('autocad', 0)}</td>

<td>{data.get('photoshop', 0)}</td>

<td>{data.get('autocad', 0) + data.get('photoshop', 0)}</td>

</tr>

"""

for user_id, data in users.items()

)
}

</table>

<ol>

{
''.join(
    f"<li>{user_id} — {total} ta referral</li>"
    for user_id, total in top_users[:10]
)
}

</ol>
    <h1>🔥 MASTER DARS ADMIN PANEL</h1>

    <h2>👥 Userlar: {total_users}</h2>

    <h3>📘 AutoCAD referral: {total_autocad}</h3>

    <h3>🎨 Photoshop referral: {total_photoshop}</h3>
    
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
"""
import os
def run_bot():

    os.system("python bot.py")

bot_thread = threading.Thread(target=run_bot)

bot_thread.daemon = True

bot_thread.start()

app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000))
)
