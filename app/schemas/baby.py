from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class BabyCreate(BaseModel):
    name: str
    birth_date: date
    birth_weight_grams: Optional[float] = None
    birth_height_cm: Optional[float] = None
    photo_url: Optional[str] = None


class BabyUpdate(BaseModel):
    name: Optional[str] = None
    birth_date: Optional[date] = None
    birth_weight_grams: Optional[float] = None
    birth_height_cm: Optional[float] = None
    photo_url: Optional[str] = None


class BabyResponse(BaseModel):
    id: int
    name: str
    birth_date: date
    birth_weight_grams: Optional[float] = None
    birth_height_cm: Optional[float] = None
    photo_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
