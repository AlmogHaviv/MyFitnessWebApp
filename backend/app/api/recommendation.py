from train_model import build_interaction_matrix, recommend_buddies, train_matrix_factorization_model
from fastapi import APIRouter, HTTPException
from app.models import SimilarUsersResponse, WorkoutRecommendation, UserProfile, UserEvent
from app.database import users_collection, events_collection, workout_collection
import pandas as pd
from user_recommender import UserRecommender
import logging
from datetime import datetime

router = APIRouter()

@router.post("/similar-users", response_model=SimilarUsersResponse)
async def find_similar_users(user_profile: UserProfile) -> SimilarUsersResponse:
    """
    Find similar users based on fitness and health metrics using KNN,
    then filter by workout type preference
    """
    try:
        # Log received data
        print("Received user profile:", user_profile.model_dump())
        
        user_recommender = UserRecommender()
        user_recommender.load_model() 
        
        # Convert Pydantic model to dict and keep only the required fields
        profile_dict = {
            'age': user_profile.age,
            'id_number': user_profile.id_number,
            'full_name': user_profile.full_name,
            'weight': user_profile.weight,
            'gender': user_profile.gender,
            'height': user_profile.height,
            'daily_calories_intake': user_profile.daily_calories_intake,
            'resting_heart_rate': user_profile.resting_heart_rate,
            'VO2_max': user_profile.VO2_max,
            'body_fat': user_profile.body_fat
        }
        
        # Find similar users using the recommender (get 10 users)
        distances, id_numbers = user_recommender.find_similar_users(profile_dict)

        # Remove the user from the list of similar users (avoid self-similarity)
        id_numbers_filtered = [
            id_num for id_num in id_numbers if id_num != user_profile.id_number
        ]
        distances_filtered = [
            dist for id_num, dist in zip(id_numbers, distances) if id_num != user_profile.id_number
        ]

        # Update id_numbers and distances
        id_numbers = id_numbers_filtered
        distances = distances_filtered
        
        # Get the user's preferred workout type
        user_workout = await workout_collection.find_one({"id_number": user_profile.id_number})
        preferred_workout = user_workout["workout_type"] if user_workout else None
        print(f"Preferred workout: {preferred_workout}")
        
        # Get workout types for all similar users
        similar_users_workouts = {}
        async for workout in workout_collection.find({"id_number": {"$in": id_numbers}}):
            similar_users_workouts[workout["id_number"]] = workout["workout_type"]
        
        # If user has no workout preference, just return the top 5 similar users
        if not preferred_workout:
            final_id_numbers = id_numbers[:5]
            final_distances = distances[:5]
        else:
            # Separate users by workout type preference
            same_workout_users = []
            different_workout_users = []
            
            for id_num, distance in zip(id_numbers, distances):
                user_workout_type = similar_users_workouts.get(id_num)
                if user_workout_type == preferred_workout:
                    same_workout_users.append((id_num, distance))
                else:
                    different_workout_users.append((id_num, distance))
            
            # Sort both lists by distance (ascending)
            same_workout_users.sort(key=lambda x: x[1])
            print(f"Same workout users: {same_workout_users}")
            different_workout_users.sort(key=lambda x: x[1])
            print(f"Different workout users: {different_workout_users}")
            
            # Combine the lists, prioritizing same workout type users
            final_users = []
            final_distances = []
            final_id_numbers = []
            
            # Add same workout type users first (up to 5)
            for id_num, distance in same_workout_users[:5]:
                final_users.append(id_num)
                final_distances.append(distance)
                final_id_numbers.append(id_num)
            
            # If we don't have 5 users yet, add different workout type users
            if len(final_users) < 5:
                print(f"Adding different workout type users: {different_workout_users}")
                remaining_slots = 5 - len(final_users)
                for id_num, distance in different_workout_users[:remaining_slots]:
                    final_users.append(id_num)
                    final_distances.append(distance)
                    final_id_numbers.append(id_num)
        
        # Fetch similar users' data from MongoDB using the id numbers
        # Fetch all relevant users
        user_docs = {}
        cursor = users_collection.find({"id_number": {"$in": final_id_numbers}})
        async for user in cursor:
            if "_id" in user:
                del user["_id"]
            user["workout_type"] = similar_users_workouts.get(user["id_number"], "Unknown")
            user_docs[user["id_number"]] = user

        # Reorder users to match final_id_numbers
        similar_users_data = [user_docs[id_num] for id_num in final_id_numbers if id_num in user_docs]
        
        if not similar_users_data:
            raise HTTPException(status_code=404, detail="No similar users found")
        
        print(f"Final similar users data: {similar_users_data}")
        
        return SimilarUsersResponse(
            distances=final_distances,
            id_numbers=final_id_numbers,
            similar_users=similar_users_data
        )

    except Exception as e:
        print(f"Error in find_similar_users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/log-event")
async def log_event(event: UserEvent):
    """
    Log a like/dislike event from the frontend.
    """
    try:
        
        event_data = event.dict()
        event_data["timestamp"] = datetime.utcnow()  # Ensure the timestamp is in UTC
        print("Received event:", event_data)

        # Insert the event into the database:
        result = await events_collection.insert_one(event_data)
        return {"message": "Event logged successfully", "event_id": str(result.inserted_id)}

    except Exception as e:
        print("Error logging event:", str(e))
        raise HTTPException(status_code=500, detail="Failed to log event")

@router.get("/recommend-buddies/{user_id}")
async def recommend_buddies_endpoint(user_id: str):
    """
    Recommend buddies for a given user.
    """
    try:
        # Fetch events and build the interaction matrix
        events_df = pd.DataFrame(list(events_collection.find({})))
        sparse_matrix, user_index, buddy_index = build_interaction_matrix(events_df)

        # Train the model
        svd, user_factors, buddy_factors = train_matrix_factorization_model(sparse_matrix)

        # Make predictions
        recommended_buddies = recommend_buddies(user_id, user_factors, buddy_factors, user_index, buddy_index, top_n=10)
        return {"recommended_buddies": recommended_buddies.tolist()}

    except Exception as e:
        print("Error recommending buddies:", str(e))
        raise HTTPException(status_code=500, detail="Failed to recommend buddies")
