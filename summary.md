**You should change the content of this file. Please use all second-level headings.**

# Project Summary

## Datasets Used

- **Dataset 1** — Workout & Fitness Tracker Dataset, Sport, [link to repository](https://www.kaggle.com/datasets/adilshamim8/workout-and-fitness-tracker-data/data).

- Additional data-related information:
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
- **PyTorch** — Neural network implementation for matrix factorization (did not maded the cut to production)
- **NumPy/Pandas** — Data manipulation and numerical computations

### **Recommendation Pipeline**
1. **Content-Based Filtering**: K-NN finds physiologically similar users
2. **Collaborative Filtering**: SVD discovers latent preferences from interactions
3. **Hybrid Reranking with Contextual Enhancement**: XGBoost combines multiple signals—including recent interaction history and workout type preferences—for optimal ranking

### **Evaluation Metrics**
- **NDCG@K**: Normalized Discounted Cumulative Gain for ranking quality  
  - Formula:  
    $$\mathrm{NDCG@K} = \frac{DCG@K}{IDCG@K}$$  
    where  
    $$DCG@K = \sum_{i=1}^{K} \frac{rel_i}{\log_2(i+1)}$$  
    and $rel_i$ is the relevance of the item at position $i$, $IDCG@K$ is the maximum possible DCG (ideal ranking).
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
- **Content Analysis**: Analyzes video titles and descriptions
- **Explanation Generation**: Creates personalized workout explanations

### **YouTube Integration**
- **YouTube Data API v3** — Video search and metadata retrieval

### **AI-Powered Features**
- **Smart Query Enhancement**: LLM improves user queries for better video discovery
- **Contextual Recommendations**: Considers user profile and recent preferences

&nbsp;<br>

## Main Algorithms

Our fitness buddy recommendation system implements a sophisticated multi-algorithm approach combining collaborative filtering, content-based filtering, and machine learning techniques:

### 1. **K-Nearest Neighbors (K-NN) - Content-Based Filtering**
- **Purpose**: Find similar users based on physiological and fitness characteristics
- **Features**: Age, gender, height, weight, daily calories intake, resting heart rate, VO2_max, body fat, BMI
- **Implementation**: Separate models for male/other and female users to ensure gender diversity
- **Distance Metric**: Euclidean distance with feature weighting
- **Output**: Top 6 similar fitness buddies

### 2. **XGBoost Reranker - Contextual Hybrid Approach**
- **Purpose**: Rerank the initial K-NN recommendations by leveraging contextual features and the user's past interactions for more personalized results.
- **How it works**: The K-NN model first finds physiologically similar users. Then, XGBoost takes these candidates and reranks them using additional signals such as:
  - Compatibility score (workout type matching, physiological similarity)
  - Whether the workout type matches the user's recent preferences
  - Patterns in the user's previous likes/dislikes and interaction history
  - Contextual features (e.g., recent activity, workout type trends)
- **Hyperparameter Tuning**: RandomizedSearchCV with NDCG@10 as the optimization metric
- **Performance**:
  - Accuracy: 0.9064
  - Precision: 0.8831
  - Recall: 0.6635
  - F1-Score: 0.7577
  - ROC-AUC: 0.9386
  - NDCG@6: 0.8954
  - NDCG@10: 0.9222
- **Output**: Top 6 recommended buddies, reranked for optimal relevance

### 3. **Singular Value Decomposition (SVD) - Collaborative Filtering**
- **Purpose**: Matrix factorization to uncover latent user-buddy affinities, especially for users with sparse or ambiguous interaction histories.
- **How it complements XGBoost**: While the XGBoost reranker excels at precision and ranking the most relevant buddies at the top, it can struggle with recall—potentially missing out on less obvious but still relevant matches due to its focus on strong signals and boosting. The SVD model, by contrast, is highly effective at recall: it explores the full user-buddy interaction matrix and can surface buddies that XGBoost might overlook, ensuring that nearly all relevant candidates are considered. This is reflected in its extremely high recall (0.9964), meaning it rarely misses a possible match, even if its precision is lower.
- **Components**: 20 latent factors for user and buddy embeddings
- **Training**: Learns from the user-buddy interaction matrix (likes/dislikes)
- **Performance**: 
  - MSE: 0.4619
  - Accuracy: 0.2241
  - Precision: 0.2204
  - Recall: 0.9964  <!-- SVD "completes" the XGBoost by ensuring almost all relevant buddies are retrieved -->
  - F1-Score: 0.3610
  - ROC-AUC: 0.5460
  - NDCG@6: 0.6579
  - NDCG@10: 0.6070
- **Output**: Top 3 recommended buddies, often including candidates that XGBoost might miss, thus boosting overall system recall.

### 4. **LLM-Powered Workout Recommendations**
- **Model**: meta-llama/llama-3.1-8b-instruct via OpenRouter API
- **Purpose**: Generate personalized workout video recommendations based on a query
- **Features**: 
  - User profile analysis
  - Natural language query processing
  - YouTube video search and analysis
  - Equipment requirement identification
- **Output**: Curated workout videos with explanations and equipment lists

&nbsp;<br>

## Development Environment

- **Cursor**: Utilized primarily for UI development, enabling rapid prototyping and interface refinement.
- **VSCode**: Main editor for algorithmic development, offering robust support for Python and TypeScript.
- **Claude, Stack Overflow, YouTube**: Leveraged for troubleshooting, research, and learning best practices.
- **Collaboration**: Benefited from insights and advice from friends at Amazon and Nice, enriching both the design and implementation of core modules.

&nbsp;<br>

## Development Evolution

The development of the system progressed through several key milestones, each bringing significant improvements and valuable lessons:

- **Milestone 1:** Built the initial prototype using a K-NN-based model for buddy recommendations, along with static workout and equipment suggestions.
- **Milestone 2:** Introduced collaborative filtering via an SVD model, experimenting with both PyTorch (using a neural network with a single hidden layer to mimic SVD) and traditional approaches. we picked the SVD, which had better performances.
- **Milestone 3:** Added a workout search bar powered by Hugging Face, hosting the "declare-lab/flan-alpaca-gpt4-xl" model. However, latency proved to be a major issue, even with parallelized queries.
- **Milestone 4:** Developed an XGBoost model to replace K-NN, resulting in dramatic improvements in NDCG@10 and NDCG@6 (from 0.56 to 0.72 on NDCG@10).
- **Milestone 5:** Transitioned from Hugging Face to the  open_router_api_key, utilizing llama model which significantly improved response times and reliability.
- **Milestone 6:** Enhanced the recommendation pipeline by using XGBoost as a reranker on top of K-NN results. Leveraged RandomizedSearchCV to optimize feature selection, leading to substantial metric gains (from 0.72 to 0.86 on NDCG@10).
- **Milestone 7:** Implemented frontend filters, allowing users to refine their recommendations interactively.
- **Milestone 8:** Updated the underlying K-NN algorithm to support diversity in recommendations and retrained the XGBoost reranker with contextualized feature, leading to substantial metric gains (from 0.86 to 0.922 on NDCG@10).

Throughout these stages, the system evolved from a simple prototype to a robust, high-performing recommendation engine, with each milestone addressing previous limitations and introducing new capabilities.



&nbsp;<br>

## Open Issues, Limitations, and Future Work

- **Limitations**:
  - Retraining of the recommendation models on new data is currently performed manually, which may delay adaptation to evolving user preferences and new workout trends.

- **Planned Improvements**:
  - Automate the retraining pipeline to enable more frequent and seamless updates to the models.
  - Enhance the user interface for filtering and exploring recommendations.
  - Expand the dataset to include more diverse user profiles and workout types.

- **Potential Next Steps**:
  - Integrate RAG for LLM-powered workout recommendations. This will allow the LLM to access and utilize a broader and more robust set of data, resulting in more accurate and personalized workout suggestions.
  - Explore real-time feedback loops to further personalize recommendations.
  - Investigate additional machine learning models and hybrid approaches to further boost recommendation quality.

&nbsp;<br>

## Additional Comments

**New Insights Identified in the Code:**

- The recommendation pipeline has evolved through several algorithmic stages, with each new model (K-NN, SVD, XGBoost, hybrid reranking) directly improving NDCG metrics, demonstrating a strong focus on empirical evaluation and iterative improvement.
- The backend is designed to fetch and merge user and workout data dynamically from MongoDB, ensuring that recommendations are not only algorithmically relevant but also contextually rich (e.g., including workout type, VO2 max, body fat).
- The frontend is tightly integrated with the backend, displaying detailed user attributes and supporting interactive feedback (like/dislike), which can be leveraged for future real-time personalization.
- There is a clear separation of concerns: model training and retraining are handled offline, while the API serves real-time recommendations, suggesting a scalable architecture.
- The codebase is prepared for further automation (e.g., retraining pipelines) and integration of advanced features like RAG for LLM-powered recommendations, indicating forward-thinking design.

**Potential Difficulties and Tricks:**

- Handling user IDs and MongoDB document IDs required careful type management (e.g., converting between string and integer types).
- Ensuring the order of recommended buddies matches the model output necessitated explicit reordering after database fetches.
- Integrating multiple data sources (user profiles, workout types) and merging them for frontend consumption was non-trivial and required thoughtful data handling.

**Interesting Stories:**

- The team experimented with both neural network-based and traditional SVD approaches, ultimately choosing the one with better real-world performance, highlighting a pragmatic, results-driven development process.
- Transitioning from Hugging Face to a more responsive LLM API (open_router_api_key with Llama) was a key turning point for latency and user experience.

