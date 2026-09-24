"""看板卡片与列表过滤共用的字面量，单一来源。

看板计数、列表 ?status= / ?period= 过滤、种子数据都必须引用这里的常量，
禁止在各路由或前端之外再私写一套状态字面量（如曾经的 dyeing_active）。
"""

# 染缸状态
VAT_STATUS_READY = "ready"
VAT_STATUS_DYEING = "dyeing"
VAT_STATUS_DRAIN = "drain"
VAT_STATUSES = (VAT_STATUS_READY, VAT_STATUS_DYEING, VAT_STATUS_DRAIN)

# 可新建染程的染缸状态
VAT_STATUSES_OPEN_TO_LOT = (VAT_STATUS_READY, VAT_STATUS_DYEING)

# 色牢度抽检列表的时间过滤口径
CHECKS_PERIOD_TODAY = "today"
