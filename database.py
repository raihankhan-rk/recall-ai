import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from urllib.parse import urlparse
import os

load_dotenv()

# Database connection
def get_db_connection():
    try:
        url = urlparse(os.getenv("DATABASE_URL"))
        return mysql.connector.connect(
            host=url.hostname,
            user=url.username,
            password=url.password,
            database=url.path[1:],
            port=url.port,
            autocommit=False  # This ensures we control transactions manually
        )
    except Error as e:
        print(f"An error occurred: {e}")
        return None

# Check if user is activated
async def is_user_activated(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT is_activated FROM users WHERE user_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result and result[0]

# Activate user with license key
async def activate_user(user_id, license_key):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error"
    
    try:
        cur = conn.cursor()
        
        # Check if license key is valid and unused
        cur.execute("SELECT is_used FROM license_keys WHERE `key` = %s", (license_key,))
        key_status = cur.fetchone()
        if not key_status or key_status[0]:
            return False, "Invalid or already used license key."

        # Start transaction
        conn.start_transaction()

        # Create or update user first
        cur.execute(
            "INSERT INTO users (user_id, is_activated, activated_at) VALUES (%s, TRUE, NOW()) "
            "ON DUPLICATE KEY UPDATE is_activated = TRUE, activated_at = NOW()",
            (user_id,)
        )

        # Now mark license key as used
        cur.execute(
            "UPDATE license_keys SET is_used = TRUE, used_by = %s, used_at = NOW() WHERE `key` = %s",
            (user_id, license_key)
        )

        # Commit the transaction
        conn.commit()
        return True, "Successfully activated!"
    except Error as e:
        conn.rollback()
        return False, f"Activation failed: {str(e)}"
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()