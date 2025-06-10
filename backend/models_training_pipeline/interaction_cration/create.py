import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import json
from typing import Dict, List, Tuple
import math
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

class FitnessPartnerMatcher:
    def __init__(self, fitness_data_path: str = None, fitness_df: pd.DataFrame = None):
        """
        Initialize the matcher with fitness data
        """
        if fitness_df is not None:
            self.df = fitness_df
        elif fitness_data_path:
            self.df = pd.read_csv(fitness_data_path)
        else:
            raise ValueError("Either fitness_data_path or fitness_df must be provided")
        
        self.events = []
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess and normalize data for better compatibility scoring"""
        # Normalize numerical features for better comparison
        numerical_cols = ['age', 'height', 'weight', 'workout_duration_in_minutes', 
                         'calories_burned', 'heart_rate', 'VO2_max', 'body_fat', 'bmi']
        
        for col in numerical_cols:
            if col in self.df.columns:
                self.df[f'{col}_norm'] = (self.df[col] - self.df[col].mean()) / self.df[col].std()
    
    def calculate_advanced_compatibility(self, user1: pd.Series, user2: pd.Series) -> Dict[str, float]:
        """
        Calculate advanced compatibility scores based on multiple factors
        """
        scores = {}
        
        # 1. Workout Compatibility (25% weight)
        workout_score = 0
        if user1['workout_type'] == user2['workout_type']:
            workout_score += 4.0  # Same workout type
        else:
            # Partial compatibility for related workouts
            compatible_workouts = {
                'Cardio': ['Running', 'Cycling', 'HIIT'],
                'Running': ['Cardio', 'Cycling'],
                'Cycling': ['Cardio', 'Running'],
                'Strength': ['Weight Training', 'HIIT'],
                'Weight Training': ['Strength', 'HIIT'],
                'HIIT': ['Cardio', 'Strength', 'Weight Training'],
                'Yoga': ['Pilates', 'Stretching'],
                'Pilates': ['Yoga', 'Stretching']
            }
            if user1['workout_type'] in compatible_workouts:
                if user2['workout_type'] in compatible_workouts[user1['workout_type']]:
                    workout_score += 2.0
        
        # Workout intensity compatibility
        intensity_map = {'Low': 1, 'Medium': 2, 'High': 3}
        intensity_diff = abs(intensity_map.get(user1['workout_intensity'], 2) - 
                           intensity_map.get(user2['workout_intensity'], 2))
        workout_score += max(0, 2 - intensity_diff)
        
        # Workout duration compatibility
        duration_diff = abs(user1['workout_duration_in_minutes'] - user2['workout_duration_in_minutes'])
        if duration_diff <= 15:
            workout_score += 1.5
        elif duration_diff <= 30:
            workout_score += 1.0
        elif duration_diff <= 60:
            workout_score += 0.5
        
        scores['workout'] = min(workout_score, 7.5)
        
        # 2. Physical Compatibility (20% weight)
        physical_score = 0
        
        # Age compatibility - closer ages are better
        age_diff = abs(user1['age'] - user2['age'])
        if age_diff <= 3:
            physical_score += 3.0
        elif age_diff <= 7:
            physical_score += 2.0
        elif age_diff <= 12:
            physical_score += 1.0
        elif age_diff <= 20:
            physical_score += 0.5
        
        # Fitness level compatibility (VO2_max, body_fat)
        if not pd.isna(user1['VO2_max']) and not pd.isna(user2['VO2_max']):
            vo2_diff = abs(user1['VO2_max'] - user2['VO2_max'])
            if vo2_diff <= 5:
                physical_score += 2.0
            elif vo2_diff <= 10:
                physical_score += 1.0
            elif vo2_diff <= 15:
                physical_score += 0.5
        
        # BMI compatibility
        bmi_diff = abs(user1['bmi'] - user2['bmi'])
        if bmi_diff <= 2:
            physical_score += 1.5
        elif bmi_diff <= 5:
            physical_score += 1.0
        elif bmi_diff <= 8:
            physical_score += 0.5
        
        scores['physical'] = min(physical_score, 6.5)
        
        # 3. Lifestyle Compatibility (15% weight)
        lifestyle_score = 0
        
        # Sleep compatibility
        sleep_diff = abs(user1['sleep_hours'] - user2['sleep_hours'])
        if sleep_diff <= 0.5:
            lifestyle_score += 2.0
        elif sleep_diff <= 1.0:
            lifestyle_score += 1.5
        elif sleep_diff <= 2.0:
            lifestyle_score += 1.0
        
        # Water intake compatibility
        water_diff = abs(user1['water_intake_in_liters'] - user2['water_intake_in_liters'])
        if water_diff <= 0.3:
            lifestyle_score += 1.5
        elif water_diff <= 0.7:
            lifestyle_score += 1.0
        elif water_diff <= 1.0:
            lifestyle_score += 0.5
        
        # Calorie intake compatibility (indicates similar metabolism/goals)
        calorie_diff = abs(user1['daily_calories_intake'] - user2['daily_calories_intake'])
        if calorie_diff <= 200:
            lifestyle_score += 1.5
        elif calorie_diff <= 500:
            lifestyle_score += 1.0
        elif calorie_diff <= 800:
            lifestyle_score += 0.5
        
        scores['lifestyle'] = min(lifestyle_score, 5.0)
        
        # 4. Personality/Mood Compatibility (10% weight)
        personality_score = 0
        
        # Mood compatibility - similar moods indicate similar mindset
        mood_compatibility = {
            ('Happy', 'Energized'): 2.0,
            ('Happy', 'Happy'): 2.0,
            ('Energized', 'Energized'): 2.0,
            ('Motivated', 'Motivated'): 2.0,
            ('Motivated', 'Happy'): 1.5,
            ('Motivated', 'Energized'): 1.5,
        }
        
        mood_pair = (user1['mood_before_workout'], user2['mood_before_workout'])
        personality_score += mood_compatibility.get(mood_pair, 0)
        
        # After workout mood compatibility
        mood_pair_after = (user1['mood_after_workout'], user2['mood_after_workout'])
        personality_score += mood_compatibility.get(mood_pair_after, 0) * 0.5
        
        scores['personality'] = min(personality_score, 2.5)
        
        # 5. Goal Compatibility (15% weight) - inferred from behavior
        goal_score = 0
        
        # High calorie burn + high intensity = weight loss goal
        # Low calorie burn + strength training = muscle building
        # Consistent moderate activity = general fitness
        
        user1_goal = self._infer_goal(user1)
        user2_goal = self._infer_goal(user2)
        
        if user1_goal == user2_goal:
            goal_score += 3.0
        elif self._goals_compatible(user1_goal, user2_goal):
            goal_score += 1.5
        
        scores['goals'] = min(goal_score, 3.0)
        
        # 6. Performance Compatibility (15% weight)
        performance_score = 0
        
        # Similar performance levels work well together
        # Compare calories burned per minute, steps, distance
        if user1['workout_duration_in_minutes'] > 0 and user2['workout_duration_in_minutes'] > 0:
            user1_intensity = user1['calories_burned'] / user1['workout_duration_in_minutes']
            user2_intensity = user2['calories_burned'] / user2['workout_duration_in_minutes']
            
            intensity_ratio = min(user1_intensity, user2_intensity) / max(user1_intensity, user2_intensity)
            performance_score += intensity_ratio * 2.0
        
        # Step count compatibility
        steps_diff = abs(user1['steps_taken'] - user2['steps_taken'])
        if steps_diff <= 1000:
            performance_score += 1.5
        elif steps_diff <= 3000:
            performance_score += 1.0
        elif steps_diff <= 5000:
            performance_score += 0.5
        
        scores['performance'] = min(performance_score, 3.5)
        
        return scores
    
    def _infer_goal(self, user: pd.Series) -> str:
        """Infer user's fitness goal from their data"""
        if user['body_fat'] > 25 and user['calories_burned'] > 400:
            return 'weight_loss'
        elif user['workout_type'] in ['Strength', 'Weight Training'] and user['body_fat'] < 15:
            return 'muscle_building'
        elif user['VO2_max'] > 45:
            return 'endurance'
        else:
            return 'general_fitness'
    
    def _goals_compatible(self, goal1: str, goal2: str) -> bool:
        """Check if two goals are compatible"""
        compatible_goals = {
            'weight_loss': ['general_fitness'],
            'muscle_building': ['general_fitness'],
            'endurance': ['general_fitness', 'weight_loss'],
            'general_fitness': ['weight_loss', 'muscle_building', 'endurance']
        }
        return goal2 in compatible_goals.get(goal1, [])
    
    def calculate_like_probability(self, scores: Dict[str, float]) -> float:
        """
        Calculate probability of liking based on weighted compatibility scores
        """
        weights = {
            'workout': 0.25,
            'physical': 0.20,
            'lifestyle': 0.15,
            'personality': 0.10,
            'goals': 0.15,
            'performance': 0.15
        }
        
        # Calculate weighted total score
        total_score = sum(scores[key] * weights[key] for key in scores.keys())
        max_possible = sum(weights[key] * self._get_max_score(key) for key in weights.keys())
        
        # Normalize to 0-1
        normalized_score = total_score / max_possible
        
        # Convert to probability with some randomness
        base_prob = normalized_score * 0.8 + 0.1  # Range from 0.1 to 0.9
        
        # Add some noise for realism
        noise = random.gauss(0, 0.05)
        final_prob = max(0.05, min(0.95, base_prob + noise))
        
        return final_prob
    
    def _get_max_score(self, category: str) -> float:
        """Get maximum possible score for each category"""
        max_scores = {
            'workout': 7.5,
            'physical': 6.5,
            'lifestyle': 5.0,
            'personality': 2.5,
            'goals': 3.0,
            'performance': 3.5
        }
        return max_scores.get(category, 1.0)
    
    def generate_interactions(self, interactions_per_user: int = 25, 
                            time_span_days: int = 30) -> List[Dict]:
        """
        Generate realistic like/dislike interactions
        """
        events = []
        
        for idx, user in self.df.iterrows():
            # Select random other users to interact with
            other_users = self.df[self.df['id_number'] != user['id_number']].sample(
                n=min(interactions_per_user, len(self.df) - 1)
            )
            
            for _, other_user in other_users.iterrows():
                # Calculate compatibility scores
                scores = self.calculate_advanced_compatibility(user, other_user)
                like_prob = self.calculate_like_probability(scores)
                
                # Decide action based on probability
                action = 'like' if random.random() < like_prob else 'dislike'
                
                # Generate realistic timestamp
                days_ago = random.randint(0, time_span_days)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                
                event = {
                    'user_id': str(user['id_number']),
                    'buddy_id': str(other_user['id_number']),
                    'action': action,
                    'timestamp': timestamp,
                    'compatibility_scores': scores,
                    'like_probability': like_prob
                }
                
                events.append(event)
        
        return events
    
    def generate_training_features(self, events: List[Dict]) -> pd.DataFrame:
        """
        Generate feature matrix for XGBoost training
        """
        training_data = []
        
        for event in events:
            user_id = int(event['user_id'])
            buddy_id = int(event['buddy_id'])
            
            user_data = self.df[self.df['id_number'] == user_id].iloc[0]
            buddy_data = self.df[self.df['id_number'] == buddy_id].iloc[0]
            
            features = {
                # User features
                'user_age': user_data['age'],
                'user_gender': user_data['gender'],
                'user_bmi': user_data['bmi'],
                'user_workout_type': user_data['workout_type'],
                'user_workout_intensity': user_data['workout_intensity'],
                'user_vo2_max': user_data['VO2_max'],
                'user_body_fat': user_data['body_fat'],
                
                # Buddy features
                'buddy_age': buddy_data['age'],
                'buddy_gender': buddy_data['gender'],
                'buddy_bmi': buddy_data['bmi'],
                'buddy_workout_type': buddy_data['workout_type'],
                'buddy_workout_intensity': buddy_data['workout_intensity'],
                'buddy_vo2_max': buddy_data['VO2_max'],
                'buddy_body_fat': buddy_data['body_fat'],
                
                # Difference features
                'age_diff': abs(user_data['age'] - buddy_data['age']),
                'bmi_diff': abs(user_data['bmi'] - buddy_data['bmi']),
                'vo2_diff': abs(user_data['VO2_max'] - buddy_data['VO2_max']),
                'body_fat_diff': abs(user_data['body_fat'] - buddy_data['body_fat']),
                'workout_duration_diff': abs(user_data['workout_duration_in_minutes'] - buddy_data['workout_duration_in_minutes']),
                'calories_diff': abs(user_data['calories_burned'] - buddy_data['calories_burned']),
                
                # Similarity features
                'same_workout_type': 1 if user_data['workout_type'] == buddy_data['workout_type'] else 0,
                'same_gender': 1 if user_data['gender'] == buddy_data['gender'] else 0,
                'same_intensity': 1 if user_data['workout_intensity'] == buddy_data['workout_intensity'] else 0,
                
                # Compatibility scores
                **{f'score_{k}': v for k, v in event['compatibility_scores'].items()},
                
                # Target variable
                'liked': 1 if event['action'] == 'like' else 0
            }
            
            training_data.append(features)
        
        return pd.DataFrame(training_data)
    
    def save_data(self, events: List[Dict], output_prefix: str = 'fitness_partner'):
        """Save generated data to files"""
        
        # Save events as JSON
        events_serializable = []
        for event in events:
            event_copy = event.copy()
            event_copy['timestamp'] = event_copy['timestamp'].isoformat()
            events_serializable.append(event_copy)
        
        with open(f'{output_prefix}_events.json', 'w') as f:
            json.dump(events_serializable, f, indent=2)
        
        # Generate and save training features
        training_df = self.generate_training_features(events)
        training_df.to_csv(f'{output_prefix}_training_data.csv', index=False)
        
        # Save summary statistics
        stats = {
            'total_interactions': len(events),
            'total_likes': sum(1 for e in events if e['action'] == 'like'),
            'total_dislikes': sum(1 for e in events if e['action'] == 'dislike'),
            'like_rate': sum(1 for e in events if e['action'] == 'like') / len(events),
            'unique_users': len(set(e['user_id'] for e in events)),
            'avg_compatibility_scores': {
                key: np.mean([e['compatibility_scores'][key] for e in events])
                for key in events[0]['compatibility_scores'].keys()
            }
        }
        
        with open(f'{output_prefix}_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"Generated {len(events)} interactions")
        print(f"Like rate: {stats['like_rate']:.2%}")
        print(f"Files saved: {output_prefix}_events.json, {output_prefix}_training_data.csv, {output_prefix}_stats.json")
        
        return training_df, stats

# Example usage
def main():
    # Load your fitness data
    fitness_df = pd.read_csv('workout_fitness_tracker_data_updated.csv')
    matcher = FitnessPartnerMatcher(fitness_df=fitness_df)
    
    # Generate interactions
    events = matcher.generate_interactions(interactions_per_user=30, time_span_days=60)
    
    # Save data for XGBoost training
    training_df, stats = matcher.save_data(events, 'fitness_partner_smart')
    
    print("Script ready! Initialize with your fitness data and run generate_interactions()")

if __name__ == "__main__":
    main()