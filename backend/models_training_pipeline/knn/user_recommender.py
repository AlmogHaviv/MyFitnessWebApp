from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import NearestNeighbors
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import joblib
import numpy as np

class UserRecommender:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Separate models for different gender groups
        self.male_other_model = None
        self.female_model = None
        
        self.feature_columns = [
            'age', 'gender', 'height', 'daily_calories_intake',
            'resting_heart_rate', 'VO2_max', 'body_fat', 'bmi'
        ]
        
        # Separate user data for each gender group
        self.male_other_user_ids = None
        self.female_user_ids = None
        self.male_other_data = None
        self.female_data = None
        
        self.raw_df = None  # Needed for hybrid filtering

    def preprocess_data(self, df, fit=False):
        processed_df = df.copy()

        if fit:
            self.label_encoder.fit(processed_df['gender'])
        processed_df['gender'] = self.label_encoder.transform(processed_df['gender'])

        numerical_features = ['age', 'height', 'daily_calories_intake',
                              'resting_heart_rate', 'VO2_max', 'body_fat', 'bmi']

        if fit:
            self.scaler.fit(processed_df[numerical_features])
        processed_df[numerical_features] = self.scaler.transform(processed_df[numerical_features])

        weights = {
            'age': 1.0,
            'gender': 0.0,  # Neutralize gender in distance
            'height': 0.5,
            'daily_calories_intake': 1.0,
            'resting_heart_rate': 1.2,
            'VO2_max': 1.2,
            'body_fat': 0.9,
            'bmi': 0.9
        }

        for col in self.feature_columns:
            if col in processed_df.columns:
                processed_df[col] = processed_df[col] * weights.get(col, 1.0)

        return processed_df[self.feature_columns]

    def train(self, data_path):
        df = pd.read_csv(data_path)
        self.raw_df = df.copy()
        
        # Split data by gender
        male_other_df = df[df['gender'].isin(['Male', 'Other'])].copy()
        female_df = df[df['gender'] == 'Female'].copy()
        
        print(f"Training data distribution:")
        print(f"Male/Other users: {len(male_other_df)}")
        print(f"Female users: {len(female_df)}")
        
        if len(male_other_df) == 0 or len(female_df) == 0:
            raise ValueError("Not enough data for both gender groups. Need at least 1 user in each group.")
        
        # Store user IDs for each group
        self.male_other_user_ids = male_other_df['id_number'].tolist()
        self.female_user_ids = female_df['id_number'].tolist()
        
        # FIT the preprocessors on the FULL dataset first to learn all labels
        _ = self.preprocess_data(df, fit=True)
        
        # Now preprocess each group separately (without fitting)
        male_other_processed = self.preprocess_data(male_other_df, fit=False)
        female_processed = self.preprocess_data(female_df, fit=False)
        
        # Store processed data
        self.male_other_data = male_other_processed
        self.female_data = female_processed
        
        # Train separate models
        # For male/other model, use min of available users or 150
        male_other_neighbors = min(len(male_other_df), 150)
        self.male_other_model = NearestNeighbors(n_neighbors=male_other_neighbors, metric='euclidean')
        self.male_other_model.fit(male_other_processed)
        
        # For female model, use min of available users or 150
        female_neighbors = min(len(female_df), 150)
        self.female_model = NearestNeighbors(n_neighbors=female_neighbors, metric='euclidean')
        self.female_model.fit(female_processed)
        
        self.save_model()
        print("Training completed with separate gender models!")

    def find_similar_users(self, user_profile, k):
        profile_df = pd.DataFrame([user_profile])
        processed_profile = self.preprocess_data(profile_df, fit=False)
        
        # Calculate how many users to get from each group (aim for 50-50 split)
        k_male_other = k // 2
        k_female = k - k_male_other
        
        results = []
        
        # Get recommendations from male/other model
        if self.male_other_model is not None and len(self.male_other_user_ids) > 0:
            try:
                # Get min of requested k or available users
                actual_k_male_other = min(k_male_other, len(self.male_other_user_ids))
                distances_mo, indices_mo = self.male_other_model.kneighbors(
                    processed_profile, n_neighbors=actual_k_male_other
                )
                
                for i, (dist, idx) in enumerate(zip(distances_mo.flatten(), indices_mo.flatten())):
                    user_id = self.male_other_user_ids[idx]
                    gender = self.raw_df[self.raw_df['id_number'] == user_id]['gender'].iloc[0]
                    results.append({
                        'id': user_id,
                        'distance': dist,
                        'gender': gender,
                        'group': 'male_other'
                    })
            except Exception as e:
                print(f"Error getting male/other recommendations: {e}")
        
        # Get recommendations from female model
        if self.female_model is not None and len(self.female_user_ids) > 0:
            try:
                # Get min of requested k or available users
                actual_k_female = min(k_female, len(self.female_user_ids))
                distances_f, indices_f = self.female_model.kneighbors(
                    processed_profile, n_neighbors=actual_k_female
                )
                
                for i, (dist, idx) in enumerate(zip(distances_f.flatten(), indices_f.flatten())):
                    user_id = self.female_user_ids[idx]
                    gender = self.raw_df[self.raw_df['id_number'] == user_id]['gender'].iloc[0]
                    results.append({
                        'id': user_id,
                        'distance': dist,
                        'gender': gender,
                        'group': 'female'
                    })
            except Exception as e:
                print(f"Error getting female recommendations: {e}")
        
        # If we don't have enough results from one group, fill from the other
        if len(results) < k:
            remaining_needed = k - len(results)
            
            # Try to get more from the group that has capacity
            if len([r for r in results if r['group'] == 'male_other']) < len(self.male_other_user_ids):
                # Get more from male/other
                additional_k = min(remaining_needed, len(self.male_other_user_ids) - len([r for r in results if r['group'] == 'male_other']))
                if additional_k > 0:
                    try:
                        distances_mo, indices_mo = self.male_other_model.kneighbors(
                            processed_profile, n_neighbors=len([r for r in results if r['group'] == 'male_other']) + additional_k
                        )
                        
                        # Skip already included results
                        existing_male_other_ids = {r['id'] for r in results if r['group'] == 'male_other'}
                        added = 0
                        for dist, idx in zip(distances_mo.flatten(), indices_mo.flatten()):
                            user_id = self.male_other_user_ids[idx]
                            if user_id not in existing_male_other_ids and added < additional_k:
                                gender = self.raw_df[self.raw_df['id_number'] == user_id]['gender'].iloc[0]
                                results.append({
                                    'id': user_id,
                                    'distance': dist,
                                    'gender': gender,
                                    'group': 'male_other'
                                })
                                added += 1
                    except Exception as e:
                        print(f"Error getting additional male/other recommendations: {e}")
            
            elif len([r for r in results if r['group'] == 'female']) < len(self.female_user_ids):
                # Get more from female
                additional_k = min(remaining_needed, len(self.female_user_ids) - len([r for r in results if r['group'] == 'female']))
                if additional_k > 0:
                    try:
                        distances_f, indices_f = self.female_model.kneighbors(
                            processed_profile, n_neighbors=len([r for r in results if r['group'] == 'female']) + additional_k
                        )
                        
                        # Skip already included results
                        existing_female_ids = {r['id'] for r in results if r['group'] == 'female'}
                        added = 0
                        for dist, idx in zip(distances_f.flatten(), indices_f.flatten()):
                            user_id = self.female_user_ids[idx]
                            if user_id not in existing_female_ids and added < additional_k:
                                gender = self.raw_df[self.raw_df['id_number'] == user_id]['gender'].iloc[0]
                                results.append({
                                    'id': user_id,
                                    'distance': dist,
                                    'gender': gender,
                                    'group': 'female'
                                })
                                added += 1
                    except Exception as e:
                        print(f"Error getting additional female recommendations: {e}")
        
        # Sort by distance and limit to k
        results = sorted(results, key=lambda x: x['distance'])[:k]
        
        # Extract distances and IDs
        distances = [r['distance'] for r in results]
        user_ids = [r['id'] for r in results]
        
        # Print distribution info
        gender_dist = {}
        for r in results:
            gender_dist[r['gender']] = gender_dist.get(r['gender'], 0) + 1
        print(f"Recommendation distribution: {gender_dist}")
        
        return distances, user_ids

    def save_model(self):
        os.makedirs('models', exist_ok=True)
        
        # Save both models
        joblib.dump(self.male_other_model, 'models/male_other_model.joblib')
        joblib.dump(self.female_model, 'models/female_model.joblib')
        
        # Save preprocessing objects
        joblib.dump(self.scaler, 'models/scaler.joblib')
        joblib.dump(self.label_encoder, 'models/label_encoder.joblib')
        
        # Save user IDs for each group
        joblib.dump(self.male_other_user_ids, "models/male_other_user_ids.pkl")
        joblib.dump(self.female_user_ids, "models/female_user_ids.pkl")
        
        # Save processed data for each group
        joblib.dump(self.male_other_data, "models/male_other_data.pkl")
        joblib.dump(self.female_data, "models/female_data.pkl")
        
        print("All models and data saved successfully!")

    def load_model(self, data_path='data/workout_fitness_tracker_data_updated.csv'):
        # Load both models
        self.male_other_model = joblib.load('models/male_other_model.joblib')
        self.female_model = joblib.load('models/female_model.joblib')
        
        # Load preprocessing objects
        self.scaler = joblib.load('models/scaler.joblib')
        self.label_encoder = joblib.load('models/label_encoder.joblib')
        
        # Load user IDs for each group
        self.male_other_user_ids = joblib.load('models/male_other_user_ids.pkl')
        self.female_user_ids = joblib.load('models/female_user_ids.pkl')
        
        # Load processed data for each group
        self.male_other_data = joblib.load('models/male_other_data.pkl')
        self.female_data = joblib.load('models/female_data.pkl')
        
        # Load raw data (needed for finding similar users)
        import pandas as pd
        if os.path.exists(data_path):
            self.raw_df = pd.read_csv(data_path)
            print(f"Loaded raw data with {len(self.raw_df)} rows")
        else:
            print(f"Warning: Could not find data file at {data_path}")
            self.raw_df = None
        
        print("All models and data loaded successfully!")

    def explore_data(self, df, n_clusters=3):
        processed_data = self.preprocess_data(df, fit=False)
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(processed_data)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(processed_data)

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
        
    def get_model_info(self):
        """Get information about the trained models"""
        info = {
            'male_other_users': len(self.male_other_user_ids) if self.male_other_user_ids else 0,
            'female_users': len(self.female_user_ids) if self.female_user_ids else 0,
            'total_users': (len(self.male_other_user_ids) if self.male_other_user_ids else 0) + 
                          (len(self.female_user_ids) if self.female_user_ids else 0)
        }
        return info