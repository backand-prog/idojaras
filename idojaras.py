import requests

capitals = {
	"1": "Budapest",
	"2": "Bécs",
	"3": "Berlin",
	"4": "Brüsszel",
	"5": "Bukarest",
	"6": "London",
	"7": "Madrid",
	"8": "Párizs",
	"9": "Prága",
	"10": "Róma",
	"11": "Stockholm",
	"12": "Varsó",
}

print("Válassz egy európai fővárost:")
for number, capital in capitals.items():
	print(f"{number}. {capital}")

choice = input("A választott város sorszáma: ").strip()
if choice not in capitals:
	raise ValueError("Érvénytelen választás.")

city = capitals[choice]
url = f"https://wttr.in/{city}?format=j1"
response = requests.get(url, timeout=10)
response.raise_for_status()

weather = response.json()
temperature = weather["current_condition"][0]["temp_C"]

print(f"Jelenlegi hőmérséklet {city} városában: {temperature}°C")