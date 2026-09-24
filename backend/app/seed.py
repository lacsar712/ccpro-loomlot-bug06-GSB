from datetime import datetime, timedelta, timezone

from app.auth import hash_password
from app.constants import (
    VAT_STATUS_DYEING,
    VAT_STATUS_DRAIN,
    VAT_STATUS_READY,
)
from app.database import SessionLocal
from app.models.dye_house import DyeHouse
from app.models.dye_lot import DyeLot
from app.models.fastness_check import FastnessCheck
from app.models.user import User
from app.models.vat import Vat
from app.timeutil import cn_today_window

# 故意写入的漂字状态：看板旧实现按 dyeing_active 计数，
# 而染缸列表 ?status=dyeing 只认 dyeing —— 用来暴露「状态口径差」。
VAT_STATUS_DRIFT = "dyeing_active"


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add_all(
                [
                    User(
                        username="admin",
                        hashed_password=hash_password("123456"),
                        role="admin",
                        display_name="染坊主管",
                    ),
                    User(
                        username="dyer",
                        hashed_password=hash_password("123456"),
                        role="dyer",
                        display_name="染程操作员",
                    ),
                ]
            )
            db.commit()

        if db.query(DyeHouse).count() == 0:
            h1 = DyeHouse(
                name="蓝靛一号坊",
                water_note="软化井水，硬度约 80ppm",
                notes="主做棉麻靛蓝与草木染",
            )
            h2 = DyeHouse(
                name="青石二号坊",
                water_note="河溪砂滤水，日供约 12 吨",
                notes="专职丝绢与混纺缸染",
            )
            db.add_all([h1, h2])
            db.flush()

            v1 = Vat(
                dye_house_id=h1.id,
                vat_code="V-01",
                fiber_type="棉",
                capacity_l=800.0,
                status=VAT_STATUS_DYEING,
            )
            v2 = Vat(
                dye_house_id=h1.id,
                vat_code="V-02",
                fiber_type="麻",
                capacity_l=600.0,
                status=VAT_STATUS_DYEING,
            )
            v3 = Vat(
                dye_house_id=h2.id,
                vat_code="S-01",
                fiber_type="丝",
                capacity_l=350.0,
                status=VAT_STATUS_READY,
            )
            v4 = Vat(
                dye_house_id=h2.id,
                vat_code="S-02",
                fiber_type="混纺",
                capacity_l=500.0,
                status=VAT_STATUS_DRAIN,
            )
            # 漂字缸：旧看板会把它算进「染程中」（dyeing_active），
            # 但染缸列表按 ?status=dyeing 过滤永远不含它 —— 卡与列表行数对不上。
            v5 = Vat(
                dye_house_id=h2.id,
                vat_code="S-03",
                fiber_type="混纺",
                capacity_l=450.0,
                status=VAT_STATUS_DRIFT,
            )
            db.add_all([v1, v2, v3, v4, v5])
            db.flush()

            now = datetime.now(timezone.utc)
            lot1 = DyeLot(
                vat_id=v1.id,
                recipe_name="靛蓝冷染三浸",
                fabric_kg=42.5,
                started_at=now - timedelta(hours=6),
                operator_name="染程操作员",
            )
            lot2 = DyeLot(
                vat_id=v3.id,
                recipe_name="青蓝套染",
                fabric_kg=18.0,
                started_at=now - timedelta(days=2),
                operator_name="染坊主管",
            )
            db.add_all([lot1, lot2])
            db.flush()

            # lot2 was on ready vat historically — keep v3 ready for demo create path
            v3.status = VAT_STATUS_READY

            # 东八区今日 0 点（UTC）。日界两侧各放一条抽检，专门暴露「日界差」：
            cn_midnight, _ = cn_today_window(now)
            checks = [
                # 今日白天：新旧口径都算
                FastnessCheck(
                    dye_lot_id=lot1.id,
                    checked_at=now - timedelta(hours=1),
                    wash_fastness=4,
                    rub_fastness=3.5,
                    temp_c=40.0,
                    notes="湿摩略偏，可出货",
                ),
                # 东八区昨天 23:50（日界前 10 分钟），但落在 UTC 当日 0 点之后：
                # 旧看板按 UTC 自然日会多算这一条；东八区今日口径应排除。
                FastnessCheck(
                    dye_lot_id=lot1.id,
                    checked_at=cn_midnight - timedelta(minutes=10),
                    wash_fastness=3,
                    rub_fastness=3.0,
                    temp_c=39.0,
                    notes="东八区昨日深夜抽检：旧 UTC 口径多算",
                ),
                # 明显是昨天，新旧口径都不算
                FastnessCheck(
                    dye_lot_id=lot2.id,
                    checked_at=now - timedelta(days=1),
                    wash_fastness=5,
                    rub_fastness=4.0,
                    temp_c=37.0,
                    notes=None,
                ),
            ]
            # 东八区今天 00:10（日界后 10 分钟），但落在 UTC 昨日：
            # 旧看板按 UTC 自然日会少算这一条；东八区今日口径应计入。
            # 仅当该时刻已过去时才写入，避免凌晨刚过日界时造出未来数据。
            after_midnight = cn_midnight + timedelta(minutes=10)
            if after_midnight <= now:
                checks.append(
                    FastnessCheck(
                        dye_lot_id=lot1.id,
                        checked_at=after_midnight,
                        wash_fastness=4,
                        rub_fastness=3.5,
                        temp_c=38.5,
                        notes="东八区今日凌晨抽检：旧 UTC 口径少算",
                    )
                )
            db.add_all(checks)
            db.commit()
            print("Seed data inserted.")
        else:
            print("Seed skipped (data exists).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
