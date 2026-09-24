from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.constants import VAT_STATUS_DYEING, VAT_STATUS_READY
from app.database import get_db
from app.models.dye_house import DyeHouse
from app.models.dye_lot import DyeLot
from app.models.fastness_check import FastnessCheck
from app.models.user import User
from app.models.vat import Vat
from app.schemas.dashboard import DashboardStats
from app.timeutil import cn_today_window

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    now = datetime.now(timezone.utc)
    # 与 GET /api/vats?status=dyeing 列表过滤同一字面量（constants 单一来源）
    dyeing_count = (
        db.query(func.count(Vat.id))
        .filter(Vat.status == VAT_STATUS_DYEING)
        .scalar()
        or 0
    )
    ready_count = (
        db.query(func.count(Vat.id))
        .filter(Vat.status == VAT_STATUS_READY)
        .scalar()
        or 0
    )
    # 「近一天」= 东八区自然日 0 点至今，与 GET /api/fastness-checks?period=today 同源
    today_start, _ = cn_today_window(now)
    checks = (
        db.query(func.count(FastnessCheck.id))
        .filter(FastnessCheck.checked_at >= today_start)
        .scalar()
        or 0
    )
    return DashboardStats(
        dye_house_total=db.query(func.count(DyeHouse.id)).scalar() or 0,
        vat_ready_count=ready_count,
        vat_dyeing_count=dyeing_count,
        lots_last_7d=(
            db.query(func.count(DyeLot.id))
            .filter(DyeLot.started_at >= now - timedelta(days=7))
            .scalar()
            or 0
        ),
        checks_today=checks,
    )
