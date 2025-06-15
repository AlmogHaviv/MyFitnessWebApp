from fastapi import APIRouter, HTTPException
from app.database import users_collection, workout_collection
from models_training_pipeline.svd.svd_recommender import SVDRecommender
import pandas as pd

router = APIRouter()

@router.get("/recommend-buddies/{user_id}")
async def recommend_buddies_endpoint(user_id: str):
    """
    Recommend buddies for a given user based on activity and fetch their data from MongoDB,
    including their workout type.
    """
    try:
        # Load the SVD recommender model
        svd_recommender = SVDRecommender()
        svd_recommender.load("models/svd_model")

        # Get the top 5 recommended buddy IDs
        recommended_buddy_ids = svd_recommender.recommend(user_id, top_n=5)
        
        # If user is not in the dataset, return empty list
        if recommended_buddy_ids is None:
            print(f"User {user_id} not found in SVD training set")
            return {
                "recommended_buddies": []
            }
            
        print(f"Recommended buddy IDs: {recommended_buddy_ids}")

        # Ensure IDs are in the correct format (e.g., integers if stored as integers in MongoDB)
        if isinstance(recommended_buddy_ids, pd.Index):
            recommended_buddy_ids = recommended_buddy_ids.tolist()
        recommended_buddy_ids = [int(id_num) for id_num in recommended_buddy_ids]

        # Fetch recommended buddies' data from MongoDB
        buddy_docs = {}
        cursor = users_collection.find({"id_number": {"$in": recommended_buddy_ids}})
        async for buddy in cursor:
            if "_id" in buddy:
                del buddy["_id"]  # Remove MongoDB's internal ID field
            buddy_docs[buddy["id_number"]] = buddy

        # Fetch workout types for the recommended buddies
        workout_types = {}
        async for workout in workout_collection.find({"id_number": {"$in": recommended_buddy_ids}}):
            workout_types[workout["id_number"]] = workout["workout_type"]

        # Reorder the fetched buddies to match the order of recommended_buddy_ids
        recommended_buddies_data = []
        for id_num in recommended_buddy_ids:
            if id_num in buddy_docs:
                buddy = buddy_docs[id_num]
                buddy["workout_type"] = workout_types.get(id_num, "Unknown")  # Add workout type
                recommended_buddies_data.append(buddy)

        if not recommended_buddies_data:
            print(f"No recommended buddies found for user {user_id}")
            return {
                "recommended_buddies": []
            }

        print(f"Final recommended buddies data: {recommended_buddies_data}")

        return {
            "recommended_buddies": recommended_buddies_data
        }

    except Exception as e:
        print(f"Error in recommend_buddies_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 