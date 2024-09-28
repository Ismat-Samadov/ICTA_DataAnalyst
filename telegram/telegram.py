import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Your FastAPI server URL
API_URL = 'http://127.0.0.1:8000'

# Define the start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the Employee Data Bot! Use /attendance, /holiday, or /permission to get data.')

# Fetch and send attendance data
def attendance(update: Update, context: CallbackContext) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        message = "Attendance Data:\n"
        for record in data[:5]:  # Limit to first 5 records
            message += f"Employee: {record['employee']}, Date: {record['Date']}, Entry: {record['entry']}, Exit: {record['Exit']}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text("Failed to fetch attendance data.")

# Fetch and send holiday data
def holiday(update: Update, context: CallbackContext) -> None:
    response = requests.get(f"{API_URL}/holiday")
    if response.status_code == 200:
        data = response.json()
        message = "Holiday Data:\n"
        for record in data[:5]:
            message += f"Employee: {record['Employee']}, Start: {record['Start']}, End: {record['End']}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text("Failed to fetch holiday data.")

# Fetch and send permission data
def permission(update: Update, context: CallbackContext) -> None:
    response = requests.get(f"{API_URL}/permission")
    if response.status_code == 200:
        data = response.json()
        message = "Permission Data:\n"
        for record in data[:5]:
            message += f"Employee: {record['Employee']}, Date: {record['Date']}, Start: {record['Start']}, End: {record['End']}\n"
        update.message.reply_text(message)
    else:
        update.message.reply_text("Failed to fetch permission data.")

def main():
    # Replace with your bot token
    TOKEN = "YOUR_BOT_TOKEN"
    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("attendance", attendance))
    dispatcher.add_handler(CommandHandler("holiday", holiday))
    dispatcher.add_handler(CommandHandler("permission", permission))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
