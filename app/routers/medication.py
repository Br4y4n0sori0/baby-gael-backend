from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.baby import Baby
from app.models.logs import MedicationLog
from app.schemas.logs import MedicationLogCreate, MedicationLogUpdate, MedicationLogResponse

router = APIRouter(prefix="/api/babies/{baby_id}/medication", tags=["medication"])


def get_baby_or_404(baby_id: int, db: Session):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    return baby


@router.get("/", response_model=List[MedicationLogResponse])
def list_medications(baby_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    return (
        db.query(MedicationLog)
        .filter(MedicationLog.baby_id == baby_id)
        .order_by(MedicationLog.time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=MedicationLogResponse, status_code=201)
def create_medication(baby_id: int, med: MedicationLogCreate, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    db_log = MedicationLog(baby_id=baby_id, **med.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/{med_id}", response_model=MedicationLogResponse)
def get_medication(baby_id: int, med_id: int, db: Session = Depends(get_db)):
    log = db.query(MedicationLog).filter(MedicationLog.id == med_id, MedicationLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Medication log not found")
    return log


@router.patch("/{med_id}", response_model=MedicationLogResponse)
def update_medication(baby_id: int, med_id: int, update: MedicationLogUpdate, db: Session = Depends(get_db)):
    log = db.query(MedicationLog).filter(MedicationLog.id == med_id, MedicationLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Medication log not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{med_id}", status_code=204)
def delete_medication(baby_id: int, med_id: int, db: Session = Depends(get_db)):
    log = db.query(MedicationLog).filter(MedicationLog.id == med_id, MedicationLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Medication log not found")
    db.delete(log)
    db.commit()
