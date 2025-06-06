from fastapi import APIRouter, HTTPException, Query
from app.models import UserProfile, WorkoutRecommendationEvent
from app.database import users_collection, workout_collection
from models_training_pipeline.workout_recommender import WorkoutRecommender

router = APIRouter()

@router.post("/best-workout-recommendation", response_model=WorkoutRecommendationEvent)
async def find_best_workout_recommendation(
    user_profile: UserProfile,
    query: str = Query(..., description="User's workout goal or query")
) -> WorkoutRecommendationEvent:
    """
    Recommend the best workout(s) for a user based on their profile and a query.
    This is a placeholder endpoint; the recommendation logic will be implemented later.
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
        
        workout_recommender = WorkoutRecommender(profile_dict, query)

        return WorkoutRecommendationEvent(
            workout_urls_and_explanations=workout_recommender.workout_urls_and_explanations(),
            relevant_equipment=workout_recommender.relevant_equipment()
        )

    except Exception as e:
        print(f"Error in find_best_workout_recommendation: {e}")
        raise HTTPException(status_code=500, detail=str(e))