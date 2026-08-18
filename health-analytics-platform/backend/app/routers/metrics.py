from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid
import logging

from ..models.database import get_db
from ..models.models import ComponentMetric, Component
from ..services.collectors import get_collector_status

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["metrics"])

data_quality_counters = {
    "rejected_null_component_id": 0,
    "rejected_null_metric_name": 0,
    "rejected_null_value": 0,
    "rejected_future_timestamp": 0,
    "rejected_unknown_component": 0,
    "total_received": 0,
    "total_stored": 0,
}


class MetricPoint(BaseModel):
    component_id: str
    metric_name: str
    value: float
    unit: str
    labels: Optional[Dict[str, str]] = {}


class MetricsRequest(BaseModel):
    metrics: List[MetricPoint]


class MetricsResponse(BaseModel):
    status: str
    received: int
    stored: int
    timestamp: datetime


def validate_metric(metric: MetricPoint) -> Optional[str]:
    """Validate a metric. Returns error message if invalid, None if valid."""
    if not metric.component_id:
        data_quality_counters["rejected_null_component_id"] += 1
        logger.warning(f"Rejected metric: null component_id")
        return "component_id is required"
    
    if not metric.metric_name:
        data_quality_counters["rejected_null_metric_name"] += 1
        logger.warning(f"Rejected metric: null metric_name for component {metric.component_id}")
        return "metric_name is required"
    
    return None


@router.post("/metrics", response_model=MetricsResponse)
async def receive_metrics(request: MetricsRequest, db: Session = Depends(get_db)):
    """
    Receive metrics from simulated collectors.
    Stores metric data in the database.
    """
    stored_count = 0
    data_quality_counters["total_received"] += len(request.metrics)
    
    for metric in request.metrics:
        error = validate_metric(metric)
        if error:
            continue
        
        component = db.query(Component).filter(Component.id == metric.component_id).first()
        if not component:
            data_quality_counters["rejected_unknown_component"] += 1
            logger.warning(f"Rejected metric: unknown component {metric.component_id}")
            continue
        
        db_metric = ComponentMetric(
            component_id=metric.component_id,
            metric_type="system",
            metric_name=metric.metric_name,
            value=metric.value,
            unit=metric.unit,
            labels=metric.labels,
            timestamp=datetime.utcnow(),
            source="simulated"
        )
        db.add(db_metric)
        stored_count += 1
    
    data_quality_counters["total_stored"] += stored_count
    db.commit()
    
    return MetricsResponse(
        status="success",
        received=len(request.metrics),
        stored=stored_count,
        timestamp=datetime.utcnow()
    )


@router.post("/write", response_model=MetricsResponse)
async def remote_write_metrics(request: MetricsRequest, db: Session = Depends(get_db)):
    """
    Receive metrics via remote-write protocol.
    Accepts remote-write format and stores in database.
    """
    stored_count = 0
    
    if request.metrics:
        data_quality_counters["total_received"] += len(request.metrics)
        
        for metric in request.metrics:
            error = validate_metric(metric)
            if error:
                continue
            
            component_id = metric.component_id
            
            component = db.query(Component).filter(Component.id == component_id).first()
            if not component:
                data_quality_counters["rejected_unknown_component"] += 1
                continue
            
            db_metric = ComponentMetric(
                component_id=component_id,
                metric_type="system",
                metric_name=metric.metric_name,
                value=metric.value,
                unit=metric.unit,
                labels=metric.labels,
                timestamp=datetime.utcnow(),
                source="simulated"
            )
            db.add(db_metric)
            stored_count += 1
    
    data_quality_counters["total_stored"] += stored_count
    db.commit()
    
    return MetricsResponse(
        status="success",
        received=stored_count,
        stored=stored_count,
        timestamp=datetime.utcnow()
    )


@router.get("/metrics/health")
async def metrics_health():
    """Health check endpoint for metrics ingestion."""
    return {"status": "healthy", "service": "metrics-ingestion"}


@router.get("/metrics/quality")
async def get_data_quality():
    """Get data quality metrics."""
    total = data_quality_counters["total_received"]
    stored = data_quality_counters["total_stored"]
    loss_rate = ((total - stored) / total * 100) if total > 0 else 0
    
    return {
        "counters": data_quality_counters,
        "data_loss_rate_percent": round(loss_rate, 2)
    }


@router.get("/collector/status")
async def collector_status():
    """Get metric collector status."""
    return get_collector_status()


@router.post("/collector/start")
async def start_collector_endpoint():
    """Start the metric collector."""
    from ..services.collectors import start_collector
    await start_collector()
    return {"status": "started"}


@router.post("/collector/stop")
async def stop_collector_endpoint():
    """Stop the metric collector."""
    from ..services.collectors import stop_collector
    await stop_collector()
    return {"status": "stopped"}