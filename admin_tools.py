from pymongo import MongoClient
import os
from dotenv import load_dotenv
import secrets
import string
from datetime import datetime

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv("MONGODB_URI"))
    return client[os.getenv("DB_NAME")]

def generate_license_key(num_keys=1):
    db = get_db_connection()

    try:
        for _ in range(num_keys):
            while True:
                # Generate a random 16-character key
                key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16))

                # Check if the key already exists
                if db.license_keys.find_one({"key": key}) is None:
                    # If the key doesn't exist, insert it
                    db.license_keys.insert_one({"key": key, "is_used": False})
                    print(f"Generated license key: {key}")
                    break
    except Exception as e:
        print(f"An error occurred: {e}")

def deactivate_user(identifier):
    db = get_db_connection()
    try:
        query = {}
        if '@' in identifier:
            query["username"] = identifier[1:]
        else:
            query["license_key"] = identifier

        user = db.users.find_one(query)
        if not user:
            return False, "User not found"

        # Deactivate user
        result = db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"is_activated": False, "activated_at": None}}
        )

        if result.modified_count == 0:
            return False, "User was not modified. They may already be deactivated."

        # Reset license key
        db.license_keys.update_one(
            {"key": user["license_key"]},
            {"$set": {"is_used": False, "used_by": None, "username": None, "used_at": None}}
        )

        return True, f"User {user['username']} has been deactivated"
    except Exception as e:
        return False, f"Deactivation failed: {str(e)}"

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
            identifier = input("Enter username or license key to deactivate: ")
            success, message = deactivate_user(identifier)
            print(message)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")