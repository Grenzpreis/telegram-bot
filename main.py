
import requests
import datetime
import os

# === KONFIGURATION ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
NEWS_API_KEY = os.environ["NEWS_API_KEY"]
CITY = "Berlin"
LANG = "de"

def get_joke():
    url = "https://v2.jokeapi.dev/joke/Any?lang=de&type=single"
    r = requests.get(url)
    if r.ok:
        data = r.json()
        return data.get("joke", "Heute kein Witz 🤷‍♂️")
    return "Witz konnte nicht geladen werden."

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric&lang={LANG}"
    r = requests.get(url)
    if r.ok:
        data = r.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"Wetter in {CITY}: {desc}, {temp}°C"
    return "Wetter konnte nicht geladen werden."

def get_quote():
    url = "https://api.quotable.io/random"
    r = requests.get(url)
    if r.ok:
        data = r.json()
        return f"„{data.get('content')}“ — *{data.get('author')}*"
    return "Zitat konnte nicht geladen werden."

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=de&apiKey={NEWS_API_KEY}&pageSize=3"
    r = requests.get(url)
    if r.ok:
        articles = r.json().get("articles", [])
        if articles:
            return "\n".join([f"• [{a['title']}]({a['url']})" for a in articles])
    return "Keine aktuellen Schlagzeilen gefunden."

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    r = requests.post(url, data=payload)
    return r.ok

def main():
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    weather = get_weather()
    joke = get_joke()
    quote = get_quote()
    news = get_news()

    msg = (
        f"📅 *Guten Morgen!*\n\n🗓 *{today}*\n\n"
        f"☀️ {weather}\n\n"
        f"📰 *Top-Nachrichten:*\n{news}\n\n"
        f"😂 *Witz des Tages:*\n{joke}\n\n"
        f"💬 *Zitat des Tages:*\n{quote}"
    )

    success = send_telegram_message(msg)
    print("Nachricht gesendet:", success)

if __name__ == "__main__":
    main()
