from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime


class UserProfile(BaseModel):
    age: int
    full_name: str
    id_number: int 
    gender: str
    height: int
    weight: int
    daily_calories_intake: int
    resting_heart_rate: int
    VO2_max: float
    body_fat: float

    class Config:
        validate_by_name = True  # Pydantic v2 replacement for allow_population_by_field_name
        json_encoders = {ObjectId: str}  # Convert ObjectId to string


# Model for Workout
class Workout(BaseModel):
    id_number: int
    workout_type: str
    # workout_intensity: str
    # duration: int  # in minutes

# Model for Exercises
class Exercise(BaseModel):
    exercise_id: int
    name: str
    description: str
    difficulty: str
    duration: int  # in minutes

class WorkoutLog(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: int  # MongoDB stores user_id as an int
    age: int
    gender: str
    height: int
    weight: int
    workout_type: str
    workout_duration_in_minutes: int  # Keep the name as in MongoDB
    calories_burned: int
    heart_rate: int
    steps_taken: int
    distance_in_km: float
    workout_intensity: str
    sleep_hours: float
    water_intake_in_liters: float
    daily_calories_intake: int
    resting_heart_rate: int
    VO2_max: float
    body_fat: float
    mood_before_workout: str
    mood_after_workout: str

    class Config:
        validate_by_name = True  # Pydantic v2 replacement for allow_population_by_field_name
        json_encoders = {ObjectId: str}  # Convert ObjectId to string

    class Config:
        validate_by_name = True
        json_encoders = {ObjectId: str}  # Convert ObjectId to string


class SimilarUsersResponse(BaseModel):
    distances: List[float]
    id_numbers: List[int]
    similar_users: List[Dict]


class WorkoutRecommendation(BaseModel):
    recommended_workouts: List[Dict]
    confidence_score: float


class UserEvent(BaseModel):
    user_id: str
    buddy_id: str
    action: str  # "like" or "dislike"
    timestamp: datetime = datetime.utcnow()