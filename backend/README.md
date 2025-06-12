# MyFitnessWebApp Backend - Getting Started

## 1. Set Up and Activate a Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Set Up MongoDB (Required for Backend to Work)
### If its your first time, go to [atlas Mongo](https://cloud.mongodb.com/v2/67e6b4e83a7e692ce4f84747#/setup/access) and enter the tab of security quickstart. Once inside, scroll down to `Add entries to your IP Access List` and click Add My Current IP Address.
### NOTE: All of this should happend uner project 0.

 
## 4. Run the FastAPI Server

```bash
uvicorn app.main:app --reload
```

## 5. Verify the API
Open [http://localhost:8000/docs](http://localhost:8000/docs) to access the FastAPI documentation.

## 6.  Accessing MongoDB Data
If you're using the remote MongoDB cluster, follow these steps to verify the data:

Go to your MongoDB [Atlas dashboard](https://cloud.mongodb.com/v2/67e6b4e83a7e692ce4f84747#/overview).

Navigate to your workout_app database enter the needed collection.
## 7. Connect to Hugging Face (for LLM Usage)

To use the Hugging Face model locally (required for features like video recommendation and explanation):

1. **Install the Hugging Face CLI** (if you haven’t already):

   ```bash
   pip install huggingface_hub
   ```

Log in via the CLI:

 ```bash

huggingface-cli login
```

This will prompt you for a Hugging Face access token. You can generate a personal access token from your Hugging Face account settings.

Run the example script to test LLM usage:
```bash
python example_llm_usage.py
```

This will verify that your authentication works and that the model (declare-lab/flan-alpaca-gpt4-xl) loads correctly.

Note: If you're running in an environment that does not allow direct downloads or model hosting (e.g., restricted servers), you may need to manually download and cache the model beforehand.

## 8. Set Up OpenRouter API (for LLM Usage in the workout reccomeder)

You need to:

1. Create a free account at [OpenRouter](https://openrouter.ai/)
2. Generate an API key from your OpenRouter dashboard
3. Add the API key to the models_training_pipeline\llm_workout_recs\llm_model_open_ai_api.py as an input - change the dummy string

Now you're ready to build and extend the backend! 🚀

