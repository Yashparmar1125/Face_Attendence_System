import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '1125'),
            database=os.getenv('DB_NAME', 'attendence_record')
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f'Error: {e}')
        return None

def execute_query(query, params=None):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def commit_changes():
    connection = create_connection()
    cursor = connection.cursor()
    connection.commit()
    cursor.close()
    connection.close()
