from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, users, jobs, employer, job_seeker, notifications, applications, bookmarks, websocket

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(employer.router, prefix="/employer", tags=["employer"])
api_router.include_router(job_seeker.router, prefix="/job-seeker", tags=["Job Seeker"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["Bookmarks"])
api_router.include_router(applications.router, prefix="/applications", tags=["Applications"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
