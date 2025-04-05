import pandas as pd
import logging
from user_recommender import UserRecommender
import random
import os
import time
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_and_save_model():
    """Train the recommender system, save the model, and find similar users."""
    try:
        # # block of code to generate random names, bmi, vo2_max and body fat and id_numbers
        # # Load the real data
        # df = pd.read_csv('data/workout_fitness_tracker_data.csv')

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
        
        # # Add BMI column
        # height_in_meters = df['height'] / 100
        # df['bmi'] = (df['weight'] / (height_in_meters ** 2)).round(1)

        # # Adjust body fat based on BMI
        # for index, row in df.iterrows():
        #     bmi = row['bmi']
        #     if bmi < 18.5:
        #         df.at[index, 'body_fat'] = random.uniform(5, 12)
        #     elif 18.5 <= bmi <= 24.9:
        #         df.at[index, 'body_fat'] = random.uniform(9, 18)
        #     elif 25.0 <= bmi <= 29.9:
        #         df.at[index, 'body_fat'] = random.uniform(15, 25)
        #     else: # BMI >= 30
        #         df.at[index, 'body_fat'] = random.uniform(23, 45)
        # df['body_fat'] = df['body_fat'].round(1)

        # # Adjust VO2 max values
        # for index, row in df.iterrows():
        #     age = row['age']
        #     gender = row['gender']
        #     rhr = row['resting_heart_rate']
        #     intensity = row['workout_intensity']
            
        #     max_hr = 220 - age
        #     base_vo2 = 15 * (max_hr / rhr)
            
        #     if gender.lower() == 'female':
        #         base_vo2 *= 0.9
            
        #     intensity_factor = {
        #         'Low': 0.85,
        #         'Medium': 1.0,
        #         'High': 1.15
        #     }
        #     base_vo2 *= intensity_factor.get(intensity, 1.0)
            
        #     variation = random.uniform(0.95, 1.05)
        #     final_vo2 = base_vo2 * variation
        #     final_vo2 = max(20, min(80, final_vo2))
        #     df.at[index, 'VO2_max'] = round(final_vo2, 1)

        # # Save updated data back to CSV
        # df.to_csv('data/workout_fitness_tracker_data.csv', index=False)
        # processed_df = df.copy()

        logger.info("Initializing recommender system...")
        recommender = UserRecommender()

        # Training the model
        logger.info("Training model...")
        # Get the absolute path to the project root directory
        csv_path = os.path.join('data', 'workout_fitness_tracker_data.csv')
        recommender.train(csv_path)

        # Save the model after training
        recommender.save_model()
        logger.info("Model training completed and saved successfully!")

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
            'body_fat': 15
        }

        # Finding similar users
        logger.info("Finding similar users for the provided profile...")
        distances, id_numbers = recommender.find_similar_users(user_profile)

        if not id_numbers:
            logger.warning("No similar users found.")
            return

        # Get the user IDs of similar users (assuming indices map directly to user IDs)
        logger.info(f"Distances: {distances}")
        logger.info(f"Indices of similar users: {id_numbers}")

        # Load the dataset and filter similar users
        df = pd.read_csv('data/workout_fitness_tracker_data.csv')
        similar_users_data = df[df['id_number'].isin(id_numbers)]

        logger.info("Dataset for similar users:")
        print(similar_users_data)

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise


def test_loaded_model():
    """Test that the saved model can be loaded and used correctly."""
    try:
        logger.info("\nTesting saved model...")
        test_recommender = UserRecommender()
        test_recommender.load_model()
        logger.info("Model loaded successfully!")

        # Test with the same user profile
        test_profile = {
            'age': 25,
            'full_name': 'John Smith',
            'id_number': 207298720,
            'gender': 'Male',
            'height': 180,
            'weight': 70,
            'daily_calories_intake': 2500,
            'resting_heart_rate': 65,
            'VO2_max': 45,
            'body_fat': 15
        }

        logger.info("Testing inference with loaded model...")
        distances, id_numbers = test_recommender.find_similar_users(test_profile)
        
        logger.info("Model test results:")
        logger.info(f"Found {len(distances)} similar users")
        logger.info(f"Distances: {distances[:5]}")  # Show first 5 distances
        logger.info(f"User IDs: {id_numbers[:5]}")  # Show first 5 IDs
        
        return True

    except Exception as e:
        logger.error(f"Error testing loaded model: {e}")
        return False


if __name__ == "__main__":
    train_and_save_model()
    # Add a pause between training and testing
    logger.info("\nWaiting a moment before testing loaded model...")
    time.sleep(2)
    # Test the loaded model
    test_loaded_model()
