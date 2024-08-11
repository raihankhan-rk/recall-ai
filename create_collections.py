from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def create_collections():
    client = MongoClient(os.getenv("MONGODB_URI"))
    db = client[os.getenv("DB_NAME")]

    try:
        # Create users collection
        if "users" not in db.list_collection_names():
            db.create_collection("users")
            db.users.create_index("user_id", unique=True)

        # Create license_keys collection
        if "license_keys" not in db.list_collection_names():
            db.create_collection("license_keys")
            db.license_keys.create_index("key", unique=True)

        print("Collections created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    create_collections()