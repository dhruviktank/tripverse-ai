"""FastAPI backend server for TripVerse AI."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
from config import get_settings
from orchestrator import get_trip_planning_orchestrator
from auth_routes import router as auth_router
from trip_routes import router as trip_router, dashboard_router
from database import create_tables
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    try:
        logger.info("Creating database tables...")
        await create_tables()
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.warning(f"Could not create tables on startup (will retry on first request): {e}")
    yield

# Initialize app
settings = get_settings()
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router)
app.include_router(trip_router)
app.include_router(dashboard_router)

# Pydantic models
class TripPlanRequest(BaseModel):
    """Request model for trip planning."""
    trip_description: str = Field(..., description="Description of the desired trip")
    budget: str = Field(..., description="Budget range (e.g., 'Value explorer', 'Balanced')")
    pace: str = Field(..., description="Travel pace (e.g., 'Relaxed', 'Balanced', 'High energy')")
    starting_from: str = Field(..., description="Starting location for the trip")


class TripPlanResponse(BaseModel):
    """Response model for trip planning."""
    success: bool
    plan: Optional[dict] = None
    error: Optional[str] = None
    errors: Optional[list] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.api_version
    }


# Trip planning endpoint
@app.post("/api/trips/plan", response_model=TripPlanResponse)
async def plan_trip(request: TripPlanRequest):
    """
    Generate a personalized trip plan using GenAI orchestration.
    
    - **trip_description**: Description of the desired trip
    - **budget**: Budget range
    - **pace**: Travel pace preference
    - **starting_from**: Starting location
    """
    try:
        orchestrator = get_trip_planning_orchestrator()
        
        trip_input = {
            "trip_description": request.trip_description,
            "budget": request.budget,
            "pace": request.pace,
            "starting_from": request.starting_from
        }
        
        logger.info(f"Planning trip: {request.trip_description}")
        result = await orchestrator.plan_trip(trip_input)
        
        if result.get("success"):
            return TripPlanResponse(
                success=True,
                plan=result.get("plan"),
                errors=result.get("errors")
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate trip plan")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error planning trip: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Destination search endpoint (placeholder for future enhancement)
@app.get("/api/destinations/search")
async def search_destinations(query: str, limit: int = 5):
    """
    Search for destinations using vector similarity.
    """
    try:
        from vector_db import get_vector_db_client
        vector_db = get_vector_db_client()
        results = await vector_db.search_documents(
            query=query,
            top_k=limit
        )
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching destinations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "TripVerse AI Backend",
        "docs": "/docs",
        "version": settings.api_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
