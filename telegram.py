import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Define the URL to your Dash dashboard
DASHBOARD_URL = "https://your-dashboard-link.com"  # Replace with the actual link to your deployed dashboard

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        f"Welcome to the Employee Performance Dashboard Bot!\n\n"
        f"You can access the dashboard here: {DASHBOARD_URL}\n"
        f"Use /charts to request specific charts or KPIs."
    )

# Define charts command to send a link or image of a chart
def charts(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        f"Here's the link to the dashboard where you can view charts and KPIs: {DASHBOARD_URL}"
    )
    # You can customize this part to send specific charts or images based on user input

# Error handler
def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')

# Main function to start the bot
def main():
    # Get the bot token from BotFather
    TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot's token

    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("charts", charts))

    # Log all errors
    dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
