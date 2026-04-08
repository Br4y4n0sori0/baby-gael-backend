from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.baby import Baby
from app.models.logs import GrowthLog
from app.schemas.logs import GrowthLogCreate, GrowthLogUpdate, GrowthLogResponse

router = APIRouter(prefix="/api/babies/{baby_id}/growth", tags=["growth"])


def get_baby_or_404(baby_id: int, db: Session):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    return baby


@router.get("/", response_model=List[GrowthLogResponse])
def list_growth(baby_id: int, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    return (
        db.query(GrowthLog)
        .filter(GrowthLog.baby_id == baby_id)
        .order_by(GrowthLog.date.desc())
        .all()
    )


@router.post("/", response_model=GrowthLogResponse, status_code=201)
def create_growth(baby_id: int, growth: GrowthLogCreate, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    db_log = GrowthLog(baby_id=baby_id, **growth.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/chart", response_model=List[GrowthLogResponse])
def growth_chart(baby_id: int, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    return (
        db.query(GrowthLog)
        .filter(GrowthLog.baby_id == baby_id)
        .order_by(GrowthLog.date.asc())
        .all()
    )


@router.get("/{growth_id}", response_model=GrowthLogResponse)
def get_growth(baby_id: int, growth_id: int, db: Session = Depends(get_db)):
    log = db.query(GrowthLog).filter(GrowthLog.id == growth_id, GrowthLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Growth log not found")
    return log


@router.patch("/{growth_id}", response_model=GrowthLogResponse)
def update_growth(baby_id: int, growth_id: int, update: GrowthLogUpdate, db: Session = Depends(get_db)):
    log = db.query(GrowthLog).filter(GrowthLog.id == growth_id, GrowthLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Growth log not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{growth_id}", status_code=204)
def delete_growth(baby_id: int, growth_id: int, db: Session = Depends(get_db)):
    log = db.query(GrowthLog).filter(GrowthLog.id == growth_id, GrowthLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Growth log not found")
    db.delete(log)
    db.commit()
