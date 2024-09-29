import logging
import requests
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# API Endpoints and Bot Token from .env
API_URL = os.getenv('API_URL')
ATTENDANCE_URL = f"{API_URL}attendance"
HOLIDAY_URL = f"{API_URL}holiday"
PERMISSION_URL = f"{API_URL}permission"
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Fetch data from API
def fetch_data(url):
    response = requests.get(url)
    return pd.DataFrame(response.json())

# Start command
async def start(update: Update, context) -> None:
    await update.message.reply_text('Welcome to the Analytics Bot! Use /attendance, /holiday, or /analytics to get insights.')

# Attendance command
async def attendance(update: Update, context) -> None:
    attendance_df = fetch_data(ATTENDANCE_URL)
    await update.message.reply_text(f"Attendance Data:\n{attendance_df.head()}")

# Holiday command
async def holiday(update: Update, context) -> None:
    holiday_df = fetch_data(HOLIDAY_URL)
    await update.message.reply_text(f"Holiday Data:\n{holiday_df.head()}")

# Analytics command
async def analytics(update: Update, context) -> None:
    attendance_df = fetch_data(ATTENDANCE_URL)
    holiday_df = fetch_data(HOLIDAY_URL)
    permission_df = fetch_data(PERMISSION_URL)

    # Example analytics: Total attendance per employee
    attendance_df['Date'] = pd.to_datetime(attendance_df['Date'])
    total_days = attendance_df.groupby('employee').size()

    # Plotting the total attendance
    plt.figure(figsize=(10, 6))
    total_days.plot(kind='bar', title="Total Attendance Days Per Employee")
    plt.ylabel("Days")
    plt.xlabel("Employee")
    plt.tight_layout()
    plt.savefig("attendance.png")

    # Send image to the user
    await update.message.reply_photo(photo=open('attendance.png', 'rb'))

# Main function to set up the bot
def main():
    # Create the application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attendance", attendance))
    application.add_handler(CommandHandler("holiday", holiday))
    application.add_handler(CommandHandler("analytics", analytics))

    # Run the bot until you press Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
