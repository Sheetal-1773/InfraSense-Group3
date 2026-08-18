from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.database import get_db
from ..models.models import Prediction, Component
from ..services.data_source_manager import get_data_source_manager
from ..services.prediction_generator import get_prediction_generator

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("")
def get_predictions(
    component_id: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Get components from all sources
    dsm = get_data_source_manager()
    components = dsm.discover_components()
    
    # Generate predictions dynamically
    pred_gen = get_prediction_generator()
    dynamic_predictions = pred_gen.generate_predictions(components)
    
    # Filter by severity if specified
    if severity:
        dynamic_predictions = [p for p in dynamic_predictions if p.get("severity") == severity]
    
    # Filter by component_id if specified
    if component_id:
        dynamic_predictions = [p for p in dynamic_predictions if p.get("component_id") == component_id]
    
    # Also get predictions from database
    query = db.query(Prediction)
    
    if component_id:
        query = query.filter(Prediction.component_id == component_id)
    if status:
        query = query.filter(Prediction.status == status)
    if severity:
        query = query.filter(Prediction.severity == severity)
    
    predictions = query.order_by(Prediction.created_at.desc()).all()
    
    result = []
    
    # Add dynamic predictions first
    for pred in dynamic_predictions:
        result.append({
            "id": pred.get("id"),
            "component_id": pred.get("component_id"),
            "component_name": pred.get("component_name"),
            "metric_id": None,
            "prediction_type": pred.get("prediction_type"),
            "current_value": pred.get("current_value"),
            "predicted_value": pred.get("predicted_value"),
            "predicted_threshold": None,
            "threshold_direction": None,
            "time_to_breach_minutes": pred.get("time_to_breach_minutes"),
            "confidence": pred.get("confidence"),
            "severity": pred.get("severity"),
            "probability": pred.get("confidence", 0) / 100,
            "impact": None,
            "explanation": pred.get("explanation"),
            "recommended_action": pred.get("recommended_action"),
            "status": pred.get("status"),
            "created_at": pred.get("created_at"),
            "updated_at": pred.get("created_at")
        })
    
    # Add database predictions
    for pred in predictions:
        component = db.query(Component).filter(Component.id == pred.component_id).first()
        result.append({
            "id": pred.id,
            "component_id": pred.component_id,
            "component_name": component.name if component else "Unknown",
            "metric_id": pred.metric_id,
            "prediction_type": pred.prediction_type,
            "current_value": pred.current_value,
            "predicted_value": pred.predicted_value,
            "predicted_threshold": pred.predicted_threshold,
            "threshold_direction": pred.threshold_direction,
            "time_to_breach_minutes": pred.time_to_breach_minutes,
            "confidence": pred.confidence,
            "severity": pred.severity,
            "probability": pred.probability,
            "impact": pred.impact,
            "explanation": pred.explanation,
            "recommended_action": pred.recommended_action,
            "status": pred.status,
            "created_at": pred.created_at,
            "updated_at": pred.updated_at
        })
    
    return {"data": result}


@router.get("/active")
def get_active_predictions(db: Session = Depends(get_db)):
    predictions = db.query(Prediction).filter(
        Prediction.status == "active"
    ).order_by(Prediction.created_at.desc()).all()
    
    result = []
    for pred in predictions:
        component = db.query(Component).filter(Component.id == pred.component_id).first()
        result.append({
            "id": pred.id,
            "component_id": pred.component_id,
            "component_name": component.name if component else "Unknown",
            "metric_id": pred.metric_id,
            "prediction_type": pred.prediction_type,
            "current_value": pred.current_value,
            "predicted_value": pred.predicted_value,
            "predicted_threshold": pred.predicted_threshold,
            "threshold_direction": pred.threshold_direction,
            "time_to_breach_minutes": pred.time_to_breach_minutes,
            "confidence": pred.confidence,
            "severity": pred.severity,
            "probability": pred.probability,
            "impact": pred.impact,
            "explanation": pred.explanation,
            "recommended_action": pred.recommended_action,
            "prediction_time": pred.prediction_time,
            "expected_breach_time": pred.expected_breach_time,
            "status": pred.status,
            "created_at": pred.created_at,
            "updated_at": pred.updated_at
        })
    
    return result


@router.get("/accuracy")
def get_prediction_accuracy(db: Session = Depends(get_db)):
    from ..services.prediction_service import track_prediction_accuracy
    return track_prediction_accuracy(db)


@router.get("/generate")
def generate_predictions_from_sources():
    """
    Generate predictions from all data sources based on historical trends.
    """
    dsm = get_data_source_manager()
    components = dsm.discover_components()
    
    pred_gen = get_prediction_generator()
    predictions = pred_gen.generate_predictions(components)
    summary = {
        "total": len(predictions),
        "critical": sum(1 for p in predictions if p.get("severity") == "critical"),
        "warning": sum(1 for p in predictions if p.get("severity") == "warning"),
    }
    
    return {
        "predictions": predictions,
        "summary": summary,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{prediction_id}")
def get_prediction(prediction_id: str, db: Session = Depends(get_db)):
    pred = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    component = db.query(Component).filter(Component.id == pred.component_id).first()
    
    return {
        "id": pred.id,
        "component_id": pred.component_id,
        "component_name": component.name if component else "Unknown",
        "metric_id": pred.metric_id,
        "prediction_type": pred.prediction_type,
        "current_value": pred.current_value,
        "predicted_value": pred.predicted_value,
        "predicted_threshold": pred.predicted_threshold,
        "threshold_direction": pred.threshold_direction,
        "time_to_breach_minutes": pred.time_to_breach_minutes,
        "confidence": pred.confidence,
        "severity": pred.severity,
        "probability": pred.probability,
        "impact": pred.impact,
        "explanation": pred.explanation,
        "recommended_action": pred.recommended_action,
        "prediction_time": pred.prediction_time,
        "expected_breach_time": pred.expected_breach_time,
        "status": pred.status,
        "created_at": pred.created_at,
        "updated_at": pred.updated_at
    }


@router.post("/generate")
def generate_predictions(db: Session = Depends(get_db)):
    from ..services.seed_service import seed_predictions
    seed_predictions(db)
    return {"status": "success", "message": "Predictions generated"}


@router.post("/cleanup")
def cleanup_predictions(db: Session = Depends(get_db)):
    from datetime import timedelta
    from ..models.models import Prediction
    cutoff = datetime.utcnow() - timedelta(hours=24)
    db.query(Prediction).filter(Prediction.created_at < cutoff).delete()
    db.commit()
    return {"status": "success", "message": "Old predictions cleaned up"}


@router.post("/run")
def run_predictions(db: Session = Depends(get_db)):
    from ..services.prediction_service import run_prediction_engine
    predictions = run_prediction_engine(db)
    return {"status": "success", "predictions_created": len(predictions)}


@router.get("/patterns/{component_id}")
def get_historical_patterns(component_id: str, metric_name: str, db: Session = Depends(get_db)):
    from ..services.prediction_service import find_historical_patterns
    patterns = find_historical_patterns(db, component_id, metric_name)
    return {"component_id": component_id, "metric_name": metric_name, "patterns": patterns}