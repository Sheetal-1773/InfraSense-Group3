import platform
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available, local infrastructure metrics will be limited")

from .base import DataSourceAdapter


class LocalInfrastructureAdapter(DataSourceAdapter):
    """Adapter for local PC/server infrastructure metrics."""
    
    def __init__(self):
        self._components = self._discover_local_components()
        self._last_metrics = {}
        self._metrics_history = []
        self._max_history = 100
    
    @property
    def cloud_provider(self) -> str:
        return "local"
    
    def _discover_local_components(self) -> List[Dict]:
        """Discover local infrastructure components."""
        components = []
        hostname = platform.node()
        
        components.append({
            "id": f"local-{hostname}-system",
            "name": f"Local System: {hostname}",
            "category": "server",
            "type": "server",
            "hostname": hostname,
            "environment": "local",
            "status": "healthy",
            "provider": "local",
            "source": "psutil",
            "description": f"Local development machine ({platform.system()} {platform.release()})"
        })
        
        components.append({
            "id": f"local-{hostname}-cpu",
            "name": f"Local CPU: {hostname}",
            "category": "server",
            "type": "server",
            "hostname": hostname,
            "environment": "local",
            "status": "healthy",
            "provider": "local",
            "source": "psutil",
            "description": f"CPU on {hostname}"
        })
        
        components.append({
            "id": f"local-{hostname}-memory",
            "name": f"Local Memory: {hostname}",
            "category": "server",
            "type": "server",
            "hostname": hostname,
            "environment": "local",
            "status": "healthy",
            "provider": "local",
            "source": "psutil",
            "description": f"Memory on {hostname}"
        })
        
        components.append({
            "id": f"local-{hostname}-disk",
            "name": f"Local Disk: {hostname}",
            "category": "server",
            "type": "server",
            "hostname": hostname,
            "environment": "local",
            "status": "healthy",
            "provider": "local",
            "source": "psutil",
            "description": f"Disk on {hostname}"
        })
        
        components.append({
            "id": f"local-{hostname}-network",
            "name": f"Local Network: {hostname}",
            "category": "network",
            "type": "network",
            "hostname": hostname,
            "environment": "local",
            "status": "healthy",
            "provider": "local",
            "source": "psutil",
            "description": f"Network on {hostname}"
        })
        
        components.append({
            "id": "local-development-app",
            "name": "Local Development Application",
            "category": "application",
            "type": "application",
            "hostname": hostname,
            "environment": "local",
            "status": "healthy",
            "provider": "local",
            "source": "psutil",
            "description": "Local running applications"
        })
        
        return components
    
    def _collect_system_metrics(self) -> Dict:
        """Collect system-level metrics."""
        if not PSUTIL_AVAILABLE:
            return self._get_fallback_metrics()
        
        metrics = {}
        
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            metrics["cpu_usage"] = cpu_percent
            metrics["cpu_count"] = cpu_count
            if cpu_freq:
                metrics["cpu_frequency"] = cpu_freq.current
            
            cpu_times = psutil.cpu_times()
            metrics["cpu_user"] = cpu_times.user
            metrics["cpu_system"] = cpu_times.system
            metrics["cpu_idle"] = cpu_times.idle
            
        except Exception as e:
            logger.warning(f"Failed to collect CPU metrics: {e}")
            metrics["cpu_usage"] = 50
        
        try:
            memory = psutil.virtual_memory()
            metrics["memory_total"] = memory.total
            metrics["memory_available"] = memory.available
            metrics["memory_used"] = memory.used
            metrics["memory_percent"] = memory.percent
        except Exception as e:
            logger.warning(f"Failed to collect memory metrics: {e}")
            metrics["memory_percent"] = 50
        
        try:
            disk = psutil.disk_usage('/')
            metrics["disk_total"] = disk.total
            metrics["disk_used"] = disk.used
            metrics["disk_free"] = disk.free
            metrics["disk_percent"] = disk.percent
        except Exception as e:
            logger.warning(f"Failed to collect disk metrics: {e}")
            metrics["disk_percent"] = 50
        
        try:
            net_io = psutil.net_io_counters()
            metrics["network_bytes_sent"] = net_io.bytes_sent
            metrics["network_bytes_recv"] = net_io.bytes_recv
            metrics["network_packets_sent"] = net_io.packets_sent
            metrics["network_packets_recv"] = net_io.packets_recv
            metrics["network_errin"] = net_io.errin
            metrics["network_errout"] = net_io.errout
        except Exception as e:
            logger.warning(f"Failed to collect network metrics: {e}")
        
        try:
            boot_time = psutil.boot_time()
            uptime = datetime.now().timestamp() - boot_time
            metrics["uptime_seconds"] = uptime
            metrics["uptime_hours"] = uptime / 3600
        except Exception as e:
            logger.warning(f"Failed to collect uptime: {e}")
            metrics["uptime_hours"] = 24
        
        return metrics
    
    def _get_fallback_metrics(self) -> Dict:
        """Return fallback metrics when psutil is not available."""
        return {
            "cpu_usage": 45,
            "cpu_count": 4,
            "memory_percent": 55,
            "disk_percent": 50,
            "network_bytes_sent": 1000000,
            "network_bytes_recv": 1000000,
            "uptime_hours": 24
        }
    
    def _calculate_health_score(self, metrics: Dict) -> tuple:
        """Calculate health score and status from metrics."""
        cpu = metrics.get("cpu_usage", 0)
        memory = metrics.get("memory_percent", 0)
        disk = metrics.get("disk_percent", 0)
        
        scores = []
        
        if cpu >= 90:
            scores.append(20)
        elif cpu >= 75:
            scores.append(50)
        elif cpu >= 50:
            scores.append(80)
        else:
            scores.append(100)
        
        if memory >= 90:
            scores.append(20)
        elif memory >= 75:
            scores.append(50)
        elif memory >= 50:
            scores.append(80)
        else:
            scores.append(100)
        
        if disk >= 95:
            scores.append(20)
        elif disk >= 85:
            scores.append(50)
        elif disk >= 70:
            scores.append(80)
        else:
            scores.append(100)
        
        health_score = sum(scores) / len(scores) if scores else 100
        
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 50:
            status = "warning"
        else:
            status = "critical"
        
        return health_score, status
    
    def get_components(self) -> List[Dict]:
        """Get all local components with current metrics."""
        metrics = self._collect_system_metrics()
        
        self._metrics_history.append({
            "timestamp": datetime.utcnow(),
            "metrics": metrics.copy()
        })
        
        if len(self._metrics_history) > self._max_history:
            self._metrics_history.pop(0)
        
        health_score, status = self._calculate_health_score(metrics)
        
        result = []
        for comp in self._components:
            comp_copy = comp.copy()
            comp_copy["status"] = status
            comp_copy["health_score"] = health_score
            comp_copy["last_seen"] = datetime.utcnow().isoformat()
            comp_copy["metrics"] = metrics.copy()
            result.append(comp_copy)
        
        return result
    
    def get_component(self, component_id: str) -> Optional[Dict]:
        """Get a specific component."""
        for comp in self.get_components():
            if comp["id"] == component_id:
                return comp
        return None
    
    def get_metrics(self, component_id: str, metric_names: List[str],
                    start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get historical metrics for a component."""
        metrics = []
        
        for entry in self._metrics_history:
            if start_time <= entry["timestamp"] <= end_time:
                for metric_name in metric_names:
                    if metric_name in entry["metrics"]:
                        metrics.append({
                            "timestamp": entry["timestamp"],
                            "metric_name": metric_name,
                            "value": entry["metrics"][metric_name]
                        })
        
        return metrics
    
    def get_latest_metrics(self, component_id: str) -> Dict[str, float]:
        """Get latest metrics for a component."""
        if self._metrics_history:
            return self._metrics_history[-1]["metrics"].copy()
        return self._collect_system_metrics()
    
    def get_all_latest_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get latest metrics for all components."""
        metrics = self._collect_system_metrics()
        
        result = {}
        for comp in self._components:
            result[comp["id"]] = metrics.copy()
        
        return result
    
    def is_available(self) -> bool:
        """Check if local metrics are available."""
        return True
    
    def get_historical_trend(self, metric_name: str, hours: int = 24) -> Dict:
        """Get historical trend for a metric."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        values = []
        timestamps = []
        
        for entry in self._metrics_history:
            if entry["timestamp"] >= cutoff and metric_name in entry["metrics"]:
                values.append(entry["metrics"][metric_name])
                timestamps.append(entry["timestamp"])
        
        if not values:
            return {
                "metric": metric_name,
                "current": 0,
                "average": 0,
                "min": 0,
                "max": 0,
                "trend": "stable",
                "rate_of_change": 0
            }
        
        current = values[-1]
        average = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)
        
        if len(values) >= 2:
            rate_of_change = (values[-1] - values[0]) / len(values)
            if rate_of_change > 0.5:
                trend = "increasing"
            elif rate_of_change < -0.5:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            rate_of_change = 0
            trend = "stable"
        
        return {
            "metric": metric_name,
            "current": current,
            "average": average,
            "min": min_val,
            "max": max_val,
            "trend": trend,
            "rate_of_change": rate_of_change,
            "data_points": len(values)
        }


def get_local_adapter() -> LocalInfrastructureAdapter:
    """Factory function to get the local infrastructure adapter."""
    return LocalInfrastructureAdapter()