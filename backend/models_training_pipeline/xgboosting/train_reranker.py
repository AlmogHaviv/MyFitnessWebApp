import os
import pandas as pd
import asyncio
from sklearn.model_selection import train_test_split

from data_preprocessor import DataPreprocessor
from xgb_reranker import XGBReranker

CSV_PATH = "cached_training_data.csv"
MONGO_URI = "mongodb+srv://almoghaviv:almoghaviv@workoutapp.e0r5zoq.mongodb.net/?retryWrites=true&w=majority&appName=workoutApp"

class ReRankerTrainer:
    def __init__(self, csv_path=CSV_PATH, mongo_uri=MONGO_URI, tune_before_train=True):
        self.csv_path = csv_path
        self.mongo_uri = mongo_uri
        self.data = None
        self.tune_before_train = tune_before_train

    async def prepare_data(self):
        if os.path.exists(self.csv_path):
            print(f"📂 Loading training data from cached CSV: {self.csv_path}")
            self.data = pd.read_csv(self.csv_path)
        else:
            print("🔄 Fetching and processing data from MongoDB...")
            processor = DataPreprocessor(self.mongo_uri, self.csv_path)
            self.data = await processor.generate_interaction_feature_csv()

        print("🔍 Training data preview:")
        print(self.data.head())

    def train_model(self):
        print("🚀 Starting model training...")

        # --- Refine data ---
        print("🛠️ Refining interaction data for model training...")
        refined_df = DataPreprocessor.refine_interaction_data(self.data)

        # --- Prepare features and labels ---
        X = refined_df.drop(columns=["label", "user_id", "buddy_id"])
        y = refined_df["label"]
        user_ids = refined_df["user_id"]
        buddy_ids = refined_df["buddy_id"]

        # Initial split: train+val vs test
        X_train, X_test, y_train, y_test, user_ids_train, user_ids_test, buddy_ids_train, buddy_ids_test = train_test_split(
            X, y, user_ids, buddy_ids, stratify=y, test_size=0.2, random_state=42
        )

        # Split training set into actual train and validation parts
        X_train_part, X_val, y_train_part, y_val, user_ids_part, user_ids_val = train_test_split(
            X_train, y_train, user_ids_train, test_size=0.2, stratify=y_train, random_state=42
        )

        # --- Initialize reranker model ---
        model = XGBReranker()

        # --- Hyperparameter tuning ---
        if self.tune_before_train:
            print("🔧 Tuning hyperparameters with RandomizedSearchCV...")
            # Pass user_ids_part for metrics like NDCG@k
            model.tune_hyperparameters(X_train_part, y_train_part, n_iter=30, cv=3)

        # --- Train with validation ---
        print("📈 Training final model with early stopping...")
        model.train(X_train_part, y_train_part, X_val, y_val)

        # --- Evaluate on test set ---
        print("📊 Evaluating on test set...")
        metrics = model.evaluate(X_test, y_test, user_ids=user_ids_test)
        for k, v in metrics.items():
            print(f"{k}: {v:.4f}")

        # --- Save model ---
        model.save("xgb_reranker_model.json")
        print("💾 Model saved to xgb_reranker_model.json")

    async def run(self):
        await self.prepare_data()
        self.train_model()

# Entry point
async def main():
    trainer = ReRankerTrainer()
    await trainer.run()

if __name__ == "__main__":
    asyncio.run(main())
