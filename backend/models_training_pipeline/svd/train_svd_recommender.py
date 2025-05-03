from models_training_pipeline.svd.SVDPreprocessor import SVDPreprocessor
from backend.models_training_pipeline.svd.svd_recommender import SVDRecommender
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import asyncio

# Step 1: Load raw event data from Mongo or a file
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


async def main():
    raw_events = await load_events_from_mongo()

    # Step 2: Preprocess
    preprocessor = SVDPreprocessor(raw_events)
    train_df, val_df = preprocessor.split_train_validation()
    interaction_matrix, user_index, buddy_index = preprocessor.build_interaction_matrix()

    # Step 3: Train model
    recommender = SVDRecommender(n_components=20)
    recommender.train(interaction_matrix, user_index, buddy_index)

    # Step 4: Evaluate
    loss = recommender.evaluate(val_df)
    print(f"Validation MSE: {loss:.4f}")

    # Step 5: Save model
    recommender.save("svd_model")


if __name__ == "__main__":
    asyncio.run(main())

