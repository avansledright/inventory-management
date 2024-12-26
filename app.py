from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
import os
import time

app = Flask(__name__)

def connect_with_retry(uri, max_retries=5, delay=5):
    """Attempt to connect to MongoDB with retries"""
    for attempt in range(max_retries):
        try:
            client = MongoClient(uri)
            # Test the connection
            client.admin.command('ismaster')
            print(f"Successfully connected to MongoDB on attempt {attempt + 1}")
            return client
        except Exception as e:
            if attempt + 1 == max_retries:
                print(f"Final connection attempt failed: {str(e)}")
                raise
            print(f"Connection attempt {attempt + 1} failed, retrying in {delay} seconds...")
            time.sleep(delay)

# MongoDB connection with retry logic
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/inventory_db')
print(f"Attempting to connect to MongoDB at: {mongo_uri}")
client = connect_with_retry(mongo_uri)
db = client.inventory_db

# Collections
general_info = db.general_info
sensitive_info = db.sensitive_info

# Collections
general_info = db.general_info
sensitive_info = db.sensitive_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug/insert-test-data')
def insert_test_data():
    """Debug endpoint to insert test data"""
    try:
        # Insert general information
        general_info.insert_many([
            {
                "asset_id": "A123",
                "customer": "John Doe",
                "address": "123 Main St, City, State 12345",
                "phone_number": "555-0123"
            },
            {
                "asset_id": "B456",
                "customer": "Jane Smith",
                "address": "456 Oak Ave, Town, State 67890",
                "phone_number": "555-4567"
            }
        ])

        # Insert sensitive information
        sensitive_info.insert_many([
            {
                "asset_id": "A123",
                "model": "XYZ-1000",
                "floor_location": "3rd Floor",
                "room_location": "Room 304",
                "notes": "Regular maintenance required"
            },
            {
                "asset_id": "B456",
                "model": "ABC-2000",
                "floor_location": "2nd Floor",
                "room_location": "Room 215",
                "notes": "Special handling required"
            }
        ])
        return jsonify({"message": "Test data inserted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug/assets')
def list_assets():
    """Debug endpoint to list all assets in the database"""
    general_assets = list(general_info.find())
    sensitive_assets = list(sensitive_info.find())
    return jsonify({
        'general_assets': dumps(general_assets),
        'sensitive_assets': dumps(sensitive_assets),
        'general_count': len(general_assets),
        'sensitive_count': len(sensitive_assets)
    })

@app.route('/search/<asset_id>')
def search_asset(asset_id):
    # Log the search attempt
    print(f"Searching for asset_id: {asset_id}")
    
    try:
        # Get general information
        general_data = general_info.find_one({'asset_id': asset_id})
        print(f"General data found: {general_data is not None}")
        
        if not general_data:
            print(f"No data found for asset_id: {asset_id}")
            return jsonify({'error': 'Asset not found'}), 404
        
        # Get sensitive information
        sensitive_data = sensitive_info.find_one({'asset_id': asset_id})
        print(f"Sensitive data found: {sensitive_data is not None}")
        
        # Combine the data
        result = {
            'general': dumps(general_data),
            'sensitive': dumps(sensitive_data) if sensitive_data else None
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error occurred while searching: {str(e)}")
        return jsonify({'error': 'An error occurred while searching'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)