
# 📰 Guten-Morgen-Bot für Telegram

Dieser Bot sendet dir jeden Morgen um 8 Uhr:

- Wetterbericht für eine Stadt
- Witz des Tages
- Zitat des Tages
- Top-3-Nachrichten aus Deutschland

## 🔧 Einrichtung

1. [Replit.com](https://replit.com) Account erstellen
2. Dieses Repository importieren
3. Gehe zu "Secrets" (🔒-Symbol) und trage folgende Variablen ein:
   - `BOT_TOKEN`
   - `CHAT_ID`
   - `WEATHER_API_KEY`
   - `NEWS_API_KEY`
4. Stadt ändern (in `main.py`, Variable `CITY`)
5. Optional: Replit "Always-on" aktivieren oder extern über [cron-job.org](https://cron-job.org) täglich triggern

## 📬 Ergebnis

Nachricht per Telegram, z. B.:

```
📅 Guten Morgen!

🗓 29.05.2025

☀️ Wetter in Berlin: klarer Himmel, 17°C

📰 Top-Nachrichten:
• [Bundestag beschließt neues Gesetz](#)
• [DAX erreicht neuen Höchststand](#)
• [Streik im Bahnverkehr angekündigt](#)

😂 Witz des Tages:
Warum können Geister so schlecht lügen? Weil man durch sie hindurchsieht!

💬 Zitat des Tages:
„Stay hungry, stay foolish.“ — Steve Jobs
```
