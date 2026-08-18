from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..models.database import get_db
from ..models.models import Correlation, Component, Alert
from ..services.data_source_manager import get_data_source_manager
from ..services.alert_generator import get_alert_generator
from ..services.correlation_engine import get_correlation_engine

router = APIRouter(prefix="/api/correlations", tags=["correlations"])


@router.get("")
def get_correlations(db: Session = Depends(get_db)):
    # Get components from all data sources
    dsm = get_data_source_manager()
    components = dsm.discover_components()
    
    # Generate dynamic correlations based on component health and metrics
    correlations = []
    
    # Find database components and their dependent applications
    db_components = [c for c in components if c.get("category") == "database" or c.get("type") == "database"]
    app_components = [c for c in components if c.get("category") == "application" or c.get("type") == "application"]
    
    for db_comp in db_components:
        db_health = db_comp.get("health_score", 100)
        db_status = db_comp.get("status", "healthy")
        db_metrics = db_comp.get("metrics", {})
        
        # Check for database issues that could affect applications
        db_latency = db_metrics.get("db_query_latency", 0)
        db_connections = db_metrics.get("db_connections", 0)
        
        for app_comp in app_components:
            app_metrics = app_comp.get("metrics", {})
            app_latency = app_metrics.get("api_latency", 0)
            
            # Check correlation between DB issues and API latency
            if db_status != "healthy" or db_health < 80:
                if app_latency > 300 or app_comp.get("status") != "healthy":
                    correlation_score = 0.5 + (100 - db_health) / 100
                    correlations.append({
                        "id": f"corr-{db_comp.get('id')}-{app_comp.get('id')}",
                        "source_component_id": db_comp.get("id"),
                        "source_component_name": db_comp.get("name"),
                        "target_component_id": app_comp.get("id"),
                        "target_component_name": app_comp.get("name"),
                        "correlation_type": "performance_degradation",
                        "correlation_score": round(correlation_score, 2),
                        "direction": "upstream",
                        "evidence": f"Database health degraded ({db_health}%), affecting {app_comp.get('name')} performance",
                        "detected_at": datetime.utcnow().isoformat(),
                        "status": "active"
                    })
            
            # Check latency propagation
            if db_latency > 500 and app_latency > 300:
                correlations.append({
                    "id": f"corr-lat-{db_comp.get('id')}-{app_comp.get('id')}",
                    "source_component_id": db_comp.get("id"),
                    "source_component_name": db_comp.get("name"),
                    "target_component_id": app_comp.get("id"),
                    "target_component_name": app_comp.get("name"),
                    "correlation_type": "latency_propagation",
                    "correlation_score": 0.75,
                    "direction": "upstream",
                    "evidence": f"Database query latency ({db_latency:.0f}ms) correlates with API latency ({app_latency:.0f}ms)",
                    "detected_at": datetime.utcnow().isoformat(),
                    "status": "active"
                })
    
    # Find network components affecting applications
    network_components = [c for c in components if c.get("category") == "network" or c.get("type") == "network"]
    
    for net_comp in network_components:
        net_status = net_comp.get("status", "healthy")
        net_metrics = net_comp.get("metrics", {})
        net_latency = net_metrics.get("network_latency", 0)
        
        if net_status != "healthy" or net_latency > 100:
            for app_comp in app_components:
                app_metrics = app_comp.get("metrics", {})
                app_latency = app_metrics.get("api_latency", 0)
                
                if app_latency > 200:
                    correlations.append({
                        "id": f"corr-net-{net_comp.get('id')}-{app_comp.get('id')}",
                        "source_component_id": net_comp.get("id"),
                        "source_component_name": net_comp.get("name"),
                        "target_component_id": app_comp.get("id"),
                        "target_component_name": app_comp.get("name"),
                        "correlation_type": "network_impact",
                        "correlation_score": 0.65,
                        "direction": "upstream",
                        "evidence": f"Network latency ({net_latency:.0f}ms) affecting API response time ({app_latency:.0f}ms)",
                        "detected_at": datetime.utcnow().isoformat(),
                        "status": "active"
                    })
    
    # Find server issues affecting all components
    server_components = [c for c in components if c.get("category") == "server" or c.get("type") == "server"]
    
    for srv_comp in server_components:
        srv_health = srv_comp.get("health_score", 100)
        srv_status = srv_comp.get("status", "healthy")
        
        if srv_status == "critical" or srv_health < 40:
            # Find components on this server (by hostname pattern)
            srv_hostname = srv_comp.get("hostname", "")
            
            for comp in components:
                if comp.get("id") != srv_comp.get("id"):
                    comp_hostname = comp.get("hostname", "")
                    if srv_hostname and srv_hostname in comp_hostname:
                        correlations.append({
                            "id": f"corr-srv-{srv_comp.get('id')}-{comp.get('id')}",
                            "source_component_id": srv_comp.get("id"),
                            "source_component_name": srv_comp.get("name"),
                            "target_component_id": comp.get("id"),
                            "target_component_name": comp.get("name"),
                            "correlation_type": "resource_contention",
                            "correlation_score": 0.8,
                            "direction": "upstream",
                            "evidence": f"Server health critical ({srv_health}%), impacting {comp.get('name')}",
                            "detected_at": datetime.utcnow().isoformat(),
                            "status": "active"
                        })
    
    # If no dynamic correlations found, create at least one based on current state
    if not correlations and components:
        # Create a baseline correlation showing system health
        critical_comps = [c for c in components if c.get("status") == "critical"]
        warning_comps = [c for c in components if c.get("status") in ["warning", "degraded"]]
        
        if critical_comps:
            correlations.append({
                "id": f"corr-sys-{critical_comps[0].get('id')}",
                "source_component_id": critical_comps[0].get("id"),
                "source_component_name": critical_comps[0].get("name"),
                "target_component_id": "system",
                "target_component_name": "Overall System",
                "correlation_type": "health_degradation",
                "correlation_score": 0.9,
                "direction": "upstream",
                "evidence": f"Critical component affecting overall system health",
                "detected_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
        elif warning_comps:
            correlations.append({
                "id": f"corr-sys-{warning_comps[0].get('id')}",
                "source_component_id": warning_comps[0].get("id"),
                "source_component_name": warning_comps[0].get("name"),
                "target_component_id": "system",
                "target_component_name": "Overall System",
                "correlation_type": "health_degradation",
                "correlation_score": 0.6,
                "direction": "upstream",
                "evidence": f"Degraded component affecting overall system health",
                "detected_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
    
    return correlations


@router.post("/correlate-alerts")
def correlate_alerts(alert_ids: List[str], db: Session = Depends(get_db)):
    """
    Manually correlate multiple alerts.
    """
    if len(alert_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 alert IDs required")
    
    alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
    if len(alerts) != len(alert_ids):
        raise HTTPException(status_code=404, detail="One or more alerts not found")
    
    correlation_id = f"manual-corr-{int(datetime.utcnow().timestamp())}"
    
    first_alert = alerts[0]
    correlation = Correlation(
        id=correlation_id,
        source_component_id=first_alert.component_id,
        target_component_id=first_alert.component_id,
        correlation_type="manual",
        correlation_score=1.0,
        direction="bidirectional",
        evidence=f"Manually correlated alerts: {', '.join(alert_ids)}",
        status="active"
    )
    
    db.add(correlation)
    db.commit()
    
    return {
        "correlation_id": correlation_id,
        "alert_count": len(alerts),
        "status": "correlated"
    }


@router.get("/ranked/root-cause")
def get_ranked_root_causes(db: Session = Depends(get_db)):
    """
    Get alerts ranked by root cause probability.
    """
    active_alerts = db.query(Alert).filter(
        Alert.status.in_(["active", "acknowledged"])
    ).order_by(Alert.created_at.desc()).limit(20).all()
    
    ranked = []
    for alert in active_alerts:
        component = db.query(Component).filter(Component.id == alert.component_id).first()
        
        downstream_count = db.query(Correlation).filter(
            Correlation.source_component_id == alert.component_id,
            Correlation.status == "active"
        ).count()
        
        root_cause_score = 0
        if alert.severity == "critical":
            root_cause_score += 30
        if downstream_count > 0:
            root_cause_score += 20 * min(downstream_count, 3)
        if alert.alert_type == "predictive":
            root_cause_score += 15
        
        ranked.append({
            "alert_id": alert.id,
            "component_id": alert.component_id,
            "component_name": component.name if component else "Unknown",
            "title": alert.title,
            "severity": alert.severity,
            "alert_type": alert.alert_type,
            "downstream_impact": downstream_count,
            "root_cause_probability": min(100, root_cause_score)
        })
    
    ranked.sort(key=lambda x: x["root_cause_probability"], reverse=True)
    
    return ranked


@router.get("/incidents")
def get_correlated_incidents():
    """
    Get correlated incidents from current alerts.
    """
    dsm = get_data_source_manager()
    components = dsm.discover_components()
    
    alert_gen = get_alert_generator()
    alerts = alert_gen.analyze_all_components(components)
    
    corr_engine = get_correlation_engine()
    incidents = corr_engine.analyze_alerts(alerts)
    summary = corr_engine.get_incident_summary(incidents)
    
    return {
        "incidents": incidents,
        "summary": summary,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/component/{component_id}/downstream")
def get_downstream_impact(component_id: str, db: Session = Depends(get_db)):
    """
    Get downstream impact (blast radius) for a component.
    """
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    downstream = db.query(Correlation).filter(
        Correlation.source_component_id == component_id,
        Correlation.status == "active"
    ).all()
    
    impact = []
    for corr in downstream:
        target = db.query(Component).filter(Component.id == corr.target_component_id).first()
        if target:
            impact.append({
                "component_id": target.id,
                "component_name": target.name,
                "component_type": target.category.type if target.category else target.environment,
                "criticality": target.criticality,
                "health_score": target.health_score,
                "status": target.status,
                "dependency_type": corr.correlation_type,
                "correlation_score": corr.correlation_score
            })
    
    return {
        "component_id": component_id,
        "component_name": component.name,
        "downstream_count": len(impact),
        "downstream_components": impact
    }


@router.get("/component/{component_id}/upstream")
def get_upstream_impact(component_id: str, db: Session = Depends(get_db)):
    """
    Get upstream dependencies for a component.
    """
    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    
    upstream = db.query(Correlation).filter(
        Correlation.target_component_id == component_id,
        Correlation.status == "active"
    ).all()
    
    impact = []
    for corr in upstream:
        source = db.query(Component).filter(Component.id == corr.source_component_id).first()
        if source:
            impact.append({
                "component_id": source.id,
                "component_name": source.name,
                "component_type": source.category.type if source.category else source.environment,
                "criticality": source.criticality,
                "health_score": source.health_score,
                "status": source.status,
                "dependency_type": corr.correlation_type,
                "correlation_score": corr.correlation_score
            })
    
    return {
        "component_id": component_id,
        "component_name": component.name,
        "upstream_count": len(impact),
        "upstream_components": impact
    }


@router.get("/topology")
def get_topology(db: Session = Depends(get_db)):
    """
    Get full dependency topology for visualization.
    """
    components = db.query(Component).all()
    correlations = db.query(Correlation).filter(Correlation.status == "active").all()
    
    nodes = []
    for comp in components:
        nodes.append({
            "id": comp.id,
            "name": comp.name,
            "type": comp.category.type if comp.category else comp.environment,
            "criticality": comp.criticality,
            "health_score": comp.health_score,
            "status": comp.status
        })
    
    edges = []
    for corr in correlations:
        edges.append({
            "id": corr.id,
            "source": corr.source_component_id,
            "target": corr.target_component_id,
            "type": corr.correlation_type,
            "score": corr.correlation_score
        })
    
    return {"nodes": nodes, "edges": edges}


@router.get("/{correlation_id}")
def get_correlation(correlation_id: str, db: Session = Depends(get_db)):
    corr = db.query(Correlation).filter(Correlation.id == correlation_id).first()
    if not corr:
        return {"error": "Correlation not found"}
    
    source = db.query(Component).filter(Component.id == corr.source_component_id).first()
    target = db.query(Component).filter(Component.id == corr.target_component_id).first()
    
    return {
        "id": corr.id,
        "source_component_id": corr.source_component_id,
        "source_component_name": source.name if source else "Unknown",
        "target_component_id": corr.target_component_id,
        "target_component_name": target.name if target else "Unknown",
        "correlation_type": corr.correlation_type,
        "correlation_score": corr.correlation_score,
        "direction": corr.direction,
        "evidence": corr.evidence,
        "detected_at": corr.detected_at.isoformat() if corr.detected_at else None,
        "status": corr.status
    }