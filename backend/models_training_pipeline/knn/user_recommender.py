from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
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

        # Adjust feature weights based on correlation strength:
        # - Gender has a weak correlation, so assign a low weight (0.3)
        # - VO2_max and resting_heart_rate are more important (1.2)
        # - Body fat and BMI moderately important (0.9)
        weights = {
            'age': 1.0,
            'gender': 0.3,  # weak correlation, less influence
            'height': 0.5,  # weak correlation, less influence
            'daily_calories_intake': 1.0,
            'resting_heart_rate': 1.2,
            'VO2_max': 1.2,
            'body_fat': 0.9,
            'bmi': 0.9
        }

        # Apply weights to scaled features
        for col in self.feature_columns:
            if col in numerical_features or col == 'gender':
                processed_df[col] = processed_df[col] * weights.get(col, 1.0)

        return processed_df[self.feature_columns]

    def train(self, data_path):
        """Train the KNN model on the provided data."""
        df = pd.read_csv(data_path)

        # Store user_ids for lookup
        self.user_ids = df['id_number'].tolist()

        # Preprocess with fitting
        processed_data = self.preprocess_data(df, fit=True)

        # Use cosine distance because:
        # "Cosine similarity focuses on the orientation of vectors rather than their magnitude,
        #  which helps in comparing user profiles that may differ in scale but have similar patterns."
        self.model = NearestNeighbors(n_neighbors=150, metric='cosine')
        self.model.fit(processed_data)
        
        self.save_model()

    
    def find_similar_users(self, user_profile, k):
        profile_df = pd.DataFrame([user_profile])
        processed_profile = self.preprocess_data(profile_df, fit=False)

        distances, indices = self.model.kneighbors(processed_profile)

        if k is not None:
            distances = distances[:, :k]
            indices = indices[:, :k]

        similar_user_ids = [self.user_ids[i] for i in indices.flatten()]
        return distances.flatten(), similar_user_ids

    def save_model(self):
        """Save the trained model and preprocessing objects."""
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, 'models/user_recommender_model.joblib')
        joblib.dump(self.scaler, 'models/scaler.joblib')
        joblib.dump(self.label_encoder, 'models/label_encoder.joblib')
        joblib.dump(self.user_ids, "models/user_ids.pkl")


    def load_model(self):
        """Load the trained model and preprocessing objects."""
        self.model = joblib.load('models/user_recommender_model.joblib')
        self.scaler = joblib.load('models/scaler.joblib')
        self.label_encoder = joblib.load('models/label_encoder.joblib')
        self.user_ids = joblib.load('models/user_ids.pkl')

    def explore_data(self, df, n_clusters=3):
        """
        Explore the dataset by performing PCA for dimensionality reduction and KMeans clustering,
        then visualizing the clusters on a 2D scatter plot.

        Parameters:
        - df: pandas DataFrame with raw data
        - n_clusters: number of clusters for KMeans (default=4)
        """
        # Preprocess without fitting (assumes scaler/encoder already fit)
        processed_data = self.preprocess_data(df, fit=False)

        # PCA to reduce to 2D
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(processed_data)

        # KMeans clustering on processed data
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(processed_data)

        # Plot
        plt.figure(figsize=(10, 7))
        sns.scatterplot(
            x=pca_result[:, 0], y=pca_result[:, 1],
            hue=cluster_labels,
            palette='Set2',
            legend='full'
        )
        plt.title(f'PCA Visualization with {n_clusters} Clusters')
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        plt.show()
