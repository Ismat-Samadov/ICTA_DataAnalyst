from fastapi import FastAPI
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the FastAPI app
app = FastAPI()

# Database connection parameters
db_params = {
    "dbname": os.getenv('PGDATABASE'),
    "user": os.getenv('PGUSER'),
    "password": os.getenv('PGPASSWORD'),
    "host": os.getenv('PGHOST'),
    "port": "5432"
}

def get_db_connection():
    """Creates a connection to the PostgreSQL database"""
    return psycopg2.connect(**db_params)

@app.get("/attendance")
async def get_attendance():
    """Fetch attendance data from the database"""
    conn = get_db_connection()
    attendance_query = 'SELECT "Date", "Department", "Employee", "Entry", "Exit" FROM public.attendance;'
    attendance_df = pd.read_sql(attendance_query, conn)
    conn.close()
    return attendance_df.to_dict(orient='records')

@app.get("/holiday")
async def get_holiday():
    """Fetch holiday data from the database"""
    conn = get_db_connection()
    holiday_query = 'SELECT "Department", "Employee", "Start", "End" FROM public.holiday;'
    holiday_df = pd.read_sql(holiday_query, conn)
    conn.close()
    return holiday_df.to_dict(orient='records')

@app.get("/permission")
async def get_permission():
    """Fetch permission data from the database"""
    conn = get_db_connection()
    permission_query = 'SELECT "Date", "Department", "Employee", "Start", "End" FROM public."permission";'
    permission_df = pd.read_sql(permission_query, conn)
    conn.close()
    return permission_df.to_dict(orient='records')