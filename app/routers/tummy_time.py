from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
import json

from app.database import get_db
from app.models.baby import Baby
from app.models.logs import TummyTimeLog, ActiveSession, SessionType
from app.schemas.logs import TummyTimeLogCreate, TummyTimeLogUpdate, TummyTimeLogResponse, ActiveSessionResponse

router = APIRouter(prefix="/api/babies/{baby_id}/tummytime", tags=["tummy_time"])


def get_baby_or_404(baby_id: int, db: Session):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    return baby


@router.get("/", response_model=List[TummyTimeLogResponse])
def list_tummy(baby_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    return (
        db.query(TummyTimeLog)
        .filter(TummyTimeLog.baby_id == baby_id)
        .order_by(TummyTimeLog.start_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=TummyTimeLogResponse, status_code=201)
def create_tummy(baby_id: int, tummy: TummyTimeLogCreate, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    db_log = TummyTimeLog(baby_id=baby_id, **tummy.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/{tummy_id}", response_model=TummyTimeLogResponse)
def get_tummy(baby_id: int, tummy_id: int, db: Session = Depends(get_db)):
    log = db.query(TummyTimeLog).filter(TummyTimeLog.id == tummy_id, TummyTimeLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Tummy time log not found")
    return log


@router.patch("/{tummy_id}", response_model=TummyTimeLogResponse)
def update_tummy(baby_id: int, tummy_id: int, update: TummyTimeLogUpdate, db: Session = Depends(get_db)):
    log = db.query(TummyTimeLog).filter(TummyTimeLog.id == tummy_id, TummyTimeLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Tummy time log not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{tummy_id}", status_code=204)
def delete_tummy(baby_id: int, tummy_id: int, db: Session = Depends(get_db)):
    log = db.query(TummyTimeLog).filter(TummyTimeLog.id == tummy_id, TummyTimeLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Tummy time log not found")
    db.delete(log)
    db.commit()


@router.post("/start", response_model=ActiveSessionResponse, status_code=201)
def start_tummy(baby_id: int, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    session = ActiveSession(
        baby_id=baby_id,
        session_type=SessionType.tummy_time,
        start_time=datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/stop", response_model=TummyTimeLogResponse)
def stop_tummy(baby_id: int, session_id: int, notes: str = None, db: Session = Depends(get_db)):
    session = db.query(ActiveSession).filter(
        ActiveSession.id == session_id,
        ActiveSession.baby_id == baby_id,
        ActiveSession.session_type == SessionType.tummy_time,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")

    end_time = datetime.now(timezone.utc)
    start = session.start_time if session.start_time.tzinfo else session.start_time.replace(tzinfo=timezone.utc)
    duration = (end_time - start).total_seconds() / 60

    log = TummyTimeLog(
        baby_id=baby_id,
        start_time=session.start_time,
        end_time=end_time,
        duration_minutes=round(duration, 2),
        notes=notes,
    )
    db.add(log)
    db.delete(session)
    db.commit()
    db.refresh(log)
    return log
