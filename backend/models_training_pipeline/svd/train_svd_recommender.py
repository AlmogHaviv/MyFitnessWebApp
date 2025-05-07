from SVDPreprocessor import SVDPreprocessor
from svd_recommender import SVDRecommender
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import asyncio
import pandas as pd
from collections import defaultdict

# Step 1: Load raw event data from Mongo
async def load_events_from_mongo():
    uri = "mongodb+srv://almoghaviv:almoghaviv@workoutapp.e0r5zoq.mongodb.net/?retryWrites=true&w=majority&appName=workoutApp"
    client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))
    db = client.workoutApp
    events_collection = db.events

    events = []
    async for event in events_collection.find():
        if "_id" in event:
            del event["_id"]
        events.append(event)
    return events

# Precision@K
def precision_at_k_svd(recommender, val_df, user_index, buddy_index, k=10):
    user_true_positives = defaultdict(set)
    for _, row in val_df.iterrows():
        user_true_positives[row['user_id']].add(row['buddy_id'])

    precisions = []
    for user_id in user_true_positives:
        if user_id not in user_index:
            continue
        try:
            user_idx = user_index.get_loc(user_id)
        except KeyError:
            continue

        all_scores = {}
        for buddy_id in buddy_index:
            if buddy_id == user_id:
                continue
            try:
                buddy_idx = buddy_index.get_loc(buddy_id)
                all_scores[buddy_id] = recommender.predict(user_idx, buddy_idx)
            except KeyError:
                continue

        top_k_buddies = sorted(all_scores, key=all_scores.get, reverse=True)[:k]
        true_positives = user_true_positives[user_id]
        hits = len(set(top_k_buddies) & true_positives)
        precisions.append(hits / k)

    return sum(precisions) / len(precisions) if precisions else 0.0

# Main
async def main():
    raw_events = await load_events_from_mongo()

    preprocessor = SVDPreprocessor(raw_events)
    train_df, val_df = preprocessor.split_train_validation()
    interaction_matrix, user_index, buddy_index = preprocessor.build_interaction_matrix()

    recommender = SVDRecommender(n_components=20)
    recommender.train(interaction_matrix, user_index, buddy_index)

    loss = recommender.evaluate(val_df)
    print(f"Validation MSE: {loss:.4f}")

    p_at_10 = precision_at_k_svd(recommender, val_df, user_index, buddy_index, k=10)
    print(f"Validation Precision@10: {p_at_10:.4f}")

    recommender.save("svd_model")

if __name__ == "__main__":
    asyncio.run(main())
