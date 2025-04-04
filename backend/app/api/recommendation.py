from fastapi import APIRouter, HTTPException
from app.models import SimilarUsersResponse, WorkoutRecommendation, UserProfile
from app.database import users_collection
from typing import List, Dict
import os
from datetime import datetime
from user_recommender import UserRecommender
import pandas as pd


router = APIRouter()

# Initialize the recommenders
user_recommender = UserRecommender()

# Define model paths
workout_model_path = "backend/app/models/workout_recommender.joblib"
user_model_path = "backend/app/models/user_recommender_model.joblib"

# Load the user recommender model if it exists
if os.path.exists(user_model_path):
    user_recommender.load_model(user_model_path)  # Make sure to pass the correct path if needed

@router.get("/similar-users", response_model=SimilarUsersResponse)
async def find_similar_users(user_profile: UserProfile) -> SimilarUsersResponse:
    """
    Find similar users based on fitness and health metrics using KNN
    """
    try:
        # Convert Pydantic model to dict
        profile_dict = user_profile.model_dump()
        
        # Find similar users using the recommender
        distances, id_numbers = user_recommender.find_similar_users(profile_dict)
        
        # Load data from MongoDB for the similar users in one batch query
        cursor = users_collection.find({"id_number": {"$in": id_numbers}})
        similar_users_data = []
        async for user_data in cursor:
            # Convert ObjectId to string for JSON serialization
            similar_users_data.append(user_data)

        # Return the result
        return SimilarUsersResponse(
            distances=distances.tolist(),  # Convert distances to list for JSON response
            id_numbers=id_numbers.tolist(),  # Convert indices to list
            similar_users=similar_users_data  # List of similar users from MongoDB
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
