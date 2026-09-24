from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.constants import VAT_ALL_STATUSES, VAT_STATUS_DRAIN
from app.database import get_db
from app.models.dye_house import DyeHouse
from app.models.user import User
from app.models.vat import Vat
from app.schemas.vat import VatCreate, VatUpdate, VatOut

router = APIRouter(prefix="/api/vats", tags=["vats"])


@router.get("", response_model=List[VatOut])
def list_vats(
    dye_house_id: Optional[int] = Query(None, alias="dyeHouseId"),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Vat)
    if dye_house_id is not None:
        q = q.filter(Vat.dye_house_id == dye_house_id)
    # 看板「染程中」卡使用同一字面量常量（?status=dyeing），卡数即本过滤的行数。
    if status_filter:
        if status_filter not in VAT_ALL_STATUSES:
            raise HTTPException(status_code=400, detail="未知染缸状态")
        q = q.filter(Vat.status == status_filter)
    return q.order_by(Vat.id).all()


@router.post("", response_model=VatOut, status_code=status.HTTP_201_CREATED)
def create_vat(
    payload: VatCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    house = db.query(DyeHouse).filter(DyeHouse.id == payload.dye_house_id).first()
    if not house:
        raise HTTPException(status_code=400, detail="染坊不存在")
    item = Vat(
        dye_house_id=payload.dye_house_id,
        vat_code=payload.vat_code,
        fiber_type=payload.fiber_type,
        capacity_l=payload.capacity_l,
        status=payload.status,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="同坊染缸编号已存在")
    db.refresh(item)
    return item


@router.get("/{vat_id}", response_model=VatOut)
def get_vat(
    vat_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Vat).filter(Vat.id == vat_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="染缸不存在")
    return item


@router.put("/{vat_id}", response_model=VatOut)
def update_vat(
    vat_id: int,
    payload: VatUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Vat).filter(Vat.id == vat_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="染缸不存在")
    data = payload.model_dump(exclude_unset=True)
    if "dye_house_id" in data:
        house = db.query(DyeHouse).filter(DyeHouse.id == data["dye_house_id"]).first()
        if not house:
            raise HTTPException(status_code=400, detail="染坊不存在")
    for k, v in data.items():
        setattr(item, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="同坊染缸编号已存在")
    db.refresh(item)
    return item


@router.post("/{vat_id}/drain", response_model=VatOut)
def drain_vat(
    vat_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Vat).filter(Vat.id == vat_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="染缸不存在")
    if item.status == VAT_STATUS_DRAIN:
        raise HTTPException(status_code=400, detail="染缸已在排液状态")
    item.status = VAT_STATUS_DRAIN
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{vat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vat(
    vat_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(Vat).filter(Vat.id == vat_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="染缸不存在")
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="该染缸仍有关联记录，无法删除")
