from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from ..models.database import get_db
from ..models.models import Component, ComponentMetric, Category, HealthScoreHistory
from ..schemas.schemas import ComponentResponse, ComponentWithMetrics, ComponentCreate
from ..services.health_service import update_component_metrics

router = APIRouter(prefix="/api/components", tags=["components"])


@router.post("", response_model=ComponentResponse, status_code=201)
def create_component(component: ComponentCreate, db: Session = Depends(get_db)):
    """
    Register a new infrastructure component.
    Creates a component with a unique UUID.
    """
    existing = db.query(Component).filter(
        Component.name == component.name,
        Component.category_id == component.category_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Component with name '{component.name}' already exists in this category"
        )
    
    category = db.query(Category).filter(Category.id == component.category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Invalid category_id")
    
    new_component = Component(
        id=str(uuid.uuid4()),
        name=component.name,
        category_id=component.category_id,
        hostname=component.hostname,
        environment=component.environment,
        criticality=component.criticality,
        owner=component.owner,
        description=component.description,
        status="healthy",
        health_score=100
    )
    
    db.add(new_component)
    db.commit()
    db.refresh(new_component)
    
    return {
        "id": new_component.id,
        "category_id": new_component.category_id,
        "name": new_component.name,
        "hostname": new_component.hostname,
        "environment": new_component.environment,
        "status": new_component.status,
        "health_score": new_component.health_score,
        "criticality": new_component.criticality,
        "owner": new_component.owner,
        "description": new_component.description,
        "last_seen": new_component.last_seen,
        "created_at": new_component.created_at,
        "updated_at": new_component.updated_at
    }


@router.get("")
def get_components(
    category: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    import logging
    from ..services.data_source_manager import get_data_source_manager

    logger = logging.getLogger(__name__)
    logger.info(f"get_components called with source={source}, category={category}, status={status}")

    dsm = get_data_source_manager()
    discovered_components = dsm.discover_components()
    logger.info(f"Total discovered components: {len(discovered_components)}")

    # Log sources
    sources = set(c.get("source") for c in discovered_components if c.get("source"))
    logger.info(f"Available sources: {sources}")

    filtered = discovered_components

    if category:
        filtered = [c for c in filtered if c.get("category") == category or c.get("type") == category]
    if status:
        filtered = [c for c in filtered if c.get("status") == status]
    if source:
        filtered = [c for c in filtered if c.get("source") == source]
        logger.info(f"After source filter ({source}): {len(filtered)} components")
    
    total = len(filtered)
    paginated = filtered[offset:offset + limit]
    
    result = []
    for comp in paginated:
        result.append({
            "id": comp.get("id"),
            "category_id": comp.get("category_id"),
            "name": comp.get("name"),
            "hostname": comp.get("hostname"),
            "environment": comp.get("environment"),
            "status": comp.get("status"),
            "health_score": comp.get("health_score", 0),
            "criticality": comp.get("criticality"),
            "owner": comp.get("owner"),
            "description": comp.get("description"),
            "last_seen": comp.get("last_seen"),
            "source": comp.get("source"),
            "category": comp.get("category"),
            "type": comp.get("type"),
            "metrics": comp.get("metrics", {})
        })
    
    return {
        "data": result,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/discover")
def discover_components(db: Session = Depends(get_db)):
    """
    Discover and return all components from all data sources.
    """
    import os
    from ..services.data_source_manager import get_data_source_manager
    
    dsm = get_data_source_manager()
    discovered_components = dsm.discover_components()
    
    result = []
    for comp in discovered_components:
        result.append({
            "id": comp.get("id", ""),
            "name": comp.get("name", "Unknown"),
            "type": comp.get("category", comp.get("type", "unknown")),
            "status": comp.get("status", "unknown"),
            "health_score": comp.get("health_score", 0),
            "environment": comp.get("environment", "unknown"),
            "provider": comp.get("provider", os.getenv("CLOUD_PROVIDER", "local")),
            "source": comp.get("source", "unknown"),
            "hostname": comp.get("hostname", ""),
            "description": comp.get("description", ""),
            "metrics": comp.get("metrics", {}),
            "last_seen": comp.get("last_seen", datetime.utcnow().isoformat())
        })
    
    return {
        "discovered": len(result),
        "components": result,
        "cloud_provider": os.getenv("CLOUD_PROVIDER", "local"),
        "data_sources": dsm.get_status()
    }


@router.get("/health")
def get_health(db: Session = Depends(get_db)):
    from ..services.data_source_manager import get_data_source_manager
    
    dsm = get_data_source_manager()
    components = dsm.discover_components()
    
    healthy = len([c for c in components if c.get("status") == "healthy"])
    warning = len([c for c in components if c.get("status") in ["warning", "degraded"]])
    critical = len([c for c in components if c.get("status") == "critical"])
    offline = len([c for c in components if c.get("status") == "offline"])
    
    total = len(components)
    overall = 0
    if total > 0:
        scores = [c.get("health_score", 0) for c in components]
        overall = sum(scores) / len(scores)
    
    return {
        "overall": round(overall, 1),
        "components": {
            "healthy": healthy,
            "warning": warning,
            "critical": critical,
            "offline": offline
        },
        "total": total,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/by-source")
def get_sources_breakdown(db: Session = Depends(get_db)):
    """
    Get breakdown of components by source (local, simulator, simulated).
    """
    from ..services.data_source_manager import get_data_source_manager
    
    dsm = get_data_source_manager()
    components = dsm.discover_components()
    
    by_source = {}
    by_source_and_type = {}
    
    for comp in components:
        source = comp.get("source", "unknown")
        comp_type = comp.get("category", comp.get("type", "unknown"))
        
        if source not in by_source:
            by_source[source] = {"total": 0, "healthy": 0, "warning": 0, "critical": 0}
        
        by_source[source]["total"] += 1
        status = comp.get("status", "unknown")
        if status == "healthy":
            by_source[source]["healthy"] += 1
        elif status in ["warning", "degraded"]:
            by_source[source]["warning"] += 1
        elif status in ["critical", "down"]:
            by_source[source]["critical"] += 1
        
        key = f"{source}_{comp_type}"
        if key not in by_source_and_type:
            by_source_and_type[key] = {"source": source, "type": comp_type, "count": 0}
        by_source_and_type[key]["count"] += 1
    
    return {
        "sources": by_source,
        "by_source_and_type": list(by_source_and_type.values()),
        "total": len(components),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/{component_id}", response_model=ComponentWithMetrics)
def get_component(component_id: str, db: Session = Depends(get_db)):
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    metrics = db.query(ComponentMetric).filter(
        ComponentMetric.component_id == component_id
    ).order_by(ComponentMetric.timestamp.desc()).limit(20).all()
    
    metrics_list = []
    for m in metrics:
        metrics_list.append({
            "id": m.id,
            "component_id": m.component_id,
            "metric_type": m.metric_type,
            "metric_name": m.metric_name,
            "current_value": m.value,
            "unit": m.unit,
            "warning_threshold": m.warning_threshold,
            "critical_threshold": m.critical_threshold,
            "timestamp": m.timestamp,
            "source": m.source
        })
    
    return {
        "id": component.id,
        "category_id": component.category_id,
        "name": component.name,
        "hostname": component.hostname,
        "environment": component.environment,
        "status": component.status,
        "health_score": component.health_score,
        "criticality": component.criticality,
        "owner": component.owner,
        "description": component.description,
        "last_seen": component.last_seen,
        "created_at": component.created_at,
        "updated_at": component.updated_at,
        "metrics": metrics_list
    }


@router.post("/{component_id}/refresh")
def refresh_component_metrics(component_id: str, db: Session = Depends(get_db)):
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    updated = update_component_metrics(db, component)
    return {"status": "success", "component_id": updated.id, "health_score": updated.health_score}


@router.post("/refresh-all")
def refresh_all_components(db: Session = Depends(get_db)):
    components = db.query(Component).all()
    for component in components:
        update_component_metrics(db, component)
    return {"status": "success", "updated": len(components)}


@router.get("/{component_id}/health-history")
def get_component_health_history(
    component_id: str,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    from datetime import datetime, timedelta
    from ..models.models import HealthScoreHistory
    
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    history = db.query(HealthScoreHistory).filter(
        HealthScoreHistory.component_id == component_id,
        HealthScoreHistory.timestamp >= cutoff
    ).order_by(HealthScoreHistory.timestamp.asc()).all()
    
    return [
        {
            "score": h.score,
            "timestamp": h.timestamp.isoformat()
        }
        for h in history
    ]


@router.get("/{component_id}/predictions")
def get_component_predictions(component_id: str, db: Session = Depends(get_db)):
    from ..models.models import Prediction
    
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    predictions = db.query(Prediction).filter(
        Prediction.component_id == component_id,
        Prediction.status == "active"
    ).order_by(Prediction.created_at.desc()).all()
    
    return [
        {
            "id": p.id,
            "component_id": p.component_id,
            "metric_name": p.metric_name,
            "predicted_value": p.predicted_value,
            "threshold": p.threshold,
            "time_to_breach": p.time_to_breach,
            "confidence": p.confidence,
            "prediction_type": p.prediction_type,
            "explanation": p.explanation,
            "status": p.status,
            "created_at": p.created_at.isoformat()
        }
        for p in predictions
    ]


@router.get("/{component_id}/alerts")
def get_component_alerts(
    component_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from ..models.models import Alert
    
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    query = db.query(Alert).filter(Alert.component_id == component_id)
    if status:
        query = query.filter(Alert.status == status)
    
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    return [
        {
            "id": a.id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "title": a.title,
            "description": a.description,
            "metric": a.metric,
            "current_value": a.current_value,
            "threshold": a.threshold,
            "time_to_breach": a.time_to_breach,
            "confidence": a.confidence,
            "status": a.status,
            "acknowledged": a.acknowledged,
            "created_at": a.created_at.isoformat()
        }
        for a in alerts
    ]


@router.get("/grafana/health")
def get_grafana_health_data(db: Session = Depends(get_db)):
    """
    Grafana-compatible health data endpoint.
    Returns data in format suitable for Grafana simple JSON datasource.
    """
    components = db.query(Component).all()
    
    data = []
    for comp in components:
        data.append({
            "name": comp.name,
            "health": comp.health_score,
            "status": comp.status,
            "criticality": comp.criticality,
            "type": comp.type
        })
    
    return {"data": data}


@router.get("/infrastructure/summary")
def get_infrastructure_summary(db: Session = Depends(get_db)):
    """
    Get infrastructure summary with counts by type and status from all sources.
    """
    import os
    from ..services.data_source_manager import get_data_source_manager
    
    dsm = get_data_source_manager()
    discovered_components = dsm.discover_components()
    
    by_type = {"server": 0, "application": 0, "database": 0, "network": 0}
    by_status = {"healthy": 0, "warning": 0, "critical": 0, "unknown": 0}
    by_provider = {"local": 0, "simulated": 0, "prometheus": 0}
    total = 0
    
    for comp in discovered_components:
        comp_type = comp.get("category", comp.get("type", "unknown")).lower()
        if comp_type in by_type:
            by_type[comp_type] += 1
            total += 1
        elif 'server' in comp_type or 'srv' in comp_type:
            by_type["server"] += 1
            total += 1
        elif 'application' in comp_type or 'app' in comp_type or 'api' in comp_type:
            by_type["application"] += 1
            total += 1
        elif 'database' in comp_type or 'db' in comp_type or 'postgres' in comp_type or 'mysql' in comp_type or 'redis' in comp_type:
            by_type["database"] += 1
            total += 1
        elif 'network' in comp_type or 'router' in comp_type or 'switch' in comp_type or 'loadbalancer' in comp_type:
            by_type["network"] += 1
            total += 1
        
        status = comp.get("status", "unknown")
        if status in by_status:
            by_status[status] += 1
        elif status == 'degraded':
            by_status["warning"] += 1
        elif status == 'down':
            by_status["critical"] += 1
        else:
            by_status["unknown"] += 1
        
        source = comp.get("source", comp.get("provider", "unknown"))
        if source == "mock" or source == "simulator":
            source = "simulated"
        
        if source in by_provider:
            by_provider[source] += 1
        else:
            by_provider[source] = by_provider.get(source, 0) + 1
    
    return {
        "total": total,
        "by_type": by_type,
        "by_status": by_status,
        "by_provider": by_provider,
        "cloud_provider": os.getenv("CLOUD_PROVIDER", "local"),
        "timestamp": datetime.utcnow().isoformat(),
        "data_sources": dsm.get_status()
    }


@router.get("/infrastructure/source-category")
def get_source_category_breakdown(db: Session = Depends(get_db)):
    """
    Get breakdown of components by source and category (network, application, server, database).
    """
    from ..services.data_source_manager import get_data_source_manager
    
    dsm = get_data_source_manager()
    discovered_components = dsm.discover_components()
    
    result = {}
    
    for comp in discovered_components:
        source = comp.get("source", comp.get("provider", "unknown"))
        if source == "mock" or source == "simulator":
            source = "simulated"
        
        comp_type = comp.get("category", comp.get("type", "unknown")).lower()
        
        if 'server' in comp_type or 'srv' in comp_type:
            category = "server"
        elif 'application' in comp_type or 'app' in comp_type or 'api' in comp_type:
            category = "application"
        elif 'database' in comp_type or 'db' in comp_type or 'postgres' in comp_type or 'mysql' in comp_type or 'redis' in comp_type:
            category = "database"
        elif 'network' in comp_type or 'router' in comp_type or 'switch' in comp_type or 'loadbalancer' in comp_type:
            category = "network"
        else:
            category = "other"
        
        if source not in result:
            result[source] = {"network": 0, "application": 0, "server": 0, "database": 0, "other": 0}
        result[source][category] += 1
    
    return result