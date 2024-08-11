import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

load_dotenv()

def create_tables():
    try:
        # Parse the DATABASE_URL
        url = urlparse(os.getenv("DB_URL"))
        conn = mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],  # Remove leading '/'
            port=url.port
        )
        cur = conn.cursor()

        # Create users table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username VARCHAR(255),
            is_activated BOOLEAN DEFAULT FALSE,
            activated_at TIMESTAMP
        )
        """)

        # Create license_keys table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS license_keys (
            `key` VARCHAR(255) PRIMARY KEY,
            is_used BOOLEAN DEFAULT FALSE,
            used_by BIGINT,
            used_at TIMESTAMP,
            FOREIGN KEY (used_by) REFERENCES users(user_id)
        )
        """)

        conn.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

if __name__ == "__main__":
    create_tables()