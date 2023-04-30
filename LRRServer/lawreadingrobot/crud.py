
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import models, schemas


def validate_housebill(db: Session, housebill_id: str) -> None:
    housebill: models.HouseBill | None = db.query(models.HouseBill).filter(models.HouseBill.id == housebill_id).first()
    if housebill is None:
        raise HTTPException(status_code=404, detail='HouseBill not found')


def get_housebill(db: Session, housebill_id: str) -> models.HouseBill:
    housebill: models.HouseBill | None = db.query(models.HouseBill).filter(models.HouseBill.id == housebill_id).first()

    if housebill is None:
        raise HTTPException(status_code=404, detail='HouseBill not found')

    return housebill


def get_housebills(db: Session, skip: int = 0, limit: int = 100) -> List[models.HouseBill]:
    return db.query(models.HouseBill).offset(skip).limit(limit).all()


def create_housebill(db: Session, housebill: schemas.HouseBillCreate) -> models.HouseBill:
    db_housebill = models.HouseBill(**housebill.dict())
    db.add(db_housebill)
    db.commit()
    db.refresh(db_housebill)
    return db_housebill
