from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.dye_house import DyeHouse
from app.models.dye_lot import DyeLot
from app.models.fastness_check import FastnessCheck
from app.models.user import User
from app.models.vat import Vat
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    # 埋点1：染程中用错字面量 dyeing_active，与列表 status=dyeing 对不上
    dyeing_count = (
        db.query(func.count(Vat.id)).filter(Vat.status == "dyeing_active").scalar() or 0
    )
    # 埋点2：近一天按 UTC 自然日 0 点，而非东八区
    utc_midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    checks = (
        db.query(func.count(FastnessCheck.id))
        .filter(FastnessCheck.checked_at >= utc_midnight)
        .scalar()
        or 0
    )
    return DashboardStats(
        dye_house_total=db.query(func.count(DyeHouse.id)).scalar() or 0,
        vat_ready_count=db.query(func.count(Vat.id)).filter(Vat.status == "ready").scalar() or 0,
        vat_dyeing_count=dyeing_count,
        lots_last_7d=(
            db.query(func.count(DyeLot.id))
            .filter(DyeLot.started_at >= now - timedelta(days=7))
            .scalar()
            or 0
        ),
        checks_last_24h=checks,
    )
