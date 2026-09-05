"""Routes package export."""
from backend.routes.health import router as health_router
from backend.routes.teaching import router as teaching_router
from backend.routes.documents import router as documents_router

__all__ = ["health_router", "teaching_router", "documents_router"]
