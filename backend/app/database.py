from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import pandas as pd
import os
import asyncio

# MongoDB URI
uri = "mongodb+srv://almoghaviv:almoghaviv@workoutapp.e0r5zoq.mongodb.net/?retryWrites=true&w=majority&appName=workoutApp"

# Create a new asynchronous client and connect to the server
client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))

# Define the database and collections
db = client.workoutApp
users_collection = db.users
workout_collection = db.workout
events_collection = db.events  

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test the connection by sending a ping (asynchronous)
async def test_connection():
    try:
        # MongoDB 4.4+ supports async ping with 'admin.command' using motor
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")


# This function is used to populate the MongoDB database with initial user data from a CSV file.
# It should only be run once when setting up the database for the first time, or when needing
# to reset the database with fresh data. Running this multiple times will create duplicate records.
# The CSV file must contain the following columns matching the UserProfile model:
# - age: integer
# - full_name: string
# - id_number: integer
# - gender: string
# - height: integer
# - weight: integer
# - daily_calories_intake: integer
# - resting_heart_rate: integer
# - VO2_max: float
# - body_fat: float

# async def upload_data_to_mongo():
#     try:
#         # Read the CSV file using the absolute path
#         csv_path = os.path.join(PROJECT_ROOT, 'data', 'workout_fitness_tracker_data.csv')
#         df = pd.read_csv(csv_path)
        
#         # Convert DataFrame records to list of dictionaries
#         records = df.to_dict('records')
        
#         # Process each record to match the UserProfile model structure
#         processed_records = []
#         for record in records:
#             # Extract only the fields that match our UserProfile model
#             user_record = {
#                 "age": record["age"],
#                 "full_name": record["full_name"],
#                 "id_number": record["id_number"], 
#                 "gender": record["gender"],
#                 "height": record["height"],
#                 "weight": record["weight"],
#                 "daily_calories_intake": record["daily_calories_intake"],
#                 "resting_heart_rate": record["resting_heart_rate"],
#                 "VO2_max": record["VO2_max"],
#                 "body_fat": record["body_fat"]
#             }
#             processed_records.append(user_record)

#         # Insert the processed records into MongoDB
#         result = await users_collection.insert_many(processed_records)
#         print(f"Successfully uploaded {len(result.inserted_ids)} records to MongoDB")
#         return True

#     except Exception as e:
#         print(f"Error uploading data to MongoDB: {e}")
#         return False

# async def upload_data_to_mongo():
#     try:
#         # Read the CSV file using the absolute path
#         csv_path = os.path.join(PROJECT_ROOT, 'data', 'workout_fitness_tracker_data.csv')
#         df = pd.read_csv(csv_path)
        
#         # Convert DataFrame records to list of dictionaries
#         records = df.to_dict('records')
        
#         # Process each record to match the UserProfile model structure
#         processed_records = []
#         for record in records:
#             # Extract only the fields that match our UserProfile model
#             user_record = {
#                 "id_number": record["id_number"], 
#                 "workout_type": record["workout_type"]
#             }
#             processed_records.append(user_record)

#         # Insert the processed records into MongoDB
#         result = await workout_collection.insert_many(processed_records)
#         print(f"Successfully uploaded {len(result.inserted_ids)} records to MongoDB")
#         return True

#     except Exception as e:
#         print(f"Error uploading data to MongoDB: {e}")
#         return False
    
# async def main():
#     success = await upload_data_to_mongo()
#     if success:
#         print("Data upload completed successfully!")
#     else:
#         print("Data upload failed!")

# if __name__ == "__main__":
#     asyncio.run(main()) 