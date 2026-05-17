from flask import Flask
import json

app = Flask(__name__)

def load_users():

    try:

        with open("users.json", "r") as file:

            return json.load(file)

    except:

        return {}

@app.route("/")
def home():

    users = load_users()

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

app.run(host="0.0.0.0", port=5000)
