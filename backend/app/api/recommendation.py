from fastapi import APIRouter, HTTPException
from app.models import SimilarUsersResponse, UserProfile, UserEvent
from app.database import users_collection, events_collection, workout_collection
import pandas as pd
import numpy as np
from models_training_pipeline.knn.user_recommender import UserRecommender
from models_training_pipeline.xgboosting.xgb_reranker import XGBReranker
from models_training_pipeline.xgboosting.data_preprocessor import DataPreprocessor
from models_training_pipeline.svd.svd_recommender import SVDRecommender
from datetime import datetime


router = APIRouter()

# Global model instances to avoid reloading on each request
user_recommender = None
xgb_reranker = None
svd_recommender = None

def load_models():
    """Load all models once at startup"""
    global user_recommender, xgb_reranker, svd_recommender
    
    if user_recommender is None:
        user_recommender = UserRecommender()
        user_recommender.load_model()
        
    if xgb_reranker is None:
        xgb_reranker = XGBReranker()
        xgb_reranker.load("models/xgb_reranker_model.json")
        
    if svd_recommender is None:
        svd_recommender = SVDRecommender()
        svd_recommender.load("models/svd_model")



async def get_raw_data_for_user_and_candidates(user_profile: dict, candidate_ids: list[str]) -> pd.DataFrame:
    """
    Fetch raw data needed for feature generation from MongoDB
    Returns a DataFrame with the required columns for DataPreprocessor
    Includes the user profile data even if they're not in the database yet
    """
    user_id = user_profile['id_number']
    
    # Convert string IDs to integers if needed
    try:
        candidate_ids_int = [int(cid) for cid in candidate_ids]
        user_id_int = int(user_id)
    except ValueError:
        candidate_ids_int = candidate_ids
        user_id_int = user_id
    
    # Fetch candidate data from MongoDB
    users_cursor = users_collection.find({"id_number": {"$in": candidate_ids_int}})
    users_data = []
    async for user in users_cursor:
        user_dict = dict(user)
        user_dict.pop("_id", None)
        users_data.append(user_dict)
    
    # Fetch workout data for candidates
    workouts_cursor = workout_collection.find({"id_number": {"$in": candidate_ids_int}})
    workout_data = {}
    async for workout in workouts_cursor:
        workout_data[workout["id_number"]] = workout.get("workout_type", "Unknown")
    
    # Add workout types to candidate data
    for user in users_data:
        user["workout_type"] = workout_data.get(user["id_number"], "Unknown")
    
    # Create user data from profile (in case user is not in database yet)
    user_data = {
        'id_number': user_profile['id_number'],
        'full_name': user_profile['full_name'],
        'age': user_profile['age'],
        'gender': user_profile['gender'],
        'height': user_profile['height'],
        'weight': user_profile['weight'],
        'daily_calories_intake': user_profile['daily_calories_intake'],
        'resting_heart_rate': user_profile['resting_heart_rate'],
        'VO2_max': user_profile['VO2_max'],
        'body_fat': user_profile['body_fat'],
        'bmi': user_profile['bmi'],
        'workout_type': user_profile.get('workout_type', 'Unknown')  # Default if not provided
    }
    
    # Check if user already exists in the fetched data, if not add them
    user_exists = any(user['id_number'] == user_id_int for user in users_data)
    if not user_exists:
        users_data.append(user_data)
    
    return pd.DataFrame(users_data)

def create_features_for_candidates(user_id: str, candidate_ids: list[str], raw_data: pd.DataFrame) -> pd.DataFrame:
    """Generate features for user-candidate pairs"""
    return DataPreprocessor.generate_features_for_pairs(user_id, candidate_ids, raw_data)

def get_candidates(user_profile: dict, k: int = 150) -> list[str]:
    """Get candidate users from KNN model"""
    global user_recommender
    if user_recommender is None:
        load_models()
    
    _, candidate_ids = user_recommender.find_similar_users(user_profile, k=k)
    return candidate_ids

def rerank_candidates(user_profile: dict, candidate_ids: list[str], raw_data: pd.DataFrame) -> list[str]:
    """Rerank candidates using XGBoost model"""
    global xgb_reranker
    if xgb_reranker is None:
        load_models()
    
    try:
        # Ensure user_profile has workout_type if needed
        if 'workout_type' not in user_profile:
            user_profile['workout_type'] = 'Unknown'
            
        features = create_features_for_candidates(user_profile['id_number'], candidate_ids, raw_data)
        
        # Drop non-feature columns that were not in training
        drop_cols = ['user_id_number', 'buddy_id_number', 'label']
        features = features.drop(columns=[col for col in drop_cols if col in features.columns])

        if features.empty:
            print("Warning: No features generated, falling back to original candidate order")
            return candidate_ids[:10]  # Return first 10 candidates as fallback

        # Match the order of columns as in training
        expected_cols = xgb_reranker.model.feature_names_in_.tolist()
        
        # Ensure all expected columns are present
        missing_cols = [col for col in expected_cols if col not in features.columns]
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols}, falling back to original order")
            return candidate_ids[:10]
            
        features = features[expected_cols]

        scores = xgb_reranker.predict_proba(features)
        scored_df = pd.DataFrame({
            'buddy_id': candidate_ids,
            'score': scores
        })
        ranked_candidates = scored_df.sort_values(by='score', ascending=False)['buddy_id'].tolist()
        return ranked_candidates
        
    except Exception as e:
        print(f"Error in reranking: {e}")
        print("Falling back to original candidate order")
        return candidate_ids[:10]  # Fallback to first 10 candidates


@router.post("/similar-users-reranked", response_model=SimilarUsersResponse)
async def find_similar_users_with_reranking(user_profile: UserProfile) -> SimilarUsersResponse:
    """
    Find similar users using KNN + XGBoost reranking pipeline
    """
    try:
        # Load models
        load_models()
        
        # Log received data
        print("Received user profile:", user_profile.model_dump())
        
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
            'body_fat': user_profile.body_fat,
            'bmi': user_profile.bmi
        }
        
        # Step 1: Get candidates from KNN
        candidate_ids = get_candidates(profile_dict, k=150)
        
        # Remove the user from the candidates
        candidate_ids = [cid for cid in candidate_ids if cid != user_profile.id_number]
        
        if not candidate_ids:
            raise HTTPException(status_code=404, detail="No candidate users found")
        
        # Step 2: Get raw data for feature generation
        raw_data = await get_raw_data_for_user_and_candidates(
            profile_dict, 
            [str(cid) for cid in candidate_ids]
        )
        
        if raw_data.empty:
            raise HTTPException(status_code=404, detail="No raw data found for feature generation")
        
        # Step 3: Rerank candidates using XGBoost
        ranked_candidate_ids = rerank_candidates(profile_dict, candidate_ids, raw_data)
        
        if not ranked_candidate_ids:
            raise HTTPException(status_code=404, detail="No ranked candidates found")
        
        # Step 4: Get top 5 recommendations
        top_candidates = ranked_candidate_ids[:5]
        
        # Step 5: Fetch detailed user data for top candidates
        users_cursor = users_collection.find({"id_number": {"$in": top_candidates}})
        workouts_cursor = workout_collection.find({"id_number": {"$in": top_candidates}})

        # Build a dict of id_number -> workout_type
        workout_map = {}
        async for workout in workouts_cursor:
            workout_map[workout["id_number"]] = workout.get("workout_type", "Unknown")

        # Build the final user data list
        user_docs = {}
        async for user in users_cursor:
            user_dict = dict(user)
            user_dict.pop("_id", None)
            user_dict["workout_type"] = workout_map.get(user_dict["id_number"], "Unknown")
            user_docs[user["id_number"]] = user_dict

        # Reorder users to match ranking
        similar_users_data = [user_docs[id_num] for id_num in top_candidates if id_num in user_docs]
        
        if not similar_users_data:
            raise HTTPException(status_code=404, detail="No similar users found")
        
        print(f"Reranked similar users: {[user['id_number'] for user in similar_users_data]}")
        
        # For distances, we'll use dummy values since XGBoost provides scores instead
        # You could modify this to return actual scores if needed
        dummy_distances = [0.0] * len(similar_users_data)
        final_id_numbers = [user['id_number'] for user in similar_users_data]
        
        return SimilarUsersResponse(
            distances=dummy_distances,
            id_numbers=final_id_numbers,
            similar_users=similar_users_data
        )

    except Exception as e:
        print(f"Error in find_similar_users_with_reranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
            'body_fat': user_profile.body_fat,
            'bmi': user_profile.bmi
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
        
        event_data = event.model_dump()
        event_data["timestamp"] = datetime.now()  # Ensure the timestamp is in UTC
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
    Recommend buddies for a given user based on activity and fetch their data from MongoDB,
    including their workout type.
    """
    try:
        # Load the SVD recommender model
        svd_recommender = SVDRecommender()
        svd_recommender.load("models/svd_model")

        # Get the top 5 recommended buddy IDs
        recommended_buddy_ids = svd_recommender.recommend(user_id, top_n=5)
        
        # If user is not in the dataset, return empty list
        if recommended_buddy_ids is None:
            print(f"User {user_id} not found in SVD training set")
            return {
                "recommended_buddies": []
            }
            
        print(f"Recommended buddy IDs: {recommended_buddy_ids}")

        # Ensure IDs are in the correct format (e.g., integers if stored as integers in MongoDB)
        if isinstance(recommended_buddy_ids, pd.Index):
            recommended_buddy_ids = recommended_buddy_ids.tolist()
        recommended_buddy_ids = [int(id_num) for id_num in recommended_buddy_ids]

        # Fetch recommended buddies' data from MongoDB
        buddy_docs = {}
        cursor = users_collection.find({"id_number": {"$in": recommended_buddy_ids}})
        async for buddy in cursor:
            if "_id" in buddy:
                del buddy["_id"]  # Remove MongoDB's internal ID field
            buddy_docs[buddy["id_number"]] = buddy

        # Fetch workout types for the recommended buddies
        workout_types = {}
        async for workout in workout_collection.find({"id_number": {"$in": recommended_buddy_ids}}):
            workout_types[workout["id_number"]] = workout["workout_type"]

        # Reorder the fetched buddies to match the order of recommended_buddy_ids
        recommended_buddies_data = []
        for id_num in recommended_buddy_ids:
            if id_num in buddy_docs:
                buddy = buddy_docs[id_num]
                buddy["workout_type"] = workout_types.get(id_num, "Unknown")  # Add workout type
                recommended_buddies_data.append(buddy)

        if not recommended_buddies_data:
            print(f"No recommended buddies found for user {user_id}")
            return {
                "recommended_buddies": []
            }

        print(f"Final recommended buddies data: {recommended_buddies_data}")

        return {
            "recommended_buddies": recommended_buddies_data
        }

    except Exception as e:
        print(f"Error in recommend_buddies_endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
