from fastapi import APIRouter, HTTPException
from app.models import UserProfile, Workout
from app.database import users_collection, workout_collection
from bson import ObjectId

router = APIRouter()

# Route to create a new user
@router.post("/users", response_model=UserProfile)
async def create_user(user: UserProfile):
    user_dict = user.model_dump(exclude={"id"})  # Exclude "id" because MongoDB generates it
    result = await users_collection.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)  # Convert ObjectId to string
    return user_dict

# Route to create a new workout entry
@router.post("/workouts", response_model=Workout)
async def create_workout(workout: Workout):
    try:
        print(f"Received workout data: {workout.model_dump()}")
        
        # Find the user document to get its _id
        user = await users_collection.find_one({"id_number": workout.id_number})
        print(f"Found user: {user}")
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create workout document with the same _id as the user
        workout_dict = workout.model_dump()
        workout_dict["_id"] = user["_id"]  # Use the same _id as the user
        print(f"Created workout dict: {workout_dict}")
        
        # Use replace_one with upsert=True to either update or insert
        result = await workout_collection.replace_one(
            {"id_number": workout.id_number},  # Use id_number in the query
            workout_dict,
            upsert=True
        )
        print(f"Replace result: {result.raw_result}")
        
        return workout_dict
    except Exception as e:
        print(f"Error in create_workout: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Route to get a user by ID
@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user
    raise HTTPException(status_code=404, detail="User not found")

