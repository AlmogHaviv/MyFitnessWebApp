import pandas as pd
import logging
from user_recommender import UserRecommender
import random
import os
import time
import traceback
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_and_save_model():
    """Train the recommender system, save the model, and find similar users."""
    try:
        # Load the real data
        df = pd.read_csv('data/workout_fitness_tracker_data.csv')

        # # Generate random names based on gender
        # male_names = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles',
        #              'Daniel', 'Matthew', 'Anthony', 'Donald', 'Mark', 'Paul', 'Steven', 'Andrew', 'Kenneth', 'Joshua',
        #              'Kevin', 'Brian', 'George', 'Timothy', 'Ronald', 'Jason', 'Edward', 'Jeffrey', 'Ryan', 'Jacob',
        #              'Gary', 'Nicholas', 'Eric', 'Jonathan', 'Stephen', 'Larry', 'Justin', 'Scott', 'Brandon', 'Benjamin',
        #              'Samuel', 'Gregory', 'Alexander', 'Patrick', 'Frank', 'Raymond', 'Jack', 'Dennis', 'Jerry', 'Tyler']
        
        # female_names = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen',
        #                'Lisa', 'Nancy', 'Betty', 'Margaret', 'Sandra', 'Ashley', 'Kimberly', 'Emily', 'Donna', 'Michelle',
        #                'Carol', 'Amanda', 'Dorothy', 'Melissa', 'Deborah', 'Stephanie', 'Rebecca', 'Sharon', 'Laura', 'Cynthia',
        #                'Amy', 'Angela', 'Helen', 'Anna', 'Brenda', 'Pamela', 'Nicole', 'Emma', 'Samantha', 'Katherine',
        #                'Christine', 'Debra', 'Rachel', 'Catherine', 'Carolyn', 'Janet', 'Ruth', 'Maria', 'Heather', 'Diane']
        
        # other_names = ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Avery', 'Quinn', 'Skylar', 'Parker',
        #               'Sam', 'Drew', 'Blake', 'Charlie', 'Sage', 'Remy', 'Winter', 'River', 'Robin', 'Storm',
        #               'Phoenix', 'Salem', 'Raven', 'Ash', 'Aiden', 'Eden', 'Nova', 'Rowan', 'Blair', 'Lennon',
        #               'Oakley', 'Reese', 'Finley', 'Jules', 'Arden', 'Milan', 'Lennox', 'Remy', 'Marlowe', 'Alix',
        #               'Sky', 'Ocean', 'Sage', 'Rain', 'August', 'Brook', 'Dawn', 'Vale', 'West', 'North']

        # last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
        #              'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
        #              'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
        #              'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
        #              'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts',
        #              'Chen', 'Wong', 'Kumar', 'Singh', 'Patel', 'Evans', 'Edwards', 'Collins', 'Stewart', 'Morris',
        #              'Murphy', 'Cook', 'Rogers', 'Morgan', 'Peterson', 'Cooper', 'Reed', 'Bailey', 'Bell', 'Gomez',
        #              'Kelly', 'Howard', 'Ward', 'Cox', 'Diaz', 'Richardson', 'Wood', 'Watson', 'Brooks', 'Bennett',
        #              'Gray', 'James', 'Reyes', 'Cruz', 'Hughes', 'Price', 'Myers', 'Long', 'Foster', 'Sanders',
        #              'Ross', 'Morales', 'Powell', 'Sullivan', 'Russell', 'Ortiz', 'Jenkins', 'Gutierrez', 'Perry', 'Butler']

        # # Add name and ID columns based on gender
        # df['id_number'] = [random.randint(100000000, 999999999) for _ in range(len(df))]
        # df['full_name'] = df.apply(lambda row: f"{random.choice(male_names)} {random.choice(last_names)}" if row['gender'] == 'Male'
        #                           else f"{random.choice(female_names)} {random.choice(last_names)}" if row['gender'] == 'Female'
        #                           else f"{random.choice(other_names)} {random.choice(last_names)}", axis=1)

        def calculate_bmi(weight, height_cm):
            height_m = height_cm / 100
            return round(weight / (height_m ** 2), 1)

        def estimate_body_fat(bmi, age, gender):
            if gender == 'Male':
                body_fat = 1.15 * bmi + 0.20 * age - 17.0
            elif gender == 'Female':
                body_fat = 1.15 * bmi + 0.20 * age - 6.0
            else:
                body_fat = 1.15 * bmi + 0.20 * age - 11.5
            return round(min(max(body_fat, 5), 45), 1)

        def estimate_vo2_max(age, rhr, gender, intensity):
            max_hr = 220 - age
            base_vo2 = 15 * (max_hr / rhr)

            if gender.lower() == 'female':
                base_vo2 *= 0.9
            elif gender.lower() == 'other':
                base_vo2 *= 0.95

            intensity_factor = {'Low': 0.85, 'Medium': 1.0, 'High': 1.15}
            base_vo2 *= intensity_factor.get(intensity, 1.0)
            base_vo2 *= random.uniform(0.95, 1.05)

            return round(min(max(base_vo2, 20), 80), 1)

        # Ensure float dtype
        df['weight'] = df['weight'].astype(float)

        # Generate realistic weight → derive BMI, body fat, VO2
        for index, row in df.iterrows():
            height_m = row['height'] / 100

            # Generate a realistic weight from BMI ~ N(24, 3)
            target_bmi = np.clip(np.random.normal(loc=24, scale=3), 18.5, 32)
            weight = round(target_bmi * (height_m ** 2), 1)

            df.at[index, 'weight'] = weight
            df.at[index, 'bmi'] = calculate_bmi(weight, row['height'])

            body_fat = estimate_body_fat(df.at[index, 'bmi'], row['age'], row['gender'])
            df.at[index, 'body_fat'] = body_fat

            vo2_max = estimate_vo2_max(
                age=row['age'],
                rhr=row['resting_heart_rate'],
                gender=row['gender'],
                intensity=row['workout_intensity']
            )
            df.at[index, 'VO2_max'] = vo2_max

        # Save it
        df.to_csv('data/workout_fitness_tracker_data_updated.csv', index=False)
        print("Data updated and saved.")

        # Print descriptive statistics for key health columns
        print("\n=== Descriptive Statistics ===")
        print(df[['age', 'height', 'weight', 'bmi', 'VO2_max', 'body_fat']].describe())

        # Value counts for categorical columns
        print("\n=== Workout Intensity Distribution ===")
        print(df['workout_intensity'].value_counts())

        print("\n=== Gender Distribution ===")
        gender_counts = df['gender'].value_counts()
        print(gender_counts)
        
        # Check if we have enough data for both groups
        male_other_count = gender_counts.get('Male', 0) + gender_counts.get('Other', 0)
        female_count = gender_counts.get('Female', 0)
        
        print(f"\nTraining data split:")
        print(f"Male/Other users: {male_other_count}")
        print(f"Female users: {female_count}")
        
        if male_other_count == 0 or female_count == 0:
            logger.error("Not enough users in both gender groups for separate models!")
            return

        print("\n=== Mood Before Workout Distribution ===")
        print(df['mood_before_workout'].value_counts())

        print("\n=== Mood After Workout Distribution ===")
        print(df['mood_after_workout'].value_counts())

        # Correlation between BMI and body fat, and BMI vs. VO2 max
        print("\n=== Correlation Matrix (Health Metrics) ===")
        print(df[['bmi', 'body_fat', 'VO2_max']].corr())

        logger.info("Initializing recommender system...")
        recommender = UserRecommender()

        # Training the model
        logger.info("Training model with separate gender groups...")
        # Get the absolute path to the project root directory
        csv_path = os.path.join('data', 'workout_fitness_tracker_data_updated.csv')
        recommender.train(csv_path)

        # Save the model after training
        recommender.save_model()
        logger.info("Model training completed and saved successfully!")

        # Print model information
        model_info = recommender.get_model_info()
        logger.info(f"Model info: {model_info}")

        # Define a sample user profile for finding similar users
        user_profile = {
            'age': 25,
            'full_name': 'John Smith',
            'id_number': 207298720,
            'gender': 'Male',
            'height': 180,
            'weight': 70,
            'daily_calories_intake': 2500,
            'resting_heart_rate': 65,
            'VO2_max': 45,
            'body_fat': 18,
            'bmi': 22
        }

        # Finding similar users
        logger.info("Finding similar users for the provided profile...")
        distances, id_numbers = recommender.find_similar_users(user_profile, 15)

        if not id_numbers:
            logger.warning("No similar users found.")
            return

        # Get the user IDs of similar users
        logger.info(f"Distances: {distances}")
        logger.info(f"Indices of similar users: {id_numbers}")

        # Load the dataset and filter similar users
        df = pd.read_csv('data/workout_fitness_tracker_data_updated.csv')
        similar_users_data = df[df['id_number'].isin(id_numbers)]

        logger.info("Dataset for similar users:")
        print(similar_users_data[['id_number', 'full_name', 'gender', 'age', 'bmi', 'VO2_max', 'body_fat']])
        
        # Show gender distribution in recommendations
        gender_dist = similar_users_data['gender'].value_counts()
        logger.info("Gender distribution in recommendations:")
        for gender, count in gender_dist.items():
            logger.info(f"{gender}: {count}")

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        traceback.print_exc()
        raise

def test_loaded_model():
    """Test that the saved model can be loaded and used correctly."""
    try:
        logger.info("\nTesting saved model...")
        test_recommender = UserRecommender()
        test_recommender.load_model()
        logger.info("Model loaded successfully!")
        
        # Print model info
        model_info = test_recommender.get_model_info()
        logger.info(f"Loaded model info: {model_info}")
        
        df = pd.read_csv('data/workout_fitness_tracker_data_updated.csv')
        test_recommender.raw_df = df  # Set raw_df for the loaded model
        test_recommender.explore_data(df, n_clusters=3)

        # Test with multiple user profiles to verify balanced recommendations
        test_profiles = [
            {
                'age': 25,
                'full_name': 'John Smith',
                'id_number': 207298720,
                'gender': 'Male',
                'height': 180,
                'weight': 70,
                'daily_calories_intake': 2500,
                'resting_heart_rate': 65,
                'VO2_max': 45,
                'body_fat': 15,
                'bmi': 23
            },
            {
                'age': 30,
                'full_name': 'Jane Doe',
                'id_number': 207298721,
                'gender': 'Female',
                'height': 165,
                'weight': 60,
                'daily_calories_intake': 2200,
                'resting_heart_rate': 70,
                'VO2_max': 40,
                'body_fat': 22,
                'bmi': 22
            },
            {
                'age': 35,
                'full_name': 'Alex Johnson',
                'id_number': 207298722,
                'gender': 'Other',
                'height': 175,
                'weight': 75,
                'daily_calories_intake': 2400,
                'resting_heart_rate': 68,
                'VO2_max': 42,
                'body_fat': 20,
                'bmi': 24
            }
        ]

        for i, test_profile in enumerate(test_profiles):
            logger.info(f"\nTesting inference with profile {i+1} ({test_profile['gender']})...")
            distances, ids = test_recommender.find_similar_users(test_profile, k=10)

            similar_users_data = df[df['id_number'].isin(ids)]

            gender_counts = similar_users_data['gender'].value_counts()
            logger.info("Gender distribution among similar users:")
            for gender, count in gender_counts.items():
                logger.info(f"{gender}: {count}")

            logger.info("Model test results:")
            logger.info(f"Found {len(distances)} similar users")
            logger.info(f"Average distance: {np.mean(distances):.3f}")
        
        return True

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error testing loaded model: {e}")
        return False


if __name__ == "__main__":
    train_and_save_model()
    # Add a pause between training and testing
    logger.info("\nWaiting a moment before testing loaded model...")
    time.sleep(2)
    # Test the loaded model
    test_loaded_model()
