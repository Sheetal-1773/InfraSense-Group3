import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
import statistics

from ..models.models import Component, ComponentMetric, Threshold, Anomaly as AnomalyModel

logger = logging.getLogger(__name__)

ANOMALY_STD_DEV_THRESHOLD = float(os.getenv("ANOMALY_STD_DEV_THRESHOLD", "2.5"))


class Anomaly:
    def __init__(self, component_id: str, metric_name: str, value: float,
                 threshold: float, threshold_type: str, severity: str,
                 anomaly_type: str = "threshold", explanation: str = None):
        self.component_id = component_id
        self.metric_name = metric_name
        self.value = value
        self.threshold = threshold
        self.threshold_type = threshold_type
        self.severity = severity
        self.anomaly_type = anomaly_type
        self.explanation = explanation
        self.timestamp = datetime.utcnow()


def check_static_thresholds(db: Session, component: Component, metrics: List[ComponentMetric]) -> List[Anomaly]:
    """Check metrics against static thresholds and return list of anomalies."""
    anomalies = []

    thresholds = db.query(Threshold).filter(
        Threshold.component_type == component.category.type if component.category else "server"
    ).all()

    threshold_map = {t.metric_name: t for t in thresholds}

    for metric in metrics:
        threshold_def = threshold_map.get(metric.metric_name)
        if not threshold_def:
            continue

        if metric.value >= threshold_def.critical_threshold:
            anomalies.append(Anomaly(
                component_id=component.id,
                metric_name=metric.metric_name,
                value=metric.value,
                threshold=threshold_def.critical_threshold,
                threshold_type="critical",
                severity="critical",
                explanation=f"Value {metric.value:.1f} exceeds critical threshold {threshold_def.critical_threshold}"
            ))
        elif metric.value >= threshold_def.warning_threshold:
            anomalies.append(Anomaly(
                component_id=component.id,
                metric_name=metric.metric_name,
                value=metric.value,
                threshold=threshold_def.warning_threshold,
                threshold_type="warning",
                severity="warning",
                explanation=f"Value {metric.value:.1f} exceeds warning threshold {threshold_def.warning_threshold}"
            ))

    return anomalies


def detect_statistical_anomalies(db: Session, component_id: str, metric_name: str,
                                  lookback_hours: int = 24, min_data_points: int = 10) -> Optional[Dict]:
    """Detect statistical anomalies using historical data."""
    cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)

    metrics = db.query(ComponentMetric).filter(
        ComponentMetric.component_id == component_id,
        ComponentMetric.metric_name == metric_name,
        ComponentMetric.timestamp >= cutoff
    ).order_by(ComponentMetric.timestamp.asc()).all()

    if len(metrics) < min_data_points:
        return None

    values = [m.value for m in metrics if m.value is not None]
    if len(values) < min_data_points:
        return None

    try:
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0

        if stdev == 0:
            return None

        latest_value = values[-1]
        z_score = abs(latest_value - mean) / stdev

        if z_score > ANOMALY_STD_DEV_THRESHOLD:
            direction = "above" if latest_value > mean else "below"
            return {
                "type": "statistical",
                "z_score": round(z_score, 2),
                "mean": round(mean, 2),
                "stdev": round(stdev, 2),
                "latest_value": latest_value,
                "direction": direction,
                "explanation": f"Current value {latest_value:.1f} is {z_score:.1f} standard deviations {direction} the historical mean of {mean:.1f}"
            }

    except statistics.StatisticsError as e:
        logger.error(f"Statistics error for {component_id}/{metric_name}: {e}")

    return None


def detect_trend_anomalies(db: Session, component_id: str, metric_name: str,
                           lookback_points: int = 10) -> Optional[Dict]:
    """Detect sudden changes in metric trends."""
    metrics = db.query(ComponentMetric).filter(
        ComponentMetric.component_id == component_id,
        ComponentMetric.metric_name == metric_name
    ).order_by(ComponentMetric.timestamp.desc()).limit(lookback_points).all()

    if len(metrics) < 5:
        return None

    values = [m.value for m in reversed(metrics)]

    if len(values) >= 3:
        recent_change = values[-1] - values[-3]
        if abs(recent_change) > 30:
            return {
                "type": "trend",
                "change": round(recent_change, 2),
                "explanation": f"Sudden change of {recent_change:.1f}% detected in last 3 data points"
            }

    return None


def detect_pattern_anomalies(db: Session, component_id: str, metric_name: str) -> Optional[Dict]:
    """Detect unusual patterns in metric data."""
    cutoff_1h = datetime.utcnow() - timedelta(hours=1)
    cutoff_24h = datetime.utcnow() - timedelta(hours=24)

    recent = db.query(ComponentMetric).filter(
        ComponentMetric.component_id == component_id,
        ComponentMetric.metric_name == metric_name,
        ComponentMetric.timestamp >= cutoff_1h
    ).all()

    historical = db.query(ComponentMetric).filter(
        ComponentMetric.component_id == component_id,
        ComponentMetric.metric_name == metric_name,
        ComponentMetric.timestamp >= cutoff_24h,
        ComponentMetric.timestamp < cutoff_1h
    ).all()

    if len(recent) < 3 or len(historical) < 3:
        return None

    recent_avg = statistics.mean([m.value for m in recent])
    historical_avg = statistics.mean([m.value for m in historical])

    if historical_avg > 0:
        pct_change = ((recent_avg - historical_avg) / historical_avg) * 100

        if abs(pct_change) > 50:
            return {
                "type": "pattern",
                "recent_avg": round(recent_avg, 2),
                "historical_avg": round(historical_avg, 2),
                "pct_change": round(pct_change, 2),
                "explanation": f"Current average {recent_avg:.1f} differs by {pct_change:.1f}% from historical average {historical_avg:.1f}"
            }

    return None


def analyze_component_anomalies(db: Session, component_id: str) -> List[Anomaly]:
    """Perform comprehensive anomaly analysis on a component."""
    anomalies = []

    component = db.query(Component).filter(Component.id == component_id).first()
    if not component:
        return anomalies

    metrics = db.query(ComponentMetric).filter(
        ComponentMetric.component_id == component_id
    ).order_by(ComponentMetric.timestamp.desc()).limit(20).all()

    metric_names = set(m.metric_name for m in metrics)

    threshold_anomalies = check_static_thresholds(db, component, metrics)
    anomalies.extend(threshold_anomalies)

    for metric_name in metric_names:
        statistical = detect_statistical_anomalies(db, component_id, metric_name)
        if statistical:
            latest_metric = next((m for m in metrics if m.metric_name == metric_name), None)
            if latest_metric:
                anomalies.append(Anomaly(
                    component_id=component_id,
                    metric_name=metric_name,
                    value=latest_metric.value,
                    threshold=statistical.get("mean", 0),
                    threshold_type="statistical",
                    severity="warning" if statistical.get("z_score", 0) < 3 else "critical",
                    anomaly_type="statistical",
                    explanation=statistical.get("explanation")
                ))

        trend = detect_trend_anomalies(db, component_id, metric_name)
        if trend:
            latest_metric = next((m for m in metrics if m.metric_name == metric_name), None)
            if latest_metric:
                anomalies.append(Anomaly(
                    component_id=component_id,
                    metric_name=metric_name,
                    value=latest_metric.value,
                    threshold=0,
                    threshold_type="trend",
                    severity="warning",
                    anomaly_type="trend",
                    explanation=trend.get("explanation")
                ))

    return anomalies


def save_anomalies(db: Session, anomalies: List[Anomaly]) -> List[AnomalyModel]:
    """Save anomalies to the database."""
    saved = []
    for anomaly in anomalies:
        existing = db.query(AnomalyModel).filter(
            AnomalyModel.component_id == anomaly.component_id,
            AnomalyModel.metric_name == anomaly.metric_name,
            AnomalyModel.detected_at >= datetime.utcnow() - timedelta(minutes=5)
        ).first()

        if existing:
            continue

        db_anomaly = AnomalyModel(
            id=f"anomaly-{anomaly.component_id}-{anomaly.metric_name}-{int(anomaly.timestamp.timestamp() * 1000)}",
            component_id=anomaly.component_id,
            metric_name=anomaly.metric_name,
            value=anomaly.value,
            threshold=anomaly.threshold,
            threshold_type=anomaly.threshold_type,
            severity=anomaly.severity,
            detected_at=anomaly.timestamp
        )
        db.add(db_anomaly)
        saved.append(db_anomaly)

    db.commit()
    return saved


def detect_anomalies(db: Session, component_id: str, save: bool = True) -> List[Dict]:
    """Detect anomalies for a specific component."""
    anomalies = analyze_component_anomalies(db, component_id)

    if save and anomalies:
        save_anomalies(db, anomalies)

    return [
        {
            "component_id": a.component_id,
            "metric_name": a.metric_name,
            "value": a.value,
            "threshold": a.threshold,
            "threshold_type": a.threshold_type,
            "anomaly_type": a.anomaly_type,
            "severity": a.severity,
            "explanation": a.explanation,
            "timestamp": a.timestamp.isoformat()
        }
        for a in anomalies
    ]


def get_all_anomalies(db: Session, hours: int = 24) -> List[Dict]:
    """Get all recent anomalies across all components."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    anomalies = db.query(AnomalyModel).filter(
        AnomalyModel.detected_at >= cutoff
    ).order_by(AnomalyModel.detected_at.desc()).all()

    return [
        {
            "id": a.id,
            "component_id": a.component_id,
            "metric_name": a.metric_name,
            "value": a.value,
            "threshold": a.threshold,
            "threshold_type": a.threshold_type,
            "severity": a.severity,
            "detected_at": a.detected_at.isoformat()
        }
        for a in anomalies
    ]


def run_anomaly_detection(db: Session):
    """Run anomaly detection on all components."""
    components = db.query(Component).all()

    for component in components:
        try:
            anomalies = detect_anomalies(db, component.id, save=True)
            if anomalies:
                logger.info(f"Detected {len(anomalies)} anomalies for {component.id}")
        except Exception as e:
            logger.error(f"Error detecting anomalies for {component.id}: {e}")