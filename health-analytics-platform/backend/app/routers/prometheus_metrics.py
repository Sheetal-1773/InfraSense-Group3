from fastapi import APIRouter, Response
from prometheus_client import Counter, Gauge, generate_latest
from datetime import datetime

router = APIRouter(tags=["prometheus"])

infrasense_components_total = Gauge(
    'infrasense_components_total',
    'Total number of monitored components'
)

infrasense_healthy_components = Gauge(
    'infrasense_healthy_components',
    'Number of healthy components'
)

infrasense_critical_components = Gauge(
    'infrasense_critical_components',
    'Number of critical components'
)

infrasense_health_score = Gauge(
    'infrasense_health_score',
    'Overall system health score',
    ['component_id', 'component_name']
)

infrasense_alerts_total = Counter(
    'infrasense_alerts_total',
    'Total number of alerts generated',
    ['severity', 'alert_type']
)

infrasense_predictions_total = Counter(
    'infrasense_predictions_total',
    'Total number of predictions generated',
    ['prediction_type']
)


@router.get("/metrics")
async def prometheus_metrics():
    from ..services.data_source_manager import get_data_source_manager
    
    try:
        data_source_manager = get_data_source_manager()
        components = data_source_manager.discover_components()
        
        healthy = sum(1 for c in components if c.get("status") == "healthy")
        critical = sum(1 for c in components if c.get("status") == "critical")
        
        infrasense_components_total.set(len(components))
        infrasense_healthy_components.set(healthy)
        infrasense_critical_components.set(critical)
        
        for comp in components:
            infrasense_health_score.labels(
                component_id=comp.get("id", "unknown"),
                component_name=comp.get("name", "unknown")
            ).set(comp.get("health_score", 0))
        
    except Exception:
        pass
    
    return Response(content=generate_latest(), media_type="text/plain")