# MyFitnessWebApp


### **1. Introduction**
**Objective:**
The goal of this project is to build a personalized workout recommendation system that suggests relevant exercises based on user input and feedback. The system will improve recommendations over time using a machine learning model trained on user preferences and performance.

**Scope:**
- A web application with a frontend in TypeScript and a backend in Python.
- A machine learning model that generates workout recommendations based on user data and feedback.
- A database to store user profiles, workout logs, and feedback.

---

### **2. System Architecture**
**Overview:**
The system follows a client-server architecture where the frontend communicates with the backend via REST APIs. The backend processes user data and invokes the machine learning model to generate recommendations.

#### **Tech Stack:**
- **Frontend:** TypeScript (Reacts)
- **Backend:** Python (FastAPI)
- **Database:** PostgreSQL/MySQL
- **ML Frameworks:** Scikit-learn/TensorFlow/PyTorch
- **Hosting:** Localhost (for now)

#### **Component Breakdown:**
1. **Frontend:** 
   - User authentication and profile setup.
   - Dashboard to display recommendations and collect user feedback.
   - Workout logging interface.

2. **Backend:**
   - API for user authentication and data retrieval.
   - API for workout recommendations.
   - API to log workouts and feedback.
   - Integration with the ML model for personalized recommendations.

3. **Machine Learning Model:**
   - Training pipeline to process user data and generate workout recommendations.
   - Model evaluation and continuous improvement based on feedback.

4. **Database:**
   - Stores user profiles (age, fitness level, preferences, etc.).
   - Stores workout logs and user feedback.
   - Stores recommendation history for model retraining.

---

### **3. Code Implementation Plan**

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

### **4. How to Start Working on the Project**

#### **Frontend (React + TypeScript)**
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd MyFitnessWebApp/frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open `http://localhost:3000` in your browser.

#### **Backend (FastAPI)**
 - check backend README

---

### **5. Future Improvements**
- Improve ML model with reinforcement learning.
- Add support for workout video recommendations.
- Implement social features (friends, challenges, etc.).
- Expand to mobile applications.

---

### **6. Conclusion**
This MVP aims to provide personalized workout recommendations based on user input and feedback. The system will leverage a machine learning model for continuous improvement, offering a dynamic and engaging experience for users. Future iterations will enhance personalization and introduce additional features to optimize user engagement and effectiveness.

