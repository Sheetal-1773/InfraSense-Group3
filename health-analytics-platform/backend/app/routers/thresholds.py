from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.database import get_db
from ..models.models import Threshold
from ..schemas.schemas import ThresholdCreate, ThresholdResponse

router = APIRouter(prefix="/api/thresholds", tags=["thresholds"])


@router.get("", response_model=List[ThresholdResponse])
def get_thresholds(component_type: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all thresholds, optionally filtered by component type."""
    query = db.query(Threshold)
    if component_type:
        query = query.filter(Threshold.component_type == component_type)
    return query.all()


@router.post("", response_model=ThresholdResponse, status_code=201)
def create_threshold(threshold: ThresholdCreate, db: Session = Depends(get_db)):
    """Create a new threshold configuration."""
    if threshold.warning_threshold >= threshold.critical_threshold:
        raise HTTPException(
            status_code=400,
            detail="warning_threshold must be less than critical_threshold"
        )
    
    existing = db.query(Threshold).filter(
        Threshold.component_type == threshold.component_type,
        Threshold.metric_name == threshold.metric_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Threshold for {threshold.component_type}.{threshold.metric_name} already exists"
        )
    
    new_threshold = Threshold(
        component_type=threshold.component_type,
        metric_name=threshold.metric_name,
        warning_threshold=threshold.warning_threshold,
        critical_threshold=threshold.critical_threshold,
        is_dynamic=threshold.is_dynamic
    )
    
    db.add(new_threshold)
    db.commit()
    db.refresh(new_threshold)
    
    return new_threshold


@router.put("/{threshold_id}", response_model=ThresholdResponse)
def update_threshold(threshold_id: int, threshold: ThresholdCreate, db: Session = Depends(get_db)):
    """Update an existing threshold."""
    if threshold.warning_threshold >= threshold.critical_threshold:
        raise HTTPException(
            status_code=400,
            detail="warning_threshold must be less than critical_threshold"
        )
    
    existing = db.query(Threshold).filter(Threshold.id == threshold_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Threshold not found")
    
    existing.warning_threshold = threshold.warning_threshold
    existing.critical_threshold = threshold.critical_threshold
    existing.is_dynamic = threshold.is_dynamic
    
    db.commit()
    db.refresh(existing)
    
    return existing


@router.delete("/{threshold_id}")
def delete_threshold(threshold_id: int, db: Session = Depends(get_db)):
    """Delete a threshold."""
    existing = db.query(Threshold).filter(Threshold.id == threshold_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Threshold not found")
    
    db.delete(existing)
    db.commit()
    
    return {"status": "deleted", "id": threshold_id}