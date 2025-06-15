from fastapi import APIRouter, HTTPException
from app.models import SimilarUsersRerankerResponse, UserProfile
from app.database import users_collection, workout_collection
from models_training_pipeline.knn.user_recommender import UserRecommender
from models_training_pipeline.xgboosting.xgb_reranker import XGBReranker
from models_training_pipeline.xgboosting.data_preprocessor import DataPreprocessor
import pandas as pd

router = APIRouter()

# Global model instances to avoid reloading on each request
user_recommender = None
xgb_reranker = None

def load_models():
    """Load all models once at startup"""
    global user_recommender, xgb_reranker
    
    if user_recommender is None:
        user_recommender = UserRecommender()
        user_recommender.load_model()
        
    if xgb_reranker is None:
        xgb_reranker = XGBReranker()
        xgb_reranker.load("models/xgb_reranker_model.json")

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

@router.post("/similar-users-reranked", response_model=SimilarUsersRerankerResponse)
async def find_similar_users_with_reranking(user_profile: UserProfile) -> SimilarUsersRerankerResponse:
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
        
        # Step 4: Get top 25 recommendations
        top_candidates = ranked_candidate_ids[:25]
        
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
        
        final_id_numbers = [user['id_number'] for user in similar_users_data]
        
        return SimilarUsersRerankerResponse(
            id_numbers=final_id_numbers,
            similar_users=similar_users_data
        )

    except Exception as e:
        print(f"Error in find_similar_users_with_reranking: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 