from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricNormalizer:
    """Normalizes metrics from various sources into the InfraSense common format."""

    COMPONENT_TYPES = ["server", "database", "network", "application"]

    METRIC_MAPPINGS = {
        "server": {
            "cpu_usage": {"name": "cpu_usage", "unit": "percent", "type": "cpu"},
            "cpu_idle": {"name": "cpu_idle", "unit": "percent", "type": "cpu"},
            "memory_usage": {"name": "memory_usage", "unit": "percent", "type": "memory"},
            "memory_available": {"name": "memory_available", "unit": "bytes", "type": "memory"},
            "disk_usage": {"name": "disk_usage", "unit": "percent", "type": "disk"},
            "disk_free": {"name": "disk_free", "unit": "bytes", "type": "disk"},
            "disk_total": {"name": "disk_total", "unit": "bytes", "type": "disk"},
            "disk_read": {"name": "disk_read", "unit": "bytes/s", "type": "disk_io"},
            "disk_write": {"name": "disk_write", "unit": "bytes/s", "type": "disk_io"},
            "network_receive": {"name": "network_receive", "unit": "bytes/s", "type": "network"},
            "network_transmit": {"name": "network_transmit", "unit": "bytes/s", "type": "network"},
            "network_errors": {"name": "network_errors", "unit": "count/s", "type": "network"},
            "load_avg": {"name": "load_avg", "unit": "processes", "type": "load"},
            "processes": {"name": "processes", "unit": "count", "type": "process"},
            "uptime": {"name": "uptime", "unit": "seconds", "type": "system"},
        },
        "database": {
            "db_connections": {"name": "db_connections", "unit": "count", "type": "connections"},
            "db_max_connections": {"name": "db_max_connections", "unit": "count", "type": "connections"},
            "db_connection_usage": {"name": "db_connection_usage", "unit": "percent", "type": "connections"},
            "db_query_latency": {"name": "db_query_latency", "unit": "ms", "type": "performance"},
            "db_transactions": {"name": "db_transactions", "unit": "txn/s", "type": "transactions"},
            "db_transactions_commit": {"name": "db_transactions_commit", "unit": "txn/s", "type": "transactions"},
            "db_transactions_rollback": {"name": "db_transactions_rollback", "unit": "txn/s", "type": "transactions"},
            "db_cache_hit_ratio": {"name": "db_cache_hit_ratio", "unit": "percent", "type": "performance"},
            "db_rows_inserted": {"name": "db_rows_inserted", "unit": "rows/s", "type": "operations"},
            "db_rows_updated": {"name": "db_rows_updated", "unit": "rows/s", "type": "operations"},
            "db_rows_deleted": {"name": "db_rows_deleted", "unit": "rows/s", "type": "operations"},
            "db_storage_used": {"name": "db_storage_used", "unit": "bytes", "type": "storage"},
            "db_storage_free": {"name": "db_storage_free", "unit": "bytes", "type": "storage"},
            "db_storage_usage": {"name": "db_storage_usage", "unit": "percent", "type": "storage"},
            "db_lock_wait": {"name": "db_lock_wait", "unit": "count", "type": "locks"},
            "db_deadlocks": {"name": "db_deadlocks", "unit": "count", "type": "locks"},
        },
        "network": {
            "lb_request_count": {"name": "lb_request_count", "unit": "requests/s", "type": "traffic"},
            "lb_response_time": {"name": "lb_response_time", "unit": "ms", "type": "latency"},
            "lb_4xx_count": {"name": "lb_4xx_count", "unit": "count/s", "type": "errors"},
            "lb_5xx_count": {"name": "lb_5xx_count", "unit": "count/s", "type": "errors"},
            "lb_error_rate": {"name": "lb_error_rate", "unit": "percent", "type": "errors"},
            "lb_healthy_hosts": {"name": "lb_healthy_hosts", "unit": "count", "type": "health"},
            "lb_unhealthy_hosts": {"name": "lb_unhealthy_hosts", "unit": "count", "type": "health"},
            "network_throughput": {"name": "network_throughput", "unit": "Mbps", "type": "traffic"},
            "network_latency": {"name": "network_latency", "unit": "ms", "type": "latency"},
            "network_packet_loss": {"name": "network_packet_loss", "unit": "percent", "type": "quality"},
        },
        "application": {
            "request_count": {"name": "request_count", "unit": "requests/s", "type": "traffic"},
            "request_duration_p50": {"name": "request_duration_p50", "unit": "ms", "type": "latency"},
            "request_duration_p95": {"name": "request_duration_p95", "unit": "ms", "type": "latency"},
            "request_duration_p99": {"name": "request_duration_p99", "unit": "ms", "type": "latency"},
            "request_duration_avg": {"name": "request_duration_avg", "unit": "ms", "type": "latency"},
            "error_rate": {"name": "error_rate", "unit": "percent", "type": "errors"},
            "error_count": {"name": "error_count", "unit": "count/s", "type": "errors"},
            "active_requests": {"name": "active_requests", "unit": "count", "type": "traffic"},
            "throughput": {"name": "throughput", "unit": "requests/s", "type": "traffic"},
            "availability": {"name": "availability", "unit": "percent", "type": "health"},
        }
    }

    @classmethod
    def normalize_metric(cls, component_type: str, metric_name: str, value: Any,
                        labels: Optional[Dict] = None, source: str = "simulated") -> Optional[Dict]:
        """Normalize a single metric into InfraSense format."""
        if component_type not in cls.COMPONENT_TYPES:
            logger.warning(f"Unknown component type: {component_type}")
            return None

        mappings = cls.METRIC_MAPPINGS.get(component_type, {})

        if metric_name not in mappings:
            normalized_name = metric_name
            metric_unit = ""
            metric_type = "unknown"
        else:
            mapping = mappings[metric_name]
            normalized_name = mapping["name"]
            metric_unit = mapping["unit"]
            metric_type = mapping["type"]

        try:
            numeric_value = float(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid metric value: {value}")
            return None

        normalized = {
            "component_type": component_type,
            "metric_name": normalized_name,
            "value": numeric_value,
            "unit": metric_unit,
            "metric_type": metric_type,
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
        }

        if labels:
            normalized["labels"] = labels
            normalized["environment"] = labels.get("environment", "production")
            normalized["region"] = labels.get("region", "us-east-1")

        return normalized

    @classmethod
    def normalize_metrics(cls, component_type: str, metrics: Dict[str, Any],
                         labels: Optional[Dict] = None, source: str = "simulated") -> List[Dict]:
        """Normalize multiple metrics."""
        normalized = []

        for metric_name, value in metrics.items():
            result = cls.normalize_metric(component_type, metric_name, value, labels, source)
            if result:
                normalized.append(result)

        return normalized

    @classmethod
    def get_metric_schema(cls) -> Dict[str, List[Dict]]:
        """Get the complete metric schema."""
        schema = {}

        for component_type, mappings in cls.METRIC_MAPPINGS.items():
            schema[component_type] = []
            for metric_name, config in mappings.items():
                schema[component_type].append({
                    "name": config["name"],
                    "unit": config["unit"],
                    "type": config["type"]
                })

        return schema

    @classmethod
    def get_default_thresholds(cls) -> Dict[str, Dict[str, float]]:
        """Get default thresholds for metrics."""
        return {
            "server": {
                "cpu_usage": {"warning": 70, "critical": 85},
                "memory_usage": {"warning": 75, "critical": 90},
                "disk_usage": {"warning": 80, "critical": 95},
                "network_errors": {"warning": 10, "critical": 50},
                "load_avg": {"warning": 4, "critical": 8},
            },
            "database": {
                "db_connection_usage": {"warning": 80, "critical": 95},
                "db_query_latency": {"warning": 200, "critical": 500},
                "db_storage_usage": {"warning": 80, "critical": 95},
                "db_lock_wait": {"warning": 5, "critical": 20},
                "db_deadlocks": {"warning": 1, "critical": 5},
            },
            "network": {
                "lb_error_rate": {"warning": 2, "critical": 5},
                "lb_response_time": {"warning": 500, "critical": 1000},
                "network_latency": {"warning": 100, "critical": 200},
                "network_packet_loss": {"warning": 1, "critical": 5},
            },
            "application": {
                "error_rate": {"warning": 2, "critical": 5},
                "request_duration_p95": {"warning": 500, "critical": 1000},
                "request_duration_p99": {"warning": 1000, "critical": 2000},
                "availability": {"warning": 99, "critical": 95},
            }
        }

    @classmethod
    def infer_component_type(cls, labels: Dict) -> str:
        """Infer component type from metric labels."""
        job = labels.get("job", "").lower()
        component_type = labels.get("component_type", "").lower()

        if component_type:
            return component_type

        if "node" in job or "system" in job:
            return "server"
        elif "postgres" in job or "mysql" in job or "database" in job or "rds" in job:
            return "database"
        elif "alb" in job or "nlb" in job or "network" in job:
            return "network"
        elif "api" in job or "app" in job or "service" in job:
            return "application"
        else:
            return "server"

    @classmethod
    def extract_component_id(cls, labels: Dict) -> str:
        """Extract component ID from metric labels."""
        for key in ["component_id", "application_id", "database_id", "hostname", "instance", "job"]:
            if key in labels and labels[key]:
                value = labels[key]
                if isinstance(value, str):
                    return value.split(":")[0]
                return str(value)

        return labels.get("instance", "unknown")