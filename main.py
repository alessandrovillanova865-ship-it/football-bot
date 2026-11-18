import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from google import genai

# Configurazione dei log
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Recupero chiavi dalle variabili d'ambiente di Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Inizializzazione del client Gemini
ai_client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

# Funzione per il comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇮🇹 Serie A", callback_data="league_serie_a")],
        [InlineKeyboardButton("🇬🇧 Premier League", callback_data="league_premier")],
        [InlineKeyboardButton("🇪🇸 La Liga", callback_data="league_laliga")],
        [InlineKeyboardButton("🇩🇪 Bundesliga", callback_data="league_bundesliga")],
        [InlineKeyboardButton("🇫🇷 Ligue 1", callback_data="league_ligue1")],
        [InlineKeyboardButton("🇪🇺 Champions League", callback_data="league_ucl")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚽ **Bot Pronostici attivo!** Scegli una lega per generare statistiche e pronostici (corner, cartellini, over/under, BTTS, multigol, 1X2):",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Gestore dei click sui pulsanti delle leghe
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    league_name = query.data.replace("league_", "").replace("_", " ").upper()
    
    await query.edit_message_text(text=f"🔄 Analisi in corso per la {league_name} con Gemini AI...")

    if not ai_client:
        await query.edit_message_text(text="⚠️ Errore: Chiave Gemini non configurata correttamente su Railway.")
        return

    try:
        # Prompt ottimizzato per generare le statistiche richieste
        prompt = (
            f"Fornisci un'analisi approfondita e un pronostico dettagliato per le prossime partite di {league_name}. "
            "Includi stime per: corner medi, cartellini, esito 1X2, Over/Under 2.5, Goal/No Goal (BTTS) e Multigol. "
            "Usa una formattazione chiara, pulita e pronta per Telegram."
        )

        # Chiamata al modello Gemini aggiornato
        response = ai_client.models.generate_content(
            model='gemini-3.8-flash',
            contents=prompt,
        )
        
        prediction_text = response.text

        # Pulsante per tornare al menu principale
        keyboard = [[InlineKeyboardButton("🔙 Torna al Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Tronca il testo se troppo lungo per i limiti di Telegram
        if len(prediction_text) > 4000:
            prediction_text = prediction_text[:4000] + "\n\n*(Testo troncato per limiti di lunghezza)*"

        await query.edit_message_text(
            text=f"📊 **Pronostici {league_name}**\n\n{prediction_text}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Errore durante la generazione con Gemini: {e}")
        keyboard = [[InlineKeyboardButton("🔙 Torna al Menu", callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="⚠️ **Non è stato possibile completare l'analisi.** Riprova tra poco.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# Gestore per tornare al menu iniziale dai pulsanti interni
async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🇮🇹 Serie A", callback_data="league_serie_a")],
        [InlineKeyboardButton("🇬🇧 Premier League", callback_data="league_premier")],
        [InlineKeyboardButton("🇪🇸 La Liga", callback_data="league_laliga")],
        [InlineKeyboardButton("🇩🇪 Bundesliga", callback_data="league_bundesliga")],
        [InlineKeyboardButton("🇫🇷 Ligue 1", callback_data="league_ligue1")],
        [InlineKeyboardButton("🇪🇺 Champions League", callback_data="league_ucl")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="⚽ **Menu Principale** Scegli una lega:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN non trovato nelle variabili d'ambiente!")
        return

    # Costruzione dell'applicazione del bot
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Registrazione dei gestori
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_to_menu$"))
    application.add_handler(CallbackQueryHandler(button_handler, pattern="^league_"))

    logger.info("Bot avviato con successo e in ascolto...")
    application.run_polling()

if __name__ == "__main__":
    main()
