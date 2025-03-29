from fastapi import APIRouter, HTTPException
from app.models import User
from app.database import users_collection
from bson import ObjectId

router = APIRouter()

# Route to create a new user
@router.post("/users", response_model=User)
async def create_user(user: User):
    user_dict = user.dict(exclude={"id"})  # Exclude "id" because MongoDB generates it
    result = await users_collection.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)  # Convert ObjectId to string
    return user_dict

# Route to get a user by ID
@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        return user
    raise HTTPException(status_code=404, detail="User not found")
