from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.baby import Baby
from app.schemas.baby import BabyCreate, BabyUpdate, BabyResponse

router = APIRouter(prefix="/api/babies", tags=["babies"])


@router.get("/", response_model=List[BabyResponse])
def list_babies(db: Session = Depends(get_db)):
    return db.query(Baby).all()


@router.post("/", response_model=BabyResponse, status_code=201)
def create_baby(baby: BabyCreate, db: Session = Depends(get_db)):
    db_baby = Baby(**baby.model_dump())
    db.add(db_baby)
    db.commit()
    db.refresh(db_baby)
    return db_baby


@router.get("/{baby_id}", response_model=BabyResponse)
def get_baby(baby_id: int, db: Session = Depends(get_db)):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    return baby


@router.patch("/{baby_id}", response_model=BabyResponse)
def update_baby(baby_id: int, baby_update: BabyUpdate, db: Session = Depends(get_db)):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    for field, value in baby_update.model_dump(exclude_unset=True).items():
        setattr(baby, field, value)
    db.commit()
    db.refresh(baby)
    return baby


@router.delete("/{baby_id}", status_code=204)
def delete_baby(baby_id: int, db: Session = Depends(get_db)):
    baby = db.query(Baby).filter(Baby.id == baby_id).first()
    if not baby:
        raise HTTPException(status_code=404, detail="Baby not found")
    db.delete(baby)
    db.commit()
