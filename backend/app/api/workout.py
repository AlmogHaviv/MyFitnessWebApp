from fastapi import APIRouter, HTTPException
from app.models import WorkoutLog
from app.database import user_and_feelings_collection

router = APIRouter()

# Route to fetch workouts for a given user from MongoDB
@router.get("/workouts")
async def get_rec_workout(customer_id: str):
    try:
        # Query MongoDB for workouts of this customer
        customer_workouts = await user_and_feelings_collection.find({"user_id": int(customer_id)}).to_list(length=100)

        if not customer_workouts:
            raise HTTPException(status_code=404, detail="No workouts found for this user")

        # Convert MongoDB documents to list of WorkoutLog models
        workouts = [
            WorkoutLog(
                id=str(workout["_id"]),
                user_id=workout["user_id"],
                age=workout["age"],
                gender=workout["gender"],
                height=workout["height"],
                weight=workout["weight"],
                workout_type=workout["workout_type"],
                workout_duration_in_minutes=workout["workout_duration_in_minutes"],
                calories_burned=workout["calories_burned"],
                heart_rate=workout["heart_rate"],
                steps_taken=workout["steps_taken"],
                distance_in_km=workout["distance_in_km"],
                workout_intensity=workout["workout_intensity"],
                sleep_hours=workout["sleep_hours"],
                water_intake_in_liters=workout["water_intake_in_liters"],
                daily_calories_intake=workout["daily_calories_intake"],
                resting_heart_rate=workout["resting_heart_rate"],
                VO2_max=workout["VO2_max"],
                body_fat=workout["body_fat"],
                mood_before_workout=workout["mood_before_workout"],
                mood_after_workout=workout["mood_after_workout"],
            )
            for workout in customer_workouts
        ]

        return workouts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to add a new workout log for a user
@router.post("/workouts", response_model=WorkoutLog)
async def create_workout_log(workout: WorkoutLog):
    try:
        # Convert model to dictionary and remove None values
        workout_dict = workout.dict(exclude={"id"})  # MongoDB generates _id

        # Insert into MongoDB
        result = await user_and_feelings_collection.insert_one(workout_dict)

        # Assign the generated ObjectId to the response
        workout_dict["_id"] = str(result.inserted_id)

        return workout_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
