"""Dashboard stats API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_user
from api.dependencies.database import get_db
from models import User
from schemas.trips import DashboardStatsResponse
from services.trip.service import build_dashboard_stats

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stats = await build_dashboard_stats(db, current_user.id)
    return DashboardStatsResponse(success=True, stats=stats)
