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


Now you're ready to build and extend the backend! 🚀

