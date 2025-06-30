# Installation Guide

This web application is hosted on [Render](https://render.com) using the free tier. As such, the backend may take **2–3 minutes to become responsive** if it hasn't been used recently.

You can try it out here:
👉 [https://myfitnesswebapp-frontend.onrender.com](https://myfitnesswebapp-frontend.onrender.com)

> **Tip:** Open the link above right away to start the backend warm-up process. Meanwhile, if you'd like to test the app thoroughly or develop locally, follow the instructions in the local deployment guide below.

---

## Local Deployment

If you'd like to run the application **locally**, follow the instructions in this guide. This setup allows you to develop, test, or customize the app on your own machine.


## Prerequisites

You will need:
* Python 3.8+ installed on your system
* Node.js 14+ and npm installed on your system
* Git for cloning the repository
* A MongoDB Atlas account (free tier available)
* An OpenRouter API account (free tier available for LLM features)

## Installation Steps

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <repo-url>
   cd MyFitnessWebApp
   ```

2. **Set up the Backend:**
   ```bash
   cd backend
   python -m venv venv # Run only once!
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt # If you are on MacOS, remove the winkerberos line from requirements.txt before running this command.
   ```

3. **Configure MongoDB:**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com/v2/67e6b4e83a7e692ce4f84747#/setup/access)
   - Navigate to Security Quickstart
   - Scroll down to "Add entries to your IP Access List"
   - Click "Add My Current IP Address"
   - Note: This should be done under project 0

4. **Set up OpenRouter API (for LLM workout recommendations):**
   - Create a free account at [OpenRouter](https://openrouter.ai/)
   - Generate an API key from your OpenRouter dashboard
   - Open `backend/models_training_pipeline/llm_workout_recs/llm_model_open_ai_api.py`
   - Replace the dummy API key with your actual OpenRouter API key
   - **Important:** Never commit your API key to version control

5. **Set up the Frontend:**
   ```bash
   cd ../frontend
   npm install
   ```

6. **Start the application:**
   - **Backend:** In the backend directory with venv activated:
     ```bash
     uvicorn app.main:app --reload
     ```
   - **Frontend:** In a new terminal tab, in the frontend directory:
     ```bash
     npm start
     ```

## Post‑install / Verification

* **Full Functionality Verification:** 
  - Open [http://localhost:3000](http://localhost:3000) in your browser
  - Test user registration: Click "SIGNUP" and fill out the profile form
  - Test user login: Use an existing ID number to log in
  - Test buddy recommendations: Like/dislike fitness buddies and view contact information
  - Test buddy recommendations: Change the filters and see you get the desired buddies
  - Test workout recommendations: Enter a fitness goal and receive personalized video recommendations
  - Test all navigation between pages and ensure the UI is responsive

* **Backend verification:** Open [http://localhost:8000/docs](http://localhost:8000/docs) to access the FastAPI documentation
* **Frontend verification:** Open [http://localhost:3000](http://localhost:3000) to view the application in your browser
* **LLM verification:** Test the LLM functionality by running:
  ```bash
  cd backend
  python models_training_pipeline/llm_workout_recs/example_llm_usage.py
  ```
* **Database verification:** Access your MongoDB Atlas dashboard to verify data is being stored correctly


## Troubleshooting

* **OpenRouter API Error 429:** This indicates you've exceeded the free quota. Wait 24 hours or create a new OpenRouter account and API key
* **MongoDB Connection Issues:** Ensure your IP address is whitelisted in MongoDB Atlas and you're using the correct connection string
* **Python Virtual Environment Issues:** Make sure you're activating the virtual environment before installing dependencies or running the backend
* **npm Install Failures:** Try clearing npm cache with `npm cache clean --force` and then run `npm install` again
* **API Key Security:** If you accidentally commit your API key, immediately regenerate new one in OpenRouter and update the code

