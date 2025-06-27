# MyFitnessWebApp

### **1. Introduction**
**Objective:**
The goal of this project is to build a personalized workout recommendation system that suggests relevant exercises based on user input and feedback. The system will improve recommendations over time using a machine learning model trained on user preferences and performance.

**Scope:**
- A web application with a frontend in TypeScript and a backend in Python.
- A machine learning model that generates workout recommendations based on user data and feedback.
- A database to store user profiles, workout logs, and feedback.

---

### **2. How to Run the Project (Backend + Frontend)**

#### **Clone the Repository**

```bash
git clone <repo-url>
cd MyFitnessWebApp
```

To run the full application, you need to start both the backend and the frontend servers.  
**Each part has its own README file with detailed setup instructions:**

- **Backend:**  
  See [`backend/README.md`](./backend/README.md) for instructions on setting up the Python FastAPI backend, installing dependencies, configuring MongoDB, and running the server.

- **Frontend:**  
  See [`frontend/README.md`](./frontend/README.md) for instructions on setting up the React + TypeScript frontend, installing dependencies, and running the development server.

**Quick Start:**

1. **Backend**
   ```bash
   cd backend
   # Follow backend/README.md for environment setup and dependencies
   uvicorn app.main:app --reload
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser to use the app.

---

### **3. System Architecture**
**Overview:**
The system follows a client-server architecture where the frontend communicates with the backend via REST APIs. The backend processes user data and invokes the machine learning model to generate recommendations.

#### **Tech Stack:**
- **Frontend:** TypeScript (React)
- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL/MySQL
- **ML Frameworks:** Scikit-learn/TensorFlow/PyTorch
- **Hosting:** Localhost (for now)

#### **Component Breakdown:**
1. **Frontend:** 
   - **Login Page:** Allows users to log in using their ID number ([`LoginPage.tsx`](frontend/src/components/pages/LoginPage.tsx)).
   - **Landing Page:** Form for new users to enter profile details and register ([`LandingPage.tsx`](frontend/src/components/pages/LandingPage.tsx)).
   - **Main Page:** 
     - Displays recommended fitness buddies and similar users with filters for gender, workout type, and age ([`MainPage.tsx`](frontend/src/components/pages/MainPage.tsx)).
     - Allows users to like/dislike buddies and view contact info.
     - Lets users enter a fitness goal to receive personalized workout video recommendations.
   - **Recommendations Page:** Shows personalized workout video recommendations based on the user’s fitness goal and LLM model ([`RecommendationsPage.tsx`](frontend/src/components/pages/RecommendationsPage.tsx)).
   - **API Services:** Handles all API requests to the backend ([`api.ts`](frontend/src/services/api.ts)).

2. **Backend:**
   - **User API:** Endpoints for user registration, authentication, and profile management ([`app/api/user.py`](backend/app/api/user.py)).
   - **Workout API:** Endpoints to log user workout preferences and workout logs ([`app/api/user.py`](backend/app/api/user.py)).
   - **Recommendation API:** Endpoints for recommending buddies and generating personalized workout recommendations ([`app/api/recommendation.py`](backend/app/api/recommendation.py), [`app/api/workoutRecommendations.py`](backend/app/api/workoutRecommendations.py)).
   - **Database Layer:** MongoDB integration for storing users, workouts, and events ([`database.py`](backend/app/database.py)).
   - **ML Model Integration:** Loads and serves collaborative filtering, SVD, and XGBoost models for recommendations ([`models/`](backend/models/), [`models_training_pipeline/`](backend/models_training_pipeline/)).
   - **LLM Integration:** Uses OpenRouter API for LLM-based workout video recommendations ([`models_training_pipeline/llm_workout_recs/`](backend/models_training_pipeline/llm_workout_recs/)).
   - **Event Logging:** Stores user interactions (like/dislike) for feedback and model retraining.

3. **Machine Learning Model:**
   - **Training Pipelines:** Includes KNN, SVD, matrix factorization, and XGBoost-based reranker models for generating and refining recommendations ([`models_training_pipeline/`](backend/models_training_pipeline/)).
   - **Model Files:** Stores trained model artifacts such as embeddings, scalers, and serialized models ([`models/`](backend/models/)).
   - **LLM Integration:** Uses OpenRouter API and custom logic to generate personalized workout video explanations ([`models_training_pipeline/llm_workout_recs/`](backend/models_training_pipeline/llm_workout_recs/)).
   - **Data Preprocessing:** Loads and processes user, workout, and event data from MongoDB for model training ([`xgboosting/data_preprocessor.py`](backend/models_training_pipeline/xgboosting/data_preprocessor.py)).
   - **Evaluation:** Implements metrics such as Precision@K and MSE for model validation and selection.
   - **Continuous Improvement:** Models are retrained and updated based on new user interactions and feedback.

4. **Database:**
   - **MongoDB:** Stores all persistent data for the application.
   - **Collections:**
     - `users`: User profiles (age, gender, fitness metrics, etc.).
     - `workout`: User workout preferences and logs.
     - `events`: User interactions (like/dislike) for feedback and model retraining.
   - **Integration:** Accessed asynchronously via Motor in the backend ([`database.py`](backend/app/database.py)).
   - **Data Loading:** Supports initial population from CSV and ongoing updates via API endpoints.
   - **Usage:** Serves as the source of truth for both the web application and ML pipelines.

---

### **4. Code Implementation Plan**

#### **Step 1: Project Setup**
- Initialize a monorepo for frontend and backend.
- Setup React for frontend and FastAPI for backend.
- Configure database and API endpoints.

#### **Step 2: Frontend Implementation**
- **Landing Page:** Form for user data entry and account creation.
- **Home Page:** 
  - Dashboard displaying recommended workouts.
  - Workout logging feature.
  - Like/dislike buttons for feedback collection.

#### **Step 3: Backend Implementation**
- Implement API for user registration and authentication.
- Develop API endpoints for:
  - Fetching user profiles.
  - Fetching and updating workout recommendations.
  - Logging workouts and feedback.
- Implement database schema and ORM models.

#### **Step 4: Machine Learning Model Development**
- **Data Processing:**
  - Preprocess user data (e.g., normalize age, encode fitness levels).
  - Store feedback to improve model training.
- **Model Training:**
  - Use collaborative filtering or a hybrid model (content-based + collaborative filtering).
  - Train on initial dataset, then refine with real user interactions.
- **Model Deployment:**
  - Serve the trained model using FastAPI.
  - Expose an API for recommendations.

#### **Step 5: Integration and Testing**
- Integrate frontend with backend APIs.
- Conduct unit testing on APIs and ML model.
- Test user flows and refine UI/UX.

#### **Step 6: Deployment and Monitoring**
- Deploy backend on localhost.
- Deploy frontend using local server.
- Set up logging and monitoring for API requests and ML model performance.

---

### **5. Future Improvements**
- Improve ML model with reinforcement learning.
- Add support for workout video recommendations.
- Implement social features (friends, challenges, etc.).
- Expand to mobile applications.

---

### **6. Conclusion**
This MVP aims to provide personalized workout recommendations based on user input and feedback. The system will leverage a machine learning model for continuous improvement, offering a dynamic and engaging experience for users. Future iterations will enhance personalization and introduce additional features to optimize user engagement and effectiveness.

