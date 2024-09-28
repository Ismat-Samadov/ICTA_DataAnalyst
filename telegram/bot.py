import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import matplotlib.pyplot as plt
import pandas as pd
import asyncio

# Load environment variables from the .env file
load_dotenv()

# Read API URL and Bot Token from .env
API_URL = os.getenv('API_URL')
TOKEN = os.getenv('BOT_TOKEN')

# Define the start command
async def start(update: Update, context) -> None:
    await update.message.reply_text(
        'Welcome to the Employee Data Bot!\n\n'
        'Available commands:\n'
        '/attendance - Get recent attendance data\n'
        '/holiday - Get recent holiday data\n'
        '/permission - Get recent permission data\n'
        '/overtime_employee - Overtime by Employee (Chart)\n'
        '/delay_department - Delay by Department (Chart)\n'
        '/attendance_rate - Attendance Rate by Employee (Chart)\n'
        '/overtime_vs_delay - Overtime vs Delay (Chart)\n'
        '/fines_employee - Fines by Employee (Chart)\n'
        '/bonuses_department - Bonuses by Department (Chart)\n'
        '/top_overtime - Top 5 Employees with Most Overtime (Chart)'
    )

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

# Generate and send overtime by employee chart
async def overtime_employee(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Ensure the Overtime column exists and is numeric
        df['Overtime'] = pd.to_numeric(df.get('Overtime', 0), errors='coerce').fillna(0)

        # Generate bar chart for overtime
        plt.figure(figsize=(10, 6))
        df.groupby('employee')['Overtime'].sum().plot(kind='bar', color='skyblue')
        plt.title("Total Overtime by Employee")
        plt.xlabel("Employee")
        plt.ylabel("Overtime (Hours)")
        plt.tight_layout()

        # Save and send the image
        image_path = 'overtime_employee.png'
        plt.savefig(image_path)
        plt.close()  # Close the plot to free memory
        
        try:
            await context.bot.send_photo(update.effective_chat.id, photo=open(image_path, 'rb'))
        except Exception as e:
            await update.message.reply_text(f"Error sending chart: {e}")
    else:
        await update.message.reply_text("Failed to fetch data.")

# Main function to start the bot
async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attendance", attendance))
    application.add_handler(CommandHandler("holiday", holiday))
    application.add_handler(CommandHandler("permission", permission))
    application.add_handler(CommandHandler("overtime_employee", overtime_employee))

    # Run the bot
    await application.run_polling()

if __name__ == '__main__':
    # Use asyncio's get_running_loop() to check if an event loop is already running
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # If no loop is running, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Run the event loop
    try:
        loop.run_until_complete(main())
    except RuntimeError as e:
        print(f"Error running the bot: {e}")
