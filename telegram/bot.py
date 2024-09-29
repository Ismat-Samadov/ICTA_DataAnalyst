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

# Analytics command with chart functionality
async def analytics(update: Update, context) -> None:
    attendance_df = fetch_data(ATTENDANCE_URL)
    holiday_df = fetch_data(HOLIDAY_URL)
    permission_df = fetch_data(PERMISSION_URL)

    # Data processing as per your requirements
    attendance_df['Entry'] = pd.to_datetime(attendance_df['Entry'], format='%H:%M')
    attendance_df['Exit'] = pd.to_datetime(attendance_df['Exit'], format='%H:%M')

    # Calculate work hours, overtime, and delay
    attendance_df['Work_Hours'] = (attendance_df['Exit'] - attendance_df['Entry']).dt.total_seconds() / 3600
    attendance_df['Overtime'] = attendance_df['Work_Hours'] - 8
    attendance_df['Overtime'] = attendance_df['Overtime'].apply(lambda x: x if x > 0 else 0)
    attendance_df['Delay'] = 8 - attendance_df['Work_Hours']
    attendance_df['Delay'] = attendance_df['Delay'].apply(lambda x: x if x > 0 else 0)

    # Permission data processing
    permission_df['Start'] = pd.to_datetime(permission_df['Start'], format='%H:%M:%S')
    permission_df['End'] = pd.to_datetime(permission_df['End'], format='%H:%M:%S')
    permission_df['Permission_Hours'] = (permission_df['End'] - permission_df['Start']).dt.total_seconds() / 3600

    # Merge attendance with permission data
    attendance_with_permission = pd.merge(attendance_df, 
                                          permission_df[['Date', 'Department', 'Employee', 'Permission_Hours']], 
                                          on=['Date', 'Department', 'Employee'], how='left')

    attendance_with_permission['Adjusted_Work_Hours'] = attendance_with_permission['Work_Hours'] - attendance_with_permission['Permission_Hours'].fillna(0)

    # Holiday data processing
    holiday_df['Start'] = pd.to_datetime(holiday_df['Start'])
    holiday_df['End'] = pd.to_datetime(holiday_df['End'])

    leave_dates = []
    for idx, row in holiday_df.iterrows():
        leave_dates += pd.date_range(row['Start'], row['End']).to_list()

    attendance_with_permission['On_Leave'] = attendance_with_permission['Date'].isin(leave_dates)
    attendance_with_permission['Date'] = pd.to_datetime(attendance_with_permission['Date'])
    attendance_with_permission['Is_Weekend'] = attendance_with_permission['Date'].dt.weekday >= 5

    attendance_with_permission = attendance_with_permission[~(attendance_with_permission['On_Leave'] & attendance_with_permission['Is_Weekend'])]
    attendance_with_permission = attendance_with_permission[~attendance_with_permission['On_Leave']]

    # Final dataset
    final_data = attendance_with_permission[['Date', 'Department', 'Employee', 'Adjusted_Work_Hours', 'Overtime', 'Delay']]

    # Plot the data (example: total adjusted work hours by employee)
    plt.figure(figsize=(10, 6))
    final_data.groupby('Employee')['Adjusted_Work_Hours'].sum().plot(kind='bar', title="Total Adjusted Work Hours by Employee")
    plt.ylabel("Adjusted Work Hours")
    plt.xlabel("Employee")
    plt.tight_layout()
    plt.savefig("adjusted_work_hours.png")

    # Send the chart to the user
    await update.message.reply_photo(photo=open('adjusted_work_hours.png', 'rb'))

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
