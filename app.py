import os
import sqlite3
from urllib.parse import quote

import requests
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
DATABASE = os.path.join(os.path.dirname(__file__), "weather.db")

CAPITALS = [
    "Budapest",
    "Bécs",
    "Berlin",
    "Brüsszel",
    "Bukarest",
    "London",
    "Madrid",
    "Párizs",
    "Prága",
    "Róma",
    "Stockholm",
    "Varsó",
]


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def get_temperature(city):
    url = f"https://wttr.in/{quote(city)}?format=j1"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()["current_condition"][0]["temp_C"]


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_confirmation = request.form.get("password_confirmation", "")

        if len(username) < 3:
            flash("A felhasználónév legalább 3 karakter legyen.", "error")
        elif len(password) < 8:
            flash("A jelszó legalább 8 karakter legyen.", "error")
        elif password != password_confirmation:
            flash("A két jelszó nem egyezik.", "error")
        else:
            try:
                with get_db() as connection:
                    connection.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, generate_password_hash(password)),
                    )
                flash("A regisztráció sikeres. Most már bejelentkezhetsz.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Ez a felhasználónév már foglalt.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as connection:
            user = connection.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Hibás felhasználónév vagy jelszó.", "error")
        else:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/")
def index():
    city = request.args.get("city", CAPITALS[0])
    if city not in CAPITALS:
        city = CAPITALS[0]

    temperature = None
    error = None
    try:
        temperature = get_temperature(city)
    except (requests.RequestException, KeyError, IndexError, ValueError):
        error = "Az időjárási adatok most nem érhetők el. Próbáld újra később."

    return render_template(
        "index.html",
        capitals=CAPITALS,
        city=city,
        temperature=temperature,
        error=error,
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


init_db()