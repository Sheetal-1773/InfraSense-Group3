import hashlib
import math
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .base import DataSourceAdapter


class MockSolarWindsAdapter(DataSourceAdapter):
    """Mock SolarWinds data source adapter for development and testing."""
    
    def __init__(self):
        self._components = self._generate_mock_components()
        self._metrics_cache = {}
        self._metrics_history = []
        self._max_history = 100
        self._base_time = datetime.utcnow()
    
    @property
    def cloud_provider(self) -> str:
        return "mock"
    
    def _generate_mock_components(self) -> List[Dict]:
        """Generate realistic mock components."""
        components = []
        
        servers = [
            ("prod-web-01", "Production Web Server 1", "server"),
            ("prod-web-02", "Production Web Server 2", "server"),
            ("prod-api-01", "Production API Server 1", "server"),
            ("prod-db-01", "Production Database Primary", "server"),
            ("prod-db-02", "Production Database Replica", "server"),
            ("staging-web-01", "Staging Web Server", "server"),
            ("dev-server-01", "Development Server", "server"),
        ]
        
        for comp_id, name, comp_type in servers:
            components.append({
                "id": comp_id,
                "name": name,
                "category": comp_type,
                "type": comp_type,
                "hostname": f"{comp_id}.example.com",
                "environment": "production" if "prod" in comp_id else "staging" if "staging" in comp_id else "development",
                "status": "healthy",
                "provider": "mock",
                "source": "mock",
                "description": f"Synthetic {comp_type} component"
            })
        
        networks = [
            ("core-router-01", "Core Router 1", "network"),
            ("edge-firewall-01", "Edge Firewall 1", "network"),
            ("switch-core-01", "Core Switch 1", "network"),
            ("app-network-01", "Application Network", "network"),
        ]
        
        for comp_id, name, comp_type in networks:
            components.append({
                "id": comp_id,
                "name": name,
                "category": comp_type,
                "type": comp_type,
                "hostname": f"{comp_id}.example.com",
                "environment": "production",
                "status": "healthy",
                "provider": "mock",
                "source": "mock",
                "description": f"Synthetic {comp_type} component"
            })
        
        applications = [
            ("customer-api-prod", "Customer API", "application"),
            ("payment-api-prod", "Payment API", "application"),
            ("auth-api-prod", "Authentication API", "application"),
            ("monitoring-api-prod", "Monitoring API", "application"),
        ]
        
        for comp_id, name, comp_type in applications:
            components.append({
                "id": comp_id,
                "name": name,
                "category": comp_type,
                "type": comp_type,
                "hostname": f"{comp_id}.example.com",
                "environment": "production",
                "status": "healthy",
                "provider": "mock",
                "source": "mock",
                "description": f"Synthetic {comp_type} component"
            })
        
        databases = [
            ("synthetic-customer-db", "Synthetic Customer DB", "database"),
            ("synthetic-payment-db", "Synthetic Payment DB", "database"),
            ("synthetic-auth-db", "Synthetic Auth DB", "database"),
            ("synthetic-monitoring-db", "Synthetic Monitoring DB", "database"),
        ]
        
        for comp_id, name, comp_type in databases:
            components.append({
                "id": comp_id,
                "name": name,
                "category": comp_type,
                "type": comp_type,
                "hostname": f"{comp_id}.example.com",
                "environment": "production",
                "status": "healthy",
                "provider": "mock",
                "source": "mock",
                "description": f"Synthetic {comp_type} component"
            })
        
        return components
    
    def _generate_metric_value(self, metric_name: str, timestamp: datetime, 
                                component_type: str, component_id: str) -> float:
        """Generate deterministic metric values with patterns."""
        base_values = {
            "server": {
                "cpu_usage": 45,
                "memory_usage": 60,
                "disk_usage": 55,
                "disk_io_read": 50000000,
                "disk_io_write": 30000000,
                "network_rx": 10000000,
                "network_tx": 5000000,
            },
            "network": {
                "bandwidth_utilization": 35,
                "packet_loss": 0.1,
                "latency": 5,
                "error_rate": 0.01,
            },
            "application": {
                "response_time": 150,
                "request_rate": 500,
                "error_rate": 0.5,
                "active_connections": 200,
            },
            "database": {
                "query_latency": 25,
                "connection_pool_usage": 65,
                "buffer_cache_hit_ratio": 95,
                "disk_io": 20000000,
            },
        }
        
        base = base_values.get(component_type, {}).get(metric_name, 50)
        
        hour_of_day = timestamp.hour
        day_factor = 1.0 + 0.3 * math.sin(2 * math.pi * (hour_of_day - 6) / 24)
        
        component_hash = int(hashlib.md5(f"{component_id}_{metric_name}".encode()).hexdigest()[:8], 16) % 100
        variance = (component_hash - 50) / 500
        
        trend = 0
        if "cpu" in metric_name or "memory" in metric_name:
            trend = (component_hash - 50) / 500
        
        value = base * day_factor * (1 + variance + trend)
        
        if "percent" in metric_name or "usage" in metric_name or "utilization" in metric_name:
            value = min(100, max(0, value))
        
        return round(value, 2)
    
    def get_components(self) -> List[Dict]:
        """Get list of all components with current metrics."""
        now = datetime.utcnow()
        
        self._metrics_history.append({
            "timestamp": now,
            "components": {c["id"]: self._generate_metric_values(c) for c in self._components}
        })
        
        if len(self._metrics_history) > self._max_history:
            self._metrics_history.pop(0)
        
        result = []
        for comp in self._components:
            comp_copy = comp.copy()
            metrics = self._generate_metric_values(comp)
            comp_copy["metrics"] = metrics
            comp_copy["last_seen"] = now.isoformat()
            
            health_score, status = self._calculate_health(comp["category"], metrics)
            comp_copy["health_score"] = health_score
            comp_copy["status"] = status
            
            result.append(comp_copy)
        
        return result
    
    def _generate_metric_values(self, component: Dict) -> Dict:
        """Generate metric values for a component."""
        component_type = component.get("category", component.get("type", "server"))
        component_id = component["id"]
        now = datetime.utcnow()
        
        metric_names = {
            "server": ["cpu_usage", "memory_usage", "disk_usage", "network_rx", "network_tx"],
            "network": ["bandwidth_utilization", "packet_loss", "latency", "error_rate"],
            "application": ["response_time", "request_rate", "error_rate", "active_connections"],
            "database": ["query_latency", "connection_pool_usage", "buffer_cache_hit_ratio", "disk_io"],
        }
        
        names = metric_names.get(component_type, ["cpu_usage", "memory_usage"])
        
        metrics = {}
        for name in names:
            metrics[name] = self._generate_metric_value(name, now, component_type, component_id)
        
        return metrics
    
    def _calculate_health(self, component_type: str, metrics: Dict) -> tuple:
        """Calculate health score and status from metrics."""
        scores = []
        
        if component_type == "server":
            cpu = metrics.get("cpu_usage", 0)
            memory = metrics.get("memory_usage", 0)
            disk = metrics.get("disk_usage", 0)
            
            for val in [cpu, memory, disk]:
                if val >= 90:
                    scores.append(20)
                elif val >= 75:
                    scores.append(50)
                elif val >= 50:
                    scores.append(80)
                else:
                    scores.append(100)
        
        elif component_type == "network":
            latency = metrics.get("latency", 0)
            packet_loss = metrics.get("packet_loss", 0)
            error_rate = metrics.get("error_rate", 0)
            
            if latency >= 100:
                scores.append(20)
            elif latency >= 50:
                scores.append(50)
            elif latency >= 25:
                scores.append(80)
            else:
                scores.append(100)
            
            if packet_loss >= 5:
                scores.append(20)
            elif packet_loss >= 2:
                scores.append(50)
            elif packet_loss >= 1:
                scores.append(80)
            else:
                scores.append(100)
            
            if error_rate >= 5:
                scores.append(20)
            elif error_rate >= 2:
                scores.append(50)
            elif error_rate >= 1:
                scores.append(80)
            else:
                scores.append(100)
        
        elif component_type == "application":
            response_time = metrics.get("response_time", 0)
            error_rate = metrics.get("error_rate", 0)
            
            if response_time >= 1000:
                scores.append(20)
            elif response_time >= 500:
                scores.append(50)
            elif response_time >= 200:
                scores.append(80)
            else:
                scores.append(100)
            
            if error_rate >= 5:
                scores.append(20)
            elif error_rate >= 2:
                scores.append(50)
            elif error_rate >= 1:
                scores.append(80)
            else:
                scores.append(100)
        
        elif component_type == "database":
            query_latency = metrics.get("query_latency", 0)
            pool_usage = metrics.get("connection_pool_usage", 0)
            
            if query_latency >= 500:
                scores.append(20)
            elif query_latency >= 200:
                scores.append(50)
            elif query_latency >= 100:
                scores.append(80)
            else:
                scores.append(100)
            
            if pool_usage >= 90:
                scores.append(20)
            elif pool_usage >= 75:
                scores.append(50)
            elif pool_usage >= 50:
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
    
    def get_component(self, component_id: str) -> Optional[Dict]:
        """Get a specific component by ID."""
        for comp in self._components:
            if comp["id"] == component_id:
                return comp
        return None
    
    def get_metrics(self, component_id: str, metric_names: List[str],
                    start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get time-series metrics for a component."""
        component = self.get_component(component_id)
        if not component:
            return []
        
        component_type = component["type"]
        metrics = []
        
        current = start_time
        while current <= end_time:
            for metric_name in metric_names:
                value = self._generate_metric_value(
                    metric_name, current, component_type, component_id
                )
                metrics.append({
                    "timestamp": current,
                    "metric_name": metric_name,
                    "value": value,
                })
            current += timedelta(minutes=1)
        
        return metrics
    
    def get_latest_metrics(self, component_id: str) -> Dict[str, float]:
        """Get the latest metric values for a component."""
        component = self.get_component(component_id)
        if not component:
            return {}
        
        metric_names = {
            "server": ["cpu_usage", "memory_usage", "disk_usage", "network_rx", "network_tx"],
            "network": ["bandwidth_utilization", "packet_loss", "latency", "error_rate"],
            "application": ["response_time", "request_rate", "error_rate", "active_connections"],
            "database": ["query_latency", "connection_pool_usage", "buffer_cache_hit_ratio", "disk_io"],
        }
        
        component_type = component["type"]
        names = metric_names.get(component_type, [])
        
        now = datetime.utcnow()
        latest = {}
        for name in names:
            latest[name] = self._generate_metric_value(name, now, component_type, component_id)
        
        return latest
    
    def is_available(self) -> bool:
        """Check if the data source is available."""
        return True


def get_data_source() -> DataSourceAdapter:
    """Factory function to get the data source adapter."""
    return MockSolarWindsAdapter()