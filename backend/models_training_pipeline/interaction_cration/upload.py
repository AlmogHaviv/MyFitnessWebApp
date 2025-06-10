import json
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel

class UserEvent(BaseModel):
    user_id: str
    buddy_id: str
    action: str  # "like" or "dislike"
    timestamp: datetime

async def upload_events_from_json(json_file_path: str = 'fitness_partner_smart_events.json'):
    """
    Read events from JSON file and upload to MongoDB
    """
    # MongoDB URI
    uri = "mongodb+srv://almoghaviv:almoghaviv@workoutapp.e0r5zoq.mongodb.net/?retryWrites=true&w=majority&appName=workoutApp"
    
    # Create MongoDB client
    client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))
    db = client.workoutApp
    events_collection = db.events
    
    try:
        # 1. Read the JSON file
        print(f"Reading events from {json_file_path}...")
        with open(json_file_path, 'r') as f:
            events_data = json.load(f)
        
        print(f"Found {len(events_data)} events")
        
        # 2. Convert to UserEvent format and prepare for MongoDB
        events_to_insert = []
        for event_data in events_data:
            # Parse timestamp string back to datetime
            timestamp = datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00')) if 'Z' in event_data['timestamp'] else datetime.fromisoformat(event_data['timestamp'])
            
            # Create UserEvent
            user_event = UserEvent(
                user_id=event_data['user_id'],
                buddy_id=event_data['buddy_id'],
                action=event_data['action'],
                timestamp=timestamp
            )
            
            # Convert to dict for MongoDB
            events_to_insert.append(user_event.dict())
        
        # 3. Upload to MongoDB
        print(f"Uploading {len(events_to_insert)} events to MongoDB...")
        result = await events_collection.insert_many(events_to_insert)
        
        # Print results
        likes = sum(1 for e in events_to_insert if e['action'] == 'like')
        dislikes = len(events_to_insert) - likes
        like_rate = likes / len(events_to_insert)
        
        print(f"Successfully inserted {len(result.inserted_ids)} events")
        print(f"Likes: {likes}, Dislikes: {dislikes}")
        print(f"Like rate: {like_rate:.2%}")
        
        return {
            'total_events': len(result.inserted_ids),
            'likes': likes,
            'dislikes': dislikes,
            'like_rate': like_rate
        }
        
    except FileNotFoundError:
        print(f"Error: File {json_file_path} not found")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        # Close MongoDB connection
        client.close()

# Simple main function
async def main():
    """Upload events from JSON to MongoDB"""
    stats = await upload_events_from_json('fitness_partner_smart_events.json')
    if stats:
        print("Upload completed successfully!")
        print(f"Final stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())