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

### Option 1: Use Local MongoDB
- Ensure MongoDB is installed and running on `localhost:27017`.
- If not installed, download and install from [MongoDB Official Site](https://www.mongodb.com/try/download/community).

### Option 2: Use Docker (Recommended)
If you don’t want to install MongoDB manually, run:
```bash
docker run -d --name mongodb -p 27017:27017 mongo
```
If you haven't installed Docker yet, download it from [Docker Official Site](https://www.docker.com/get-started).

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

