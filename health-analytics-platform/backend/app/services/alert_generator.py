import hashlib
import logging
from typing import List, Dict, Optional
from datetime import datetime
from ..models.models import Alert
from ..models.database import SessionLocal

logger = logging.getLogger(__name__)


def safe_float(value, default=0):
    """Safely convert value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class AlertGenerator:
    """Generates alerts based on component health and metrics."""
    
    def __init__(self):
        self.last_check = {}
    
    def check_components(self, components: List[Dict]) -> List[Dict]:
        """Check components and generate alerts."""
        alerts = []
        db = SessionLocal()
        
        try:
            for comp in components:
                comp_id = comp.get("id")
                status = comp.get("status", "unknown")
                health_score = safe_float(comp.get("health_score", 100))
                source = comp.get("source", "unknown")
                name = comp.get("name", comp_id)
                metrics = comp.get("metrics", {})
                
                # Check for critical status
                if status == "critical" or health_score < 30:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="critical",
                        title=f"Critical: {name}",
                        description=f"Component health is critical ({health_score:.1f}%). Immediate attention required.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                
                # Check for warning/degraded status
                elif status in ["warning", "degraded"] or (health_score < 70 and health_score >= 30):
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="warning",
                        title=f"Warning: {name}",
                        description=f"Component health is degraded ({health_score:.1f}%). Monitor closely.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                
                # Check CPU threshold
                cpu = safe_float(metrics.get("cpu_usage", 0))
                if cpu > 90:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="critical",
                        title=f"High CPU: {name}",
                        description=f"CPU usage is very high at {cpu:.1f}%.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                elif cpu > 75:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="warning",
                        title=f"Elevated CPU: {name}",
                        description=f"CPU usage is elevated at {cpu:.1f}%.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                
                # Check memory threshold
                memory = safe_float(metrics.get("memory_usage", metrics.get("memory_percent", 0)))
                if memory > 90:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="critical",
                        title=f"High Memory: {name}",
                        description=f"Memory usage is very high at {memory:.1f}%.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                elif memory > 80:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="warning",
                        title=f"Elevated Memory: {name}",
                        description=f"Memory usage is elevated at {memory:.1f}%.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                
                # Check disk threshold
                disk = safe_float(metrics.get("disk_usage", metrics.get("disk_percent", 0)))
                if disk > 95:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="critical",
                        title=f"Disk Pressure: {name}",
                        description=f"Disk usage is critical at {disk:.1f}%.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                elif disk > 85:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="warning",
                        title=f"Disk Warning: {name}",
                        description=f"Disk usage is high at {disk:.1f}%.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                
                # Check error rate for applications
                error_rate = safe_float(metrics.get("error_rate", 0))
                if error_rate > 10:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="critical",
                        title=f"High Error Rate: {name}",
                        description=f"Error rate is critical at {error_rate:.1f}%.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                elif error_rate > 5:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="warning",
                        title=f"Error Rate: {name}",
                        description=f"Error rate is elevated at {error_rate:.1f}%.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                
                # Check API latency
                latency = safe_float(metrics.get("api_latency", 0))
                if latency > 1000:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="critical",
                        title=f"High Latency: {name}",
                        description=f"API latency is critical at {latency:.0f}ms.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
                elif latency > 500:
                    alert = self._create_alert(
                        comp_id=comp_id,
                        name=name,
                        severity="warning",
                        title=f"Latency Warning: {name}",
                        description=f"API latency is elevated at {latency:.0f}ms.",
                        source=source,
                        metrics=metrics
                    )
                    alerts.append(alert)
        
        finally:
            db.close()
        
        return alerts
    
    def _create_alert(self, comp_id: str, name: str, severity: str, 
                     title: str, description: str, source: str, metrics: Dict) -> Dict:
        """Create an alert object."""
        title_slug = hashlib.md5(title.encode("utf-8")).hexdigest()[:10]
        return {
            "id": f"alert-{comp_id}-{severity}-{title_slug}",
            "component_id": comp_id,
            "component_name": name,
            "severity": severity,
            "status": "active",
            "title": title,
            "description": description,
            "source": source,
            "metrics": metrics,
            "created_at": datetime.utcnow().isoformat()
        }


_alert_generator = None


def get_alert_generator() -> AlertGenerator:
    global _alert_generator
    if _alert_generator is None:
        _alert_generator = AlertGenerator()
    return _alert_generator