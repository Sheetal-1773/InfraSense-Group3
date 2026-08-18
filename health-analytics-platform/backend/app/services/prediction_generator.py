import logging
import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PredictionGenerator:
    """Generates predictions based on component health trends."""
    
    def __init__(self):
        self._history = {}
    
    def generate_predictions(self, components: List[Dict]) -> List[Dict]:
        """Generate predictions for components."""
        predictions = []
        
        for comp in components:
            comp_id = comp.get("id")
            name = comp.get("name", comp_id)
            health_score = comp.get("health_score", 100)
            status = comp.get("status", "healthy")
            source = comp.get("source", "unknown")
            metrics = comp.get("metrics", {})
            
            # Skip healthy components
            if status == "healthy" and health_score > 80:
                continue
            
            # Predict CPU failure
            cpu = metrics.get("cpu_usage", 0)
            if cpu > 60:
                time_to_breach = max(5, 30 - (cpu - 60) * 0.5)
                confidence = min(95, 60 + (cpu - 60) * 0.8)
                predictions.append({
                    "id": f"pred-cpu-{comp_id}",
                    "component_id": comp_id,
                    "component_name": name,
                    "prediction_type": "cpu_failure",
                    "severity": "critical" if cpu > 80 else "warning",
                    "current_value": cpu,
                    "predicted_value": min(100, cpu + 20),
                    "time_to_breach_minutes": time_to_breach,
                    "confidence": confidence,
                    "explanation": f"CPU usage is at {cpu:.1f}% and trending upward. Expected to reach critical levels in {time_to_breach:.0f} minutes.",
                    "recommended_action": "Scale horizontally or optimize CPU-intensive processes",
                    "source": source,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat()
                })
            
            # Predict memory failure
            memory = metrics.get("memory_usage", metrics.get("memory_percent", 0))
            if memory > 60:
                time_to_breach = max(5, 30 - (memory - 60) * 0.5)
                confidence = min(95, 60 + (memory - 60) * 0.8)
                predictions.append({
                    "id": f"pred-mem-{comp_id}",
                    "component_id": comp_id,
                    "component_name": name,
                    "prediction_type": "memory_failure",
                    "severity": "critical" if memory > 80 else "warning",
                    "current_value": memory,
                    "predicted_value": min(100, memory + 20),
                    "time_to_breach_minutes": time_to_breach,
                    "confidence": confidence,
                    "explanation": f"Memory usage is at {memory:.1f}% and trending upward. Expected to reach critical levels in {time_to_breach:.0f} minutes.",
                    "recommended_action": "Increase memory allocation or optimize memory usage",
                    "source": source,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat()
                })
            
            # Predict disk failure
            disk = metrics.get("disk_usage", metrics.get("disk_percent", 0))
            if disk > 70:
                time_to_breach = max(10, 60 - (disk - 70) * 1.5)
                confidence = min(95, 50 + (disk - 70) * 1.2)
                predictions.append({
                    "id": f"pred-disk-{comp_id}",
                    "component_id": comp_id,
                    "component_name": name,
                    "prediction_type": "disk_failure",
                    "severity": "critical" if disk > 90 else "warning",
                    "current_value": disk,
                    "predicted_value": min(100, disk + 15),
                    "time_to_breach_minutes": time_to_breach,
                    "confidence": confidence,
                    "explanation": f"Disk usage is at {disk:.1f}%. Expected to reach critical levels in {time_to_breach:.0f} minutes.",
                    "recommended_action": "Clean up old logs, archives, or expand storage",
                    "source": source,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat()
                })
            
            # Predict API latency
            latency = metrics.get("api_latency", 0)
            if latency > 300:
                time_to_breach = max(5, 20 - (latency - 300) * 0.05)
                confidence = min(90, 50 + (latency - 300) * 0.1)
                predictions.append({
                    "id": f"pred-latency-{comp_id}",
                    "component_id": comp_id,
                    "component_name": name,
                    "prediction_type": "latency_failure",
                    "severity": "critical" if latency > 800 else "warning",
                    "current_value": latency,
                    "predicted_value": latency * 1.5,
                    "time_to_breach_minutes": time_to_breach,
                    "confidence": confidence,
                    "explanation": f"API latency is at {latency:.0f}ms. Expected to increase further.",
                    "recommended_action": "Check database queries and optimize API endpoints",
                    "source": source,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat()
                })
            
            # Predict error rate
            error_rate = metrics.get("error_rate", 0)
            if error_rate > 2:
                time_to_breach = max(5, 15 - error_rate * 0.5)
                confidence = min(95, 60 + error_rate * 2)
                predictions.append({
                    "id": f"pred-error-{comp_id}",
                    "component_id": comp_id,
                    "component_name": name,
                    "prediction_type": "error_failure",
                    "severity": "critical" if error_rate > 10 else "warning",
                    "current_value": error_rate,
                    "predicted_value": min(50, error_rate * 2),
                    "time_to_breach_minutes": time_to_breach,
                    "confidence": confidence,
                    "explanation": f"Error rate is at {error_rate:.1f}%. Expected to increase further.",
                    "recommended_action": "Check application logs for errors and fix underlying issues",
                    "source": source,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat()
                })
            
            # General health prediction
            if health_score < 70:
                time_to_breach = max(10, (health_score - 30) * 0.5)
                confidence = min(90, 50 + (70 - health_score) * 0.8)
                predictions.append({
                    "id": f"pred-health-{comp_id}",
                    "component_id": comp_id,
                    "component_name": name,
                    "prediction_type": "health_degradation",
                    "severity": "critical" if health_score < 40 else "warning",
                    "current_value": health_score,
                    "predicted_value": max(0, health_score - 20),
                    "time_to_breach_minutes": time_to_breach,
                    "confidence": confidence,
                    "explanation": f"Component health score is {health_score:.1f}%. Risk of failure increasing.",
                    "recommended_action": "Investigate component health and address root causes",
                    "source": source,
                    "status": "active",
                    "created_at": datetime.utcnow().isoformat()
                })
        
        return predictions


_prediction_generator = None


def get_prediction_generator() -> PredictionGenerator:
    global _prediction_generator
    if _prediction_generator is None:
        _prediction_generator = PredictionGenerator()
    return _prediction_generator