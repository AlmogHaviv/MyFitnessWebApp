from backend.models_training_pipeline.llm_workout_recs.llm_model_open_ai_api import WorkoutRecommender

def main():
    recommender = WorkoutRecommender(
        user_profile={
            "age": 25,
            "weight": 75,
            "gender": "male",
            "height": 180,
            "daily_calories_intake": 2500,
            "resting_heart_rate": 65,
            "VO2_max": 45,
            "body_fat": 18
        },
        query="I want to learn proper form for deadlifts and squats"
    )

    try:
        recommendations = recommender.workout_urls_and_explanations()
        print("\nRecommended workouts:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. Workout Video")
            print(f"URL: {rec['url']}")
            print(f"Explanation: {rec['explanation']}")
            print(f"Required Equipment: {', '.join(rec['equipment'])}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()