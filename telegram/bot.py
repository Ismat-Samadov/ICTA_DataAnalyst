import logging
import requests
import pandas as pd
import matplotlib.pyplot as plt
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import seaborn as sns
import openai 

# Load environment variables from the .env file
load_dotenv()

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Set OpenAI API Key
openai.api_key = os.getenv('OPENAI_API_KEY')

# API Endpoints and Bot Token from .env
API_URL = os.getenv('API_URL')
ATTENDANCE_URL = f"{API_URL}attendance"
HOLIDAY_URL = f"{API_URL}holiday"
PERMISSION_URL = f"{API_URL}permission"
BOT_TOKEN = os.getenv('BOT_TOKEN')

def fetch_data(url):
    response = requests.get(url)
    print(f"API Response: {response.text}")  
    try:
        return pd.DataFrame(response.json())
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if parsing fails

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

# Analytics command with chart functionality for monthly evaluation
async def analytics(update: Update, context) -> None:
    attendance_df = fetch_data(ATTENDANCE_URL)
    holiday_df = fetch_data(HOLIDAY_URL)
    permission_df = fetch_data(PERMISSION_URL)

    # Data processing as per your example
    attendance_df['Entry'] = pd.to_datetime(attendance_df['Entry'], format='%H:%M')
    attendance_df['Exit'] = pd.to_datetime(attendance_df['Exit'], format='%H:%M')
    attendance_df['Work_Hours'] = (attendance_df['Exit'] - attendance_df['Entry']).dt.total_seconds() / 3600
    attendance_df['Overtime'] = attendance_df['Work_Hours'] - 8
    attendance_df['Overtime'] = attendance_df['Overtime'].apply(lambda x: x if x > 0 else 0)
    attendance_df['Delay'] = 8 - attendance_df['Work_Hours']
    attendance_df['Delay'] = attendance_df['Delay'].apply(lambda x: x if x > 0 else 0)

    # Convert permission Start and End times to datetime to calculate permission hours
    permission_df['Start'] = pd.to_datetime(permission_df['Start'], format='%H:%M', errors='coerce')
    permission_df['End'] = pd.to_datetime(permission_df['End'], format='%H:%M', errors='coerce')

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

    # Monthly data extraction
    attendance_with_permission['Month'] = attendance_with_permission['Date'].dt.to_period('M')

    monthly_data = attendance_with_permission.groupby(['Employee', 'Department', 'Month']).agg({
        'Delay': 'sum',
        'Overtime': 'sum'
    }).reset_index()

    # Fines and Bonuses
    monthly_data['Fine'] = 0.0
    monthly_data['Bonus'] = 0.0
    monthly_data.loc[monthly_data['Delay'] > 3, 'Fine'] = 0.02
    monthly_data.loc[monthly_data['Delay'] > 10, 'Fine'] = 0.03
    monthly_data.loc[monthly_data['Delay'] > 20, 'Fine'] = 0.05
    monthly_data.loc[monthly_data['Overtime'] > 3, 'Bonus'] = 0.02
    monthly_data.loc[monthly_data['Overtime'] > 10, 'Bonus'] = 0.03
    monthly_data.loc[monthly_data['Overtime'] > 20, 'Bonus'] = 0.05

    # Now generate the charts and send them to the user

    # 1. Total Overtime by Employee
    plt.figure(figsize=(10, 6))
    monthly_data.groupby('Employee')['Overtime'].sum().plot(kind='bar', title="Total Overtime by Employee", color='skyblue')
    plt.xlabel('Employee')
    plt.ylabel('Total Overtime (Hours)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("total_overtime.png")
    await update.message.reply_photo(photo=open('total_overtime.png', 'rb'))

    # 2. Average Overtime by Employee
    plt.figure(figsize=(10, 6))
    monthly_data.groupby('Employee')['Overtime'].mean().plot(kind='bar', title="Average Overtime by Employee", color='green')
    plt.xlabel('Employee')
    plt.ylabel('Average Overtime (Hours)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("average_overtime.png")
    await update.message.reply_photo(photo=open('average_overtime.png', 'rb'))

    # 3. Total Delay by Employee
    plt.figure(figsize=(10, 6))
    monthly_data.groupby('Employee')['Delay'].sum().plot(kind='bar', title="Total Delay by Employee", color='red')
    plt.xlabel('Employee')
    plt.ylabel('Total Delay (Hours)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("total_delay.png")
    await update.message.reply_photo(photo=open('total_delay.png', 'rb'))

    # 4. Total Fines by Employee
    plt.figure(figsize=(10, 6))
    monthly_data.groupby('Employee')['Fine'].sum().plot(kind='bar', title="Total Fines by Employee", color='purple')
    plt.xlabel('Employee')
    plt.ylabel('Total Fines')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("total_fines.png")
    await update.message.reply_photo(photo=open('total_fines.png', 'rb'))

    # 5. Total Bonuses by Employee
    plt.figure(figsize=(10, 6))
    monthly_data.groupby('Employee')['Bonus'].sum().plot(kind='bar', title="Total Bonuses by Employee", color='blue')
    plt.xlabel('Employee')
    plt.ylabel('Total Bonuses')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("total_bonuses.png")
    await update.message.reply_photo(photo=open('total_bonuses.png', 'rb'))

    # 6. Overtime and Delay by Department (Stacked Bar Chart)
    plt.figure(figsize=(10, 6))
    department_data = monthly_data.groupby('Department')[['Overtime', 'Delay']].sum()
    department_data.plot(kind='bar', stacked=True, title="Overtime and Delay by Department", color=['orange', 'red'])
    plt.xlabel('Department')
    plt.ylabel('Hours')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("overtime_delay_by_department.png")
    await update.message.reply_photo(photo=open('overtime_delay_by_department.png', 'rb'))

    # 7. Overtime vs Delay (Scatter Plot)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=monthly_data, x='Overtime', y='Delay', hue='Employee', s=100, alpha=0.7)
    plt.title('Overtime vs Delay')
    plt.xlabel('Overtime (Hours)')
    plt.ylabel('Delay (Hours)')
    plt.tight_layout()
    plt.savefig("overtime_vs_delay.png")
    await update.message.reply_photo(photo=open('overtime_vs_delay.png', 'rb'))


def summarize_data(data, max_rows=5):
    """
    Summarizes the API data to avoid exceeding token limits.
    Reduces the size of the data while retaining important information.
    """
    summarized_data = {}
    for key, value in data.items():
        # Take only the first 'max_rows' rows for each key
        summarized_data[key] = {k: value[k] for k in list(value)[:max_rows]}
    return summarized_data

# OpenAI response generation function (updated for token limits)
def generate_openai_response(user_query, api_data):
    # Summarize the data to reduce token count
    summarized_data = summarize_data(api_data)
    
    prompt = f"""
    You are a data analyst assistant. Below is some summarized data from an API:
    {summarized_data}
    
    Based on this data, answer the following question:
    {user_query}
    """
    
    try:
        # Call OpenAI API using ChatCompletion method
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful data analyst assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.InvalidRequestError as e:
        return f"Error generating response from OpenAI: {str(e)}"

# New OpenAI query handler
async def openai_query(update: Update, context) -> None:
    user_query = update.message.text  # Get the user's query
    
    # Fetch data from the API to use in the OpenAI response
    attendance_df = fetch_data(ATTENDANCE_URL)
    holiday_df = fetch_data(HOLIDAY_URL)
    permission_df = fetch_data(PERMISSION_URL)

    # Combine the data into a single context for OpenAI
    api_data = {
        "attendance": attendance_df.to_dict(),
        "holiday": holiday_df.to_dict(),
        "permission": permission_df.to_dict()
    }
    
    # Generate a response using OpenAI
    openai_response = generate_openai_response(user_query, api_data)

    # Send the OpenAI-generated response back to the user
    await update.message.reply_text(openai_response)

# Main function to set up the bot
def main():
    # Create the application
    application = Application.builder().token(BOT_TOKEN).build()
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attendance", attendance))
    application.add_handler(CommandHandler("holiday", holiday))
    application.add_handler(CommandHandler("analytics", analytics))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, openai_query))
    # Run the bot until you press Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
