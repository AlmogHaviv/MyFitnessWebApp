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

- **PyTorch** — for matrix factorization...
- **scikit-learn** — for content-based recommendations...
- ...

### Data Platforms

- **MongoDB** — for storing and retriving real time suer interaction and data

### AI

- **Llama model** — for embedding items...

&nbsp;<br>

## Main Algorithms

A brief summary of the key algorithms and features developed:

- **Collaborative filtering (SVD)** — solely based on like giving:
mse: 0.4619
accuracy: 0.2241
precision: 0.2204
recall: 0.9964
f1_score: 0.3610
roc_auc: 0.5460
ndcg@6: 0.6579
ndcg@10: 0.6070
- **XGboost content base and Collaborative filtering** - based on interaction with 3 advences features: competability score, is_same_workout and last_liked_worlout giving amazing benchmarks:
accuracy: 0.9064
precision: 0.8831
recall: 0.6635
f1_score: 0.7577
roc_auc: 0.9386
ndcg@6: 0.8954
ndcg@10: 0.9222
- **Embedding model (OpenAI Model X)** — for feature 4 (help in bootstrapping new items)

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

