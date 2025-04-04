from fastapi import APIRouter, HTTPException
from app.models import SimilarUsersResponse, WorkoutRecommendation, UserProfile
from app.database import users_collection
import pandas as pd
from user_recommender import UserRecommender

router = APIRouter()

@router.post("/similar-users", response_model=SimilarUsersResponse)
async def find_similar_users(user_profile: UserProfile) -> SimilarUsersResponse:
    """
    Find similar users based on fitness and health metrics using KNN
    """
    try:
        user_recommender = UserRecommender()
        user_recommender.load_model() 
        # Convert Pydantic model to dict and keep only the required fields
        profile_dict = {
            'age': user_profile.age,
            'id_number': user_profile.id_number,
            'full_name': user_profile.full_name,
            'weight': user_profile.weight,
            'gender': user_profile.gender,
            'height': user_profile.height,
            'daily_calories_intake': user_profile.daily_calories_intake,
            'resting_heart_rate': user_profile.resting_heart_rate,
            'VO2_max': user_profile.VO2_max,
            'body_fat': user_profile.body_fat
        }
        
        print(type(user_recommender))
        # Find similar users using the recommender
        distances, id_numbers = user_recommender.find_similar_users(profile_dict)
        print(distances)
        print(id_numbers)
        
        # Fetch similar users' data from MongoDB using the id numbers
        similar_users_data = []
        cursor = users_collection.find({"id_number": {"$in": id_numbers}})
        async for user in cursor:
            # Remove MongoDB _id field if present
            if "_id" in user:
                del user["_id"]
            similar_users_data.append(user)
        
        if not similar_users_data:
            raise HTTPException(status_code=404, detail="No similar users found")
        
        return SimilarUsersResponse(
            distances=distances.tolist(),
            id_numbers=id_numbers,
            similar_users=similar_users_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
