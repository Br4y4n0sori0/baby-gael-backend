from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone
import json

from app.database import get_db
from app.models.baby import Baby
from app.models.logs import SleepLog, ActiveSession, SessionType, SleepType, SleepLocation
from app.schemas.logs import SleepLogCreate, SleepLogUpdate, SleepLogResponse, ActiveSessionResponse

router = APIRouter(prefix="/api/babies/{baby_id}/sleep", tags=["sleep"])


def get_baby_or_404(baby_id: int, db: Session):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    return baby


@router.get("/", response_model=List[SleepLogResponse])
def list_sleeps(baby_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    return (
        db.query(SleepLog)
        .filter(SleepLog.baby_id == baby_id)
        .order_by(SleepLog.start_time.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=SleepLogResponse, status_code=201)
def create_sleep(baby_id: int, sleep: SleepLogCreate, db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    db_sleep = SleepLog(baby_id=baby_id, **sleep.model_dump())
    db.add(db_sleep)
    db.commit()
    db.refresh(db_sleep)
    return db_sleep


@router.get("/stats", response_model=dict)
def sleep_stats(baby_id: int, days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    get_baby_or_404(baby_id, db)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    logs = (
        db.query(SleepLog)
        .filter(SleepLog.baby_id == baby_id, SleepLog.start_time >= since, SleepLog.duration_minutes.isnot(None))
        .order_by(SleepLog.start_time)
        .all()
    )

    daily: dict = {}
    for log in logs:
        day_key = log.start_time.strftime("%Y-%m-%d")
        daily.setdefault(day_key, {"nap_minutes": 0, "night_minutes": 0, "count": 0, "longest": 0})
        daily[day_key]["count"] += 1
        if log.sleep_type == SleepType.nap:
            daily[day_key]["nap_minutes"] += log.duration_minutes
        else:
            daily[day_key]["night_minutes"] += log.duration_minutes
        if log.duration_minutes > daily[day_key]["longest"]:
            daily[day_key]["longest"] = log.duration_minutes

    total_minutes = sum(l.duration_minutes for l in logs)
    longest = max((l.duration_minutes for l in logs), default=0)
    avg_per_day = total_minutes / days if days else 0

    return {
        "days": days,
        "total_sessions": len(logs),
        "avg_per_day_minutes": round(avg_per_day, 1),
        "longest_stretch_minutes": longest,
        "daily": daily,
    }


@router.get("/{sleep_id}", response_model=SleepLogResponse)
def get_sleep(baby_id: int, sleep_id: int, db: Session = Depends(get_db)):
    log = db.query(SleepLog).filter(SleepLog.id == sleep_id, SleepLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    return log


@router.patch("/{sleep_id}", response_model=SleepLogResponse)
def update_sleep(baby_id: int, sleep_id: int, update: SleepLogUpdate, db: Session = Depends(get_db)):
    log = db.query(SleepLog).filter(SleepLog.id == sleep_id, SleepLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{sleep_id}", status_code=204)
def delete_sleep(baby_id: int, sleep_id: int, db: Session = Depends(get_db)):
    log = db.query(SleepLog).filter(SleepLog.id == sleep_id, SleepLog.baby_id == baby_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    db.delete(log)
    db.commit()


@router.post("/start", response_model=ActiveSessionResponse, status_code=201)
def start_sleep(
    baby_id: int,
    sleep_type: SleepType = Query(SleepType.nap),
    location: SleepLocation = Query(SleepLocation.crib),
    db: Session = Depends(get_db),
):
    get_baby_or_404(baby_id, db)
    session = ActiveSession(
        baby_id=baby_id,
        session_type=SessionType.sleep,
        start_time=datetime.now(timezone.utc),
        metadata_json=json.dumps({"sleep_type": sleep_type.value, "location": location.value}),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/stop", response_model=SleepLogResponse)
def stop_sleep(
    baby_id: int,
    session_id: int,
    notes: str = None,
    db: Session = Depends(get_db),
):
    session = db.query(ActiveSession).filter(
        ActiveSession.id == session_id,
        ActiveSession.baby_id == baby_id,
        ActiveSession.session_type == SessionType.sleep,
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")

    end_time = datetime.now(timezone.utc)
    start = session.start_time if session.start_time.tzinfo else session.start_time.replace(tzinfo=timezone.utc)
    duration = (end_time - start).total_seconds() / 60

    meta = json.loads(session.metadata_json) if session.metadata_json else {}
    sleep_type = SleepType(meta.get("sleep_type", SleepType.nap.value))
    location = SleepLocation(meta.get("location", SleepLocation.crib.value))

    log = SleepLog(
        baby_id=baby_id,
        start_time=session.start_time,
        end_time=end_time,
        duration_minutes=round(duration, 2),
        sleep_type=sleep_type,
        location=location,
        notes=notes,
    )
    db.add(log)
    db.delete(session)
    db.commit()
    db.refresh(log)
    return log
