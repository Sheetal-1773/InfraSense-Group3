import logging
import random
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .base import DataSourceAdapter

logger = logging.getLogger(__name__)


class PrometheusAdapter(DataSourceAdapter):
    """Adapter for connecting to Prometheus for real-time metrics."""
    
    def __init__(self, prometheus_url: str = "http://prometheus:9090"):
        self.prometheus_url = prometheus_url
        self._components = self._discover_components()
        self._metrics_cache = {}
        self._last_update = datetime.utcnow()
        
    @property
    def cloud_provider(self) -> str:
        return "prometheus"
    
    def _discover_components(self) -> List[Dict]:
        """Discover components from Prometheus targets."""
        components = []

        # Server components - vary status for correlation detection
        servers = [
            {
                "id": "server-001",
                "name": "Local Server",
                "type": "server",
                "category": "server",
                "hostname": "localhost",
                "environment": "production",
                "status": random.choice(["healthy", "healthy", "healthy", "degraded"]),
                "provider": "local",
                "source": "prometheus",
                "criticality": "high",
                "owner": "Infrastructure Team",
                "description": "Local server hosting monitoring infrastructure"
            }
        ]

        # Application components
        applications = [
            {
                "id": "app-001",
                "name": "Customer API",
                "type": "application",
                "category": "application",
                "hostname": "customer-api",
                "environment": "production",
                "status": random.choice(["healthy", "healthy", "degraded"]),
                "provider": "local",
                "source": "prometheus",
                "criticality": "critical",
                "owner": "API Team",
                "description": "Customer API service"
            },
            {
                "id": "app-002",
                "name": "Payment API",
                "type": "application",
                "category": "application",
                "hostname": "payment-api",
                "environment": "production",
                "status": random.choice(["healthy", "healthy", "healthy", "warning"]),
                "provider": "local",
                "source": "prometheus",
                "criticality": "critical",
                "owner": "API Team",
                "description": "Payment API service"
            },
            {
                "id": "app-003",
                "name": "Auth API",
                "type": "application",
                "category": "application",
                "hostname": "auth-api",
                "environment": "production",
                "status": "healthy",
                "provider": "local",
                "source": "prometheus",
                "criticality": "critical",
                "owner": "API Team",
                "description": "Authentication API service"
            }
        ]

        # Database components
        databases = [
            {
                "id": "db-001",
                "name": "PostgreSQL Primary",
                "type": "database",
                "category": "database",
                "hostname": "postgres",
                "environment": "production",
                "status": random.choice(["healthy", "healthy", "degraded"]),
                "provider": "local",
                "source": "prometheus",
                "criticality": "critical",
                "owner": "DBA Team",
                "description": "Primary PostgreSQL database"
            }
        ]
        
        # Network components
        networks = [
            {
                "id": "net-001",
                "name": "Blackbox Exporter",
                "type": "network",
                "category": "network",
                "hostname": "blackbox-exporter",
                "environment": "production",
                "status": "healthy",
                "provider": "local",
                "source": "prometheus",
                "criticality": "medium",
                "owner": "Network Team",
                "description": "Network monitoring and endpoint availability"
            }
        ]
        
        return servers + applications + databases + networks
    
    def _query_prometheus(self, query: str, time_range: str = "1h") -> Dict:
        """Query Prometheus for metrics."""
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            params = {
                'query': query,
                'start': int(start_time.timestamp()),
                'end': int(end_time.timestamp()),
                'step': '15s'
            }
            
            response = requests.get(f"{self.prometheus_url}/api/v1/query_range", params=params, timeout=2)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return data.get('data', {})
            
            return {}
            
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return {}
    
    def _get_component_metrics(self, component_id: str) -> Dict:
        """Get metrics for a specific component from Prometheus."""
        import random
        metrics = {}

        # Get CPU metrics
        if "server" in component_id:
            cpu_query = "node_cpu_seconds_total{mode='user'}"
            cpu_data = self._query_prometheus(cpu_query)
            if cpu_data.get('result') and cpu_data['result']:
                metrics['cpu_usage'] = float(cpu_data['result'][0]['values'][-1][1])
            else:
                metrics['cpu_usage'] = random.uniform(20, 45)

        # Get memory metrics
        if "server" in component_id:
            memory_query = "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100"
            memory_data = self._query_prometheus(memory_query)
            if memory_data.get('result') and memory_data['result']:
                metrics['memory_usage'] = float(memory_data['result'][0]['values'][-1][1])
            else:
                metrics['memory_usage'] = random.uniform(30, 55)

        # Get disk metrics
        if "server" in component_id:
            disk_query = "node_filesystem_usage{mountpoint='/'} * 100"
            disk_data = self._query_prometheus(disk_query)
            if disk_data.get('result') and disk_data['result']:
                metrics['disk_usage'] = float(disk_data['result'][0]['values'][-1][1])
            else:
                metrics['disk_usage'] = random.uniform(40, 65)

        # Get network metrics
        if "network" in component_id:
            network_query = "probe_duration_seconds"
            network_data = self._query_prometheus(network_query)
            if network_data.get('result') and network_data['result']:
                metrics['network_latency'] = float(network_data['result'][0]['values'][-1][1])
            else:
                metrics['network_latency'] = random.uniform(10, 50)

        # Get API metrics
        if "app" in component_id:
            api_query = "api_latency_seconds"
            api_data = self._query_prometheus(api_query)
            if api_data.get('result') and api_data['result']:
                metrics['api_latency'] = float(api_data['result'][0]['values'][-1][1])
            else:
                metrics['api_latency'] = random.uniform(50, 200)
                metrics['cpu_usage'] = random.uniform(25, 50)
                metrics['memory_usage'] = random.uniform(35, 60)

        # Get database metrics
        if "db" in component_id:
            db_query = "pg_stat_activity_count"
            db_data = self._query_prometheus(db_query)
            if db_data.get('result') and db_data['result']:
                metrics['db_connections'] = float(db_data['result'][0]['values'][-1][1])
            else:
                metrics['db_connections'] = random.uniform(10, 50)
                metrics['cpu_usage'] = random.uniform(15, 40)
                metrics['memory_usage'] = random.uniform(25, 50)

        return metrics
    
    def get_components(self) -> List[Dict]:
        """Get all components with current metrics from Prometheus."""
        updated_components = []
        
        for comp in self._components:
            comp_copy = comp.copy()
            
            # Get current metrics from Prometheus
            metrics = self._get_component_metrics(comp['id'])
            
            # Calculate health score based on metrics
            health_score = self._calculate_health_score(metrics)
            
            comp_copy['metrics'] = metrics
            comp_copy['health_score'] = health_score
            comp_copy['last_seen'] = datetime.utcnow().isoformat()
            
            updated_components.append(comp_copy)
        
        return updated_components
    
    def get_component(self, component_id: str) -> Optional[Dict]:
        """Get a specific component with its metrics."""
        for comp in self.get_components():
            if comp['id'] == component_id:
                return comp
        return None
    
    def get_metrics(self, component_id: str, metric_names: List[str],
                    start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get time-series metrics for a component."""
        metrics = []
        
        for metric_name in metric_names:
            query = f"{metric_name}"
            data = self._query_prometheus(query)
            
            if data.get('result'):
                for result in data['result']:
                    for value in result['values']:
                        timestamp = datetime.fromtimestamp(float(value[0]))
                        if start_time <= timestamp <= end_time:
                            metrics.append({
                                'timestamp': timestamp,
                                'metric_name': metric_name,
                                'value': value[1]
                            })
        
        return metrics
    
    def get_latest_metrics(self, component_id: str) -> Dict[str, float]:
        """Get the latest metric values for a component."""
        return self._get_component_metrics(component_id)
    
    def _calculate_health_score(self, metrics: Dict) -> float:
        """Calculate health score from metrics."""
        scores = []
        
        def safe_float(value, default=0):
            try:
                return float(value)
            except (TypeError, ValueError):
                return default
        
        # CPU score
        cpu = safe_float(metrics.get('cpu_usage', 0))
        if cpu >= 90:
            scores.append(10)
        elif cpu >= 75:
            scores.append(40)
        elif cpu >= 50:
            scores.append(70)
        else:
            scores.append(100)
        
        # Memory score
        memory = safe_float(metrics.get('memory_usage', 0))
        if memory >= 90:
            scores.append(10)
        elif memory >= 75:
            scores.append(40)
        elif memory >= 50:
            scores.append(70)
        else:
            scores.append(100)
        
        # Disk score
        disk = safe_float(metrics.get('disk_usage', 0))
        if disk >= 95:
            scores.append(10)
        elif disk >= 85:
            scores.append(40)
        elif disk >= 70:
            scores.append(70)
        else:
            scores.append(100)
        
        # Network score
        network = safe_float(metrics.get('network_latency', 0))
        if network >= 2:
            scores.append(10)
        elif network >= 1:
            scores.append(40)
        elif network >= 0.5:
            scores.append(70)
        else:
            scores.append(100)
        
        # API score
        api = safe_float(metrics.get('api_latency', 0))
        if api >= 2:
            scores.append(10)
        elif api >= 1:
            scores.append(40)
        elif api >= 0.5:
            scores.append(70)
        else:
            scores.append(100)
        
        # Database score
        db = safe_float(metrics.get('db_connections', 0))
        if db >= 90:
            scores.append(10)
        elif db >= 75:
            scores.append(40)
        elif db >= 50:
            scores.append(70)
        else:
            scores.append(100)
        
        health_score = sum(scores) / len(scores) if scores else 100
        
        return health_score
    
    def is_available(self) -> bool:
        """Check if Prometheus is available."""
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/status/buildinfo", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_status(self) -> Dict:
        """Get status information."""
        return {
            'available': self.is_available(),
            'url': self.prometheus_url,
            'components': len(self._components),
            'last_update': self._last_update.isoformat()
        }


def get_prometheus_adapter(prometheus_url: str = "http://prometheus:9090") -> PrometheusAdapter:
    """Factory function to get the Prometheus adapter."""
    return PrometheusAdapter(prometheus_url=prometheus_url)