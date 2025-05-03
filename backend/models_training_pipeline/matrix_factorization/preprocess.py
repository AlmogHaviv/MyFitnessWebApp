from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import asyncio
import pandas as pd
import random
from datetime import datetime

async def load_events_from_mongo():
    """
    Load events from MongoDB events collection
    """

    # MongoDB URI
    uri = "mongodb+srv://almoghaviv:almoghaviv@workoutapp.e0r5zoq.mongodb.net/?retryWrites=true&w=majority&appName=workoutApp"

    # Create a new asynchronous client and connect to the server
    client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))

    # Define the database and collections
    db = client.workoutApp
    events_collection = db.events

    events = []
    async for event in events_collection.find():
        if "_id" in event:
            del event["_id"]  # Remove MongoDB's _id field
        events.append(event)
    return events

def encode_ids(events):
    users = set()
    for e in events:
        users.add(e["user_id"])
        users.add(e["buddy_id"])
    
    id_to_index = {uid: idx for idx, uid in enumerate(sorted(users))}
    index_to_id = {idx: uid for uid, idx in id_to_index.items()}
    return id_to_index, index_to_id

def build_liked_disliked_pairs(events, id_to_index):
    liked = []
    disliked = []

    for e in events:
        uid = id_to_index[e["user_id"]]
        bid = id_to_index[e["buddy_id"]]
        if e["action"] == "like":
            liked.append((uid, bid))
        elif e["action"] == "dislike":
            disliked.append((uid, bid))
    
    return liked, disliked

def compatibility_score(u1, u2):
    score = 0
    if u1["workout_type"] == u2["workout_type"]:
        score += 2
    if abs(u1["age"] - u2["age"]) <= 5:
        score += 1
    if u1["gender"] == u2["gender"]:
        score += 0.5
    if abs(u1["VO2_max"] - u2["VO2_max"]) <= 5:
        score += 0.5
    if abs(u1["body_fat"] - u2["body_fat"]) <= 5:
        score += 0.5
    return score

def decide_like(score):
    prob = 0
    if score >= 3.5:
        prob = 0.85
    elif score >= 2.0:
        prob = 0.65
    elif score >= 1.0:
        prob = 0.4
    else:
        prob = 0.2
    return "like" if random.random() < prob else "dislike"

async def populate_events():
    """
    Populate the events collection with simulated user interactions
    """
    # MongoDB URI
    uri = "mongodb+srv://almoghaviv:almoghaviv@workoutapp.e0r5zoq.mongodb.net/?retryWrites=true&w=majority&appName=workoutApp"

    # Create a new asynchronous client and connect to the server
    client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))

    # Define the database and collections
    db = client.workoutApp
    users_collection = db.users
    workout_collection = db.workout
    events_collection = db.events

    # 1. Load users and workout data into DataFrames
    users_data = []
    async for user in users_collection.find():
        if "_id" in user:
            del user["_id"]
        users_data.append(user)
    users_df = pd.DataFrame(users_data)

    workout_data = []
    async for workout in workout_collection.find():
        if "_id" in workout:
            del workout["_id"]
        workout_data.append(workout)
    workout_df = pd.DataFrame(workout_data)

    # Merge users and workout data
    merged_df = pd.merge(users_df, workout_df, on='id_number', how='left')

    # 2. Generate events for each user
    events_to_insert = []
    for _, user in merged_df.iterrows():
        # Randomly select 20 other users
        other_users = merged_df[merged_df['id_number'] != user['id_number']].sample(n=min(20, len(merged_df)-1))
        
        for _, other_user in other_users.iterrows():
            # Calculate compatibility score
            score = compatibility_score(user, other_user)
            
            # Decide if it's a like or dislike
            action = decide_like(score)
            
            # Create event document
            event = {
                "user_id": str(user['id_number']),
                "buddy_id": str(other_user['id_number']),
                "action": action,
                "timestamp": datetime.now()
            }
            events_to_insert.append(event)

    # Insert all events into MongoDB
    if events_to_insert:
        await events_collection.insert_many(events_to_insert)
        print(f"Successfully inserted {len(events_to_insert)} events")

async def main():
    await  populate_events()
    # events = await load_events_from_mongo()
    # id_to_index, index_to_id = encode_ids(events)
    # liked_pairs, disliked_pairs = build_liked_disliked_pairs(events, id_to_index)

    # print("Sample liked:", liked_pairs[:5])
    # print("Sample disliked:", disliked_pairs[:5])
    # print(f"Total users: {len(id_to_index)}")

    # # Optionally save for reuse
    # with open("id_mapping.json", "w") as f:
    #     json.dump(index_to_id, f)

if __name__ == "__main__":
    asyncio.run(main())

