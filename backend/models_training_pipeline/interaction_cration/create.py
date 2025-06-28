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

# --- Heuristic scoring with adjusted weights ---
def compatibility_score(u1, u2, u1_id, u2_id, last_liked_workouts=None, debug=False):
    score = 0.0

    # 🔥 Most important: workout type and past liked types
    if u1["workout_type"] == u2["workout_type"]:
        score += 3.0

    if last_liked_workouts and u2["workout_type"] in last_liked_workouts:
        score += 2.5
        if debug:
            print(f"[+] Bonus applied: workout_type match with past likes → "
                  f"User: {u1_id} | Buddy: {u2_id} | "
                  f"Score: {score:.2f} ({u2['workout_type']})")

    # 🧬 Physiology compatibility (moderate importance)
    if abs(u1["resting_heart_rate"] - u2["resting_heart_rate"]) <= 5:
        score += 1.0
    if u1["gender"] == u2["gender"]:
        if abs(u1["body_fat"] - u2["body_fat"]) <= 5:
            score += 0.8
        if abs(u1["bmi"] - u2["bmi"]) <= 2:
            score += 0.5
    else:
        # More lenient for cross-gender matching
        if abs(u1["body_fat"] - u2["body_fat"]) <= 8:
            score += 0.8  # lower weight but more inclusive
        if abs(u1["bmi"] - u2["bmi"]) <= 3:
            score += 0.5

    # 👥 Age has small influence
    if abs(u1["age"] - u2["age"]) <= 5:
        score += 0.3

    # ⚖️ Gender — almost negligible
    if u1["gender"] == u2["gender"]:
        score += 0.1

    return score

def decide_like(score):
    if score >= 7.0:
        return "like"
    elif score >= 5.5:
        return "like" if random.random() < 0.85 else "dislike"
    elif score >= 4.0:
        return "like" if random.random() < 0.6 else "dislike"
    elif score >= 2.5:
        return "like" if random.random() < 0.25 else "dislike"
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
    users = await users_collection.find().to_list(length=None)
    for u in users:
        u.pop("_id", None)
    print(f"Loaded {len(users)} users.")

    print("Loading workouts from MongoDB...")
    workouts = await workout_collection.find().to_list(length=None)
    for w in workouts:
        w.pop("_id", None)
    print(f"Loaded {len(workouts)} workouts.")

    users_df = pd.DataFrame(users)
    workout_df = pd.DataFrame(workouts)

    print("Merging user and workout data...")
    merged_df = pd.merge(users_df, workout_df, on="id_number", how="left")
    merged_df.set_index("id_number", inplace=True)

    print("Loading recommendation model...")
    user_recommender = UserRecommender()
    user_recommender.load_model()
    print("Model loaded.")

    events_to_insert = []
    total_events_generated = 0

    print("Generating interactions...")
    for i, (user_id, user) in enumerate(merged_df.iterrows()):
        print(f"\nProcessing user {i+1}/{len(merged_df)} - ID: {user_id}")
        profile_dict = {
            'age': user['age'],
            'id_number': user_id,
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
            print(f"Error finding similar users for ID {user_id}: {e}")
            continue

        candidates = merged_df.loc[merged_df.index.isin(similar_ids)]
        candidates = candidates[candidates.index != user_id]

        sample_size = min(75, len(candidates))
        if sample_size == 0:
            print(f"No candidates to sample for user {user_id}. Skipping...")
            continue

        sampled = candidates.sample(n=sample_size, random_state=42)
        print(f"Sampled {len(sampled)} candidates for interaction generation.")

        # Initialize recent likes list for this user (just for this run)
        recent_workouts = []

        for buddy_id, buddy in sampled.iterrows():
            # Compute compatibility with current context of recent likes
            score = compatibility_score(user, buddy,user_id, buddy_id, last_liked_workouts=set(recent_workouts), debug=False)
            action = decide_like(score)

            # Save event
            event = {
                "user_id": str(user_id),
                "buddy_id": str(buddy_id),
                "action": action,
                "timestamp": datetime.now()
            }
            events_to_insert.append(event)

            # Update context cache if it's a like
            if action == "like":
                workout_type = buddy["workout_type"]
                recent_workouts.insert(0, workout_type)
                recent_workouts = recent_workouts[:3]  # Keep only last 3

        total_events_generated += len(sampled)

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
