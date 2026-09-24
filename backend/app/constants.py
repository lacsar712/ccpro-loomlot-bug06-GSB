from datetime import datetime, timedelta, timezone

# 染缸状态字面量：看板计数、列表过滤、染程开缸必须共用同一套，
# 避免看板（如 dyeing_active）与列表 ?status=dyeing 口径漂移。
VAT_STATUS_READY = "ready"
VAT_STATUS_DYEING = "dyeing"
VAT_STATUS_DRAIN = "drain"

VAT_ALL_STATUSES = (VAT_STATUS_READY, VAT_STATUS_DYEING, VAT_STATUS_DRAIN)
VAT_OPEN_LOT_STATUSES = (VAT_STATUS_READY, VAT_STATUS_DYEING)

# 业务日界按东八区自然日（不是 UTC 0 点，也不是滚动 24 小时）。
CN_TZ = timezone(timedelta(hours=8))


def cn_day_window(now: datetime | None = None) -> tuple[datetime, datetime]:
    """东八区自然日窗口 [今日 00:00, 次日 00:00)，看板与列表共用。"""
    current = (now or datetime.now(timezone.utc)).astimezone(CN_TZ)
    start = current.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, start + timedelta(days=1)

