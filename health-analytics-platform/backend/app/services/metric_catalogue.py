from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

METRIC_CATALOGUE: Dict[str, List[Dict]] = {
    "server": [
        {
            "name": "cpu_usage",
            "display_name": "CPU Usage",
            "unit": "percent",
            "type": "gauge",
            "description": "Percentage of CPU utilization",
            "min_value": 0,
            "max_value": 100,
        },
        {
            "name": "memory_usage",
            "display_name": "Memory Usage",
            "unit": "percent",
            "type": "gauge",
            "description": "Percentage of memory utilization",
            "min_value": 0,
            "max_value": 100,
        },
        {
            "name": "disk_usage",
            "display_name": "Disk Usage",
            "unit": "percent",
            "type": "gauge",
            "description": "Percentage of disk space used",
            "min_value": 0,
            "max_value": 100,
        },
        {
            "name": "disk_io_read",
            "display_name": "Disk I/O Read",
            "unit": "bytes_per_second",
            "type": "counter",
            "description": "Disk read operations per second",
            "min_value": 0,
            "max_value": None,
        },
        {
            "name": "disk_io_write",
            "display_name": "Disk I/O Write",
            "unit": "bytes_per_second",
            "type": "counter",
            "description": "Disk write operations per second",
            "min_value": 0,
            "max_value": None,
        },
        {
            "name": "network_rx",
            "display_name": "Network Received",
            "unit": "bytes_per_second",
            "type": "counter",
            "description": "Network bytes received per second",
            "min_value": 0,
            "max_value": None,
        },
        {
            "name": "network_tx",
            "display_name": "Network Transmitted",
            "unit": "bytes_per_second",
            "type": "counter",
            "description": "Network bytes transmitted per second",
            "min_value": 0,
            "max_value": None,
        },
    ],
    "network": [
        {
            "name": "bandwidth_utilization",
            "display_name": "Bandwidth Utilization",
            "unit": "percent",
            "type": "gauge",
            "description": "Percentage of bandwidth used",
            "min_value": 0,
            "max_value": 100,
        },
        {
            "name": "packet_loss",
            "display_name": "Packet Loss",
            "unit": "percent",
            "type": "gauge",
            "description": "Percentage of packets lost",
            "min_value": 0,
            "max_value": 100,
        },
        {
            "name": "latency",
            "display_name": "Latency",
            "unit": "milliseconds",
            "type": "gauge",
            "description": "Network latency in milliseconds",
            "min_value": 0,
            "max_value": None,
        },
        {
            "name": "error_rate",
            "display_name": "Error Rate",
            "unit": "percent",
            "type": "gauge",
            "description": "Percentage of errors",
            "min_value": 0,
            "max_value": 100,
        },
    ],
    "application": [
        {
            "name": "response_time",
            "display_name": "Response Time",
            "unit": "milliseconds",
            "type": "gauge",
            "description": "Average response time",
            "min_value": 0,
            "max_value": None,
        },
        {
            "name": "request_rate",
            "display_name": "Request Rate",
            "unit": "requests_per_second",
            "type": "gauge",
            "description": "Requests per second",
            "min_value": 0,
            "max_value": None,
        },
        {
            "name": "error_rate",
            "display_name": "Error Rate",
            "unit": "percent",
            "type": "gauge",
            "description": "Percentage of failed requests",
            "min_value": 0,
            "max_value": 100,
        },
        {
            "name": "active_connections",
            "display_name": "Active Connections",
            "unit": "count",
            "type": "gauge",
            "description": "Number of active connections",
            "min_value": 0,
            "max_value": None,
        },
    ],
    "database": [
        {
            "name": "query_latency",
            "display_name": "Query Latency",
            "unit": "milliseconds",
            "type": "gauge",
            "description": "Average query execution time",
            "min_value": 0,
            "max_value": None,
        },
        {
            "name": "connection_pool_usage",
            "display_name": "Connection Pool Usage",
            "unit": "percent",
            "type": "gauge",
            "description": "Percentage of connection pool used",
            "min_value": 0,
            "max_value": 100,
        },
        {
            "name": "buffer_cache_hit_ratio",
            "display_name": "Buffer Cache Hit Ratio",
            "unit": "percent",
            "type": "gauge",
            "description": "Cache hit ratio percentage",
            "min_value": 0,
            "max_value": 100,
        },
        {
            "name": "disk_io",
            "display_name": "Disk I/O",
            "unit": "bytes_per_second",
            "type": "counter",
            "description": "Database disk I/O operations",
            "min_value": 0,
            "max_value": None,
        },
    ],
}


def get_metric_catalogue() -> Dict[str, List[Dict]]:
    """Get the complete metric catalogue."""
    return METRIC_CATALOGUE


def get_metrics_for_type(component_type: str) -> List[Dict]:
    """Get metrics for a specific component type."""
    return METRIC_CATALOGUE.get(component_type.lower(), [])


def validate_metric(metric_name: str, component_type: str, value: float) -> tuple[bool, Optional[str]]:
    """
    Validate a metric against the catalogue.
    Returns (is_valid, error_message).
    """
    metrics = get_metrics_for_type(component_type)
    
    metric_def = None
    for m in metrics:
        if m["name"] == metric_name:
            metric_def = m
            break
    
    if not metric_def:
        logger.warning(f"Unknown metric '{metric_name}' for component type '{component_type}'")
        return False, f"Unknown metric: {metric_name}"
    
    min_val = metric_def.get("min_value")
    max_val = metric_def.get("max_value")
    
    if min_val is not None and value < min_val:
        return False, f"Value {value} below minimum {min_val} for {metric_name}"
    
    if max_val is not None and value > max_val:
        return False, f"Value {value} above maximum {max_val} for {metric_name}"
    
    return True, None


def get_metric_definition(metric_name: str, component_type: str) -> Optional[Dict]:
    """Get a specific metric definition."""
    metrics = get_metrics_for_type(component_type)
    for m in metrics:
        if m["name"] == metric_name:
            return m
    return None