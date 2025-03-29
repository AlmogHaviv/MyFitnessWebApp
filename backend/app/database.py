from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import pandas as pd
import re

# MongoDB URI (make sure to replace <db_password> with your actual password)
uri = "mongodb+srv://almoghaviv:almoghaviv@workoutapp.e0r5zoq.mongodb.net/?retryWrites=true&w=majority&appName=workoutApp"

# Create a new asynchronous client and connect to the server
client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))

# Define the database and collection
db = client.workout_app  # You can change 'workout_app' to your database name
users_collection = db.users  # You can change 'users' to your desired collection name
user_and_feelings_collection = db.workout_fitness_tracker
# Test the connection by sending a ping (asynchronous)
async def test_connection():
    try:
        # MongoDB 4.4+ supports async ping with 'admin.command' using motor
        await client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
