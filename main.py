import os, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from google import genai
logging.basicConfig(level=logging.INFO)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
LEAGUES = [("🇮🇹 Serie A", "serie_a"), ("🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "premier_league"), ("🇪🇸 La Liga", "la_liga"), ("🇩🇪 Bundesliga", "bundesliga"), ("🇫🇷 Ligue 1", "ligue_1"), ("🇪🇺 Champions League", "champions_league")]
async def start(u, c):
    kb = [[InlineKeyboardButton(n, callback_data=cd)] for n, cd in LEAGUES]
    await u.message.reply_text("⚽ **Bot Pronostici attivo!** Scegli una lega o scrivi una partita:", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
async def cb(u, c):
    q = u.callback_query; await q.answer()
    r = client.models.generate_content(model='gemini-2.5-flash', contents=f"Analisi pronostici, corner, cartellini, over/under, BTTS e combo 1X2 per {q.data}")
    await q.message.reply_text(r.text[:4000])
async def msg(u, c):
    r = client.models.generate_content(model='gemini-2.5-flash', contents=f"Pronostici 1X2, Over/Under, BTTS, corner e cartellini per: {u.message.text}")
    await u.message.reply_text(r.text)
def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(cb))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), msg))
    app.run_polling()
if __name__ == '__main__': main()
