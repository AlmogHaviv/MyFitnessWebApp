from fastapi import APIRouter
from app.models import Workout, User
from typing import List

router = APIRouter()

# Route to get workout recommendations for a user based on their profile
@router.post("/recommendations")
def get_recommendations(user: User) -> List[Workout]:
    # Placeholder logic for generating recommendations
    # For now, we’ll just return all workouts, but this will later use a machine learning model
    recommended_workouts = [
        Workout(workout_id=1, name="Push-ups", description="Upper body workout", difficulty="Medium", duration=10),
        Workout(workout_id=2, name="Squats", description="Lower body workout", difficulty="Medium", duration=15),
    ]
    return recommended_workouts
