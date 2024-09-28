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
        await context.bot.send_photo(update.effective_chat.id, photo=open('overtime_employee.png', 'rb'))
    else:
        await update.message.reply_text("Failed to fetch data.")

# Generate and send delay chart by department
async def delay_department(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Generate bar chart for delays
        plt.figure(figsize=(10, 6))
        df.groupby('department')['Delay'].sum().plot(kind='bar', color='red')
        plt.title("Total Delay by Department")
        plt.xlabel("Department")
        plt.ylabel("Delay (Hours)")
        plt.tight_layout()

        # Save and send the image
        plt.savefig('delay_department.png')
        await context.bot.send_photo(update.effective_chat.id, photo=open('delay_department.png', 'rb'))
    else:
        await update.message.reply_text("Failed to fetch data.")

# Generate and send attendance rate pie chart
async def attendance_rate(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Assuming we have present and absent days in data
        df['Present'] = df['entry'].notna().astype(int)  # 1 for present, 0 for absent

        # Generate pie chart for attendance
        attendance_summary = df.groupby('employee')['Present'].sum()
        total_days = len(df['Date'].unique())
        attendance_rate = (attendance_summary / total_days) * 100

        plt.figure(figsize=(7, 7))
        attendance_rate.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title("Attendance Rate by Employee")
        plt.tight_layout()

        # Save and send the image
        plt.savefig('attendance_rate.png')
        await context.bot.send_photo(update.effective_chat.id, photo=open('attendance_rate.png', 'rb'))
    else:
        await update.message.reply_text("Failed to fetch data.")

# Generate and send fines chart by employee
async def fines_employee(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Generate bar chart for fines
        plt.figure(figsize=(10, 6))
        df.groupby('employee')['Fine'].sum().plot(kind='bar', color='purple')
        plt.title("Total Fines by Employee")
        plt.xlabel("Employee")
        plt.ylabel("Fines")
        plt.tight_layout()

        # Save and send the image
        plt.savefig('fines_employee.png')
        await context.bot.send_photo(update.effective_chat.id, photo=open('fines_employee.png', 'rb'))
    else:
        await update.message.reply_text("Failed to fetch data.")

# Main function to run the bot
async def main():
    # Initialize the application
    application = Application.builder().token(TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attendance", attendance))
    application.add_handler(CommandHandler("holiday", holiday))
    application.add_handler(CommandHandler("permission", permission))
    application.add_handler(CommandHandler("overtime_employee", overtime_employee))
    application.add_handler(CommandHandler("delay_department", delay_department))
    application.add_handler(CommandHandler("attendance_rate", attendance_rate))
    application.add_handler(CommandHandler("fines_employee", fines_employee))

    # Start the bot
    await application.start()
    await application.updater.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
