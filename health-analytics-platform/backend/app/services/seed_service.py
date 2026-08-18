import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.models import Category, Component, ComponentMetric, Prediction, Alert, Correlation


def seed_categories(db: Session):
    categories_data = [
        {"name": "Network", "type": "network", "description": "Network infrastructure components"},
        {"name": "Applications", "type": "application", "description": "Application services and APIs"},
        {"name": "Databases", "type": "database", "description": "Database servers and clusters"},
        {"name": "Servers", "type": "server", "description": "Physical and virtual servers"},
    ]
    
    for cat_data in categories_data:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            db.add(Category(**cat_data))
    
    db.commit()


def seed_components(db: Session):
    network_cat = db.query(Category).filter(Category.type == "network").first()
    app_cat = db.query(Category).filter(Category.type == "application").first()
    db_cat = db.query(Category).filter(Category.type == "database").first()
    server_cat = db.query(Category).filter(Category.type == "server").first()

    components_data = [
        {"name": "Core Router 01", "hostname": "core-rtr-01.infrasense.local", "category_id": network_cat.id, "type": "network", "criticality": "critical", "owner": "Network Team"},
        {"name": "Firewall 01", "hostname": "fw-01.infrasense.local", "category_id": network_cat.id, "type": "network", "criticality": "critical", "owner": "Security Team"},
        {"name": "Load Balancer 01", "hostname": "lb-01.infrasense.local", "category_id": network_cat.id, "type": "network", "criticality": "high", "owner": "Network Team"},
        
        {"name": "Payment API", "hostname": "payment-api.infrasense.local", "category_id": app_cat.id, "type": "application", "criticality": "critical", "owner": "Payments Team"},
        {"name": "Customer Portal", "hostname": "customer-portal.infrasense.local", "category_id": app_cat.id, "type": "application", "criticality": "high", "owner": "Frontend Team"},
        {"name": "Authentication Service", "hostname": "auth-service.infrasense.local", "category_id": app_cat.id, "type": "application", "criticality": "critical", "owner": "Security Team"},
        {"name": "Order Service", "hostname": "order-service.infrasense.local", "category_id": app_cat.id, "type": "application", "criticality": "high", "owner": "Orders Team"},
        
        {"name": "Production SQL DB", "hostname": "prod-sql-01.infrasense.local", "category_id": db_cat.id, "type": "database", "criticality": "critical", "owner": "DBA Team"},
        {"name": "Customer DB", "hostname": "customer-db-01.infrasense.local", "category_id": db_cat.id, "type": "database", "criticality": "high", "owner": "DBA Team"},
        
        {"name": "APP-SRV-01", "hostname": "app-srv-01.infrasense.local", "category_id": server_cat.id, "type": "server", "criticality": "high", "owner": "Infrastructure Team"},
        {"name": "DB-SRV-01", "hostname": "db-srv-01.infrasense.local", "category_id": server_cat.id, "type": "server", "criticality": "critical", "owner": "Infrastructure Team"},
        {"name": "WEB-SRV-01", "hostname": "web-srv-01.infrasense.local", "category_id": server_cat.id, "type": "server", "criticality": "medium", "owner": "Infrastructure Team"},
    ]

    for comp_data in components_data:
        existing = db.query(Component).filter(Component.name == comp_data["name"]).first()
        if not existing:
            db.add(Component(
                id=f"comp-{comp_data['name'].lower().replace(' ', '-')}",
                name=comp_data["name"],
                hostname=comp_data["hostname"],
                category_id=comp_data["category_id"],
                environment="production",
                status="healthy",
                health_score=100,
                criticality=comp_data["criticality"],
                owner=comp_data["owner"],
                description=f"{comp_data['name']} in production environment",
                last_seen=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ))

    db.commit()


def seed_metrics(db: Session):
    components = db.query(Component).all()
    
    metric_templates = {
        "network": [
            {"metric_type": "cpu", "metric_name": "CPU Usage", "unit": "%", "warning_threshold": 70, "critical_threshold": 85},
            {"metric_type": "memory", "metric_name": "Memory Usage", "unit": "%", "warning_threshold": 75, "critical_threshold": 90},
            {"metric_type": "latency", "metric_name": "Network Latency", "unit": "ms", "warning_threshold": 100, "critical_threshold": 200},
            {"metric_type": "packet_loss", "metric_name": "Packet Loss", "unit": "%", "warning_threshold": 1, "critical_threshold": 5},
            {"metric_type": "throughput", "metric_name": "Throughput", "unit": "Mbps", "warning_threshold": 80, "critical_threshold": 95},
        ],
        "application": [
            {"metric_type": "cpu", "metric_name": "CPU Usage", "unit": "%", "warning_threshold": 70, "critical_threshold": 85},
            {"metric_type": "memory", "metric_name": "Memory Usage", "unit": "%", "warning_threshold": 75, "critical_threshold": 90},
            {"metric_type": "response_time", "metric_name": "Response Time", "unit": "ms", "warning_threshold": 500, "critical_threshold": 1000},
            {"metric_type": "error_rate", "metric_name": "Error Rate", "unit": "%", "warning_threshold": 2, "critical_threshold": 5},
            {"metric_type": "availability", "metric_name": "Availability", "unit": "%", "warning_threshold": 99, "critical_threshold": 95},
        ],
        "database": [
            {"metric_type": "cpu", "metric_name": "CPU Usage", "unit": "%", "warning_threshold": 70, "critical_threshold": 85},
            {"metric_type": "memory", "metric_name": "Memory Usage", "unit": "%", "warning_threshold": 80, "critical_threshold": 90},
            {"metric_type": "disk", "metric_name": "Disk Usage", "unit": "%", "warning_threshold": 80, "critical_threshold": 95},
            {"metric_type": "connections", "metric_name": "Active Connections", "unit": "%", "warning_threshold": 80, "critical_threshold": 95},
            {"metric_type": "query_latency", "metric_name": "Query Latency", "unit": "ms", "warning_threshold": 200, "critical_threshold": 500},
        ],
        "server": [
            {"metric_type": "cpu", "metric_name": "CPU Usage", "unit": "%", "warning_threshold": 70, "critical_threshold": 85},
            {"metric_type": "memory", "metric_name": "Memory Usage", "unit": "%", "warning_threshold": 75, "critical_threshold": 90},
            {"metric_type": "disk", "metric_name": "Disk Usage", "unit": "%", "warning_threshold": 80, "critical_threshold": 95},
        ],
    }

    for component in components:
        existing_metrics = db.query(ComponentMetric).filter(ComponentMetric.component_id == component.id).count()
        if existing_metrics > 0:
            continue

        cat_type = component.name.lower()
        if "router" in cat_type or "firewall" in cat_type or "load balancer" in cat_type:
            template = metric_templates["network"]
        elif "api" in cat_type or "portal" in cat_type or "service" in cat_type:
            template = metric_templates["application"]
        elif "db" in cat_type or "sql" in cat_type:
            template = metric_templates["database"]
        else:
            template = metric_templates["server"]

        for metric in template:
            base_value = _get_realistic_base_value(metric["metric_type"])
            variation = random.uniform(-5, 5)
            current_value = max(0, min(100, base_value + variation))

            db.add(ComponentMetric(
                component_id=component.id,
                metric_type=metric["metric_type"],
                metric_name=metric["metric_name"],
                value=round(current_value, 2),
                unit=metric["unit"],
                warning_threshold=metric["warning_threshold"],
                critical_threshold=metric["critical_threshold"],
                timestamp=datetime.utcnow(),
                source="system"
            ))

    db.commit()


def _get_realistic_base_value(metric_type: str) -> float:
    bases = {
        "cpu": random.uniform(25, 65),
        "memory": random.uniform(35, 75),
        "disk": random.uniform(45, 80),
        "latency": random.uniform(15, 80),
        "packet_loss": random.uniform(0.1, 0.8),
        "throughput": random.uniform(40, 75),
        "response_time": random.uniform(150, 450),
        "error_rate": random.uniform(0.1, 1.5),
        "availability": random.uniform(99.5, 99.99),
        "connections": random.uniform(40, 70),
        "query_latency": random.uniform(50, 180),
    }
    return bases.get(metric_type, 50.0)


def seed_predictions(db: Session):
    components = db.query(Component).all()
    
    prediction_templates = [
        {
            "metric_type": "disk",
            "prediction_type": "Disk Usage",
            "current_range": (72, 82),
            "predicted_range": (88, 95),
            "threshold": 90,
            "time_range": (90, 180),
            "confidence_range": (82, 95),
            "severity": "high",
            "impact": "Service degradation due to disk exhaustion",
            "action": "Consider expanding disk capacity or cleaning up old logs"
        },
        {
            "metric_type": "memory",
            "prediction_type": "Memory Usage",
            "current_range": (70, 80),
            "predicted_range": (85, 92),
            "threshold": 90,
            "time_range": (120, 240),
            "confidence_range": (75, 90),
            "severity": "medium",
            "impact": "Potential OOM events leading to service restart",
            "action": "Review memory-intensive processes and consider scaling"
        },
        {
            "metric_type": "cpu",
            "prediction_type": "CPU Usage",
            "current_range": (65, 78),
            "predicted_range": (82, 92),
            "threshold": 85,
            "time_range": (60, 150),
            "confidence_range": (70, 88),
            "severity": "medium",
            "impact": "Increased response times due to CPU saturation",
            "action": "Review CPU-intensive queries and consider load balancing"
        },
    ]

    for component in components:
        existing_preds = db.query(Prediction).filter(
            Prediction.component_id == component.id,
            Prediction.status == "active"
        ).count()
        
        if existing_preds > 0:
            continue

        num_predictions = random.randint(1, 2)
        selected_templates = random.sample(prediction_templates, min(num_predictions, len(prediction_templates)))

        for template in selected_templates:
            current = random.uniform(*template["current_range"])
            predicted = random.uniform(*template["predicted_range"])
            time_to_breach = random.randint(*template["time_range"])
            confidence = random.randint(*template["confidence_range"])

            expected_breach = datetime.utcnow() + timedelta(minutes=time_to_breach)

            db.add(Prediction(
                id=f"pred-{component.id}-{template['metric_type']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
                component_id=component.id,
                prediction_type=template["prediction_type"],
                current_value=round(current, 2),
                predicted_value=round(predicted, 2),
                predicted_threshold=template["threshold"],
                threshold_direction="above",
                time_to_breach_minutes=time_to_breach,
                confidence=confidence,
                severity=template["severity"],
                probability=round(confidence / 100, 2),
                impact=template["impact"],
                explanation=f"{template['prediction_type']} is trending upward. Current: {current:.1f}%, Predicted to reach {predicted:.1f}% within {time_to_breach // 60}h {time_to_breach % 60}m.",
                recommended_action=template["action"],
                expected_breach_time=expected_breach,
                status="active",
                created_at=datetime.utcnow()
            ))

    db.commit()


def seed_alerts(db: Session):
    components = db.query(Component).all()
    
    alert_templates = [
        {
            "alert_type": "reactive",
            "severity": "critical",
            "title": "High CPU Usage Detected",
            "description": "CPU usage has exceeded critical threshold",
            "current_value_range": (86, 95),
            "threshold": 85,
            "impact": "Service degradation or outage",
            "action": "Scale resources or optimize workload"
        },
        {
            "alert_type": "reactive",
            "severity": "warning",
            "title": "Memory Usage Warning",
            "description": "Memory usage is approaching critical levels",
            "current_value_range": (76, 88),
            "threshold": 90,
            "impact": "Potential memory exhaustion",
            "action": "Review memory allocation and optimize usage"
        },
        {
            "alert_type": "reactive",
            "severity": "warning",
            "title": "High Response Time",
            "description": "Application response time exceeds threshold",
            "current_value_range": (520, 850),
            "threshold": 500,
            "impact": "Poor user experience",
            "action": "Analyze slow queries and optimize performance"
        },
    ]

    predictive_alert_templates = [
        {
            "severity": "high",
            "title": "Predictive Memory Warning",
            "description": "Memory usage predicted to exceed threshold",
            "current_value_range": (70, 80),
            "predicted_value_range": (88, 95),
            "threshold": 90,
            "time_to_breach_range": (60, 180),
            "confidence_range": (75, 92),
            "impact": "Memory exhaustion predicted - plan capacity increase",
            "action": "Review memory allocation and schedule capacity increase"
        },
        {
            "severity": "high",
            "title": "Predictive Disk Warning",
            "description": "Disk usage predicted to exceed threshold",
            "current_value_range": (72, 82),
            "predicted_value_range": (90, 97),
            "threshold": 90,
            "time_to_breach_range": (90, 240),
            "confidence_range": (70, 88),
            "impact": "Disk exhaustion predicted - plan storage increase",
            "action": "Clean up old logs and schedule storage expansion"
        },
        {
            "severity": "medium",
            "title": "Predictive CPU Warning",
            "description": "CPU usage predicted to exceed threshold",
            "current_value_range": (65, 75),
            "predicted_value_range": (82, 92),
            "threshold": 85,
            "time_to_breach_range": (120, 300),
            "confidence_range": (65, 85),
            "impact": "CPU saturation predicted",
            "action": "Review running processes and optimize workload"
        },
    ]

    for component in components:
        existing_alerts = db.query(Alert).filter(
            Alert.component_id == component.id,
            Alert.status.in_(["open", "acknowledged"])
        ).count()
        
        if existing_alerts > 0:
            continue

        num_alerts = random.randint(1, 2)
        selected_templates = random.sample(alert_templates, min(num_alerts, len(alert_templates)))

        for i, template in enumerate(selected_templates):
            current = random.uniform(*template["current_value_range"])

            db.add(Alert(
                id=f"alert-{component.id}-{template['alert_type']}-{i}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
                component_id=component.id,
                alert_type=template["alert_type"],
                severity=template["severity"],
                title=f"{component.name}: {template['title']}",
                description=template["description"],
                current_value=round(current, 2),
                threshold=template["threshold"],
                impact=template["impact"],
                recommended_action=template["action"],
                status="open",
                acknowledged=False,
                created_at=datetime.utcnow()
            ))

    db.commit()

    for component in components:
        existing_predictive = db.query(Alert).filter(
            Alert.component_id == component.id,
            Alert.alert_type == "predictive",
            Alert.status.in_(["open", "acknowledged"])
        ).count()
        
        if existing_predictive > 0:
            continue
        
        num_predictive = random.randint(1, 2)
        selected = random.sample(predictive_alert_templates, min(num_predictive, len(predictive_alert_templates)))
        
        for i, template in enumerate(selected):
            current = random.uniform(*template["current_value_range"])
            predicted = random.uniform(*template["predicted_value_range"])
            time_to_breach = random.randint(*template["time_to_breach_range"])
            confidence = random.randint(*template["confidence_range"])
            
            db.add(Alert(
                id=f"alert-{component.id}-predictive-{i}-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
                component_id=component.id,
                alert_type="predictive",
                severity=template["severity"],
                title=f"{component.name}: {template['title']}",
                description=template["description"],
                current_value=round(current, 2),
                predicted_value=round(predicted, 2),
                threshold=template["threshold"],
                time_to_breach=time_to_breach,
                confidence=confidence,
                impact=template["impact"],
                recommended_action=template["action"],
                status="open",
                acknowledged=False,
                created_at=datetime.utcnow()
            ))
    
    db.commit()


def seed_correlations(db: Session):
    correlations_data = [
        {
            "source": "comp-payment-api",
            "target": "comp-production-sql-db",
            "correlation_type": "performance",
            "score": 0.85,
            "direction": "unidirectional",
            "evidence": "Payment API latency increases correlate with DB query latency spikes"
        },
        {
            "source": "comp-customer-db",
            "target": "comp-customer-portal",
            "correlation_type": "availability",
            "score": 0.92,
            "direction": "bidirectional",
            "evidence": "Customer DB downtime directly impacts Customer Portal availability"
        },
        {
            "source": "comp-core-router-01",
            "target": "comp-authentication-service",
            "correlation_type": "performance",
            "score": 0.78,
            "direction": "unidirectional",
            "evidence": "Network latency spikes cause Auth Service timeouts"
        },
        {
            "source": "comp-db-srv-01",
            "target": "comp-production-sql-db",
            "correlation_type": "resource",
            "score": 0.88,
            "direction": "bidirectional",
            "evidence": "DB server CPU/memory directly affects SQL DB performance"
        },
    ]

    for corr_data in correlations_data:
        existing = db.query(Correlation).filter(
            Correlation.source_component_id == corr_data["source"],
            Correlation.target_component_id == corr_data["target"]
        ).first()
        
        if not existing:
            db.add(Correlation(
                id=f"corr-{corr_data['source']}-{corr_data['target']}",
                source_component_id=corr_data["source"],
                target_component_id=corr_data["target"],
                correlation_type=corr_data["correlation_type"],
                correlation_score=corr_data["score"],
                direction=corr_data["direction"],
                evidence=corr_data["evidence"],
                status="active"
            ))

    db.commit()


def run_full_seed(db: Session):
    seed_categories(db)
    seed_components(db)
    seed_metrics(db)
    seed_predictions(db)
    seed_alerts(db)
    seed_correlations(db)
    print("Database seeded successfully")