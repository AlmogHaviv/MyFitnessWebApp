import os
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi


class DataPreprocessor:
    def __init__(self, mongo_uri: str, csv_path: str = "cached_training_data.csv"):
        self.mongo_uri = mongo_uri
        self.csv_path = csv_path
        self.users_df = None
        self.workouts_df = None
        self.interactions_df = None
        self.merged_users_df = None

    async def load_data_from_mongo(self):
        print("Connecting to MongoDB...")
        client = AsyncIOMotorClient(self.mongo_uri,
                                    server_api=ServerApi('1'),
                                    connectTimeoutMS=120000,
                                    socketTimeoutMS=120000)
        db = client.workoutApp

        print("Loading users...")
        users_cursor = db.users.find()
        users = await users_cursor.to_list(length=None)
        for u in users:
            u.pop("_id", None)

        print("Loading workouts...")
        workouts_cursor = db.workout.find()
        workouts = await workouts_cursor.to_list(length=None)
        for w in workouts:
            w.pop("_id", None)

        print("Loading interactions...")
        events_cursor = db.events.find()
        events = await events_cursor.to_list(length=None)
        for e in events:
            e.pop("_id", None)

        self.users_df = pd.DataFrame(users)
        self.workouts_df = pd.DataFrame(workouts)
        self.interactions_df = pd.DataFrame(events)

        print("Merging users and workouts...")
        self.merged_users_df = pd.merge(self.users_df, self.workouts_df, on="id_number", how="left")

    def save_user_workout_csv(self, filename: str = "merged_users.csv"):
        if self.merged_users_df is not None:
            print(f"Saving merged user-workout data to {filename}...")
            self.merged_users_df.to_csv(filename, index=False)
        else:
            raise ValueError("Merged user-workout data not available. Run load_data_from_mongo() first.")

    async def generate_interaction_feature_csv(self):
        await self.load_data_from_mongo()
        
        print("Generating training data from interactions...")

        interactions = self.interactions_df.copy()
        interactions['label'] = (interactions['action'] == 'like').astype(int)
        
        # Convert user_id and buddy_id to string type for consistent merging
        interactions['user_id'] = interactions['user_id'].astype(str)
        interactions['buddy_id'] = interactions['buddy_id'].astype(str)
        
        # Ensure id_number columns are also string type
        self.merged_users_df['id_number'] = self.merged_users_df['id_number'].astype(str)

        merged = interactions.merge(self.merged_users_df.add_prefix("user_"), left_on="user_id", right_on="user_id_number", how="left")
        merged = merged.merge(self.merged_users_df.add_prefix("buddy_"), left_on="buddy_id", right_on="buddy_id_number", how="left")

        merged.drop(columns=["user_id_number", "buddy_id_number"], inplace=True)

        print(f"Saving interaction features data to {self.csv_path}...")
        merged.to_csv(self.csv_path, index=False)

        return merged

    @staticmethod
    def generate_features_for_pairs(user_id: str, candidate_ids: list[str], raw_data: pd.DataFrame) -> pd.DataFrame:
        # Filter user and candidate rows
        user_row = raw_data[raw_data["id_number"] == user_id].copy()
        if user_row.empty:
            raise ValueError(f"User ID {user_id} not found in raw data.")

        buddy_rows = raw_data[raw_data["id_number"].isin(candidate_ids)].copy()
        if buddy_rows.empty:
            return pd.DataFrame()  # No candidates found

        # Rename for merging
        user_row = user_row.add_prefix("user_").reset_index(drop=True)
        buddy_rows = buddy_rows.add_prefix("buddy_").reset_index(drop=True)

        # Duplicate user row for each buddy
        user_repeated = pd.concat([user_row] * len(buddy_rows), ignore_index=True)

        # Merge side-by-side
        merged = pd.concat([user_repeated, buddy_rows], axis=1)

        # Add dummy fields to match refine_interaction_data signature
        merged["label"] = 0  # Dummy
        merged["action"] = "like"  # Dummy
        merged["timestamp"] = pd.Timestamp.now()  # Dummy
        merged["user_id"] = user_id
        merged["buddy_id"] = buddy_rows["buddy_id_number"].values

        # Add any missing columns to match training format
        return DataPreprocessor.refine_interaction_data(merged)

    @staticmethod
    def compatibility_score(row) -> float:
        score = 0
        if row["user_workout_type"] == row["buddy_workout_type"]:
            score += 3
        if abs(row["user_age"] - row["buddy_age"]) <= 5:
            score += 2
        if row["user_gender"] == row["buddy_gender"]:
            score += 0.5
        if abs(row["user_VO2_max"] - row["buddy_VO2_max"]) <= 5:
            score += 0.5
        if abs(row["user_body_fat"] - row["buddy_body_fat"]) <= 5:
            score += 0.5
        if abs(row["user_bmi"] - row["buddy_bmi"]) <= 2:
            score += 0.2
        return score

    @staticmethod
    def refine_interaction_data(df: pd.DataFrame) -> pd.DataFrame:
        # 1. Add engineered features
        df["is_same_gender"] = (df["user_gender"] == df["buddy_gender"]).astype(int)
        df["is_same_workout"] = (df["user_workout_type"] == df["buddy_workout_type"]).astype(int)

        # 2. Add compatibility score feature
        df["compatibility_score"] = df.apply(DataPreprocessor.compatibility_score, axis=1)

        # 3. Encode categorical features using label encoding
        categorical_cols = ["user_gender", "user_workout_type", "buddy_gender", "buddy_workout_type"]
        for col in categorical_cols:
            df[col] = pd.Categorical(df[col]).codes

        # 4. Drop non-numeric / identifier / metadata columns
        drop_cols = ["timestamp", "user_full_name", "buddy_full_name", "action"]
        df = df.drop(columns=drop_cols)

        # 5. Drop any remaining rows with missing values (optional safeguard)
        df = df.dropna()

        # 6. Reorder columns: label last (optional)
        label = df.pop("label")
        df["label"] = label

        return df
