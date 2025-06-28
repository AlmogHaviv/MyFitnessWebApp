**You should change the content of this file. Please use all second-level headings.**

# Project Summary

## Datasets Used

- **Dataset 1** — Workout & Fitness Tracker Dataset, Sport, [link to repository](https://www.kaggle.com/datasets/adilshamim8/workout-and-fitness-tracker-data/data).

Additional data-related information:

- We enahnced Dataset1 using preprocessor in order enrich the dataset with BMI and body fat.
- We manually created **Dataset 2** by generating 750,000 interactions between the users in Dataset 1.


&nbsp;<br>

## Technologies and Frameworks

### Frontend

This frontend is a modern React application built with TypeScript. 
It uses React Router DOM for client-side routing, Material-UI (MUI) for the user interface, and Axios for API communication.
 The project follows a component-based architecture with a service layer for backend interaction and adheres to best practices with strict TypeScript configuration.

- **React** —  for building user interfaces
- **React Router DOM** — for client-side routing and navigation
- **Material-UI (MUI)** — for react component library implementing Google's Material Design
- **Axios** - for making HTTP requests to the backend API


### Backend

This backend is a modern, scalable API built with FastAPI and designed to handle fitness-related data and recommendation services.
It uses MongoDB for data storage, supports asynchronous operations via async/await, and relies on Pydantic for data validation.
The architecture is modular, with separate routers for key functionalities, and follows best practices for API development.

- **FastAPI** — for building high-performance Python web APIs
- **MongoDB** — NoSQL database, integrated with async drivers (Motor, PyMongo)
- **Pydantic** — for request/response validation using Python type hints
- **HTTPX / Requests** — for making outbound HTTP calls
- **Uvicorn** — ASGI server used to run the FastAPI app
- **Python-dotenv** — for managing environment variables
- **CORS Middleware** — enables communication between frontend and backend
- **YouTube API** — for retriving data from yotube


### Algorithmic

### **Machine Learning Stack**
- **scikit-learn** — K-Nearest Neighbors, SVD decomposition, preprocessing (StandardScaler, LabelEncoder)
- **XGBoost** — Gradient boosting for recommendation reranking with hyperparameter optimization
- **PyTorch** — Neural network implementation for matrix factorization
- **NumPy/Pandas** — Data manipulation and numerical computations

### **Recommendation Pipeline**
1. **Content-Based Filtering**: K-NN finds physiologically similar users
2. **Collaborative Filtering**: SVD discovers latent preferences from interactions
3. **Hybrid Reranking**: XGBoost combines multiple signals for optimal ranking
4. **Contextual Enhancement**: Recent interaction history and workout type preferences

### **Evaluation Metrics**
- **NDCG@K**: Normalized Discounted Cumulative Gain for ranking quality
- **Precision/Recall**: Binary classification performance
- **ROC-AUC**: Model discrimination ability
- **F1-Score**: Balanced precision-recall measure

### **Data Processing**
- **Feature Engineering**: BMI calculation, gender encoding, feature scaling
- **Interaction Generation**: Synthetic user-buddy interactions using compatibility scoring
- **Real-time Filtering**: Age range, gender, and workout type filtering

## AI

### **Large Language Models**
- **Integration**: OpenRouter API for cost-effective access
- **Applications**:
  - Natural language query understanding
  - Personalized workout video analysis
  - Video content explanation generation

### **Natural Language Processing**
- **Query Processing**: Converts user fitness goals into optimized YouTube search queries
- **Content Analysis**: Analyzes video titles, descriptions, and transcripts
- **Explanation Generation**: Creates personalized workout explanations

### **YouTube Integration**
- **YouTube Data API v3** — Video search and metadata retrieval
- **Transcript Analysis**: Automatic transcript extraction and processing
- **Multi-language Support**: Handles videos with non-English transcripts

### **AI-Powered Features**
- **Smart Query Enhancement**: LLM improves user queries for better video discovery
- **Contextual Recommendations**: Considers user profile and recent preferences
- **Equipment Intelligence**: Automatically identifies required workout equipment
- **Difficulty Assessment**: Analyzes workout complexity based on user fitness level

&nbsp;<br>

## Main Algorithms

Our fitness buddy recommendation system implements a sophisticated multi-algorithm approach combining collaborative filtering, content-based filtering, and machine learning techniques:

### 1. **K-Nearest Neighbors (K-NN) - Content-Based Filtering**
- **Purpose**: Find similar users based on physiological and fitness characteristics
- **Features**: Age, gender, height, weight, daily calories intake, resting heart rate, VO2_max, body fat, BMI
- **Implementation**: Separate models for male/other and female users to ensure gender diversity
- **Distance Metric**: Euclidean distance with feature weighting
- **Output**: Top 6 similar fitness buddies

### 2. **Singular Value Decomposition (SVD) - Collaborative Filtering**
- **Purpose**: Matrix factorization to discover latent user-buddy preferences
- **Components**: 20 latent factors for user and buddy embeddings
- **Training**: Uses user-buddy interaction matrix (likes/dislikes)
- **Performance**: 
  - MSE: 0.4619
  - Accuracy: 0.2241
  - precision: 0.2204
  - recall: 0.9964
  - f1_score: 0.3610
  - roc_auc: 0.5460
  - NDCG@6: 0.6579
  - NDCG@10: 0.6070
- **Output**: Top 3 recommended buddies

### 3. **XGBoost Reranker - Hybrid Approach**
- **Purpose**: Rerank and optimize recommendations using advanced features
- **Features**: 
  - Compatibility score (workout type matching, physiological similarity)
  - Same workout type indicator
  - Last liked workout types (contextual preferences)
  - User-buddy interaction patterns
- **Hyperparameter Tuning**: RandomizedSearchCV with NDCG@10 optimization
- **Performance**:
  - Accuracy: 0.9064
  - Precision: 0.8831
  - Recall: 0.6635
  - F1-Score: 0.7577
  - ROC-AUC: 0.9386
  - NDCG@6: 0.8954
  - NDCG@10: 0.9222


### 5. **LLM-Powered Workout Recommendations**
- **Model**: meta-llama/llama-3.1-8b-instruct via OpenRouter API
- **Purpose**: Generate personalized workout video recommendations
- **Features**: 
  - User profile analysis
  - Natural language query processing
  - YouTube video search and analysis
  - Equipment requirement identification
- **Output**: Curated workout videos with explanations and equipment lists

&nbsp;<br>

## Development Environment
- **Cursor** - used for the UI development
- **VSCode + Claude + stackOverflow + youtube + friends at Amazon and Nice** - used for the algorithmic modules

&nbsp;<br>

## Development Evolution

Describe the main stages of your system development, major changes, and lessons learned.


- **Milestone 1:** Initial prototype with K-NN based model and static workout and equipmenet recommendations.
- **Milestone 2:** Adding Collaborative filtering (SVD) model after examin both pytorch (NN with 1 hidden layer to mimic SVD).
- **Milestone 3:** Integrated workout search bar using hugging face to download and host "declare-lab/flan-alpaca-gpt4-xl" model, latecny was very bad even with parallel queries.
- **Milestone 4:** Created xgboost model to replace the K-NN seeing tremendous improvmentes in NDCG@10 and NDCG@6 from 0.56 to .
- **Milestone 5:** Moved from hugging face to OpenAI api using open_router_api_key.
- **Milestone 6:** Changed the xgboost to be model on top of the K-nn as a reranker, used RandomizedSearchCV to peak the best feataures improved metrics tremendous.
- **Milestone 7:** Added filter to froned in order to filter recommendations.
- **Milestone 8:** Modified the underlying k-nn in order to support diversity and retrain the xgboost reranker metrcis stayed the same.



&nbsp;<br>

## Open Issues, Limitations, and Future Work

- Known limitations or challenges.
- Planned improvements.
- Potential next steps.

&nbsp;<br>

## Additional Comments

Any extra insights, difficulties, tricks, or interesting stories you want to share.

