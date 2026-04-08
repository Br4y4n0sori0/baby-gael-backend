from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.baby import Baby
from app.models.logs import MilestoneLog
from app.schemas.logs import MilestoneLogCreate, MilestoneLogUpdate, MilestoneLogResponse

router = APIRouter(prefix="/api/babies/{baby_id}/milestone", tags=["milestone"])


def get_baby_or_404(baby_id: int, db: Session):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    return baby


@router.get("/", response_model=List[MilestoneLogResponse])
def list_milestones(baby_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    return (
        db.query(MilestoneLog)
        .filter(MilestoneLog.baby_id == baby_id)
        .order_by(MilestoneLog.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=MilestoneLogResponse, status_code=201)
def create_milestone(baby_id: int, milestone: MilestoneLogCreate, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    db_log = MilestoneLog(baby_id=baby_id, **milestone.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/{milestone_id}", response_model=MilestoneLogResponse)
def get_milestone(baby_id: int, milestone_id: int, db: Session = Depends(get_db)):
    log = db.query(MilestoneLog).filter(MilestoneLog.id == milestone_id, MilestoneLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Milestone log not found")
    return log


@router.patch("/{milestone_id}", response_model=MilestoneLogResponse)
def update_milestone(baby_id: int, milestone_id: int, update: MilestoneLogUpdate, db: Session = Depends(get_db)):
    log = db.query(MilestoneLog).filter(MilestoneLog.id == milestone_id, MilestoneLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Milestone log not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{milestone_id}", status_code=204)
def delete_milestone(baby_id: int, milestone_id: int, db: Session = Depends(get_db)):
    log = db.query(MilestoneLog).filter(MilestoneLog.id == milestone_id, MilestoneLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Milestone log not found")
    db.delete(log)
    db.commit()
