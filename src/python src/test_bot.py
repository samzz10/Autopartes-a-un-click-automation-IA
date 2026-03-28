from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update

TELEGRAM_TOKEN = "8619419567:AAHS07uaZSrCOhVGjECF3azU1U1XLnaFyV8"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! El bot funciona!")

app = Application.builder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
print("Bot corriendo...")
app.run_polling()