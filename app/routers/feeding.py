from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import json

from app.database import get_db
from app.models.baby import Baby
from app.models.logs import FeedingLog, ActiveSession, SessionType, FeedingType
from app.schemas.logs import FeedingLogCreate, FeedingLogUpdate, FeedingLogResponse, ActiveSessionResponse

router = APIRouter(prefix="/api/babies/{baby_id}/feeding", tags=["feeding"])


def get_baby_or_404(baby_id: int, db: Session):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    return baby


@router.get("/", response_model=List[FeedingLogResponse])
def list_feedings(baby_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    return (
        db.query(FeedingLog)
        .filter(FeedingLog.baby_id == baby_id)
        .order_by(FeedingLog.start_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=FeedingLogResponse, status_code=201)
def create_feeding(baby_id: int, feeding: FeedingLogCreate, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    db_feeding = FeedingLog(baby_id=baby_id, **feeding.model_dump())
    db.add(db_feeding)
    db.commit()
    db.refresh(db_feeding)
    return db_feeding


@router.get("/stats", response_model=dict)
def feeding_stats(baby_id: int, days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    logs = (
        db.query(FeedingLog)
        .filter(FeedingLog.baby_id == baby_id, FeedingLog.start_time >= since)
        .order_by(FeedingLog.start_time)
        .all()
    )

    # Per-day counts
    daily: dict = {}
    for log in logs:
        day_key = log.start_time.strftime("%Y-%m-%d")
        daily.setdefault(day_key, {"count": 0, "total_duration": 0, "breast": 0, "bottle": 0})
        daily[day_key]["count"] += 1
        if log.duration_minutes:
            daily[day_key]["total_duration"] += log.duration_minutes
        if log.type in (FeedingType.breast_left, FeedingType.breast_right):
            daily[day_key]["breast"] += 1
        else:
            daily[day_key]["bottle"] += 1

    total = len(logs)
    avg_duration = (
        sum(l.duration_minutes for l in logs if l.duration_minutes) / total if total else 0
    )
    breast_count = sum(
        1 for l in logs if l.type in (FeedingType.breast_left, FeedingType.breast_right)
    )
    bottle_count = total - breast_count

    return {
        "days": days,
        "total": total,
        "avg_per_day": round(total / days, 1),
        "avg_duration_minutes": round(avg_duration, 1),
        "breast_count": breast_count,
        "bottle_count": bottle_count,
        "daily": daily,
    }


@router.get("/{feeding_id}", response_model=FeedingLogResponse)
def get_feeding(baby_id: int, feeding_id: int, db: Session = Depends(get_db)):
    log = db.query(FeedingLog).filter(FeedingLog.id == feeding_id, FeedingLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Feeding log not found")
    return log


@router.patch("/{feeding_id}", response_model=FeedingLogResponse)
def update_feeding(baby_id: int, feeding_id: int, update: FeedingLogUpdate, db: Session = Depends(get_db)):
    log = db.query(FeedingLog).filter(FeedingLog.id == feeding_id, FeedingLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Feeding log not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{feeding_id}", status_code=204)
def delete_feeding(baby_id: int, feeding_id: int, db: Session = Depends(get_db)):
    log = db.query(FeedingLog).filter(FeedingLog.id == feeding_id, FeedingLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Feeding log not found")
    db.delete(log)
    db.commit()


@router.post("/start", response_model=ActiveSessionResponse, status_code=201)
def start_feeding(
    baby_id: int,
    feeding_type: FeedingType = Query(FeedingType.breast_left),
    db: Session = Depends(get_db),
):
    get_baby_or_404(baby_id, db)
    session = ActiveSession(
        baby_id=baby_id,
        session_type=SessionType.feeding,
        start_time=datetime.now(timezone.utc),
        metadata_json=json.dumps({"feeding_type": feeding_type.value}),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/stop", response_model=FeedingLogResponse)
def stop_feeding(
    baby_id: int,
    session_id: int,
    amount_ml: Optional[float] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    session = db.query(ActiveSession).filter(
        ActiveSession.id == session_id,
        ActiveSession.baby_id == baby_id,
        ActiveSession.session_type == SessionType.feeding,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")

    end_time = datetime.now(timezone.utc)
    duration = (end_time - session.start_time.replace(tzinfo=timezone.utc) if session.start_time.tzinfo is None else end_time - session.start_time).total_seconds() / 60

    meta = json.loads(session.metadata_json) if session.metadata_json else {}
    feeding_type = FeedingType(meta.get("feeding_type", FeedingType.breast_left.value))

    log = FeedingLog(
        baby_id=baby_id,
        type=feeding_type,
        start_time=session.start_time,
        end_time=end_time,
        duration_minutes=round(duration, 2),
        amount_ml=amount_ml,
        notes=notes,
    )
    db.add(log)
    db.delete(session)
    db.commit()
    db.refresh(log)
    return log
