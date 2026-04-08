from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import datetime, timedelta, date, timezone
from pydantic import BaseModel

from app.database import get_db
from app.models.baby import Baby
from app.models.logs import (
    FeedingLog, SleepLog, DiaperLog, TummyTimeLog,
    GrowthLog, MedicationLog, MilestoneLog, FeedingType
)

router = APIRouter(prefix="/api/babies/{baby_id}", tags=["dashboard"])


def get_baby_or_404(baby_id: int, db: Session):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    return baby


@router.get("/dashboard")
def dashboard(baby_id: int, db: Session = Depends(get_db)):
    baby = get_baby_or_404(baby_id, db)
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    last_feeding = (
        db.query(FeedingLog)
        .filter(FeedingLog.baby_id == baby_id)
        .order_by(FeedingLog.start_time.desc())
        .first()
    )
    last_sleep = (
        db.query(SleepLog)
        .filter(SleepLog.baby_id == baby_id)
        .order_by(SleepLog.start_time.desc())
        .first()
    )
    last_diaper = (
        db.query(DiaperLog)
        .filter(DiaperLog.baby_id == baby_id)
        .order_by(DiaperLog.time.desc())
        .first()
    )

    today_feedings = (
        db.query(FeedingLog)
        .filter(FeedingLog.baby_id == baby_id, FeedingLog.start_time >= today_start)
        .count()
    )

    sleep_logs_today = (
        db.query(SleepLog)
        .filter(
            SleepLog.baby_id == baby_id,
            SleepLog.start_time >= today_start,
            SleepLog.duration_minutes.isnot(None),
        )
        .all()
    )
    total_sleep_minutes = sum(s.duration_minutes for s in sleep_logs_today)

    tummy_logs_today = (
        db.query(TummyTimeLog)
        .filter(
            TummyTimeLog.baby_id == baby_id,
            TummyTimeLog.start_time >= today_start,
            TummyTimeLog.duration_minutes.isnot(None),
        )
        .all()
    )
    total_tummy_minutes = sum(t.duration_minutes for t in tummy_logs_today)

    # Estimate next feeding
    recent_feedings = (
        db.query(FeedingLog)
        .filter(FeedingLog.baby_id == baby_id)
        .order_by(FeedingLog.start_time.desc())
        .limit(10)
        .all()
    )
    avg_interval_minutes = None
    if len(recent_feedings) >= 2:
        intervals = []
        for i in range(len(recent_feedings) - 1):
            t1 = recent_feedings[i].start_time
            t2 = recent_feedings[i + 1].start_time
            if t1.tzinfo is None:
                t1 = t1.replace(tzinfo=timezone.utc)
            if t2.tzinfo is None:
                t2 = t2.replace(tzinfo=timezone.utc)
            diff = abs((t1 - t2).total_seconds() / 60)
            if diff < 480:  # ignore gaps > 8h
                intervals.append(diff)
        if intervals:
            avg_interval_minutes = sum(intervals) / len(intervals)

    next_feeding_at = None
    if last_feeding and avg_interval_minutes:
        last_start = last_feeding.start_time
        if last_start.tzinfo is None:
            last_start = last_start.replace(tzinfo=timezone.utc)
        next_feeding_at = (last_start + timedelta(minutes=avg_interval_minutes)).isoformat()

    def serialize_feeding(f):
        if not f:
            return None
        return {
            "id": f.id,
            "type": f.type.value,
            "start_time": f.start_time.isoformat(),
            "duration_minutes": f.duration_minutes,
        }

    def serialize_sleep(s):
        if not s:
            return None
        return {
            "id": s.id,
            "sleep_type": s.sleep_type.value,
            "start_time": s.start_time.isoformat(),
            "duration_minutes": s.duration_minutes,
        }

    def serialize_diaper(d):
        if not d:
            return None
        return {
            "id": d.id,
            "type": d.type.value,
            "time": d.time.isoformat(),
        }

    return {
        "baby_id": baby_id,
        "baby_name": baby.name,
        "last_feeding": serialize_feeding(last_feeding),
        "last_sleep": serialize_sleep(last_sleep),
        "last_diaper": serialize_diaper(last_diaper),
        "today_feedings_count": today_feedings,
        "today_sleep_minutes": total_sleep_minutes,
        "today_tummy_minutes": total_tummy_minutes,
        "avg_feeding_interval_minutes": round(avg_interval_minutes, 1) if avg_interval_minutes else None,
        "next_feeding_estimated_at": next_feeding_at,
    }


@router.get("/timeline")
def timeline(
    baby_id: int,
    date: Optional[str] = Query(None, description="YYYY-MM-DD, defaults to today"),
    db: Session = Depends(get_db),
):
    get_baby_or_404(baby_id, db)
    if date:
        day = datetime.strptime(date, "%Y-%m-%d").date()
    else:
        day = datetime.now(timezone.utc).date()

    day_start = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=timezone.utc)
    day_end = day_start + timedelta(days=1)

    events = []

    for f in db.query(FeedingLog).filter(
        FeedingLog.baby_id == baby_id,
        FeedingLog.start_time >= day_start,
        FeedingLog.start_time < day_end,
    ).all():
        events.append({
            "id": f.id,
            "log_type": "feeding",
            "time": f.start_time.isoformat(),
            "title": _feeding_title(f.type.value),
            "emoji": "🍼",
            "duration_minutes": f.duration_minutes,
            "amount_ml": f.amount_ml,
            "notes": f.notes,
            "raw": {
                "type": f.type.value,
                "end_time": f.end_time.isoformat() if f.end_time else None,
            },
        })

    for s in db.query(SleepLog).filter(
        SleepLog.baby_id == baby_id,
        SleepLog.start_time >= day_start,
        SleepLog.start_time < day_end,
    ).all():
        events.append({
            "id": s.id,
            "log_type": "sleep",
            "time": s.start_time.isoformat(),
            "title": "Siesta" if s.sleep_type.value == "nap" else "Sueño nocturno",
            "emoji": "😴",
            "duration_minutes": s.duration_minutes,
            "notes": s.notes,
            "raw": {
                "sleep_type": s.sleep_type.value,
                "location": s.location.value,
                "end_time": s.end_time.isoformat() if s.end_time else None,
            },
        })

    for d in db.query(DiaperLog).filter(
        DiaperLog.baby_id == baby_id,
        DiaperLog.time >= day_start,
        DiaperLog.time < day_end,
    ).all():
        events.append({
            "id": d.id,
            "log_type": "diaper",
            "time": d.time.isoformat(),
            "title": _diaper_title(d.type.value),
            "emoji": "💩",
            "notes": d.notes,
            "raw": {
                "type": d.type.value,
                "color": d.color,
                "consistency": d.consistency,
            },
        })

    for t in db.query(TummyTimeLog).filter(
        TummyTimeLog.baby_id == baby_id,
        TummyTimeLog.start_time >= day_start,
        TummyTimeLog.start_time < day_end,
    ).all():
        events.append({
            "id": t.id,
            "log_type": "tummy_time",
            "time": t.start_time.isoformat(),
            "title": "Tummy time",
            "emoji": "🐣",
            "duration_minutes": t.duration_minutes,
            "notes": t.notes,
            "raw": {},
        })

    for m in db.query(MedicationLog).filter(
        MedicationLog.baby_id == baby_id,
        MedicationLog.time >= day_start,
        MedicationLog.time < day_end,
    ).all():
        events.append({
            "id": m.id,
            "log_type": "medication",
            "time": m.time.isoformat(),
            "title": m.medication_name,
            "emoji": "💊",
            "notes": m.notes,
            "raw": {
                "dose": m.dose,
                "unit": m.unit.value,
            },
        })

    events.sort(key=lambda e: e["time"], reverse=True)
    return {"date": day.isoformat(), "events": events}


def _feeding_title(t: str) -> str:
    return {
        "breast_left": "Pecho izquierdo",
        "breast_right": "Pecho derecho",
        "bottle": "Biberón",
        "formula": "Fórmula",
    }.get(t, t)


def _diaper_title(t: str) -> str:
    return {
        "wet": "Pañal mojado",
        "dirty": "Pañal sucio",
        "both": "Pañal mixto",
        "dry": "Pañal seco",
    }.get(t, t)
