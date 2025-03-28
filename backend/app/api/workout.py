from fastapi import APIRouter
from app.models import Workout
import pandas as pd

router = APIRouter()

# Load the dataset from the CSV file
workout_data = pd.read_csv("../data/workout_fitness_tracker_data.csv")


# Route to fetch all available workouts
@router.get("/workouts")
def get_rec_workout(customer_id: int):
    # Until we will have recs dataset ready, fetches workout from the input dataset to the ML Model
    #
    # Filter the dataset for the given customer ID
    customer_workouts = workout_data[workout_data['User ID'] == customer_id]

    # If no data is found for the customer_id, return an empty list or a suitable response
    if customer_workouts.empty:
        return []

    # Convert the relevant columns to the required format (Workout objects)
    workouts = [
        Workout(
            workout_type=row['Workout Type'],
            workout_intensity=row['Workout Intensity'],
            duration=row['Workout Duration (mins)']
        )
        for index, row in customer_workouts.iterrows()
    ]

    return workouts
