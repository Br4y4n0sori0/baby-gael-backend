from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class FeedingType(str, enum.Enum):
    breast_left = "breast_left"
    breast_right = "breast_right"
    bottle = "bottle"
    formula = "formula"


class SleepType(str, enum.Enum):
    nap = "nap"
    night = "night"


class SleepLocation(str, enum.Enum):
    crib = "crib"
    stroller = "stroller"
    arms = "arms"
    carrier = "carrier"
    other = "other"


class DiaperType(str, enum.Enum):
    wet = "wet"
    dirty = "dirty"
    both = "both"
    dry = "dry"


class MedicationUnit(str, enum.Enum):
    ml = "ml"
    mg = "mg"
    drops = "drops"


class MilestoneCategory(str, enum.Enum):
    motor = "motor"
    social = "social"
    cognitive = "cognitive"
    language = "language"
    other = "other"


class SessionType(str, enum.Enum):
    feeding = "feeding"
    sleep = "sleep"
    tummy_time = "tummy_time"


class FeedingLog(Base):
    __tablename__ = "feeding_logs"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    type = Column(SAEnum(FeedingType), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Float, nullable=True)
    amount_ml = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baby = relationship("Baby", back_populates="feedings")


class SleepLog(Base):
    __tablename__ = "sleep_logs"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Float, nullable=True)
    sleep_type = Column(SAEnum(SleepType), nullable=False, default=SleepType.nap)
    location = Column(SAEnum(SleepLocation), nullable=False, default=SleepLocation.crib)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baby = relationship("Baby", back_populates="sleeps")


class DiaperLog(Base):
    __tablename__ = "diaper_logs"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    time = Column(DateTime(timezone=True), nullable=False)
    type = Column(SAEnum(DiaperType), nullable=False)
    color = Column(String, nullable=True)
    consistency = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baby = relationship("Baby", back_populates="diapers")


class TummyTimeLog(Base):
    __tablename__ = "tummy_time_logs"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baby = relationship("Baby", back_populates="tummy_times")


class GrowthLog(Base):
    __tablename__ = "growth_logs"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    date = Column(Date, nullable=False)
    weight_grams = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    head_circumference_cm = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baby = relationship("Baby", back_populates="growths")


class MedicationLog(Base):
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    time = Column(DateTime(timezone=True), nullable=False)
    medication_name = Column(String, nullable=False)
    dose = Column(Float, nullable=False)
    unit = Column(SAEnum(MedicationUnit), nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baby = relationship("Baby", back_populates="medications")


class MilestoneLog(Base):
    __tablename__ = "milestone_logs"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    date = Column(Date, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(SAEnum(MilestoneCategory), nullable=False, default=MilestoneCategory.other)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baby = relationship("Baby", back_populates="milestones")


class ActiveSession(Base):
    __tablename__ = "active_sessions"

    id = Column(Integer, primary_key=True, index=True)
    baby_id = Column(Integer, ForeignKey("babies.id"), nullable=False)
    session_type = Column(SAEnum(SessionType), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    metadata_json = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    baby = relationship("Baby", back_populates="active_sessions")
