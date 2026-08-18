from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from ..models.database import get_db
from ..models.models import Anomaly as AnomalyModel, Component
from ..services.anomaly_service import detect_anomalies, check_static_thresholds, save_anomalies

router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])


@router.get("")
def get_anomalies(
    hours: int = 24,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(AnomalyModel).filter(AnomalyModel.detected_at >= cutoff)
    
    if severity:
        query = query.filter(AnomalyModel.severity == severity)
    
    anomalies = query.order_by(AnomalyModel.detected_at.desc()).all()
    
    result = []
    for anomaly in anomalies:
        component = db.query(Component).filter(Component.id == anomaly.component_id).first()
        result.append({
            "id": anomaly.id,
            "component_id": anomaly.component_id,
            "component_name": component.name if component else "Unknown",
            "metric_name": anomaly.metric_name,
            "value": anomaly.value,
            "threshold": anomaly.threshold,
            "threshold_type": anomaly.threshold_type,
            "severity": anomaly.severity,
            "detected_at": anomaly.detected_at.isoformat()
        })
    
    return result


@router.get("/component/{component_id}")
def get_component_anomalies(
    component_id: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    anomalies = db.query(AnomalyModel).filter(
        AnomalyModel.component_id == component_id,
        AnomalyModel.detected_at >= cutoff
    ).order_by(AnomalyModel.detected_at.desc()).all()
    
    return [
        {
            "id": a.id,
            "metric_name": a.metric_name,
            "value": a.value,
            "threshold": a.threshold,
            "threshold_type": a.threshold_type,
            "severity": a.severity,
            "detected_at": a.detected_at.isoformat()
        }
        for a in anomalies
    ]


@router.post("/detect/{component_id}")
def run_anomaly_detection(component_id: str, db: Session = Depends(get_db)):
    anomalies = detect_anomalies(db, component_id, save=True)
    return {
        "component_id": component_id,
        "anomalies_detected": len(anomalies),
        "anomalies": anomalies
    }