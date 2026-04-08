from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from app.models.logs import (
    FeedingType, SleepType, SleepLocation, DiaperType,
    MedicationUnit, MilestoneCategory, SessionType
)


# ─── Feeding ────────────────────────────────────────────────────────────────

class FeedingLogCreate(BaseModel):
    type: FeedingType
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    amount_ml: Optional[float] = None
    notes: Optional[str] = None


class FeedingLogUpdate(BaseModel):
    type: Optional[FeedingType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    amount_ml: Optional[float] = None
    notes: Optional[str] = None


class FeedingLogResponse(BaseModel):
    id: int
    baby_id: int
    type: FeedingType
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    amount_ml: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Sleep ───────────────────────────────────────────────────────────────────

class SleepLogCreate(BaseModel):
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    sleep_type: SleepType = SleepType.nap
    location: SleepLocation = SleepLocation.crib
    notes: Optional[str] = None


class SleepLogUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    sleep_type: Optional[SleepType] = None
    location: Optional[SleepLocation] = None
    notes: Optional[str] = None


class SleepLogResponse(BaseModel):
    id: int
    baby_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    sleep_type: SleepType
    location: SleepLocation
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Diaper ──────────────────────────────────────────────────────────────────

class DiaperLogCreate(BaseModel):
    time: datetime
    type: DiaperType
    color: Optional[str] = None
    consistency: Optional[str] = None
    notes: Optional[str] = None


class DiaperLogUpdate(BaseModel):
    time: Optional[datetime] = None
    type: Optional[DiaperType] = None
    color: Optional[str] = None
    consistency: Optional[str] = None
    notes: Optional[str] = None


class DiaperLogResponse(BaseModel):
    id: int
    baby_id: int
    time: datetime
    type: DiaperType
    color: Optional[str] = None
    consistency: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Tummy Time ──────────────────────────────────────────────────────────────

class TummyTimeLogCreate(BaseModel):
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    notes: Optional[str] = None


class TummyTimeLogUpdate(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    notes: Optional[str] = None


class TummyTimeLogResponse(BaseModel):
    id: int
    baby_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Growth ──────────────────────────────────────────────────────────────────

class GrowthLogCreate(BaseModel):
    date: date
    weight_grams: Optional[float] = None
    height_cm: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    notes: Optional[str] = None


class GrowthLogUpdate(BaseModel):
    date: Optional[date] = None
    weight_grams: Optional[float] = None
    height_cm: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    notes: Optional[str] = None


class GrowthLogResponse(BaseModel):
    id: int
    baby_id: int
    date: date
    weight_grams: Optional[float] = None
    height_cm: Optional[float] = None
    head_circumference_cm: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Medication ──────────────────────────────────────────────────────────────

class MedicationLogCreate(BaseModel):
    time: datetime
    medication_name: str
    dose: float
    unit: MedicationUnit
    notes: Optional[str] = None


class MedicationLogUpdate(BaseModel):
    time: Optional[datetime] = None
    medication_name: Optional[str] = None
    dose: Optional[float] = None
    unit: Optional[MedicationUnit] = None
    notes: Optional[str] = None


class MedicationLogResponse(BaseModel):
    id: int
    baby_id: int
    time: datetime
    medication_name: str
    dose: float
    unit: MedicationUnit
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Milestone ───────────────────────────────────────────────────────────────

class MilestoneLogCreate(BaseModel):
    date: date
    title: str
    description: Optional[str] = None
    category: MilestoneCategory = MilestoneCategory.other


class MilestoneLogUpdate(BaseModel):
    date: Optional[date] = None
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[MilestoneCategory] = None


class MilestoneLogResponse(BaseModel):
    id: int
    baby_id: int
    date: date
    title: str
    description: Optional[str] = None
    category: MilestoneCategory
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Active Session ──────────────────────────────────────────────────────────

class ActiveSessionResponse(BaseModel):
    id: int
    baby_id: int
    session_type: SessionType
    start_time: datetime
    metadata_json: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
