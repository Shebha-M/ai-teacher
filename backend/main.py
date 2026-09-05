"""FastAPI Application entry point for AI Teacher backend."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from backend.config import settings
from backend.database.connection import init_db
from backend.routes.health import router as health_router
from backend.routes.teaching import router as teaching_router
from backend.routes.documents import router as documents_router
from backend.routes.media import router as media_router, general_media_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ai_teacher")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing database schemas...")
    await init_db()
    logger.info("Database schemas initialized successfully.")
    yield
    logger.info("Shutting down AI Teacher backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Human-like AI Educator API supporting adaptive teaching, questioning, misconception detection, and progress tracking.",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health_router)
app.include_router(teaching_router)
app.include_router(documents_router, prefix="/api/v1")
app.include_router(media_router)
app.include_router(general_media_router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
