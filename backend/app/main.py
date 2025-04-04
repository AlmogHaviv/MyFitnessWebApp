from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import user, recommendation

# Initialize the FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the routers from the different modules
app.include_router(user.router)
app.include_router(recommendation.router)
