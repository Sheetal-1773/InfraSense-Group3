import random
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.models import Alert, Component, ComponentMetric, Prediction, Anomaly


class AlertService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_and_create_alerts(self) -> List[Alert]:
        alerts_created = []
        components = self.db.query(Component).all()
        
        for component in components:
            if component.health_score < 70:
                alert = self._create_alert_for_component(component)
                if alert:
                    alerts_created.append(alert)
                    self.db.add(alert)
        
        self.db.commit()
        return alerts_created
    
    def create_alerts_from_anomalies(self, alert_type: str = "reactive") -> List[Alert]:
        """
        Create alerts from detected anomalies.
        alert_type: 'reactive' (already exceeded) or 'predictive' (will exceed)
        """
        alerts_created = []
        
        recent_anomalies = self.db.query(Anomaly).filter(
            Anomaly.detected_at >= datetime.utcnow()
        ).all()
        
        for anomaly in recent_anomalies:
            existing = self.db.query(Alert).filter(
                Alert.component_id == anomaly.component_id,
                Alert.metric == anomaly.metric_name,
                Alert.status.in_(['active', 'acknowledged'])
            ).first()
            
            if existing:
                continue
            
            component = self.db.query(Component).filter(
                Component.id == anomaly.component_id
            ).first()
            
            if not component:
                continue
            
            alert = Alert(
                id=f"alert-{anomaly.component_id}-{anomaly.metric_name}-{int(datetime.utcnow().timestamp())}",
                component_id=anomaly.component_id,
                alert_type=alert_type,
                severity=anomaly.severity,
                title=f"{anomaly.metric_name} {anomaly.threshold_type} threshold exceeded",
                description=f"Component '{component.name}' - {anomaly.metric_name} is {anomaly.value} (threshold: {anomaly.threshold})",
                current_value=anomaly.value,
                threshold=anomaly.threshold,
                status='active',
                component_name=component.name,
                metric=anomaly.metric_name,
                time_to_breach=random.randint(15, 120) if alert_type == "predictive" else None,
                confidence=random.randint(60, 90),
                created_at=datetime.utcnow()
            )
            
            self.db.add(alert)
            alerts_created.append(alert)
        
        self.db.commit()
        return alerts_created
    
    def deduplicate_alerts(self, deduplication_window_minutes: int = 60) -> int:
        """
        Find and link duplicate alerts within the deduplication window.
        Returns the number of duplicates linked.
        """
        cutoff = datetime.utcnow()
        
        recent_alerts = self.db.query(Alert).filter(
            Alert.created_at >= cutoff,
            Alert.parent_alert_id.is_(None)
        ).order_by(Alert.created_at.asc()).all()
        
        linked_count = 0
        
        for alert in recent_alerts:
            duplicates = self.db.query(Alert).filter(
                Alert.id != alert.id,
                Alert.component_id == alert.component_id,
                Alert.metric == alert.metric,
                Alert.status.in_(['active', 'acknowledged']),
                Alert.created_at >= cutoff
            ).all()
            
            for dup in duplicates:
                dup.parent_alert_id = alert.id
                linked_count += 1
        
        self.db.commit()
        return linked_count
    
    def resolve_linked_alerts(self, parent_alert_id: str) -> int:
        """
        Resolve all alerts linked to a parent alert.
        Returns the number of alerts resolved.
        """
        parent = self.db.query(Alert).filter(Alert.id == parent_alert_id).first()
        if not parent:
            return 0
        
        linked = self.db.query(Alert).filter(
            Alert.parent_alert_id == parent_alert_id,
            Alert.status != 'resolved'
        ).all()
        
        for alert in linked:
            alert.status = 'resolved'
            alert.resolved_at = datetime.utcnow()
        
        self.db.commit()
        return len(linked)
    
    def _create_alert_for_component(self, component: Component) -> Optional[Alert]:
        existing_active = self.db.query(Alert).filter(
            Alert.component_id == component.id,
            Alert.status == 'active'
        ).first()
        
        if existing_active:
            return None
        
        if component.health_score < 40:
            severity = 'critical'
        elif component.health_score < 70:
            severity = 'warning'
        else:
            severity = 'info'
        
        metric = self._get_worst_metric(component)
        
        return Alert(
            id=f"alert-{component.id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            title=f"{component.name} - Health {component.health_score}%",
            description=f"Component '{component.name}' health has degraded to {component.health_score}%. {metric['name']} usage is at {metric['value']}%.",
            severity=severity,
            status='active',
            component_id=component.id,
            current_value=metric['value'],
            threshold=metric['threshold'],
            time_to_breach=random.randint(15, 120) if severity != 'info' else None,
            confidence=random.randint(60, 90),
            created_at=datetime.utcnow()
        )
    
    def _get_worst_metric(self, component: Component) -> dict:
        latest_metrics = self.db.query(ComponentMetric).filter(
            ComponentMetric.component_id == component.id
        ).order_by(ComponentMetric.timestamp.desc()).limit(10).all()
        
        if not latest_metrics:
            return {'name': 'unknown', 'value': 0, 'threshold': 100}
        
        metric_map = {}
        for m in latest_metrics:
            if m.metric_type not in metric_map:
                metric_map[m.metric_type] = m
        
        metrics = []
        for mtype, m in metric_map.items():
            threshold = m.critical_threshold or 85
            metrics.append({'name': mtype, 'value': m.value, 'threshold': threshold})
        
        if not metrics:
            return {'name': 'unknown', 'value': 0, 'threshold': 100}
        
        worst = max(metrics, key=lambda m: m['value'] / m['threshold'])
        return worst
    
    def acknowledge_alert(self, alert_id: str) -> Optional[Alert]:
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert and alert.status == 'active':
            alert.status = 'acknowledged'
            alert.acknowledged_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(alert)
        return alert
    
    def resolve_alert(self, alert_id: str) -> Optional[Alert]:
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert and alert.status != 'resolved':
            alert.status = 'resolved'
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(alert)
        return alert


def get_all_alerts(db: Session, status: Optional[str] = None) -> List[Alert]:
    query = db.query(Alert).order_by(Alert.created_at.desc())
    if status:
        query = query.filter(Alert.status == status)
    return query.all()


def get_active_alerts(db: Session) -> List[Alert]:
    return db.query(Alert).filter(Alert.status == 'active').order_by(Alert.created_at.desc()).all()


def get_alert_by_id(db: Session, alert_id: str) -> Optional[Alert]:
    return db.query(Alert).filter(Alert.id == alert_id).first()