import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import matplotlib.pyplot as plt
import pandas as pd

# Load environment variables from the .env file
load_dotenv()

# Read API URL and Bot Token from .env
API_URL = os.getenv('API_URL')
TOKEN = os.getenv('BOT_TOKEN')

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

def overtime_employee(update: Update, context: CallbackContext) -> None:
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
        context.bot.send_photo(update.effective_chat.id, photo=open('overtime_employee.png', 'rb'))
    else:
        update.message.reply_text("Failed to fetch data.")

def delay_department(update: Update, context: CallbackContext) -> None:
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
        context.bot.send_photo(update.effective_chat.id, photo=open('delay_department.png', 'rb'))
    else:
        update.message.reply_text("Failed to fetch data.")


def attendance_rate(update: Update, context: CallbackContext) -> None:
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
        context.bot.send_photo(update.effective_chat.id, photo=open('attendance_rate.png', 'rb'))
    else:
        update.message.reply_text("Failed to fetch data.")


def overtime_vs_delay(update: Update, context: CallbackContext) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Generate scatter plot
        plt.figure(figsize=(10, 6))
        plt.scatter(df['Overtime'], df['Delay'], c='blue', alpha=0.5)
        plt.title("Overtime vs Delay")
        plt.xlabel("Overtime (Hours)")
        plt.ylabel("Delay (Hours)")
        plt.tight_layout()

        # Save and send the image
        plt.savefig('overtime_vs_delay.png')
        context.bot.send_photo(update.effective_chat.id, photo=open('overtime_vs_delay.png', 'rb'))
    else:
        update.message.reply_text("Failed to fetch data.")


def fines_employee(update: Update, context: CallbackContext) -> None:
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
        context.bot.send_photo(update.effective_chat.id, photo=open('fines_employee.png', 'rb'))
    else:
        update.message.reply_text("Failed to fetch data.")

def bonuses_department(update: Update, context: CallbackContext) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Generate pie chart for bonuses
        bonuses_summary = df.groupby('department')['Bonus'].sum()

        plt.figure(figsize=(7, 7))
        bonuses_summary.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title("Bonuses by Department")
        plt.tight_layout()

        # Save and send the image
        plt.savefig('bonuses_department.png')
        context.bot.send_photo(update.effective_chat.id, photo=open('bonuses_department.png', 'rb'))
    else:
        update.message.reply_text("Failed to fetch data.")


def top_overtime(update: Update, context: CallbackContext) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Get top 5 employees with the most overtime
        top_employees = df.groupby('employee')['Overtime'].sum().sort_values(ascending=False).head(5)

        plt.figure(figsize=(10, 6))
        top_employees.plot(kind='bar', color='orange')
        plt.title("Top 5 Employees with Most Overtime")
        plt.xlabel("Employee")
        plt.ylabel("Total Overtime (Hours)")
        plt.tight_layout()

        # Save and send the image
        plt.savefig('top_overtime.png')
        context.bot.send_photo(update.effective_chat.id, photo=open('top_overtime.png', 'rb'))
    else:
        update.message.reply_text("Failed to fetch data.")


def main():
    # Initialize the updater with the bot token
    updater = Updater(TOKEN, use_context=True)

    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("attendance", attendance))
    dispatcher.add_handler(CommandHandler("holiday", holiday))
    dispatcher.add_handler(CommandHandler("permission", permission))
    dispatcher.add_handler(CommandHandler("overtime_employee", overtime_employee))
    dispatcher.add_handler(CommandHandler("delay_department", delay_department))
    dispatcher.add_handler(CommandHandler("attendance_rate", attendance_rate))
    dispatcher.add_handler(CommandHandler("overtime_vs_delay", overtime_vs_delay))
    dispatcher.add_handler(CommandHandler("fines_employee", fines_employee))
    dispatcher.add_handler(CommandHandler("bonuses_department", bonuses_department))
    dispatcher.add_handler(CommandHandler("top_overtime", top_overtime))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
