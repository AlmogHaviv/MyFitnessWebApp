# MyFitnessWebApp Backend - Getting Started

## 1. Set Up and Activate a Virtual Environment

```bash
cd backend
```

One time setup: run only once:
```bash
python -m venv venv
```
Run always:
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```



## 3. Set Up MongoDB (Required for Backend to Work)
If its your first time, go to [atlas Mongo](https://cloud.mongodb.com/v2/67e6b4e83a7e692ce4f84747#/setup/access) and enter the tab of security quickstart. Once inside, scroll down to `Add entries to your IP Access List` and click Add My Current IP Address.
#### NOTE: All of this should happend udner project 0.


## 4. Set Up OpenRouter API (for LLM Usage in the workout reccomeder)

You need to:

1. Create a free account at [OpenRouter](https://openrouter.ai/)
2. Generate an API key from your OpenRouter dashboard
3. Add the API key to the models_training_pipeline\llm_workout_recs\llm_model_open_ai_api.py as an input - change the dummy string

### Do not push any code with your API key!!! If you will, open router will block the key and you will need to create a new one
Run the example script to test LLM usage:
```bash
python python models_training_pipeline/llm_workout_recs/example_llm_usage.py 
```

Notice- if you are getting:
```bash
OpenRouter API call failed: Error code: 429
```
then you need to wait a day before calling the llm again - due to free quota limitations!

or if you want, create another account (not just a key) and repeat steps 1-3 again.
 

## 5. Run the FastAPI Server

```bash
uvicorn app.main:app --reload
```


## 6. Verify the API
Open [http://localhost:8000/docs](http://localhost:8000/docs) to access the FastAPI documentation.

Or follow the front end readme to fully set up the web application (run all FE commands in a different Tab)


## Accessing MongoDB Data
If you're using the remote MongoDB cluster, follow these steps to verify the data:

Go to your MongoDB [Atlas dashboard](https://cloud.mongodb.com/v2/67e6b4e83a7e692ce4f84747#/overview).

Navigate to your workout_app database enter the needed collection.

