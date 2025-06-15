import pandas as pd
import random
from datetime import datetime
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models_training_pipeline.knn.user_recommender import UserRecommender

# --- Heuristic scoring ---
def compatibility_score(u1, u2):
    score = 0
    if u1["workout_type"] == u2["workout_type"]:
        score += 3
    if abs(u1["age"] - u2["age"]) <= 5:
        score += 2
    if u1["gender"] == u2["gender"]:
        score += 0.5
    if abs(u1["VO2_max"] - u2["VO2_max"]) <= 5:
        score += 0.5
    if abs(u1["body_fat"] - u2["body_fat"]) <= 5:
        score += 0.5
    if abs(u1["bmi"] - u2["bmi"]) <= 2:
        score += 0.2
    return score

def decide_like(score):
    if score >= 5.0:
        return "like" if random.random() < 0.9 else "dislike"
    elif score >= 3.0:
        return "like" if random.random() < 0.7 else "dislike"
    elif score >= 1.5:
        return "like" if random.random() < 0.4 else "dislike"
    else:
        return "dislike"

# --- Populate MongoDB with interactions ---
async def populate_events():
    print("Connecting to MongoDB...")
    uri = "mongodb+srv://almoghaviv:almoghaviv@workoutapp.e0r5zoq.mongodb.net/?retryWrites=true&w=majority&appName=workoutApp"
    
    client = AsyncIOMotorClient(
        uri,
        server_api=ServerApi('1'),
        connectTimeoutMS=60000,
        socketTimeoutMS=60000
    )
    db = client.workoutApp
    users_collection = db.users
    workout_collection = db.workout
    events_collection = db.events

    print("Loading users from MongoDB...")
    try:
        users = await users_collection.find().to_list(length=None)
        for u in users:
            u.pop("_id", None)
        print(f"Loaded {len(users)} users.")
    except Exception as e:
        print(f"Error loading users: {e}")
        return

    print("Loading workouts from MongoDB...")
    try:
        workouts = await workout_collection.find().to_list(length=None)
        for w in workouts:
            w.pop("_id", None)
        print(f"Loaded {len(workouts)} workouts.")
    except Exception as e:
        print(f"Error loading workouts: {e}")
        return

    users_df = pd.DataFrame(users)
    workout_df = pd.DataFrame(workouts)

    print("Merging user and workout data...")
    merged_df = pd.merge(users_df, workout_df, on="id_number", how="left")
    print(f"Merged dataset has {len(merged_df)} entries.")

    print("Loading recommendation model...")
    user_recommender = UserRecommender()
    user_recommender.load_model()
    print("Model loaded.")

    events_to_insert = []
    total_events_generated = 0

    print("Generating interactions...")
    print(f"Total users to process: {len(merged_df)}")

    for i, (_, user) in enumerate(merged_df.iterrows()):
        print(f"\nProcessing user {i+1}/{len(merged_df)} - ID: {user['id_number']}")
        profile_dict = {
            'age': user['age'],
            'id_number': user['id_number'],
            'full_name': user['full_name'],
            'weight': user['weight'],
            'gender': user['gender'],
            'height': user['height'],
            'daily_calories_intake': user['daily_calories_intake'],
            'resting_heart_rate': user['resting_heart_rate'],
            'VO2_max': user['VO2_max'],
            'body_fat': user['body_fat'],
            'bmi': user['bmi']
        }

        try:
            distances, similar_ids = user_recommender.find_similar_users(profile_dict, k=150)
        except Exception as e:
            print(f"Error finding similar users for ID {user['id_number']}: {e}")
            continue

        candidates = merged_df[merged_df["id_number"].isin(similar_ids)]
        candidates = candidates[candidates["id_number"] != user["id_number"]]

        print(f"Found {len(similar_ids)} similar users, {len(candidates)} candidates after removing self.")

        sample_size = min(150, len(candidates))
        if sample_size == 0:
            print(f"No candidates to sample for user {user['id_number']}. Skipping...")
            continue

        sampled = candidates.sample(n=sample_size, random_state=42)
        print(f"Sampled {len(sampled)} candidates for interaction generation.")

        for _, buddy in sampled.iterrows():
            score = compatibility_score(user, buddy)
            action = decide_like(score)

            event = {
                "user_id": str(user["id_number"]),
                "buddy_id": str(buddy["id_number"]),
                "action": action,
                "timestamp": datetime.now()
            }
            events_to_insert.append(event)

        total_events_generated += len(sampled)

        # Optional: print total events generated so far every 100 users processed
        if (i + 1) % 100 == 0:
            print(f"Total events generated after {i+1} users: {total_events_generated}")

    print(f"\nTotal events generated: {total_events_generated}")

    if events_to_insert:
        print(f"Inserting {len(events_to_insert)} events into MongoDB...")
        try:
            await events_collection.insert_many(events_to_insert)
            print("Insert complete.")
        except Exception as e:
            print(f"Error inserting events: {e}")

# Run
if __name__ == "__main__":
    asyncio.run(populate_events())
