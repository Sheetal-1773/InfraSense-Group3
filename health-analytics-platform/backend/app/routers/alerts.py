from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.database import get_db
from ..models.models import Alert, Component
from ..schemas.schemas import AlertResponse, AlertUpdate
from ..services.data_source_manager import get_data_source_manager
from ..services.alert_generator import get_alert_generator

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _find_dynamic_alert(alert_id: str) -> Optional[dict]:
    """Locate an alert among the currently generated dynamic alerts."""
    dsm = get_data_source_manager()
    components = dsm.discover_components()
    alert_gen = get_alert_generator()
    for alert in alert_gen.check_components(components):
        if alert.get("id") == alert_id:
            return alert
    return None


def _persist_dynamic_alert(db: Session, dynamic: dict) -> Optional[Alert]:
    """Create a database record for a dynamic alert so it can be updated."""
    alert_id = dynamic.get("id")
    existing = db.query(Alert).filter(Alert.id == alert_id).first()
    if existing:
        return existing

    alert = Alert(
        id=alert_id,
        component_id=dynamic.get("component_id"),
        alert_type="reactive",
        severity=dynamic.get("severity", "warning"),
        title=dynamic.get("title", "Alert"),
        description=dynamic.get("description"),
        status="active",
        created_at=datetime.utcnow(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("")
def get_alerts(
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    db: Session = Depends(get_db)
):
    # Get components from all sources
    dsm = get_data_source_manager()
    components = dsm.discover_components()
    
    # Generate alerts dynamically
    alert_gen = get_alert_generator()
    dynamic_alerts = alert_gen.check_components(components)
    
    # Filter by severity if specified
    if severity:
        dynamic_alerts = [a for a in dynamic_alerts if a.get("severity") == severity]
    
    # Filter by status if specified
    if status:
        dynamic_alerts = [a for a in dynamic_alerts if a.get("status") == status]
    
    # Also get alerts from database
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == status)
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    
    if alert_type == "predictive" and sort_by == "time_to_breach":
        alerts = query.order_by(Alert.time_to_breach.asc().nullslast(), Alert.created_at.desc()).all()
    else:
        alerts = query.order_by(Alert.created_at.desc()).all()
    
    result = []
    
    # Add dynamic alerts first
    for alert in dynamic_alerts:
        result.append({
            "id": alert.get("id"),
            "component_id": alert.get("component_id"),
            "component_name": alert.get("component_name"),
            "metric_id": None,
            "prediction_id": None,
            "alert_type": "dynamic",
            "severity": alert.get("severity"),
            "title": alert.get("title"),
            "description": alert.get("description"),
            "current_value": None,
            "predicted_value": None,
            "threshold": None,
            "time_to_breach": None,
            "confidence": None,
            "impact": None,
            "recommended_action": None,
            "status": alert.get("status"),
            "acknowledged": False,
            "acknowledged_at": None,
            "resolved_at": None,
            "escalated_at": None,
            "escalation_count": 0,
            "created_at": alert.get("created_at"),
            "updated_at": alert.get("created_at")
        })
    
    # Add database alerts
    for alert in alerts:
        component = db.query(Component).filter(Component.id == alert.component_id).first()
        result.append({
            "id": alert.id,
            "component_id": alert.component_id,
            "component_name": component.name if component else "Unknown",
            "metric_id": alert.metric_id,
            "prediction_id": alert.prediction_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "current_value": alert.current_value,
            "predicted_value": alert.predicted_value,
            "threshold": alert.threshold,
            "time_to_breach": alert.time_to_breach,
            "confidence": alert.confidence,
            "impact": alert.impact,
            "recommended_action": alert.recommended_action,
            "status": alert.status,
            "acknowledged": alert.acknowledged,
            "acknowledged_at": alert.acknowledged_at,
            "resolved_at": alert.resolved_at,
            "escalated_at": alert.escalated_at,
            "escalation_count": alert.escalation_count,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at
        })
    
    return {"data": result}


@router.get("/predictive")
def get_predictive_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(
        Alert.alert_type == "predictive",
        Alert.status.in_(["open", "acknowledged"])
    ).order_by(Alert.created_at.desc()).all()
    
    result = []
    for alert in alerts:
        component = db.query(Component).filter(Component.id == alert.component_id).first()
        result.append({
            "id": alert.id,
            "component_id": alert.component_id,
            "component_name": component.name if component else "Unknown",
            "metric_id": alert.metric_id,
            "prediction_id": alert.prediction_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "current_value": alert.current_value,
            "predicted_value": alert.predicted_value,
            "threshold": alert.threshold,
            "time_to_breach": alert.time_to_breach,
            "confidence": alert.confidence,
            "impact": alert.impact,
            "recommended_action": alert.recommended_action,
            "status": alert.status,
            "acknowledged": alert.acknowledged,
            "acknowledged_at": alert.acknowledged_at,
            "resolved_at": alert.resolved_at,
            "escalated_at": alert.escalated_at,
            "escalation_count": alert.escalation_count,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at
        })
    
    return result


@router.get("/reactive")
def get_reactive_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(
        Alert.alert_type == "reactive",
        Alert.status.in_(["open", "acknowledged"])
    ).order_by(Alert.created_at.desc()).all()
    
    result = []
    for alert in alerts:
        component = db.query(Component).filter(Component.id == alert.component_id).first()
        result.append({
            "id": alert.id,
            "component_id": alert.component_id,
            "component_name": component.name if component else "Unknown",
            "metric_id": alert.metric_id,
            "prediction_id": alert.prediction_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "current_value": alert.current_value,
            "predicted_value": alert.predicted_value,
            "threshold": alert.threshold,
            "time_to_breach": alert.time_to_breach,
            "confidence": alert.confidence,
            "impact": alert.impact,
            "recommended_action": alert.recommended_action,
            "status": alert.status,
            "acknowledged": alert.acknowledged,
            "acknowledged_at": alert.acknowledged_at,
            "resolved_at": alert.resolved_at,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at
        })
    
    return result


@router.get("/active")
def get_active_alerts(db: Session = Depends(get_db)):
    alerts = db.query(Alert).filter(
        Alert.status.in_(["open", "acknowledged"])
    ).order_by(Alert.created_at.desc()).all()
    
    result = []
    for alert in alerts:
        component = db.query(Component).filter(Component.id == alert.component_id).first()
        result.append({
            "id": alert.id,
            "component_id": alert.component_id,
            "component_name": component.name if component else "Unknown",
            "metric_id": alert.metric_id,
            "prediction_id": alert.prediction_id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "current_value": alert.current_value,
            "predicted_value": alert.predicted_value,
            "threshold": alert.threshold,
            "time_to_breach": alert.time_to_breach,
            "confidence": alert.confidence,
            "impact": alert.impact,
            "recommended_action": alert.recommended_action,
            "status": alert.status,
            "acknowledged": alert.acknowledged,
            "acknowledged_at": alert.acknowledged_at,
            "resolved_at": alert.resolved_at,
            "created_at": alert.created_at,
            "updated_at": alert.updated_at
        })
    
    return result


@router.get("/generate")
def generate_alerts_from_sources():
    """
    Generate alerts from all data sources based on current metrics.
    """
    dsm = get_data_source_manager()
    components = dsm.discover_components()
    
    alert_gen = get_alert_generator()
    alerts = alert_gen.check_components(components)
    summary = {
        "total": len(alerts),
        "critical": sum(1 for a in alerts if a.get("severity") == "critical"),
        "warning": sum(1 for a in alerts if a.get("severity") == "warning"),
    }
    
    return {
        "alerts": alerts,
        "summary": summary,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{alert_id}")
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    component = db.query(Component).filter(Component.id == alert.component_id).first()
    
    return {
        "id": alert.id,
        "component_id": alert.component_id,
        "component_name": component.name if component else "Unknown",
        "metric_id": alert.metric_id,
        "prediction_id": alert.prediction_id,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "description": alert.description,
        "current_value": alert.current_value,
        "predicted_value": alert.predicted_value,
        "threshold": alert.threshold,
        "time_to_breach": alert.time_to_breach,
        "confidence": alert.confidence,
        "impact": alert.impact,
        "recommended_action": alert.recommended_action,
        "status": alert.status,
        "acknowledged": alert.acknowledged,
        "acknowledged_at": alert.acknowledged_at,
        "resolved_at": alert.resolved_at,
        "created_at": alert.created_at,
        "updated_at": alert.updated_at
    }


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        dynamic = _find_dynamic_alert(alert_id)
        if dynamic:
            alert = _persist_dynamic_alert(db, dynamic)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "acknowledged"
    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    alert.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    component = db.query(Component).filter(Component.id == alert.component_id).first()
    
    return {
        "id": alert.id,
        "component_id": alert.component_id,
        "component_name": component.name if component else "Unknown",
        "metric_id": alert.metric_id,
        "prediction_id": alert.prediction_id,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "description": alert.description,
        "current_value": alert.current_value,
        "predicted_value": alert.predicted_value,
        "threshold": alert.threshold,
        "time_to_breach": alert.time_to_breach,
        "confidence": alert.confidence,
        "impact": alert.impact,
        "recommended_action": alert.recommended_action,
        "status": alert.status,
        "acknowledged": alert.acknowledged,
        "acknowledged_at": alert.acknowledged_at,
        "resolved_at": alert.resolved_at,
        "created_at": alert.created_at,
        "updated_at": alert.updated_at
    }


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        dynamic = _find_dynamic_alert(alert_id)
        if dynamic:
            alert = _persist_dynamic_alert(db, dynamic)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.status = "resolved"
    alert.resolved_at = datetime.utcnow()
    alert.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    component = db.query(Component).filter(Component.id == alert.component_id).first()
    
    return {
        "id": alert.id,
        "component_id": alert.component_id,
        "component_name": component.name if component else "Unknown",
        "metric_id": alert.metric_id,
        "prediction_id": alert.prediction_id,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "description": alert.description,
        "current_value": alert.current_value,
        "predicted_value": alert.predicted_value,
        "threshold": alert.threshold,
        "time_to_breach": alert.time_to_breach,
        "confidence": alert.confidence,
        "impact": alert.impact,
        "recommended_action": alert.recommended_action,
        "status": alert.status,
        "acknowledged": alert.acknowledged,
        "acknowledged_at": alert.acknowledged_at,
        "resolved_at": alert.resolved_at,
        "created_at": alert.created_at,
        "updated_at": alert.updated_at
    }