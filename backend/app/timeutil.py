from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

# 全系统日界统一按东八区自然日（看板「近一天」与列表 ?period=today 同源）
CN_TZ = timezone(timedelta(hours=8))


def cn_today_window(now: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """返回东八区今天 [00:00, 次日 00:00) 对应的 UTC 半开区间。

    两端均为带 UTC 时区的 datetime，可直接用于 timestamptz 列比较。
    """
    now = now or datetime.now(timezone.utc)
    start_cn = now.astimezone(CN_TZ).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start = start_cn.astimezone(timezone.utc)
    return start, start + timedelta(days=1)
