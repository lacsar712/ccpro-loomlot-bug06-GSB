from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.constants import VAT_STATUS_DYEING, VAT_STATUS_READY, cn_day_window
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
    # 染程中：与 /api/vats?status=dyeing 列表过滤共用同一字面量，
    # 卡片数字必须等于列表过滤后的行数。
    dyeing_count = (
        db.query(func.count(Vat.id)).filter(Vat.status == VAT_STATUS_DYEING).scalar() or 0
    )
    # 今日抽检：东八区自然日 [00:00, 次日00:00)，与 /api/fastness-checks?date=today 同源。
    day_start, day_end = cn_day_window(now)
    checks_today = (
        db.query(func.count(FastnessCheck.id))
        .filter(FastnessCheck.checked_at >= day_start, FastnessCheck.checked_at < day_end)
        .scalar()
        or 0
    )
    return DashboardStats(
        dye_house_total=db.query(func.count(DyeHouse.id)).scalar() or 0,
        vat_ready_count=(
            db.query(func.count(Vat.id)).filter(Vat.status == VAT_STATUS_READY).scalar() or 0
        ),
        vat_dyeing_count=dyeing_count,
        lots_last_7d=(
            db.query(func.count(DyeLot.id))
            .filter(DyeLot.started_at >= now - timedelta(days=7))
            .scalar()
            or 0
        ),
        checks_today_count=checks_today,
    )
