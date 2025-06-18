from fastapi import APIRouter, HTTPException, Query
from app.models import UserProfile, WorkoutRecommendationEvent
from app.database import users_collection, workout_collection
from models_training_pipeline.llm_workout_recs.llm_model_open_ai_api import WorkoutRecommender

router = APIRouter()

@router.post("/best-workout-recommendation", response_model=WorkoutRecommendationEvent)
async def find_best_workout_recommendation(
    user_profile: UserProfile,
    query: str = Query(..., description="User's workout goal or query")
) -> WorkoutRecommendationEvent:
    """
    Recommend the best workout(s) for a user based on their profile and a query.
    Returns a list of workout recommendations with URLs, explanations, and required equipment.
    """
    try:
        # Log received data for debugging
        print("Received user profile:", user_profile.model_dump())
        
        # Convert Pydantic model to dict and keep only the required fields
        profile_dict = {
            'age': user_profile.age,
            'weight': user_profile.weight,
            'gender': user_profile.gender,
            'height': user_profile.height,
            'daily_calories_intake': user_profile.daily_calories_intake,
            'resting_heart_rate': user_profile.resting_heart_rate,
            'VO2_max': user_profile.VO2_max,
            'body_fat': user_profile.body_fat
        }
        
        # Initialize the recommender and get recommendations
        workout_recommender = WorkoutRecommender(profile_dict, query)
        recommendations = workout_recommender.workout_urls_and_explanations()

        # Create the response event
        return WorkoutRecommendationEvent(
            workout_recommendations=recommendations
        )

    except Exception as e:
        print(f"Error in find_best_workout_recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))