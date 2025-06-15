import pandas as pd
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models_training_pipeline.knn.user_recommender import UserRecommender
from models_training_pipeline.xgboosting.xgb_reranker import XGBReranker
from models_training_pipeline.xgboosting.data_preprocessor import DataPreprocessor


def create_features_for_candidates(user_id: str, candidate_ids: list[str], raw_data: pd.DataFrame) -> pd.DataFrame:
    return DataPreprocessor.generate_features_for_pairs(user_id, candidate_ids, raw_data)


def get_candidates(user_profile: dict, raw_data: pd.DataFrame, k: int = 150 ) -> list[str]:
    knn = UserRecommender()
    knn.load_model()
    _, candidate_ids = knn.find_similar_users(user_profile, k=k)
    return candidate_ids

def rescor(user_profile: dict, candidate_ids: list[str], raw_data: pd.DataFrame, reranker: XGBReranker) -> list[str]:
    features = create_features_for_candidates(user_profile['id_number'], candidate_ids, raw_data)
    # Drop non-feature columns that were not in training
    drop_cols = ['user_id_number', 'buddy_id_number', 'label']  # or any other columns not used for training
    features = features.drop(columns=[col for col in drop_cols if col in features.columns])

    if features.empty:
        return []

    # Match the order of columns as in training
    expected_cols = reranker.model.feature_names_in_.tolist()
    features = features[expected_cols]

    scores = reranker.predict_proba(features)
    scored_df = pd.DataFrame({
        'buddy_id': candidate_ids,
        'score': scores
    })
    ranked_candidates = scored_df.sort_values(by='score', ascending=False)['buddy_id'].tolist()
    return ranked_candidates

def main(users: pd.DataFrame, positive_interactions: pd.DataFrame, raw_data: pd.DataFrame) -> None:
    reranker = XGBReranker()
    reranker.load("xgb_reranker_model.json")

    precision_at_10 = 0
    precision_at_6 = 0
    count = 0

    for _, user in users.iterrows():
        try:
            candidate_ids = get_candidates(user, raw_data)
            if not candidate_ids:
                continue

            ordered_candidates = rescor(user, candidate_ids, raw_data, reranker)
            if not ordered_candidates:
                continue

            top_10 = ordered_candidates[:10]
            top_6 = ordered_candidates[:6]

            # Get true positives for this user
            true_positives = positive_interactions[
                positive_interactions["user_id"] == user["id_number"]
            ]["buddy_id"].tolist()

            hits_at_10 = len(set(top_10) & set(true_positives))
            hits_at_6 = len(set(top_6) & set(true_positives))

            precision_at_10 += hits_at_10
            precision_at_6 += hits_at_6
            count += 1
        except Exception as e:
            print(f"Error with user {user['id_number']}: {e}")
            continue

    if count == 0:
        print("No users processed.")
        return

    print(f"Processed {count} users")
    print(f"Precision@10: {precision_at_10 / count:.4f}")
    print(f"Precision@6: {precision_at_6 / count:.4f}")


if __name__ == "__main__":
    raw_data_df = pd.read_csv("workout_fitness_tracker_data_updated.csv")

    # Filter raw_data_df to only the minimal required columns
    required_columns = [
        "id_number", "full_name", "age", "gender", "height", "weight",
        "daily_calories_intake", "resting_heart_rate", "VO2_max",
        "body_fat", "bmi", "workout_type"
    ]
    raw_data_df = raw_data_df[[col for col in required_columns if col in raw_data_df.columns]]

    users_df = raw_data_df.sample(frac=0.2, random_state=42).reset_index(drop=True)
    interactions_df = pd.read_csv("cached_training_data.csv")
    positive_interactions_df = interactions_df[interactions_df["label"] == 1]

    main(users_df, positive_interactions_df, raw_data_df)

