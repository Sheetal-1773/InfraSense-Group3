import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from ...models.database import get_db, engine
from ...models.models import Component, ComponentMetric
from ...services.websocket_manager import manager
from ...services.data_source_manager import get_data_source_manager
from ...services.metric_normalizer import MetricNormalizer

logger = logging.getLogger(__name__)


class MetricCollector:
    """Collects metrics from the active data source and stores them in the database."""

    def __init__(self, interval_seconds: int = None):
        self.interval = interval_seconds or int(os.getenv("COLLECTOR_INTERVAL", "10"))
        self.data_source_manager = get_data_source_manager()
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._last_collection_time = None
        self._collection_errors = 0

    async def start(self):
        """Start the collector background task."""
        if self.running:
            logger.warning("Collector already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._collect_loop())
        logger.info(f"Metric collector started with {self.interval}s interval")

    async def stop(self):
        """Stop the collector."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Metric collector stopped")

    async def _collect_loop(self):
        """Main collection loop."""
        while self.running:
            try:
                await self._collect_metrics()
            except Exception as e:
                logger.error(f"Collection error: {e}")
                self._collection_errors += 1

            await asyncio.sleep(self.interval)

    async def _collect_metrics(self):
        """Collect and store metrics from the active data source."""
        if not self.data_source_manager.is_available():
            logger.warning("No data source available, skipping collection")
            return

        adapter = self.data_source_manager.get_primary_adapter()
        components = adapter.get_components()

        for component in components:
            component_id = component.get("id")
            if not component_id:
                continue

            metrics = adapter.get_latest_metrics(component_id)

            if metrics:
                await self._store_metrics(component_id, metrics, component)
                await self._broadcast_metrics(component_id, metrics, component)

        self._last_collection_time = datetime.utcnow()
        logger.debug(f"Collected metrics for {len(components)} components")

    def _store_metrics_sync(self, component_id: str, metrics: Dict[str, float], component_info: Dict = None):
        """Synchronous method to store metrics in database."""
        db = Session(bind=engine)
        try:
            component = db.query(Component).filter(Component.id == component_id).first()

            if not component:
                component = self._create_component_from_discovered(db, component_id, component_info)

            for metric_name, value in metrics.items():
                if value is None or (isinstance(value, float) and (value != value or abs(value) == float('inf'))):
                    continue

                metric = ComponentMetric(
                    component_id=component_id,
                    metric_type="system",
                    metric_name=metric_name,
                    value=float(value),
                    unit=self._get_unit_for_metric(metric_name),
                    timestamp=datetime.utcnow(),
                    source="simulated"
                )
                db.add(metric)

            if component:
                component.last_seen = datetime.utcnow()

            db.commit()
            logger.debug(f"Stored {len(metrics)} metrics for {component_id}")
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            db.rollback()
        finally:
            db.close()

    def _create_component_from_discovered(self, db: Session, component_id: str, component_info: Dict = None) -> Optional[Component]:
        """Create a component from discovered data."""
        from ...models.models import Category

        if not component_info:
            return None

        component_type = component_info.get("type", "server")
        category = db.query(Category).filter(Category.type == component_type).first()

        if not category:
            category = db.query(Category).filter(Category.type == "server").first()

        if not category:
            return None

        component = Component(
            id=component_id,
            name=component_info.get("name", component_id),
            hostname=component_info.get("hostname"),
            category_id=category.id,
            environment=component_info.get("environment", "production"),
            status="healthy",
            health_score=100,
            criticality="medium",
            description=f"Auto-discovered {component_type}",
            last_seen=datetime.utcnow()
        )

        db.add(component)
        db.commit()

        logger.info(f"Created component from discovery: {component_id}")
        return component

    async def _store_metrics(self, component_id: str, metrics: Dict[str, float], component_info: Dict = None):
        """Store metrics in database."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._store_metrics_sync, component_id, metrics, component_info)

    async def _broadcast_metrics(self, component_id: str, metrics: Dict[str, float], component_info: Dict = None):
        """Broadcast metrics via WebSocket."""
        message = {
            "type": "metrics_update",
            "data": {
                "component_id": component_id,
                "component_type": component_info.get("type", "server") if component_info else "server",
                "component_name": component_info.get("name", component_id) if component_info else component_id,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        await manager.broadcast(message, "health")

    def _get_unit_for_metric(self, metric_name: str) -> str:
        """Get unit for a metric name."""
        units = {
            "cpu_usage": "%",
            "memory_usage": "%",
            "disk_usage": "%",
            "network_receive": "bytes/s",
            "network_transmit": "bytes/s",
            "disk_read": "bytes/s",
            "disk_write": "bytes/s",
            "load_avg": "processes",
            "processes": "count",
            "request_count": "requests/s",
            "request_duration_p50": "ms",
            "request_duration_p95": "ms",
            "request_duration_p99": "ms",
            "error_rate": "%",
            "active_requests": "count",
            "db_connections": "count",
            "db_query_latency": "ms",
            "db_transactions": "txn/s",
            "db_cache_hit_ratio": "%",
            "lb_request_count": "requests/s",
            "lb_response_time": "ms",
            "lb_4xx_count": "count/s",
            "lb_5xx_count": "count/s",
        }
        return units.get(metric_name, "")

    async def collect_once(self):
        """Collect metrics once (for manual trigger)."""
        await self._collect_metrics()

    def get_status(self) -> Dict:
        """Get collector status."""
        return {
            "running": self.running,
            "interval_seconds": self.interval,
            "data_source_available": self.data_source_manager.is_available(),
            "last_collection_time": self._last_collection_time.isoformat() if self._last_collection_time else None,
            "collection_errors": self._collection_errors
        }


collector = MetricCollector()


async def start_collector():
    """Start the background collector."""
    await collector.start()


async def stop_collector():
    """Stop the background collector."""
    await collector.stop()


def get_collector_status() -> Dict:
    """Get collector status."""
    return collector.get_status()