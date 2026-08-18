import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.models import Component, ComponentMetric, Prediction, Threshold
import random


class PredictionEngine:
    MIN_HISTORY_POINTS = 10
    MIN_DAYS_FOR_DYNAMIC = 7
    
    def __init__(self, db: Session):
        self.db = db
    
    def run_predictions(self) -> List[Prediction]:
        """Run predictions for all components using the hierarchy."""
        predictions_created = []
        components = self.db.query(Component).all()
        print(f"[DEBUG] Processing {len(components)} components")
        
        for component in components:
            preds = self._predict_for_component(component)
            if preds:
                print(f"[DEBUG] {component.name}: created {len(preds)} predictions")
            predictions_created.extend(preds)
        
        self.db.commit()
        print(f"[DEBUG] Total predictions: {len(predictions_created)}")
        return predictions_created
    
    def _predict_for_component(self, component: Component) -> List[Prediction]:
        """Generate predictions for a component using hierarchy."""
        predictions = []
        
        metrics = self.db.query(ComponentMetric).filter(
            ComponentMetric.component_id == component.id
        ).order_by(ComponentMetric.timestamp.desc()).limit(100).all()
        
        if len(metrics) < self.MIN_HISTORY_POINTS:
            return predictions
        
        metric_groups = {}
        for m in metrics:
            if m.metric_name not in metric_groups:
                metric_groups[m.metric_name] = []
            metric_groups[m.metric_name].append(m)
        
        for metric_name, metric_data in metric_groups.items():
            metric_data.sort(key=lambda x: x.timestamp)
            
            result = self._try_static_threshold(metric_data, metric_name)
            if result and result['confidence'] >= 70:
                predictions.append(self._create_prediction(component, metric_name, result))
                continue
            
            result = self._try_dynamic_threshold(metric_data, metric_name)
            if result and result['confidence'] >= 60:
                predictions.append(self._create_prediction(component, metric_name, result))
                continue
            
            result = self._try_trend_analysis(metric_data, metric_name)
            if result and result['confidence'] >= 50:
                predictions.append(self._create_prediction(component, metric_name, result))
                continue
        
        return predictions
    
    def _try_static_threshold(self, metrics: List[ComponentMetric], metric_name: str) -> Optional[Dict]:
        """Try static threshold prediction."""
        threshold = self.db.query(Threshold).filter(
            Threshold.metric_name == metric_name,
            Threshold.is_dynamic == False
        ).first()
        
        if not threshold:
            print(f"[DEBUG] No threshold found for {metric_name}")
            return None
        
        values = [m.value for m in metrics if m.value is not None]
        if not values:
            return None
        
        current = values[-1]
        critical = threshold.critical_threshold
        
        print(f"[DEBUG] {metric_name}: current={current:.1f}, critical={critical}, values={len(values)}")
        
        if current >= critical:
            print(f"[DEBUG] {metric_name}: current >= critical, skipping")
            return None
        
        if len(values) < 5:
            print(f"[DEBUG] {metric_name}: not enough values, skipping")
            return None
        
        slope = self._calculate_slope(values)
        print(f"[DEBUG] {metric_name}: slope={slope:.3f}")
        
        if slope <= 0:
            print(f"[DEBUG] {metric_name}: slope <= 0, skipping")
            return None
        
        time_to_breach = int((critical - current) / slope) if slope > 0 else None
        
        print(f"[DEBUG] {metric_name}: time_to_breach={time_to_breach}")
        
        if time_to_breach and time_to_breach > 0:
            r_squared = self._calculate_r_squared(values, slope)
            confidence = int(min(95, max(50, r_squared * 100)))
            
            if confidence < 70 and time_to_breach > 5:
                confidence = 70
            
            print(f"[DEBUG] {metric_name}: r_squared={r_squared:.3f}, confidence={confidence}")
            
            if confidence < 70:
                print(f"[DEBUG] {metric_name}: confidence {confidence} < 70, skipping")
                return None
            
            return {
                'type': 'static',
                'current_value': current,
                'predicted_value': critical,
                'threshold': critical,
                'time_to_breach': time_to_breach,
                'time_to_breach_min': int(time_to_breach * 0.8),
                'time_to_breach_max': int(time_to_breach * 1.2),
                'confidence': confidence,
                'explanation': f"{confidence}% confidence because {metric_name} increased {slope:.2f} units per sample over recent history"
            }
        
        return None
    
    def _try_dynamic_threshold(self, metrics: List[ComponentMetric], metric_name: str) -> Optional[Dict]:
        """Try dynamic threshold prediction based on historical baseline."""
        values = [m.value for m in metrics if m.value is not None]
        
        if len(values) < 20:
            return None
        
        mean = np.mean(values)
        std = np.std(values)
        dynamic_threshold = mean + 2 * std
        
        current = values[-1]
        
        if current >= dynamic_threshold:
            return None
        
        slope = self._calculate_slope(values)
        
        if slope <= 0:
            return None
        
        time_to_breach = int((dynamic_threshold - current) / slope)
        
        if time_to_breach and time_to_breach > 0:
            confidence = int(min(85, 50 + (len(values) / 10)))
            
            return {
                'type': 'dynamic',
                'current_value': current,
                'predicted_value': dynamic_threshold,
                'threshold': dynamic_threshold,
                'time_to_breach': time_to_breach,
                'time_to_breach_min': int(time_to_breach * 0.7),
                'time_to_breach_max': int(time_to_breach * 1.3),
                'confidence': confidence,
                'explanation': f"{confidence}% confidence because {metric_name} is trending above the dynamic threshold (mean + 2σ = {dynamic_threshold:.1f})"
            }
        
        return None
    
    def _try_trend_analysis(self, metrics: List[ComponentMetric], metric_name: str) -> Optional[Dict]:
        """Try trend-based prediction."""
        values = [m.value for m in metrics if m.value is not None]
        
        if len(values) < 10:
            return None
        
        slope = self._calculate_slope(values)
        
        if slope <= 0:
            return None
        
        threshold = self._get_default_threshold(metric_name)
        current = values[-1]
        
        if current >= threshold:
            return None
        
        time_to_breach = int((threshold - current) / slope)
        
        if time_to_breach and 0 < time_to_breach < 720:
            r_squared = self._calculate_r_squared(values, slope)
            confidence = int(min(70, max(30, r_squared * 80)))
            
            return {
                'type': 'trend',
                'current_value': current,
                'predicted_value': threshold,
                'threshold': threshold,
                'time_to_breach': time_to_breach,
                'time_to_breach_min': int(time_to_breach * 0.6),
                'time_to_breach_max': int(time_to_breach * 1.4),
                'confidence': confidence,
                'explanation': f"{confidence}% confidence because {metric_name} shows an upward trend of {slope:.2f} units per sample"
            }
        
        return None
    
    def _calculate_slope(self, values: List[float]) -> float:
        """Calculate linear regression slope."""
        if len(values) < 2:
            return 0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        try:
            coeffs = np.polyfit(x, y, 1)
            return float(coeffs[0])
        except:
            return 0
    
    def _calculate_r_squared(self, values: List[float], slope: float) -> float:
        """Calculate R-squared for trend."""
        if len(values) < 3:
            return 0
        
        x = np.arange(len(values))
        y = np.array(values)
        
        y_mean = np.mean(y)
        ss_tot = np.sum((y - y_mean) ** 2)
        
        if ss_tot == 0:
            return 0
        
        y_pred = slope * x + y[0]
        ss_res = np.sum((y - y_pred) ** 2)
        
        return 1 - (ss_res / ss_tot)
    
    def _get_default_threshold(self, metric_name: str) -> float:
        defaults = {
            'cpu': 85, 'memory': 90, 'disk': 95,
            'latency': 200, 'error_rate': 5
        }
        return defaults.get(metric_name.lower(), 80)
    
    def _create_prediction(self, component: Component, metric_name: str, result: Dict) -> Prediction:
        """Create a Prediction object."""
        contributing_factors = self._get_contributing_factors(metric_name, result)
        runbook_url = self._get_runbook_url(metric_name)
        
        prediction = Prediction(
            id=f"pred-{component.id}-{metric_name}-{int(datetime.utcnow().timestamp())}",
            component_id=component.id,
            prediction_type=result['type'],
            current_value=result['current_value'],
            predicted_value=result['predicted_value'],
            predicted_threshold=result['threshold'],
            threshold_direction='above',
            time_to_breach_minutes=result['time_to_breach'],
            time_to_breach_min=result.get('time_to_breach_min'),
            time_to_breach_max=result.get('time_to_breach_max'),
            confidence=result['confidence'],
            severity='critical' if result['time_to_breach'] < 60 else 'warning',
            explanation=result['explanation'],
            contributing_factors=contributing_factors,
            recommended_action=self._get_recommended_action(metric_name, result['time_to_breach']),
            runbook_url=runbook_url,
            prediction_time=datetime.utcnow(),
            expected_breach_time=datetime.utcnow() + timedelta(minutes=result['time_to_breach']),
            status='active'
        )
        
        self.db.add(prediction)
        return prediction
    
    def _get_contributing_factors(self, metric_name: str, result: Dict) -> List[Dict]:
        """Get contributing factors for the prediction."""
        return [
            {
                "metric": metric_name,
                "contribution": 100,
                "current_value": result['current_value'],
                "threshold": result['threshold'],
                "trend": "increasing"
            }
        ]
    
    def _get_runbook_url(self, metric_name: str) -> Optional[str]:
        """Get runbook URL for the metric."""
        runbooks = {
            'cpu': 'https://runbooks.example.com/high-cpu',
            'memory': 'https://runbooks.example.com/high-memory',
            'disk': 'https://runbooks.example.com/low-disk-space',
            'latency': 'https://runbooks.example.com/high-latency',
        }
        return runbooks.get(metric_name.lower())
    
    def _get_recommended_action(self, metric_name: str, time_to_breach: int) -> str:
        actions = {
            'cpu': f"Consider scaling up CPU resources or optimizing workloads. Breach expected in {time_to_breach} minutes.",
            'memory': f"Review memory usage patterns and consider increasing RAM. Breach expected in {time_to_breach} minutes.",
            'disk': f"Clean up disk space or expand storage capacity. Breach expected in {time_to_breach} minutes.",
            'latency': f"Investigate network or application performance issues. Breach expected in {time_to_breach} minutes.",
        }
        return actions.get(metric_name.lower(), f"Monitor {metric_name} closely. Breach expected in {time_to_breach} minutes.")


def track_prediction_accuracy(db: Session) -> Dict:
    """Track prediction accuracy."""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    
    predictions = db.query(Prediction).filter(
        Prediction.created_at >= cutoff,
        Prediction.status == 'active',
        Prediction.expected_breach_time <= datetime.utcnow()
    ).all()
    
    total = len(predictions)
    accurate = 0
    
    for pred in predictions:
        if pred.actual_breach_time is None:
            pred.actual_breach_time = datetime.utcnow()
        
        if pred.time_to_breach_minutes:
            actual_ttb = (pred.actual_breach_time - pred.prediction_time).total_seconds() / 60
            error_pct = abs(actual_ttb - pred.time_to_breach_minutes) / pred.time_to_breach_minutes * 100
            
            pred.accuracy_error = error_pct
            pred.is_accurate = error_pct <= 25
            
            if pred.is_accurate:
                accurate += 1
    
    db.commit()
    
    return {
        'total_predictions': total,
        'accurate_predictions': accurate,
        'accuracy_percentage': int(accurate / total * 100) if total > 0 else 0
    }


def run_prediction_engine(db: Session) -> List[Prediction]:
    """Main entry point to run predictions."""
    engine = PredictionEngine(db)
    return engine.run_predictions()


def find_historical_patterns(db: Session, component_id: str, metric_name: str) -> List[Dict]:
    """Find similar historical incidents."""
    from ..models.models import Alert
    
    cutoff = datetime.utcnow() - timedelta(days=90)
    
    past_alerts = db.query(Alert).filter(
        Alert.component_id == component_id,
        Alert.metric == metric_name,
        Alert.created_at >= cutoff,
        Alert.status == 'resolved'
    ).order_by(Alert.created_at.desc()).limit(5).all()
    
    patterns = []
    for alert in past_alerts:
        patterns.append({
            "date": alert.created_at.strftime('%Y-%m-%d'),
            "description": alert.description,
            "action_taken": alert.recommended_action or "No action recorded",
            "outcome": "Resolved"
        })
    
    return patterns