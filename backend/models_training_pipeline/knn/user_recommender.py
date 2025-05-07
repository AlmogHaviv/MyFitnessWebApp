from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

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
        self.model = NearestNeighbors(n_neighbors=15, metric='euclidean')
        self.model.fit(processed_data)

         # KMeans Clustering (assuming 3 clusters, but you can adjust this)
        self.kmeans = KMeans(n_clusters=3)
        df['cluster'] = self.kmeans.fit_predict(processed_data)

        # Save model and preprocessing tools
        self.save_model()

    def analyze_clusters(self, df: pd.DataFrame):
        if not hasattr(self, 'kmeans'):
            raise ValueError("KMeans model not loaded. Run train() or load_model() first.")

        # Preprocess input
        processed_df = self.preprocess_data(df, fit=False)

        # Predict cluster labels
        df['cluster'] = self.kmeans.predict(processed_df)

        # Identify existing numerical and categorical features
        numeric_features = [col for col in ['age', 'height', 'weight', 'experience', 'frequency'] if col in df.columns]
        categorical_features = [col for col in ['gender', 'goal'] if col in df.columns]

        # Numerical summary
        numeric_summary = df.groupby('cluster')[numeric_features].mean()

        # Categorical summary
        categorical_summary = df.groupby('cluster')[categorical_features].agg(lambda x: x.mode().iloc[0])

        # Combine summaries
        cluster_profiles = pd.concat([numeric_summary, categorical_summary], axis=1)

        print("\n--- Cluster Profiles ---")
        print(cluster_profiles)

        print("\n--- Cluster Interpretations ---")
        for cluster_id, row in cluster_profiles.iterrows():
            description = f"Cluster {cluster_id}:"

            if 'gender' in row and 'goal' in row:
                description += f" Predominantly {row['gender']}s aiming for {row['goal']}."

            if 'age' in row:
                description += f"\n  Avg Age: {row['age']:.1f}"
            if 'height' in row:
                description += f", Height: {row['height']:.1f} cm"
            if 'weight' in row:
                description += f", Weight: {row['weight']:.1f} kg"
            if 'experience' in row:
                description += f"\n  Experience: {row['experience']:.1f} yrs"
            if 'frequency' in row:
                description += f", Frequency: {row['frequency']:.1f} times/week"

            print(description)

        return df

    
    def plot_box_by_cluster(self, df: pd.DataFrame, feature: str = 'age'):
        if 'cluster' not in df.columns:
            raise ValueError("DataFrame must include a 'cluster' column. Run analyze_clusters first.")

        plt.figure(figsize=(8, 6))
        sns.boxplot(x='cluster', y=feature, data=df)
        plt.title(f"{feature.capitalize()} Distribution by Cluster")
        plt.xlabel("Cluster")
        plt.ylabel(feature.capitalize())
        plt.tight_layout()
        plt.show()
    
    def plot_clusters(self, df):
        """Visualize the clusters using PCA after preprocessing."""
        # Preprocess data (use fit=False because we're reusing the trained scaler and encoder)
        processed_df = self.preprocess_data(df, fit=False)

        # Perform PCA to reduce to 2D for visualization
        pca = PCA(n_components=2)
        pca_components = pca.fit_transform(processed_df)

        # Add PCA components and cluster labels to the original dataframe
        df['PCA1'] = pca_components[:, 0]
        df['PCA2'] = pca_components[:, 1]
        df['cluster'] = self.kmeans.predict(processed_df)  # use same kmeans model

        # Plotting the clusters
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x='PCA1', y='PCA2', hue='cluster', palette='Set1', data=df, s=100, edgecolor='k')
        plt.title("PCA - Clusters of Users")
        plt.xlabel("PCA Component 1")
        plt.ylabel("PCA Component 2")
        plt.legend(title="Cluster")
        plt.show()

    
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
        joblib.dump(self.user_ids, "models/user_ids.pkl")
        joblib.dump(self.kmeans, "models/kmeans_model.pkl")  # <-- Save KMeans


    def load_model(self):
        """Load the trained model and preprocessing objects."""
        self.model = joblib.load('models/user_recommender_model.joblib')
        self.scaler = joblib.load('models/scaler.joblib')
        self.label_encoder = joblib.load('models/label_encoder.joblib')
        self.user_ids = joblib.load('models/user_ids.pkl')
        self.kmeans = joblib.load("models/kmeans_model.pkl")  # <-- Load KMeans
