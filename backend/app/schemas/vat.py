from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict, Field

VatStatus = Literal["ready", "dyeing", "drain"]


class VatCreate(BaseModel):
    dye_house_id: int = Field(..., alias="dyeHouseId")
    vat_code: str = Field(..., min_length=1, max_length=64, alias="vatCode")
    fiber_type: str = Field(..., min_length=1, max_length=64, alias="fiberType")
    capacity_l: float = Field(..., gt=0, alias="capacityL")
    status: VatStatus = "ready"

    model_config = ConfigDict(populate_by_name=True)


class VatUpdate(BaseModel):
    dye_house_id: Optional[int] = Field(None, alias="dyeHouseId")
    vat_code: Optional[str] = Field(None, min_length=1, max_length=64, alias="vatCode")
    fiber_type: Optional[str] = Field(None, min_length=1, max_length=64, alias="fiberType")
    capacity_l: Optional[float] = Field(None, gt=0, alias="capacityL")
    status: Optional[VatStatus] = None

    model_config = ConfigDict(populate_by_name=True)


class VatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    dye_house_id: int = Field(serialization_alias="dyeHouseId")
    vat_code: str = Field(serialization_alias="vatCode")
    fiber_type: str = Field(serialization_alias="fiberType")
    capacity_l: float = Field(serialization_alias="capacityL")
    # 输出容忍历史脏字面量（如旧版误写的 dyeing_active）：全量列表要能把它显示出来，
    # 以便暴露与 ?status=dyeing 的口径差；写入侧 VatCreate/VatUpdate 仍受 VatStatus 严格约束。
    status: str
