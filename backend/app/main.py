from fastapi import FastAPI
from app.api import user, workout, recommendation

# Initialize the FastAPI app
app = FastAPI()

# Include the routers from the different modules
app.include_router(user.router)
app.include_router(workout.router)
app.include_router(recommendation.router)
