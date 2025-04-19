from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import os
import joblib

class UserRecommender:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.model = None
        self.feature_columns = [
            'age', 'gender', 'height', 'daily_calories_intake',
            'resting_heart_rate', 'VO2_max', 'body_fat', 'bmi'
        ]
        self.user_ids = None  # stores user_id mapping
    
    def preprocess_data(self, df, fit=False):
        """Preprocess the data for the KNN model."""
        processed_df = df.copy()

        # Encode gender column
        if fit:
            self.label_encoder.fit(processed_df['gender'])
        processed_df['gender'] = self.label_encoder.transform(processed_df['gender'])

        # Select numerical features for scaling
        numerical_features = ['age', 'height', 'daily_calories_intake', 
                              'resting_heart_rate', 'VO2_max', 'body_fat', 'bmi']
        
        if fit:
            self.scaler.fit(processed_df[numerical_features])
        processed_df[numerical_features] = self.scaler.transform(
            processed_df[numerical_features]
        )

        return processed_df[self.feature_columns]

    def train(self, data_path):
        """Train the KNN model on the provided data."""
        df = pd.read_csv(data_path)

        # Store user_ids for lookup
        self.user_ids = df['id_number'].tolist()

        # Preprocess with fitting
        processed_data = self.preprocess_data(df, fit=True)

        # Train KNN
        self.model = NearestNeighbors(n_neighbors=10, metric='euclidean')
        self.model.fit(processed_data)

        # Save model and preprocessing tools
        self.save_model()

    def find_similar_users(self, user_profile):
        """Find similar users using the KNN model."""
        height_in_meters = user_profile['height'] / 100
        user_profile['bmi'] = round(user_profile['weight'] / (height_in_meters ** 2), 1)
        
        profile_df = pd.DataFrame([user_profile])
        processed_profile = self.preprocess_data(profile_df, fit=False)

        distances, indices = self.model.kneighbors(processed_profile)

        # Convert indices to user_ids
        similar_user_ids = [self.user_ids[i] for i in indices.flatten()]

        return distances.flatten(), similar_user_ids

    def save_model(self):
        """Save the trained model and preprocessing objects."""
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/user_recommender_model.joblib')
        joblib.dump(self.scaler, 'models/scaler.joblib')
        joblib.dump(self.label_encoder, 'models/label_encoder.joblib')
        joblib.dump(self.user_ids, "models/user_ids.pkl")  # <-- Save user_ids

    def load_model(self):
        """Load the trained model and preprocessing objects."""
        self.model = joblib.load('models/user_recommender_model.joblib')
        self.scaler = joblib.load('models/scaler.joblib')
        self.label_encoder = joblib.load('models/label_encoder.joblib')
        self.user_ids = joblib.load('models/user_ids.pkl')
