import os
import requests
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

# === ENV-VARIABLEN LADEN ===
load_dotenv()

# === KONFIGURATION ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
CITY = os.environ.get("CITY", "Berlin")

# === OpenAI-Client ===
client = OpenAI(api_key=OPENAI_API_KEY)

# === WITZ DES TAGES ===
def get_joke():
    url = "https://v2.jokeapi.dev/joke/Any?lang=de&type=single"
    r = requests.get(url)
    if r.ok:
        data = r.json()
        return data.get("joke", "Heute kein Witz 🤷‍♂️")
    return "Witz konnte nicht geladen werden."

# === WETTERABFRAGE ===
def get_weather():
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={CITY}&lang=de"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            condition = data["current"]["condition"]["text"]
            temp_c = data["current"]["temp_c"]
            wind_kph = data["current"]["wind_kph"]
            humidity = data["current"]["humidity"]
            return f"Wetter in {CITY}: {condition}, {temp_c}°C, Wind {wind_kph} km/h, Luftfeuchtigkeit {humidity}%"
        else:
            return f"⚠️ Fehler beim Abrufen des Wetters: HTTP {response.status_code}"
    except Exception as e:
        return f"⚠️ Ausnahmefehler beim Wetterabruf: {e}"

# === ZITAT DES TAGES ===
def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/today")
        if r.ok:
            data = r.json()[0]
            return f"„{data['q']}“ — *{data['a']}*"
    except:
        return "Zitat konnte nicht geladen werden."
    return "Zitat konnte nicht geladen werden."

# === TEXT VON WEBSEITE EXTRAHIEREN ===
def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        text = ' '.join(p.get_text(strip=True) for p in soup.find_all("p"))
        return text[:3000]
    except Exception:
        return ""

# === ZUSAMMENFASSUNG MIT CHATGPT ===
def summarize_with_chatgpt(all_texts):
    prompt = """Du bist ein News-Analyst. Fasse die folgenden Inhalte in den fünf ungewöhnlichen, aber relevanten, inhaltlich unterschiedlichen Nachrichten zusammen.

Bedingungen:
-Es darf höchstens eine Nachricht pro Website vorkommen.
-Es sollen keine thematisch doppelten oder stark ähnlichen Nachrichten aufgenommen werden (z. B. unterschiedliche Artikel zur selben Zollentscheidung vermeiden).
-Bevorzuge Themen aus den Bereichen Business Intelligence, Künstliche Intelligenz, Daten, Technologie und Wirtschaft, wenn sie relevant sind.

Format pro Nachricht:
-<fett>Titel sehr kurz, prägnant und informativ
-genau zwei Sätze mit den wichtigsten Informationen
-die vollständige URL zum Artikel in der Originalquelle

Der Empfänger ist Teamleiter eines BI- und Daten-Teams, hat wenig Zeit und schätzt News, die ihm interessante Gespräche ermöglichen – auch außerhalb seines direkten Fachgebiets.
    
"""
    prompt += all_texts

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler bei der Zusammenfassung: {e}"

# === TEXT VON CSV-WEBSITES LADEN UND ZUSAMMENFASSEN===
def summarize_websites_from_csv():
    try:
        df = pd.read_csv("sites.csv")
        all_chunks = ""
        for i, row in df.iterrows():
            text = extract_text_from_url(row["url"])
            if text:
                all_chunks += f"Quelle: {row['url']}\n{text}\n\n"
        return summarize_with_chatgpt(all_chunks)
    except Exception as e:
        return f"Fehler beim Lesen der Webseiten: {e}"

# === ZUSAMMENFASSUNG MIT CHATGPT  für BI NEWS ===
def summarize_with_chatgpt_bi(all_texts):
    prompt = """Du bist ein Business-Intelligence-Analyst. Fasse die folgenden Inhalte in den fünf wichtigsten, inhaltlich unterschiedlichen Nachrichten zusammen.

Bedingungen:
-Es darf höchstens eine Nachricht pro Website vorkommen.
-Es sollen keine thematisch doppelten oder stark ähnlichen Nachrichten aufgenommen werden (z. B. unterschiedliche Artikel zur selben Zollentscheidung vermeiden).
-Bevorzuge Themen aus den Bereichen Business Intelligence, Künstliche Intelligenz, Daten, Technologie und Wirtschaft, wenn sie relevant sind.
-Nachrichten auf deutsch, auch wenn es die Quelle nicht ist!

Format pro Nachricht:
-Titel sehr kurz, prägnant und informativ
-genau zwei Sätze mit den wichtigsten Informationen
-die vollständige URL zur Originalquelle

Der Empfänger ist Teamleiter eines BI- und Daten-Teams, hat wenig Zeit und schätzt News, die ihm interessante Gespräche ermöglichen.
    
"""
    prompt += all_texts

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Fehler bei der Zusammenfassung: {e}"

# === TEXT VON CSV-WEBSITES LADEN UND ZUSAMMENFASSEN  für BI NEWS ===
def summarize_websites_from_csv_bi():
    try:
        df = pd.read_csv("sites_bi.csv")
        all_chunks = ""
        for i, row in df.iterrows():
            text = extract_text_from_url(row["url"])
            if text:
                all_chunks += f"Quelle: {row['url']}\n{text}\n\n"
        return summarize_with_chatgpt_bi(all_chunks)
    except Exception as e:
        return f"Fehler beim Lesen der Webseiten: {e}"



# === TELEGRAM-NACHRICHT SENDEN ===
def send_telegram_message(text):
    # Unicode-Sonderzeichen für Telegram bereinigen
    text = (
        text.replace("“", '"').replace("”", '"')
            .replace("‘", "'").replace("’", "'")
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    headers = {"Content-Type": "application/json; charset=utf-8"}
    try:
        r = requests.post(url, json=payload, headers=headers)
        return r.ok
    except Exception as e:
        print("Fehler beim Telegram-Versand:", e)
        return False

# === HAUPTFUNKTION ===
def main():
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    weather = get_weather()
    joke = get_joke()
    quote = get_quote()
    news = summarize_websites_from_csv()
    news_bi = summarize_websites_from_csv_bi()
    
    msg = (
        "📅 *Guten Morgen!*\n\n"
        f"🗓 *{today}*\n\n"
        f"☀️ {weather}\n\n"
        f"😂 *Witz des Tages:*\n{joke}\n\n"
        f"💬 *Zitat des Tages:*\n{quote}\n\n"
        f"📰 *Nachrichtenzusammenfassung:*\n{news}\n\n"
        f"📰 *BI News:*\n{news_bi}"
    )

    success = send_telegram_message(msg)
    print("Nachricht gesendet:", success)

if __name__ == "__main__":
    main()
