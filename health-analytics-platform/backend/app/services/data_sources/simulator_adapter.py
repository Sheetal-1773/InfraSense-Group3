import logging
import random
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .base import DataSourceAdapter

logger = logging.getLogger(__name__)


class Scenario:
    NORMAL = "normal"
    CPU_SPIKE = "cpu_spike"
    MEMORY_LEAK = "memory_leak"
    DISK_PRESSURE = "disk_pressure"
    NETWORK_CONGESTION = "network_congestion"
    DATABASE_SLOWDOWN = "database_slowdown"
    DATABASE_CONNECTION_EXHAUSTION = "database_connection_exhaustion"
    API_LATENCY = "api_latency"
    API_ERROR_SPIKE = "api_error_spike"
    SERVICE_DEGRADATION = "service_degradation"
    CASCADING_FAILURE = "cascading_failure"


class InfrastructureSimulatorAdapter(DataSourceAdapter):
    """Adapter for simulating realistic infrastructure components and metrics."""
    
    def __init__(self, interval: int = 3):
        self.interval = interval
        self.current_scenario = Scenario.NORMAL
        self._components = self._create_components()
        self._metrics_history = []
        self._max_history = 200
        self._start_time = datetime.utcnow()
        self._scenario_start_time = datetime.utcnow()
        
    @property
    def cloud_provider(self) -> str:
        return "simulator"
    
    def _create_components(self) -> List[Dict]:
        """Create simulated infrastructure components."""
        components = []
        
        # Servers (4)
        servers = [
            {"id": "sim-web-srv-01", "name": "Web Server 01", "hostname": "web-srv-01.infrasense.local"},
            {"id": "sim-app-srv-01", "name": "Application Server 01", "hostname": "app-srv-01.infrasense.local"},
            {"id": "sim-compute-srv-01", "name": "Compute Server 01", "hostname": "compute-srv-01.infrasense.local"},
            {"id": "sim-backup-srv-01", "name": "Backup Server 01", "hostname": "backup-srv-01.infrasense.local"},
        ]
        for srv in servers:
            components.append({
                **srv,
                "category": "server",
                "type": "server",
                "environment": "production",
                "status": "healthy",
                "provider": "simulator",
                "source": "simulator",
                "criticality": "high",
                "owner": "Infrastructure Team",
                "description": f"{srv['name']} in production environment"
            })
        
        # Databases (4)
        databases = [
            {"id": "sim-postgres-primary", "name": "PostgreSQL Primary", "hostname": "postgres-primary.infrasense.local"},
            {"id": "sim-postgres-replica", "name": "PostgreSQL Replica", "hostname": "postgres-replica.infrasense.local"},
            {"id": "sim-mysql-db", "name": "MySQL Database", "hostname": "mysql-db.infrasense.local"},
            {"id": "sim-redis-cache", "name": "Redis Cache", "hostname": "redis-cache.infrasense.local"},
        ]
        for db in databases:
            components.append({
                **db,
                "category": "database",
                "type": "database",
                "environment": "production",
                "status": "healthy",
                "provider": "simulator",
                "source": "simulator",
                "criticality": "critical",
                "owner": "DBA Team",
                "description": f"{db['name']} in production environment"
            })
        
        # Applications (4)
        apps = [
            {"id": "sim-customer-api", "name": "Customer API", "hostname": "customer-api.infrasense.local"},
            {"id": "sim-payment-api", "name": "Payment API", "hostname": "payment-api.infrasense.local"},
            {"id": "sim-auth-api", "name": "Authentication API", "hostname": "auth-api.infrasense.local"},
            {"id": "sim-order-api", "name": "Order API", "hostname": "order-api.infrasense.local"},
        ]
        for app in apps:
            components.append({
                **app,
                "category": "application",
                "type": "application",
                "environment": "production",
                "status": "healthy",
                "provider": "simulator",
                "source": "simulator",
                "criticality": "critical",
                "owner": "API Team",
                "description": f"{app['name']} in production environment"
            })
        
        # Network (4)
        networks = [
            {"id": "sim-api-gateway", "name": "API Gateway", "hostname": "api-gateway.infrasense.local"},
            {"id": "sim-load-balancer", "name": "Load Balancer", "hostname": "lb-01.infrasense.local"},
            {"id": "sim-core-router", "name": "Core Router", "hostname": "core-router-01.infrasense.local"},
            {"id": "sim-network-switch", "name": "Network Switch", "hostname": "switch-01.infrasense.local"},
        ]
        for net in networks:
            components.append({
                **net,
                "category": "network",
                "type": "network",
                "environment": "production",
                "status": "healthy",
                "provider": "simulator",
                "source": "simulator",
                "criticality": "critical",
                "owner": "Network Team",
                "description": f"{net['name']} in production environment"
            })
        
        return components
    
    def set_scenario(self, scenario: str):
        """Set the current scenario."""
        old_scenario = self.current_scenario
        self.current_scenario = scenario
        self._scenario_start_time = datetime.utcnow()
        logger.info(f"[SIMULATOR] Scenario changed: {old_scenario} -> {scenario}")
    
    def get_scenario(self) -> str:
        """Get current scenario."""
        return self.current_scenario
    
    def _get_base_metrics(self, component: Dict) -> Dict:
        """Get base metrics for a component."""
        return {
            "cpu_usage": random.uniform(20, 40),
            "memory_usage": random.uniform(30, 50),
            "disk_usage": random.uniform(40, 60),
            "network_in": random.uniform(1000, 5000),
            "network_out": random.uniform(500, 3000),
        }
    
    def _apply_scenario_modifiers(self, metrics: Dict, component: Dict) -> Dict:
        """Apply scenario-specific modifications to metrics."""
        comp_id = component["id"]
        comp_type = component.get("type", "")
        
        if self.current_scenario == Scenario.CPU_SPIKE:
            if comp_type in ["server", "application"]:
                metrics["cpu_usage"] = min(95, metrics["cpu_usage"] + 40)
            if "database" in comp_type:
                metrics["cpu_usage"] = min(85, metrics["cpu_usage"] + 25)
                
        elif self.current_scenario == Scenario.MEMORY_LEAK:
            if comp_type in ["server", "application"]:
                metrics["memory_usage"] = min(95, metrics["memory_usage"] + 35)
            if "database" in comp_type:
                metrics["memory_usage"] = min(90, metrics["memory_usage"] + 30)
                
        elif self.current_scenario == Scenario.DISK_PRESSURE:
            metrics["disk_usage"] = min(95, metrics["disk_usage"] + 30)
            
        elif self.current_scenario == Scenario.NETWORK_CONGESTION:
            metrics["network_in"] = metrics["network_in"] * 3
            metrics["network_out"] = metrics["network_out"] * 0.3
            metrics["network_latency"] = random.uniform(50, 150)
            
        elif self.current_scenario == Scenario.DATABASE_SLOWDOWN:
            if "postgres" in comp_id or "mysql" in comp_id:
                metrics["cpu_usage"] = min(90, metrics["cpu_usage"] + 30)
                metrics["db_query_latency"] = random.uniform(500, 2000)
                metrics["db_connections"] = random.uniform(80, 100)
                metrics["db_cache_hit_ratio"] = random.uniform(0.6, 0.8)
            if "payment" in comp_id or "order" in comp_id:
                metrics["api_latency"] = random.uniform(500, 1500)
                metrics["error_rate"] = random.uniform(5, 15)
                
        elif self.current_scenario == Scenario.DATABASE_CONNECTION_EXHAUSTION:
            if "postgres" in comp_id or "mysql" in comp_id:
                metrics["db_connections"] = random.uniform(95, 100)
                metrics["db_connection_errors"] = random.uniform(10, 50)
                
        elif self.current_scenario == Scenario.API_LATENCY:
            if comp_type == "application":
                metrics["api_latency"] = random.uniform(500, 2000)
                metrics["request_queue_depth"] = random.uniform(50, 200)
                
        elif self.current_scenario == Scenario.API_ERROR_SPIKE:
            if comp_type == "application":
                metrics["error_rate"] = random.uniform(10, 25)
                metrics["http_5xx_rate"] = random.uniform(5, 15)
                metrics["http_4xx_rate"] = random.uniform(10, 20)
                
        elif self.current_scenario == Scenario.SERVICE_DEGRADATION:
            if comp_type in ["application", "server"]:
                metrics["cpu_usage"] = min(85, metrics["cpu_usage"] + 20)
                metrics["memory_usage"] = min(80, metrics["memory_usage"] + 20)
                metrics["api_latency"] = random.uniform(200, 800)
                metrics["error_rate"] = random.uniform(3, 10)
                
        elif self.current_scenario == Scenario.CASCADING_FAILURE:
            # Database affects applications
            if "postgres" in comp_id or "mysql" in comp_id:
                metrics["cpu_usage"] = min(95, metrics["cpu_usage"] + 40)
                metrics["db_query_latency"] = random.uniform(1000, 3000)
            if "payment" in comp_id or "order" in comp_id or "customer" in comp_id:
                metrics["api_latency"] = random.uniform(1000, 3000)
                metrics["error_rate"] = random.uniform(15, 30)
                metrics["availability"] = random.uniform(0.7, 0.9)
        
        # Add some random variation
        metrics["cpu_usage"] += random.uniform(-3, 3)
        metrics["memory_usage"] += random.uniform(-2, 2)
        
        return metrics
    
    def _calculate_health_score(self, metrics: Dict) -> tuple:
        """Calculate health score and status from metrics."""
        scores = []
        
        cpu = metrics.get("cpu_usage", 0)
        memory = metrics.get("memory_usage", 0)
        disk = metrics.get("disk_usage", 0)
        
        # CPU score
        if cpu >= 90:
            scores.append(10)
        elif cpu >= 75:
            scores.append(40)
        elif cpu >= 50:
            scores.append(70)
        else:
            scores.append(100)
        
        # Memory score
        if memory >= 90:
            scores.append(10)
        elif memory >= 75:
            scores.append(40)
        elif memory >= 50:
            scores.append(70)
        else:
            scores.append(100)
        
        # Disk score
        if disk >= 95:
            scores.append(10)
        elif disk >= 85:
            scores.append(40)
        elif disk >= 70:
            scores.append(70)
        else:
            scores.append(100)
        
        # Error rate penalty
        error_rate = metrics.get("error_rate", 0)
        if error_rate >= 20:
            scores.append(0)
        elif error_rate >= 10:
            scores.append(30)
        elif error_rate >= 5:
            scores.append(60)
        
        # Latency penalty
        latency = metrics.get("api_latency", 0) or metrics.get("db_query_latency", 0)
        if latency >= 2000:
            scores.append(10)
        elif latency >= 1000:
            scores.append(40)
        elif latency >= 500:
            scores.append(70)
        
        health_score = sum(scores) / len(scores) if scores else 100
        
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 50:
            status = "degraded"
        else:
            status = "critical"
        
        return health_score, status
    
    def get_components(self) -> List[Dict]:
        """Get all simulated components with current metrics."""
        timestamp = datetime.utcnow()
        
        result = []
        for comp in self._components:
            base_metrics = self._get_base_metrics(comp)
            metrics = self._apply_scenario_modifiers(base_metrics, comp)
            health_score, status = self._calculate_health_score(metrics)
            
            comp_copy = comp.copy()
            comp_copy["status"] = status
            comp_copy["health_score"] = round(health_score, 1)
            comp_copy["last_seen"] = timestamp.isoformat()
            comp_copy["metrics"] = metrics
            result.append(comp_copy)
        
        # Store in history
        self._metrics_history.append({
            "timestamp": timestamp,
            "scenario": self.current_scenario,
            "components": result.copy()
        })
        
        if len(self._metrics_history) > self._max_history:
            self._metrics_history.pop(0)
        
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
                for comp in entry["components"]:
                    if comp["id"] == component_id:
                        for metric_name in metric_names:
                            if metric_name in comp.get("metrics", {}):
                                metrics.append({
                                    "timestamp": entry["timestamp"],
                                    "metric_name": metric_name,
                                    "value": comp["metrics"][metric_name]
                                })
        
        return metrics
    
    def get_latest_metrics(self, component_id: str) -> Dict[str, float]:
        """Get latest metrics for a component."""
        if self._metrics_history:
            latest = self._metrics_history[-1]
            for comp in latest["components"]:
                if comp["id"] == component_id:
                    return comp.get("metrics", {})
        
        for comp in self._components:
            if comp["id"] == component_id:
                return self._get_base_metrics(comp)
        
        return {}
    
    def is_available(self) -> bool:
        """Check if simulator is available."""
        return True
    
    def get_scenario_info(self) -> Dict:
        """Get current scenario information."""
        duration = (datetime.utcnow() - self._scenario_start_time).total_seconds()
        return {
            "current_scenario": self.current_scenario,
            "scenario_duration_seconds": duration,
            "component_count": len(self._components),
            "history_points": len(self._metrics_history)
        }


def get_simulator_adapter(interval: int = 3) -> InfrastructureSimulatorAdapter:
    """Factory function to get the simulator adapter."""
    return InfrastructureSimulatorAdapter(interval=interval)