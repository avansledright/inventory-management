# init-db.py
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import os
import time

def init_database():
    # Connect using the MONGO_URI from environment variables
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:password123@mongodb:27017/inventory_db?authSource=admin')
    max_retries = 5
    retry_delay = 3

    for attempt in range(max_retries):
        try:
            client = MongoClient(mongo_uri)
            db = client.inventory_db
            
            # Test connection
            client.admin.command('ping')
            print(f"Successfully connected to MongoDB on attempt {attempt + 1}")
            
            # Create collections if they don't exist
            if 'general_info' not in db.list_collection_names():
                db.create_collection('general_info')
            if 'sensitive_info' not in db.list_collection_names():
                db.create_collection('sensitive_info')
            
            # Create indexes
            db.general_info.create_index('asset_id', unique=True)
            db.sensitive_info.create_index('asset_id', unique=True)
            
            print("Database initialized successfully!")
            return
            
        except OperationFailure as e:
            print(f"Operation failed on attempt {attempt + 1}: {str(e)}")
            if attempt + 1 < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise
        except Exception as e:
            print(f"Error on attempt {attempt + 1}: {str(e)}")
            if attempt + 1 < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                raise
        finally:
            if 'client' in locals():
                client.close()

if __name__ == '__main__':
    # Give MongoDB time to start up
    time.sleep(10)
    init_database()