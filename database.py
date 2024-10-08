from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def get_db_connection():
    client = MongoClient(os.getenv("MONGODB_URI"))
    return client[os.getenv("DB_NAME")]

async def is_user_activated(user_id=None, username=None):
    db = get_db_connection()
    query = {}
    if user_id:
        query["user_id"] = user_id
    elif username:
        query["username"] = username
    else:
        return False
    user = db.users.find_one(query)
    return user and user.get("is_activated", False)

async def activate_user(user_id, username, license_key):
    db = get_db_connection()
    try:
        # Check if license key is valid and unused
        key_doc = db.license_keys.find_one({"key": license_key})
        if not key_doc:
            return False, "Invalid license key."
        if key_doc.get("is_used", False):
            # If the key is used by the same user, allow reactivation
            if key_doc.get("used_by") == user_id:
                db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "username": username,
                        "is_activated": True,
                        "activated_at": datetime.now(),
                        "license_key": license_key
                    }}
                )
                return True, "Your account has been reactivated!"
            else:
                return False, "This license key is already in use."

        # Mark license key as used
        db.license_keys.update_one(
            {"key": license_key},
            {"$set": {"is_used": True, "used_by": user_id, "username": username, "used_at": datetime.now()}}
        )

        # Activate user
        db.users.update_one(
            {"user_id": user_id},
            {"$set": {
                "username": username,
                "is_activated": True,
                "activated_at": datetime.now(),
                "license_key": license_key
            }},
            upsert=True
        )

        return True, "Your account has been successfully activated!"
    except Exception as e:
        return False, f"Activation failed: {str(e)}"