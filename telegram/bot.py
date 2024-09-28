import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler
import matplotlib.pyplot as plt
import pandas as pd

# Load environment variables from the .env file
load_dotenv()

# Read API URL and Bot Token from .env
API_URL = os.getenv('API_URL')
TOKEN = os.getenv('BOT_TOKEN')

# Define the start command
async def start(update: Update, context) -> None:
    await update.message.reply_text('Welcome to the Employee Data Bot! Use /attendance, /holiday, or /permission to get data.')

# Fetch and send attendance data
async def attendance(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        message = "Attendance Data:\n"
        for record in data[:5]:  # Limit to first 5 records
            message += f"Employee: {record['employee']}, Date: {record['Date']}, Entry: {record['entry']}, Exit: {record['Exit']}\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Failed to fetch attendance data.")

# Fetch and send holiday data
async def holiday(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/holiday")
    if response.status_code == 200:
        data = response.json()
        message = "Holiday Data:\n"
        for record in data[:5]:
            message += f"Employee: {record['Employee']}, Start: {record['Start']}, End: {record['End']}\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Failed to fetch holiday data.")

# Fetch and send permission data
async def permission(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/permission")
    if response.status_code == 200:
        data = response.json()
        message = "Permission Data:\n"
        for record in data[:5]:
            message += f"Employee: {record['Employee']}, Date: {record['Date']}, Start: {record['Start']}, End: {record['End']}\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Failed to fetch permission data.")

# Generate and send overtime chart
async def overtime_employee(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Generate bar chart for overtime
        plt.figure(figsize=(10, 6))
        df.groupby('employee')['Overtime'].sum().plot(kind='bar', color='skyblue')
        plt.title("Total Overtime by Employee")
        plt.xlabel("Employee")
        plt.ylabel("Overtime (Hours)")
        plt.tight_layout()

        # Save and send the image
        plt.savefig('overtime_employee.png')
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('overtime_employee.png', 'rb'))
    else:
        await update.message.reply_text("Failed to fetch data.")

def main():
    # Initialize the application
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attendance", attendance))
    application.add_handler(CommandHandler("holiday", holiday))
    application.add_handler(CommandHandler("permission", permission))
    application.add_handler(CommandHandler("overtime_employee", overtime_employee))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
