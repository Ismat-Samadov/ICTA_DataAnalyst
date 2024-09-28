import os
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
import matplotlib.pyplot as plt
import pandas as pd

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
        
        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        plt.close()
    else:
        await update.message.reply_text("Failed to fetch data.")

# Generate and send delay by department chart
async def delay_department(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        df['Delay'] = pd.to_numeric(df.get('Delay', 0), errors='coerce').fillna(0)

        plt.figure(figsize=(10, 6))
        df.groupby('department')['Delay'].sum().plot(kind='bar', color='red')
        plt.title("Total Delay by Department")
        plt.xlabel("Department")
        plt.ylabel("Delay (Hours)")
        plt.tight_layout()

        plt.savefig('delay_department.png')
        with open('delay_department.png', 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        plt.close()
    else:
        await update.message.reply_text("Failed to fetch data.")

# Generate and send attendance rate pie chart
async def attendance_rate(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        df['Present'] = df['entry'].notna().astype(int)

        attendance_summary = df.groupby('employee')['Present'].sum()
        total_days = len(df['Date'].unique())
        attendance_rate = (attendance_summary / total_days) * 100

        plt.figure(figsize=(7, 7))
        attendance_rate.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title("Attendance Rate by Employee")
        plt.tight_layout()

        plt.savefig('attendance_rate.png')
        with open('attendance_rate.png', 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        plt.close()
    else:
        await update.message.reply_text("Failed to fetch data.")

# Generate and send fines by employee chart
async def fines_employee(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        df['Fine'] = pd.to_numeric(df.get('Fine', 0), errors='coerce').fillna(0)

        plt.figure(figsize=(10, 6))
        df.groupby('employee')['Fine'].sum().plot(kind='bar', color='purple')
        plt.title("Total Fines by Employee")
        plt.xlabel("Employee")
        plt.ylabel("Fines")
        plt.tight_layout()

        plt.savefig('fines_employee.png')
        with open('fines_employee.png', 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        plt.close()
    else:
        await update.message.reply_text("Failed to fetch data.")

# Generate and send bonuses pie chart by department
async def bonuses_department(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        df['Bonus'] = pd.to_numeric(df.get('Bonus', 0), errors='coerce').fillna(0)

        bonuses_summary = df.groupby('department')['Bonus'].sum()

        plt.figure(figsize=(7, 7))
        bonuses_summary.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title("Bonuses by Department")
        plt.tight_layout()

        plt.savefig('bonuses_department.png')
        with open('bonuses_department.png', 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        plt.close()
    else:
        await update.message.reply_text("Failed to fetch data.")

# Generate and send top 5 overtime employees chart
async def top_overtime(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        df['Overtime'] = pd.to_numeric(df.get('Overtime', 0), errors='coerce').fillna(0)

        top_employees = df.groupby('employee')['Overtime'].sum().sort_values(ascending=False).head(5)

        plt.figure(figsize=(10, 6))
        top_employees.plot(kind='bar', color='orange')
        plt.title("Top 5 Employees with Most Overtime")
        plt.xlabel("Employee")
        plt.ylabel("Total Overtime (Hours)")
        plt.tight_layout()

        plt.savefig('top_overtime.png')
        with open('top_overtime.png', 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        plt.close()
    else:
        await update.message.reply_text("Failed to fetch data.")

# Generate and send overtime vs delay scatter plot
async def overtime_vs_delay(update: Update, context) -> None:
    response = requests.get(f"{API_URL}/attendance")
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        # Convert 'Overtime' and 'Delay' to numeric
        df['Overtime'] = pd.to_numeric(df.get('Overtime', 0), errors='coerce').fillna(0)
        df['Delay'] = pd.to_numeric(df.get('Delay', 0), errors='coerce').fillna(0)

        # Generate scatter plot
        plt.figure(figsize=(10, 6))
        plt.scatter(df['Overtime'], df['Delay'], c='blue', alpha=0.5)
        plt.title("Overtime vs Delay")
        plt.xlabel("Overtime (Hours)")
        plt.ylabel("Delay (Hours)")
        plt.tight_layout()

        # Save and send the image
        plt.savefig('overtime_vs_delay.png')
        with open('overtime_vs_delay.png', 'rb') as photo:
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)
        plt.close()
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
    application.add_handler(CommandHandler("delay_department", delay_department))
    application.add_handler(CommandHandler("attendance_rate", attendance_rate))
    application.add_handler(CommandHandler("overtime_vs_delay", overtime_vs_delay))
    application.add_handler(CommandHandler("fines_employee", fines_employee))
    application.add_handler(CommandHandler("bonuses_department", bonuses_department))
    application.add_handler(CommandHandler("top_overtime", top_overtime))

    # Start the bot and keep it running
    await application.start()
    await application.updater.start_polling()
    await application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
