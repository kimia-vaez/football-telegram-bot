# ⚽ Football News Bot

A multilingual Telegram bot that delivers football data: standings, recent results, upcoming fixtures and top scorers for Europe's biggest competitions. Available in **Persian, German and English**.

## Features

- 🌍 **3 languages:** Persian (فارسی), German (Deutsch), English, chosen per user via inline buttons
- 🏆 **7 competitions:** Bundesliga, Premier League, La Liga, Serie A, Ligue 1, Champions League, World Cup
- 📊 **4 views per league:** standings, last 10 results, next 10 fixtures, top 10 scorers
- ⚡ **Non-blocking API calls:** requests run in a worker thread, so the bot stays responsive for other users
- 🛡️ **Error handling:** timeouts, rate-limit detection (HTTP 429) and user-friendly error messages in the selected language

## Tech Stack

- **Python 3.10**
- [python-telegram-bot](https://python-telegram-bot.org/) (v20+, async)
- [football-data.org API v4](https://www.football-data.org/)
- `requests`, `asyncio`, `python-dotenv`

## How It Works

1. `/start` shows a language picker (inline keyboard).
2. After choosing a language, the user picks a league, then an action (standings, results, fixtures, scorers).
3. The bot fetches the data from football-data.org and edits the same message in place, so the chat stays clean.
4. User preferences (language, selected league) are kept in memory per user ID.

## Getting Started

### 1. Prerequisites

- Python 3.10 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A free API token from [football-data.org](https://www.football-data.org/client/register)

### 2. Install

```bash
git clone https://github.com/kimia-vaez/football-telegram-bot.git
cd football-telegram-bot
pip install python-telegram-bot requests python-dotenv
```

### 3. Configure

Create a file named `.env` in the project folder:

```
BOT_TOKEN=your_telegram_bot_token
FOOTBALL_TOKEN=your_football_data_api_token
```

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore`.

### 4. Run

```bash
python main.py
```

Then open your bot in Telegram and send `/start`.

## Project Structure

```
.
├── main.py            # Bot logic: handlers, API calls, translations
├── requirements.txt   # Python dependencies
├── .gitignore         # Keeps secrets (.env) out of Git
└── README.md
```

## Notes & Limitations

- The free football-data.org plan allows **10 requests per minute**. The bot shows a friendly message when this limit is hit.
- The bot runs locally (long polling), so it is online only while the script is running.
- User settings are stored in memory and reset when the bot restarts.

## Roadmap

- [ ] Persistent storage for user settings (SQLite)
- [ ] Caching API responses to reduce rate-limit hits
- [ ] Live match scores
- [ ] Deployment on a cloud host for 24/7 availability

## Author

Kimia Vaez · [GitHub](https://github.com/kimia-vaez)