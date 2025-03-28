from fastapi import APIRouter
from app.models import Workout

router = APIRouter()

# Route to fetch all available workouts
@router.get("/workouts")
def get_workouts():
    # Ideally, this would fetch workouts from a database
    workouts = [
        Workout(workout_id=1, name="Push-ups", description="Upper body workout", difficulty="Medium", duration=10),
        Workout(workout_id=2, name="Squats", description="Lower body workout", difficulty="Medium", duration=15),
    ]
    return workouts
