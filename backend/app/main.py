from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import user, recommendation, workoutRecommendations
from app.database import test_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await test_connection()
    yield
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan)

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
app.include_router(workoutRecommendations.router)
