from fastapi import APIRouter, HTTPException
from app.models import UserEvent
from app.database import events_collection
from datetime import datetime

router = APIRouter()

@router.post("/log-event")
async def log_event(event: UserEvent):
    """
    Log a like/dislike event from the frontend.
    """
    try:
        event_data = event.model_dump()
        event_data["timestamp"] = datetime.now()  # Ensure the timestamp is in UTC
        print("Received event:", event_data)

        # Insert the event into the database:
        result = await events_collection.insert_one(event_data)
        return {"message": "Event logged successfully", "event_id": str(result.inserted_id)}

    except Exception as e:
        print("Error logging event:", str(e))
        raise HTTPException(status_code=500, detail="Failed to log event") 