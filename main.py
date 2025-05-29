
import os
import requests
import datetime
import openai
import pandas as pd
from bs4 import BeautifulSoup

# === KONFIGURATION ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
CITY = os.environ.get("CITY", "Berlin")

openai.api_key = OPENAI_API_KEY

def get_joke():
    url = "https://v2.jokeapi.dev/joke/Any?lang=de&type=single"
    r = requests.get(url)
    if r.ok:
        data = r.json()
        return data.get("joke", "Heute kein Witz 🤷‍♂️")
    return "Witz konnte nicht geladen werden."

def get_weather():
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={CITY}&lang=de"
    r = requests.get(url)
    if r.ok:
        data = r.json()
        desc = data["current"]["condition"]["text"]
        temp = data["current"]["temp_c"]
        return f"Wetter in {CITY}: {desc}, {temp}°C"
    return "Wetter konnte nicht geladen werden."

def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/today")
        if r.ok:
            data = r.json()[0]
            return f"„{data['q']}“ — *{data['a']}*"
    except:
        return "Zitat konnte nicht geladen werden."
    return "Zitat konnte nicht geladen werden."

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        text = ' '.join(p.get_text(strip=True) for p in soup.find_all("p"))
        return text[:3000]  # Trimmen, um unter Token-Grenzen zu bleiben
    except Exception as e:
        return ""

def summarize_with_chatgpt(all_texts):
    prompt = (
        "Du bist ein News-Analyst. Fasse die folgenden Inhalte in den drei wichtigsten Nachrichten (je 2-3 Sätze mit Quelle) "
        "und 5 weiteren Schlagzeilen (nur Titel + Link) zusammen. Die Texte stammen von Nachrichten-Websites. 
	Der Empfänger ist Teamleiter eines BI und Daten Teams und sieht sich als Innovationstreiber:

"
    )
    prompt += all_texts

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler bei der Zusammenfassung: {e}"

def summarize_websites_from_csv():
    try:
        df = pd.read_csv("sites.csv")
        all_chunks = ""
        for i, row in df.iterrows():
            text = extract_text_from_url(row["url"])
            if text:
                all_chunks += f"Quelle: {row['url']}
{text}

"
        return summarize_with_chatgpt(all_chunks)
    except Exception as e:
        return f"Fehler beim Lesen der Webseiten: {e}"

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    r = requests.post(url, data=payload)
    return r.ok

def main():
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    weather = get_weather()
    joke = get_joke()
    quote = get_quote()
    news = summarize_websites_from_csv()

    msg = (
        f"📅 *Guten Morgen!*

🗓 *{today}*

"
        f"☀️ {weather}

"
        f"📰 *Nachrichtenzusammenfassung:*
{news}

"
        f"😂 *Witz des Tages:*
{joke}

"
        f"💬 *Zitat des Tages:*
{quote}"
    )

    success = send_telegram_message(msg)
    print("Nachricht gesendet:", success)

if __name__ == "__main__":
    main()
