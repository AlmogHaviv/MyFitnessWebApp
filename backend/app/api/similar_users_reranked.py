from fastapi import APIRouter, HTTPException
from app.models import SimilarUsersRerankerResponse, UserProfile
from app.database import users_collection, workout_collection, events_collection
from models_training_pipeline.knn.user_recommender import UserRecommender
from models_training_pipeline.xgboosting.xgb_reranker import XGBReranker
from models_training_pipeline.xgboosting.data_preprocessor import DataPreprocessor
import pandas as pd
import traceback


router = APIRouter()

# Global model instances
user_recommender = None
xgb_reranker = None

def load_models():
    global user_recommender, xgb_reranker
    if user_recommender is None:
        user_recommender = UserRecommender()
        user_recommender.load_model()
    if xgb_reranker is None:
        xgb_reranker = XGBReranker()
        xgb_reranker.load("models/xgb_reranker_model.json")

async def get_raw_data_for_user_and_candidates(user_profile: dict, candidate_ids: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    user_id = user_profile['id_number']
    try:
        candidate_ids_int = [int(cid) for cid in candidate_ids]
        user_id_int = int(user_id)
        candidate_ids_int.append(user_id_int)
    except ValueError:
        candidate_ids_int = candidate_ids
        user_id_int = user_id

    # Get candidate user data
    users_cursor = users_collection.find({"id_number": {"$in": candidate_ids_int}})
    users_data = []
    async for user in users_cursor:
        user_dict = dict(user)
        user_dict.pop("_id", None)
        users_data.append(user_dict)

    # Get candidate workout data
    workouts_cursor = workout_collection.find({"id_number": {"$in": candidate_ids_int}})
    workout_data = {}
    async for workout in workouts_cursor:
        workout_data[workout["id_number"]] = workout.get("workout_type", "Unknown")

    for user in users_data:
        user["workout_type"] = workout_data.get(user["id_number"], "Unknown")

    # Fetch last 3 liked workouts
    recent_events_cursor = events_collection.find({
        "user_id": str(user_id), "action": "like"
    }).sort("timestamp", -1).limit(3)

    recent_likes = []
    async for event in recent_events_cursor:
        buddy_id = event.get("buddy_id")
        if buddy_id:
            buddy_workout = await workout_collection.find_one({"id_number": int(buddy_id)})
            if buddy_workout and "workout_type" in buddy_workout:
                recent_likes.append(buddy_workout["workout_type"])

    # Build user profile row (including last liked workouts)
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
        'workout_type': workout_data.get(user_profile["id_number"], "Unknown"),
        'last_liked_workouts': recent_likes
    }

    return pd.DataFrame(users_data), pd.DataFrame([user_data])



def create_features_for_candidates(user_data: pd.DataFrame, candidate_ids: list[str], raw_data: pd.DataFrame) -> pd.DataFrame:
    """Refine + generate features"""
    return DataPreprocessor.generate_features_for_pairs(user_data, candidate_ids, raw_data)

def get_candidates(user_profile: dict, k: int = 150) -> list[str]:
    global user_recommender
    if user_recommender is None:
        load_models()
    _, candidate_ids = user_recommender.find_similar_users(user_profile, k=k)
    return candidate_ids

def rerank_candidates(user_profile: pd.DataFrame, candidate_ids: list[str], raw_data: pd.DataFrame) -> list[str]:
    global xgb_reranker
    if xgb_reranker is None:
        load_models()

    try:
        features = create_features_for_candidates(user_profile, candidate_ids, raw_data)
        drop_cols = ['user_id_number', 'buddy_id_number', 'label']
        features = features.drop(columns=[col for col in drop_cols if col in features.columns])
        print(features.sort_values(by='compatibility_score', ascending=False))

        if features.empty:
            print("Warning: No features generated, falling back to original candidate order")
            return candidate_ids[:100]  # Return first 30 candidates as fallback


        expected_cols = xgb_reranker.model.feature_names_in_.tolist()
        missing_cols = [col for col in expected_cols if col not in features.columns]
        if missing_cols:
            print(f"Warning: Missing columns {missing_cols}, falling back to original order")
            return candidate_ids[:100]
            
        features = features[expected_cols]


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
        return candidate_ids[:30]  # Fallback to first 30 candidates


@router.post("/similar-users-reranked", response_model=SimilarUsersRerankerResponse)
async def find_similar_users_with_reranking(user_profile: UserProfile) -> SimilarUsersRerankerResponse:
    try:
        load_models()
        print("Received user profile:", user_profile.model_dump())

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

        candidate_ids = get_candidates(profile_dict, k=150)
        candidate_ids = [cid for cid in candidate_ids if cid != user_profile.id_number]

        if not candidate_ids:
            raise HTTPException(status_code=404, detail="No candidates found")

        raw_data, user_data = await get_raw_data_for_user_and_candidates(profile_dict, [str(cid) for cid in candidate_ids])
        if raw_data.empty:
            raise HTTPException(status_code=404, detail="No raw data found")

        ranked_candidate_ids = rerank_candidates(user_data, candidate_ids, raw_data)
        if not ranked_candidate_ids:
            raise HTTPException(status_code=404, detail="No ranked candidates")

        top = min(150, len(ranked_candidate_ids) - 1)
        top_candidates = ranked_candidate_ids[:top]

        # Fetch final user data
        users_cursor = users_collection.find({"id_number": {"$in": top_candidates}})
        workouts_cursor = workout_collection.find({"id_number": {"$in": top_candidates}})
        workout_map = {}
        async for workout in workouts_cursor:
            workout_map[workout["id_number"]] = workout.get("workout_type", "Unknown")

        user_docs = {}
        async for user in users_cursor:
            user_dict = dict(user)
            user_dict.pop("_id", None)
            user_dict["workout_type"] = workout_map.get(user_dict["id_number"], "Unknown")
            user_docs[user["id_number"]] = user_dict

        similar_users_data = [user_docs[id_num] for id_num in top_candidates if id_num in user_docs]

        if not similar_users_data:
            raise HTTPException(status_code=404, detail="No similar users found")
        
        print(f"Final recommendations: {len(similar_users_data)}")
        print(f"Final recommendations: {[user['id_number'] for user in similar_users_data]}")

        # Print how many Male and Female in the top 20
        top_20 = similar_users_data[:20]
        num_male = sum(1 for user in top_20 if str(user.get('gender', '')).strip().lower() == 'male')
        num_female = sum(1 for user in top_20 if str(user.get('gender', '')).strip().lower() == 'female')
        print(f"Top 20 gender counts: Male={num_male}, Female={num_female}")

        return SimilarUsersRerankerResponse(
            id_numbers=[user['id_number'] for user in similar_users_data],
            similar_users=similar_users_data
        )

    except Exception as e:
        print(f"Error in similar-users-reranked: {e}")
        traceback.print_exc()  # prints to stderr/log
        raise HTTPException(status_code=500, detail=str(e))
