from datetime import datetime, timedelta

from app.auth import hash_password
from app.constants import CN_TZ, VAT_STATUS_DYEING, VAT_STATUS_DRAIN, VAT_STATUS_READY
from app.database import SessionLocal
from app.models.dye_house import DyeHouse
from app.models.dye_lot import DyeLot
from app.models.fastness_check import FastnessCheck
from app.models.user import User
from app.models.vat import Vat


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

            # 状态口径差：3 口 dyeing 染缸。旧看板查 dyeing_active 得 0，
            # 而染缸列表 ?status=dyeing 是 3 行——卡片与列表必然对不上。
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
            v5 = Vat(
                dye_house_id=h2.id,
                vat_code="S-03",
                fiber_type="棉",
                capacity_l=420.0,
                status=VAT_STATUS_DYEING,
            )
            db.add_all([v1, v2, v3, v4, v5])
            db.flush()

            now = datetime.now(CN_TZ)
            lot1 = DyeLot(
                vat_id=v1.id,
                recipe_name="靛蓝冷染三浸",
                fabric_kg=42.5,
                started_at=now - timedelta(hours=6),
                operator_name="染程操作员",
            )
            lot3 = DyeLot(
                vat_id=v2.id,
                recipe_name="茜草套媒染",
                fabric_kg=27.0,
                started_at=now - timedelta(hours=3),
                operator_name="染程操作员",
            )
            lot4 = DyeLot(
                vat_id=v5.id,
                recipe_name="靛蓝续缸二浸",
                fabric_kg=31.5,
                started_at=now - timedelta(hours=26),
                operator_name="染坊主管",
            )
            lot2 = DyeLot(
                vat_id=v3.id,
                recipe_name="青蓝套染",
                fabric_kg=18.0,
                started_at=now - timedelta(days=2),
                operator_name="染坊主管",
            )
            db.add_all([lot1, lot3, lot4, lot2])
            db.flush()

            # lot2 was on ready vat historically — keep v3 ready for demo create path
            v3.status = VAT_STATUS_READY

            # 日界差：抽检时间锚定东八区自然日 0 点 M（= UTC 前日 16:00）。
            # M+30m 属东八区今日：白天跑种子时 UTC 仍是“昨天”，旧 UTC 0 点口径少算 1 条；
            # M-30m 属东八区昨日：东八区深夜（23:30–24:00）跑时 UTC 还算“今天”，旧口径多算 1 条；
            # M-26h 两种口径都应排除，作为对照。正确口径（东八区自然日）今日恒为 1 条。
            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
            db.add_all(
                [
                    FastnessCheck(
                        dye_lot_id=lot1.id,
                        checked_at=midnight + timedelta(minutes=30),
                        wash_fastness=4,
                        rub_fastness=3.5,
                        temp_c=40.0,
                        notes="东八区今日凌晨：UTC 口径白天少算的那条",
                    ),
                    FastnessCheck(
                        dye_lot_id=lot3.id,
                        checked_at=midnight - timedelta(minutes=30),
                        wash_fastness=4,
                        rub_fastness=4.0,
                        temp_c=41.0,
                        notes="东八区昨日深夜：UTC 口径深夜多算的那条",
                    ),
                    FastnessCheck(
                        dye_lot_id=lot4.id,
                        checked_at=midnight - timedelta(hours=26),
                        wash_fastness=5,
                        rub_fastness=4.0,
                        temp_c=37.0,
                        notes="前日对照：两种口径都不应计入今日",
                    ),
                ]
            )
            db.commit()
            print("Seed data inserted.")
        else:
            print("Seed skipped (data exists).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
