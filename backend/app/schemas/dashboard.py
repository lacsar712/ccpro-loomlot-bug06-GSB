from pydantic import BaseModel, ConfigDict, Field


class DashboardStats(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dye_house_total: int = Field(serialization_alias="dyeHouseTotal")
    vat_ready_count: int = Field(serialization_alias="vatReadyCount")
    vat_dyeing_count: int = Field(serialization_alias="vatDyeingCount")
    lots_last_7d: int = Field(serialization_alias="lotsLast7d")
    checks_today_count: int = Field(serialization_alias="checksTodayCount")
