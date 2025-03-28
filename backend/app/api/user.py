from fastapi import APIRouter
from app.models import User

router = APIRouter()

# Route to create a new user
@router.post("/users")
def create_user(user: User):
    # Here you would store the user in a database (for now, just return it)
    return user
