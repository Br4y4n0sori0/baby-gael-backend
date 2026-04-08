from sqlalchemy import Column, Integer, String, Date, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Baby(Base):
    __tablename__ = "babies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_weight_grams = Column(Float, nullable=True)
    birth_height_cm = Column(Float, nullable=True)
    photo_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    feedings = relationship("FeedingLog", back_populates="baby", cascade="all, delete-orphan")
    sleeps = relationship("SleepLog", back_populates="baby", cascade="all, delete-orphan")
    diapers = relationship("DiaperLog", back_populates="baby", cascade="all, delete-orphan")
    tummy_times = relationship("TummyTimeLog", back_populates="baby", cascade="all, delete-orphan")
    growths = relationship("GrowthLog", back_populates="baby", cascade="all, delete-orphan")
    medications = relationship("MedicationLog", back_populates="baby", cascade="all, delete-orphan")
    milestones = relationship("MilestoneLog", back_populates="baby", cascade="all, delete-orphan")
    active_sessions = relationship("ActiveSession", back_populates="baby", cascade="all, delete-orphan")
