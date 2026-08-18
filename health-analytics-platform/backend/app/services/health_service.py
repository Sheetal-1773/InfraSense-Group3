import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from ..models.models import Category, Component, ComponentMetric, HealthScoreHistory, Threshold
from ..services.data_sources import get_data_source, DataSourceAdapter

_data_source_adapter: Optional[DataSourceAdapter] = None

_threshold_exceeded_duration: Dict[str, datetime] = {}


def get_data_adapter() -> DataSourceAdapter:
    """Get the data source adapter (singleton)."""
    global _data_source_adapter
    if _data_source_adapter is None:
        _data_source_adapter = get_data_source()
    return _data_source_adapter


def set_data_adapter(adapter: DataSourceAdapter):
    """Set a custom data source adapter (for testing)."""
    global _data_source_adapter
    _data_source_adapter = adapter


class HealthCalculator:
    DEFAULT_THRESHOLDS = {
        'cpu': {'warning': 70, 'critical': 85},
        'memory': {'warning': 75, 'critical': 90},
        'disk': {'warning': 80, 'critical': 95},
        'latency': {'warning': 100, 'critical': 200},
        'error_rate': {'warning': 2, 'critical': 5},
        'response_time': {'warning': 500, 'critical': 1000},
        'connections': {'warning': 80, 'critical': 95},
        'throughput': {'warning': 80, 'critical': 95},
        'packet_loss': {'warning': 1, 'critical': 5},
        'availability': {'warning': 99, 'critical': 95},
    }

    @staticmethod
    def safe_number(value: Optional[float], default: int = 0) -> float:
        if value is None:
            return float(default)
        if value != value:
            return float(default)
        return float(value)

    @staticmethod
    def calculate_health_score(metrics: List[ComponentMetric]) -> tuple[int, str]:
        if not metrics:
            return 0, "Unknown"

        scores = []
        for metric in metrics:
            score = HealthCalculator._calculate_metric_score(
                getattr(metric, 'current_value', None) or getattr(metric, 'value', 0),
                metric.metric_type,
                metric.warning_threshold,
                metric.critical_threshold
            )
            if score is not None:
                scores.append(score)

        if not scores:
            return 0, "Unknown"

        weighted_score = sum(scores) / len(scores)
        final_score = int(max(0, min(100, weighted_score)))
        status = HealthCalculator.get_status(final_score)

        return final_score, status

    @staticmethod
    def _calculate_metric_score(value: Optional[float], metric_type: str, 
                                  warning: Optional[float] = None, 
                                  critical: Optional[float] = None) -> Optional[float]:
        if value is None:
            return None

        w = warning if warning is not None else HealthCalculator.DEFAULT_THRESHOLDS.get(metric_type, {}).get('warning', 70)
        c = critical if critical is not None else HealthCalculator.DEFAULT_THRESHOLDS.get(metric_type, {}).get('critical', 85)

        if metric_type == 'availability':
            if value >= 99:
                return 100
            elif value >= 95:
                return 70 + (value - 95) * 6
            else:
                return max(0, (value / 95) * 70)

        if value >= c:
            return max(0, 30 - (value - c) * 2)
        elif value >= w:
            return 70 - (value - w) * (40 / (c - w)) if c > w else 70
        else:
            return 100 - (value / w) * 30 if w > 0 else 100

    @staticmethod
    def get_status(score: int) -> str:
        if score >= 90:
            return "Healthy"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Warning"
        elif score > 0:
            return "Critical"
        else:
            return "Unknown"


def calculate_category_health(db: Session, category_id: int) -> Dict:
    components = db.query(Component).filter(Component.category_id == category_id).all()
    
    if not components:
        return {
            'score': None,
            'status': 'Unknown',
            'totalComponents': 0,
            'healthyComponents': 0,
            'warningComponents': 0,
            'criticalComponents': 0,
            'unknownComponents': 0
        }

    total_score = 0
    valid_scores = 0
    healthy = 0
    warning = 0
    critical = 0
    unknown = 0

    for comp in components:
        if comp.health_score is None or comp.health_score == 0:
            unknown += 1
        elif comp.health_score >= 90:
            healthy += 1
            total_score += comp.health_score
            valid_scores += 1
        elif comp.health_score >= 70:
            warning += 1
            total_score += comp.health_score
            valid_scores += 1
        else:
            critical += 1
            total_score += comp.health_score
            valid_scores += 1

    if valid_scores > 0:
        score = int(total_score / valid_scores)
        status = HealthCalculator.get_status(score)
    else:
        score = None
        status = "Unknown"

    return {
        'score': score,
        'status': status,
        'totalComponents': len(components),
        'healthyComponents': healthy,
        'warningComponents': warning,
        'criticalComponents': critical,
        'unknownComponents': unknown
    }


def calculate_overall_health(db: Session) -> Dict:
    components = db.query(Component).all()
    
    if not components:
        return {
            'overall': {'score': None, 'status': 'Unknown'},
            'categories': {}
        }
    
    CRITICALITY_WEIGHTS = {
        'critical': 2.0,
        'high': 1.5,
        'medium': 1.0,
        'low': 0.5,
    }
    
    weighted_sum = 0
    total_weight = 0
    lowest_critical = None
    
    for comp in components:
        if comp.health_score is None or comp.health_score == 0:
            continue
        
        weight = CRITICALITY_WEIGHTS.get(comp.criticality, 1.0)
        weighted_sum += comp.health_score * weight
        total_weight += weight
        
        if comp.health_score <= 30:
            if lowest_critical is None or comp.health_score < lowest_critical:
                lowest_critical = comp.health_score
    
    if total_weight > 0:
        overall_score = int(weighted_sum / total_weight)
        
        if lowest_critical is not None and lowest_critical < overall_score:
            overall_score = lowest_critical
        
        overall_status = HealthCalculator.get_status(overall_score)
    else:
        overall_score = None
        overall_status = "Unknown"
    
    categories = db.query(Category).all()
    category_healths = {}
    for cat in categories:
        health = calculate_category_health(db, cat.id)
        category_healths[cat.type] = health

    return {
        'overall': {'score': overall_score, 'status': overall_status},
        'categories': category_healths
    }


def update_component_metrics(db: Session, component: Component) -> Component:
    metrics = db.query(ComponentMetric).filter(
        ComponentMetric.component_id == component.id
    ).order_by(ComponentMetric.timestamp.desc()).limit(20).all()

    health_score, status = HealthCalculator.calculate_health_score(metrics)
    
    component.health_score = health_score
    component.status = status.lower()
    component.last_seen = datetime.utcnow()
    component.updated_at = datetime.utcnow()

    db.add(HealthScoreHistory(
        component_id=component.id,
        score=health_score,
        timestamp=datetime.utcnow()
    ))

    db.commit()
    db.refresh(component)
    return component


def get_health_trend(db: Session, hours: int = 24) -> List[Dict]:
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    recent_scores = db.query(HealthScoreHistory).filter(
        HealthScoreHistory.timestamp >= cutoff
    ).order_by(HealthScoreHistory.timestamp).all()
    
    if not recent_scores:
        return [{'timestamp': datetime.utcnow().isoformat(), 'score': 100}]
    
    hourly_scores = {}
    for score in recent_scores:
        hour_key = score.timestamp.replace(minute=0, second=0, microsecond=0)
        if hour_key not in hourly_scores:
            hourly_scores[hour_key] = []
        hourly_scores[hour_key].append(score.score)
    
    trend = []
    for hour, scores in sorted(hourly_scores.items()):
        trend.append({
            'timestamp': hour.isoformat(),
            'score': int(sum(scores) / len(scores))
        })
    
    return trend


def get_components_from_datasource() -> List[Dict]:
    """Get components through the data source abstraction layer."""
    adapter = get_data_adapter()
    return adapter.get_components()


def get_component_metrics_from_datasource(component_id: str) -> Dict[str, float]:
    """Get latest metrics for a component through the abstraction layer."""
    adapter = get_data_adapter()
    return adapter.get_latest_metrics(component_id)


def check_threshold_duration(component_id: str, metric_name: str, 
                              is_exceeded: bool, db: Session) -> tuple[bool, Optional[int]]:
    """
    Check if a metric has exceeded its threshold for the configured duration.
    Returns (should_alert, duration_minutes).
    """
    key = f"{component_id}:{metric_name}"
    
    threshold = db.query(Threshold).filter(
        Threshold.metric_name == metric_name
    ).first()
    
    if not threshold or threshold.duration_minutes == 0:
        return is_exceeded, 0
    
    if is_exceeded:
        if key not in _threshold_exceeded_duration:
            _threshold_exceeded_duration[key] = datetime.utcnow()
        
        duration = datetime.utcnow() - _threshold_exceeded_duration[key]
        duration_minutes = int(duration.total_seconds() / 60)
        
        if duration_minutes >= threshold.duration_minutes:
            return True, duration_minutes
        return False, duration_minutes
    else:
        if key in _threshold_exceeded_duration:
            del _threshold_exceeded_duration[key]
        return False, 0


def get_threshold_exceeded_duration(component_id: str, metric_name: str) -> Optional[int]:
    """Get the current duration a threshold has been exceeded (in minutes)."""
    key = f"{component_id}:{metric_name}"
    if key not in _threshold_exceeded_duration:
        return None
    
    duration = datetime.utcnow() - _threshold_exceeded_duration[key]
    return int(duration.total_seconds() / 60)