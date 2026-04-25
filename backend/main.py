"""FastAPI backend server for TripVerse AI."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.auth import router as auth_router
from api.routes.chat import router as chat_router
from api.routes.dashboard import router as dashboard_router
from api.routes.planning import router as planning_router
from api.routes.trips import router as trip_router
from core.config import get_settings
from core.database import create_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    try:
        logger.info("Creating database tables...")
        await create_tables()
        logger.info("Database tables created successfully.")
    except Exception as exc:
        logger.warning(f"Could not create tables on startup (will retry on first request): {exc}")
    yield


def create_app() -> FastAPI:
    """Build and configure the FastAPI app."""
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://tripverseai.dhruviktank.tech",
            "https://tripverse-ai-eight.vercel.app",
            "https://tripverse-ai-dhruviks-projects.vercel.app",
            "http://localhost:3000"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(planning_router)
    app.include_router(trip_router)
    app.include_router(dashboard_router)
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
