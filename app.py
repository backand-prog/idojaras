from urllib.parse import quote

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

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


def get_temperature(city):
    url = f"https://wttr.in/{quote(city)}?format=j1"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()["current_condition"][0]["temp_C"]


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
    app.run(debug=True)