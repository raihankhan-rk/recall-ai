import mysql.connector
from mysql.connector import Error
import secrets
import string
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    url = urlparse(os.getenv("DB_URL"))
    return mysql.connector.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        database=url.path[1:],  # Remove leading '/'
        port=url.port
    )

def generate_license_key(num_keys=1):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        for _ in range(num_keys):
            while True:
                # Generate a random 16-character key
                key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))
                
                # Check if the key already exists
                cur.execute("SELECT `key` FROM license_keys WHERE `key` = %s", (key,))
                if cur.fetchone() is None:
                    # If the key doesn't exist, insert it
                    cur.execute("INSERT INTO license_keys (`key`) VALUES (%s)", (key,))
                    conn.commit()
                    print(f"Generated license key: {key}")
                    break
    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

def deactivate_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Start a transaction
        conn.start_transaction()

        # Deactivate the user
        cur.execute("UPDATE users SET is_activated = FALSE, activated_at = NULL WHERE user_id = %s", (user_id,))
        
        # Find and delete the associated license key
        cur.execute("SELECT `key` FROM license_keys WHERE used_by = %s", (user_id,))
        deleted_key = cur.fetchone()
        if deleted_key:
            cur.execute("DELETE FROM license_keys WHERE used_by = %s", (user_id,))

        # Commit the transaction
        conn.commit()

        if deleted_key:
            print(f"User {user_id} has been deactivated and their license key {deleted_key[0]} has been deleted.")
        else:
            print(f"User {user_id} has been deactivated. No associated license key was found.")

    except Error as e:
        conn.rollback()
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    while True:
        print("\n1. Generate License Key(s)")
        print("2. Deactivate User")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            num_keys = int(input("Enter the number of keys to generate: "))
            generate_license_key(num_keys)
        elif choice == '2':
            user_id = int(input("Enter the user ID to deactivate: "))
            deactivate_user(user_id)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")