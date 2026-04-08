from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.baby import Baby
from app.models.logs import DiaperLog
from app.schemas.logs import DiaperLogCreate, DiaperLogUpdate, DiaperLogResponse

router = APIRouter(prefix="/api/babies/{baby_id}/diaper", tags=["diaper"])


def get_baby_or_404(baby_id: int, db: Session):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    return baby


@router.get("/", response_model=List[DiaperLogResponse])
def list_diapers(baby_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    return (
        db.query(DiaperLog)
        .filter(DiaperLog.baby_id == baby_id)
        .order_by(DiaperLog.time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=DiaperLogResponse, status_code=201)
def create_diaper(baby_id: int, diaper: DiaperLogCreate, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    db_log = DiaperLog(baby_id=baby_id, **diaper.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/{diaper_id}", response_model=DiaperLogResponse)
def get_diaper(baby_id: int, diaper_id: int, db: Session = Depends(get_db)):
    log = db.query(DiaperLog).filter(DiaperLog.id == diaper_id, DiaperLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Diaper log not found")
    return log


@router.patch("/{diaper_id}", response_model=DiaperLogResponse)
def update_diaper(baby_id: int, diaper_id: int, update: DiaperLogUpdate, db: Session = Depends(get_db)):
    log = db.query(DiaperLog).filter(DiaperLog.id == diaper_id, DiaperLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Diaper log not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{diaper_id}", status_code=204)
def delete_diaper(baby_id: int, diaper_id: int, db: Session = Depends(get_db)):
    log = db.query(DiaperLog).filter(DiaperLog.id == diaper_id, DiaperLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Diaper log not found")
    db.delete(log)
    db.commit()
