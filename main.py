import os
from dotenv import load_dotenv
load_dotenv()
import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("football-bot")

BOT_TOKEN = os.environ.get("BOT_TOKEN")
FOOTBALL_TOKEN = os.environ.get("FOOTBALL_TOKEN")

if not BOT_TOKEN or not FOOTBALL_TOKEN:
    raise SystemExit("BOT_TOKEN یا FOOTBALL_TOKEN ست نشده!")

HEADERS = {"X-Auth-Token": FOOTBALL_TOKEN}
BASE = "https://api.football-data.org/v4/competitions"

LEAGUES = {
    "bl1": {"fa": "🇩🇪 بوندسلیگا", "de": "🇩🇪 Bundesliga", "en": "🇩🇪 Bundesliga"},
    "pl":  {"fa": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 پرمیر لیگ", "de": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "en": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League"},
    "pd":  {"fa": "🇪🇸 لالیگا", "de": "🇪🇸 La Liga", "en": "🇪🇸 La Liga"},
    "sa":  {"fa": "🇮🇹 سری آ", "de": "🇮🇹 Serie A", "en": "🇮🇹 Serie A"},
    "fl1": {"fa": "🇫🇷 لیگ ۱", "de": "🇫🇷 Ligue 1", "en": "🇫🇷 Ligue 1"},
    "cl":  {"fa": "🏆 لیگ قهرمانان", "de": "🏆 Champions League", "en": "🏆 Champions League"},
    "wc":  {"fa": "🌍 جام جهانی", "de": "🌍 WM 2026", "en": "🌍 World Cup"},
}

TEXTS = {
    "fa": {
        "welcome": "سلام! 👋 به ربات فوتبال خوش اومدی! ⚽",
        "choose_league": "لیگ مورد نظرت رو انتخاب کن:",
        "choose_action": "چی میخوای ببینی؟",
        "standings": "🏆 جدول",
        "results": "📋 نتایج",
        "next": "📅 بازی‌های آینده",
        "scorers": "⚽ گلزنان",
        "back": "🔙 بازگشت",
        "no_next": "فعلاً بازی برنامه‌ریزی شده‌ای نیست!",
        "pts": "امتیاز",
        "goals": "گل",
        "error": "❌ خطا در دریافت اطلاعات — کمی بعد دوباره امتحان کن!",
        "rate": "⏳ محدودیت تعداد درخواست — یک دقیقه صبر کن و دوباره بزن.",
    },
    "de": {
        "welcome": "Hallo! 👋 Willkommen beim Fußball-Bot! ⚽",
        "choose_league": "Wähle eine Liga:",
        "choose_action": "Was möchtest du sehen?",
        "standings": "🏆 Tabelle",
        "results": "📋 Ergebnisse",
        "next": "📅 Kommende Spiele",
        "scorers": "⚽ Torjäger",
        "back": "🔙 Zurück",
        "no_next": "Keine kommenden Spiele!",
        "pts": "Pkt",
        "goals": "Tore",
        "error": "❌ Fehler beim Laden — bitte später erneut versuchen!",
        "rate": "⏳ Zu viele Anfragen — bitte eine Minute warten.",
    },
    "en": {
        "welcome": "Hello! 👋 Welcome to the Football Bot! ⚽",
        "choose_league": "Choose a league:",
        "choose_action": "What do you want to see?",
        "standings": "🏆 Standings",
        "results": "📋 Results",
        "next": "📅 Upcoming Matches",
        "scorers": "⚽ Top Scorers",
        "back": "🔙 Back",
        "no_next": "No upcoming matches!",
        "pts": "pts",
        "goals": "goals",
        "error": "❌ Could not load data — please try again later!",
        "rate": "⏳ Rate limit reached — wait a minute and try again.",
    },
}

user_data = {}


def get_user(user_id):
    return user_data.setdefault(user_id, {"lang": "en", "league": "bl1"})


def api_get(path, params=None):
    code, _, rest = path.partition("/")
    r = requests.get(f"{BASE}/{code.upper()}/{rest}", headers=HEADERS, params=params, timeout=15)
    if r.status_code == 429:
        raise RuntimeError("RATE_LIMIT")
    r.raise_for_status()
    return r.json()


async def safe_edit(query, text, keyboard=None):
    try:
        await query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
        )
    except Exception as e:
        log.warning("edit_message_text failed: %s", e)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
        InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    ]]
    await update.message.reply_text(
        "🌍 زبان / Sprache / Language:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def show_leagues(query, lang):
    t = TEXTS[lang]
    L = lambda k: LEAGUES[k][lang]
    keyboard = [
        [InlineKeyboardButton(L("bl1"), callback_data="league_bl1"),
         InlineKeyboardButton(L("pl"), callback_data="league_pl")],
        [InlineKeyboardButton(L("pd"), callback_data="league_pd"),
         InlineKeyboardButton(L("sa"), callback_data="league_sa")],
        [InlineKeyboardButton(L("fl1"), callback_data="league_fl1"),
         InlineKeyboardButton(L("cl"), callback_data="league_cl")],
        [InlineKeyboardButton(L("wc"), callback_data="league_wc")],
    ]
    await safe_edit(query, f"{t['welcome']}\n\n{t['choose_league']}", keyboard)


async def show_menu(query, lang, league):
    t = TEXTS[lang]
    keyboard = [
        [InlineKeyboardButton(t["standings"], callback_data="action_standings"),
         InlineKeyboardButton(t["results"], callback_data="action_results")],
        [InlineKeyboardButton(t["next"], callback_data="action_next"),
         InlineKeyboardButton(t["scorers"], callback_data="action_scorers")],
        [InlineKeyboardButton(t["back"], callback_data="back_leagues")],
    ]
    await safe_edit(query, f"{LEAGUES[league][lang]}\n\n{t['choose_action']}", keyboard)


def build_text(action, league, lang):
    """اجرای درخواست‌ها (blocking) — تو thread جدا صدا زده میشه."""
    t = TEXTS[lang]
    name = LEAGUES[league][lang]

    if action == "standings":
        table = api_get(f"{league}/standings")["standings"][0]["table"]
        text = f"{t['standings']} — {name}:\n\n"
        for row in table:
            text += f"{row['position']}. {row['team']['name']} — {row['points']} {t['pts']}\n"
        return text

    if action == "results":
        matches = api_get(f"{league}/matches", {"status": "FINISHED"})["matches"][-10:]
        text = f"{t['results']} — {name}:\n\n"
        for m in matches:
            ft = m["score"]["fullTime"]
            text += f"{m['homeTeam']['name']} {ft['home']} - {ft['away']} {m['awayTeam']['name']}\n"
        return text

    if action == "next":
        matches = api_get(f"{league}/matches", {"status": "SCHEDULED,TIMED"})["matches"][:10]
        if not matches:
            return f"⚽ {t['no_next']}"
        text = f"{t['next']} — {name}:\n\n"
        for m in matches:
            text += f"{m['utcDate'][:10]}: {m['homeTeam']['name']} vs {m['awayTeam']['name']}\n"
        return text

    if action == "scorers":
        scorers = api_get(f"{league}/scorers")["scorers"][:10]
        text = f"{t['scorers']} — {name}:\n\n"
        for i, s in enumerate(scorers, 1):
            text += f"{i}. {s['player']['name']} ({s['team']['name']}) — {s['goals']} {t['goals']}\n"
        return text

    return t["error"]


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(query.from_user.id)
    data = query.data

    if data.startswith("lang_"):
        user["lang"] = data.split("_")[1]
        await show_leagues(query, user["lang"])

    elif data.startswith("league_"):
        user["league"] = data.split("_")[1]
        await show_menu(query, user["lang"], user["league"])

    elif data == "back_leagues":
        await show_leagues(query, user["lang"])

    elif data == "back_menu":
        await show_menu(query, user["lang"], user["league"])

    elif data.startswith("action_"):
        action = data.split("_")[1]
        lang, league = user["lang"], user["league"]
        t = TEXTS[lang]

        await safe_edit(query, "⏳ ...")
        try:
            text = await asyncio.to_thread(build_text, action, league, lang)
        except RuntimeError as e:
            text = t["rate"] if str(e) == "RATE_LIMIT" else t["error"]
            log.error("API error: %s", e)
        except Exception as e:
            log.exception("API error: %s", e)
            text = t["error"]

        keyboard = [[InlineKeyboardButton(t["back"], callback_data="back_menu")]]
        await safe_edit(query, text, keyboard)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    print("ربات شروع به کار کرد... ⚽")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()