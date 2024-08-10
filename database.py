import sqlite3
import os
import secrets

DB_NAME = "user_licenses.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, license_key TEXT, is_active INTEGER)''')
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_NAME)

# def generate_license_key():
#     return secrets.token_hex(16)

# def create_new_license():
#     license_key = generate_license_key()
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("INSERT INTO users (license_key, is_active) VALUES (?, 0)", (license_key,))
#     conn.commit()
#     conn.close()
#     return license_key

# def activate_user_license(user_id, license_key):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT * FROM users WHERE license_key = ? AND is_active = 0", (license_key,))
#     if c.fetchone() is not None:
#         c.execute("UPDATE users SET user_id = ?, is_active = 1 WHERE license_key = ?", (user_id, license_key))
#         conn.commit()
#         conn.close()
#         return True
#     conn.close()
#     return False

# def get_user_license_status(user_id):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("SELECT is_active FROM users WHERE user_id = ?", (user_id,))
#     result = c.fetchone()
#     conn.close()
#     return result[0] if result else False

# def deactivate_user_license(user_id):
#     conn = get_db_connection()
#     c = conn.cursor()
#     c.execute("UPDATE users SET is_active = 0 WHERE user_id = ?", (user_id,))
#     conn.commit()
#     conn.close()