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


# Main
async def main():
    raw_events = await load_events_from_mongo()

    preprocessor = SVDPreprocessor(raw_events)

    # Split raw dataframe
    train_df, val_df = preprocessor.split_train_validation()

    # Build matrix only from training set
    interaction_matrix, user_index, buddy_index = preprocessor.build_interaction_matrix(train_df)

    # Train the model
    recommender = SVDRecommender(n_components=20)
    recommender.train(interaction_matrix, user_index, buddy_index)

    # Evaluate on validation data
    metrics = recommender.evaluate(val_df)

    print("Validation Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")

    recommender.save("svd_model")

if __name__ == "__main__":
    asyncio.run(main())
