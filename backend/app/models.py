from pydantic import BaseModel
from typing import List

# Model for the User profile
class User(BaseModel):
    user_id: int
    age: int
    fitness_level: str
    preferences: List[str]

# Model for Workout
class Workout(BaseModel):
    workout_id: int
    name: str
    description: str
    difficulty: str
    duration: int  # in minutes

# Model for storing User's workout log (feedback on workouts)
class WorkoutLog(BaseModel):
    user_id: int
    workout_id: int
    liked: bool
    feedback: str
