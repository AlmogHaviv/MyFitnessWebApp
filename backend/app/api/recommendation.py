from fastapi import APIRouter
from app.api.similar_users import router as similar_users_router
from app.api.similar_users_reranked import router as similar_users_reranked_router
from app.api.events import router as events_router
from app.api.buddy_recommendations import router as buddy_recommendations_router

router = APIRouter()

# Include all the routers
router.include_router(similar_users_router)
router.include_router(similar_users_reranked_router)
router.include_router(events_router)
router.include_router(buddy_recommendations_router)
