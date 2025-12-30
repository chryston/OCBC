import os

from calculator import SaveBonusCalculator
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from utils import caffeine

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")

# =========================
# Conversation States
# =========================
(
    AVAILABLE_BALANCE,
    CURRENT_MONTH_ADB,
    ADB_INCREASE,
    BALANCE_AS_OF,
    BUFFER,
) = range(5)


calculator = SaveBonusCalculator()


# =========================
# Command Handlers
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the OCBC Save Bonus Calculator Bot.\nUse /calculate to begin."
    )


async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter Available Balance:")
    return AVAILABLE_BALANCE


# =========================
# Step Handlers
# =========================
async def available_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["available_balance"] = float(update.message.text)
    await update.message.reply_text("Enter Current Month Average Daily Balance:")
    return CURRENT_MONTH_ADB


async def current_month_adb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["current_month_adb"] = float(update.message.text)
    await update.message.reply_text(
        "Enter Average Daily Balance Increase vs Last Month:"
    )
    return ADB_INCREASE


async def adb_increase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["adb_increase_vs_last_month"] = float(update.message.text)
    await update.message.reply_text("Enter Balance As Of:")
    return BALANCE_AS_OF


async def balance_as_of(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["balance_as_of"] = int(update.message.text)
    await update.message.reply_text("Enter Safety Buffer (optional, default = 50):")
    return BUFFER


async def buffer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data["buffer"] = float(text) if text else 50.0

    result = calculator.calculate(
        available_balance=context.user_data["available_balance"],
        current_month_adb=context.user_data["current_month_adb"],
        adb_increase_vs_last_month=context.user_data["adb_increase_vs_last_month"],
        balance_as_of=context.user_data["balance_as_of"],
        buffer=context.user_data["buffer"],
    )

    await update.message.reply_text(
        "Calculation completed.\n\n"
        "Operational Notes:\n"
        "- Daily cutoff: 10:00 PM (SGT)\n"
        "- No processing on Sundays\n\n"
        f"{result}"
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Calculation cancelled.")
    return ConversationHandler.END


async def kofi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = caffeine()
    await update.message.reply_text(message)


# =========================
# Application Entry Point
# =========================
def main():
    app = ApplicationBuilder().token(TELEGRAM_API_KEY).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("calculate", calculate)],
        states={
            AVAILABLE_BALANCE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, available_balance)
            ],
            CURRENT_MONTH_ADB: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, current_month_adb)
            ],
            ADB_INCREASE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, adb_increase)
            ],
            BALANCE_AS_OF: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, balance_as_of)
            ],
            BUFFER: [MessageHandler(filters.TEXT & ~filters.COMMAND, buffer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("kofi", kofi))

    app.run_polling()


if __name__ == "__main__":
    main()
