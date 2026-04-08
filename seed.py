"""Seed script: creates sample baby + logs."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta, date, timezone
from app.database import SessionLocal, engine, Base
from app.models.baby import Baby
from app.models.logs import (
    FeedingLog, SleepLog, DiaperLog, TummyTimeLog,
    GrowthLog, MedicationLog, MilestoneLog,
    FeedingType, SleepType, SleepLocation, DiaperType,
    MedicationUnit, MilestoneCategory,
)

Base.metadata.create_all(bind=engine)
db = SessionLocal()

existing = db.query(Baby).filter(Baby.name == "Gael").first()
if existing:
    print("Seed data already exists. Skipping.")
    db.close()
    sys.exit(0)

baby = Baby(
    name="Gael",
    birth_date=date(2025, 3, 1),
    birth_weight_grams=3200,
    birth_height_cm=50,
)
db.add(baby)
db.flush()

now = datetime.now(timezone.utc)


def hours_ago(h):
    return now - timedelta(hours=h)


def days_ago(d, hour=8):
    return now - timedelta(days=d, hours=now.hour - hour)


# Feedings — last 3 days
feeding_data = [
    (FeedingType.breast_left, 2.5, 12, None),
    (FeedingType.breast_right, 3, 10, None),
    (FeedingType.bottle, 1.5, 7, 90),
    (FeedingType.breast_left, 4, 5, None),
    (FeedingType.breast_right, 2, 3.5, None),
    (FeedingType.formula, 1, 2, 100),
    (FeedingType.breast_left, 0.5, 1, None),
]
for ftype, duration, hrs_ago, amount in feeding_data:
    start = hours_ago(hrs_ago)
    end = start + timedelta(minutes=duration * 10)
    db.add(FeedingLog(
        baby_id=baby.id,
        type=ftype,
        start_time=start,
        end_time=end,
        duration_minutes=duration * 10,
        amount_ml=amount,
    ))

# Sleep — last 2 days
sleep_data = [
    (SleepType.night, SleepLocation.crib, 14, 6 * 60),
    (SleepType.nap, SleepLocation.stroller, 8, 45),
    (SleepType.nap, SleepLocation.arms, 5, 30),
    (SleepType.night, SleepLocation.crib, 38, 7 * 60),
    (SleepType.nap, SleepLocation.crib, 32, 60),
]
for stype, loc, hrs_ago, duration in sleep_data:
    start = hours_ago(hrs_ago)
    db.add(SleepLog(
        baby_id=baby.id,
        sleep_type=stype,
        location=loc,
        start_time=start,
        end_time=start + timedelta(minutes=duration),
        duration_minutes=duration,
    ))

# Diapers
diaper_data = [
    (DiaperType.wet, 1),
    (DiaperType.dirty, 2.5, "amarillo"),
    (DiaperType.both, 4),
    (DiaperType.wet, 6),
    (DiaperType.dirty, 9, "verde"),
    (DiaperType.wet, 12),
]
for item in diaper_data:
    dtype = item[0]
    hrs = item[1]
    color = item[2] if len(item) > 2 else None
    db.add(DiaperLog(baby_id=baby.id, type=dtype, time=hours_ago(hrs), color=color))

# Tummy time
for hrs, duration in [(3, 10), (7, 8), (26, 12)]:
    start = hours_ago(hrs)
    db.add(TummyTimeLog(
        baby_id=baby.id,
        start_time=start,
        end_time=start + timedelta(minutes=duration),
        duration_minutes=duration,
    ))

# Growth records
birth = date(2025, 3, 1)
growth_data = [
    (birth, 3200, 50, 34),
    (date(2025, 3, 15), 3550, 51.5, 34.8),
    (date(2025, 4, 1), 4100, 53, 35.5),
    (date(2025, 4, 6), 4350, 54, 36),
]
for d, w, h, hc in growth_data:
    db.add(GrowthLog(baby_id=baby.id, date=d, weight_grams=w, height_cm=h, head_circumference_cm=hc))

# Medication
db.add(MedicationLog(
    baby_id=baby.id,
    time=hours_ago(5),
    medication_name="Vitamina D",
    dose=0.5,
    unit=MedicationUnit.ml,
))

# Milestones
milestones = [
    (date(2025, 3, 10), "Primera sonrisa", MilestoneCategory.social),
    (date(2025, 3, 25), "Sostiene la cabeza", MilestoneCategory.motor),
    (date(2025, 4, 3), "Sigue objetos con la mirada", MilestoneCategory.cognitive),
]
for d, title, cat in milestones:
    db.add(MilestoneLog(baby_id=baby.id, date=d, title=title, category=cat))

db.commit()
baby_id = baby.id
baby_name = baby.name
db.close()
print(f"Seed complete. Baby '{baby_name}' created with id={baby_id}")
