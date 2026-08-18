import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

from .data_sources.solarwinds_mock import MockSolarWindsAdapter
from .data_sources.local_adapter import LocalInfrastructureAdapter
from .data_sources.simulator_adapter import InfrastructureSimulatorAdapter, Scenario
from .data_sources.prometheus_adapter import PrometheusAdapter

logger = logging.getLogger(__name__)


class DataSourceManager:
    """Manages multiple data sources and provides unified access to metrics."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.data_mode = os.getenv("DATA_MODE", "real").lower()
        self.cloud_provider = os.getenv("CLOUD_PROVIDER", "local")
        self.prometheus_url = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")

        self.mock_adapter = None
        self.local_adapter = None
        self.simulator_adapter = None
        self.prometheus_adapter = None
        self.simulator_enabled = os.getenv("SIMULATOR_ENABLED", "true").lower() == "true"

        self._initialize_adapters()
        self._initialized = True

    def _initialize_adapters(self):
        """Initialize data source adapters based on configuration."""
        try:
            self.local_adapter = LocalInfrastructureAdapter()
            logger.info("Local infrastructure adapter initialized")
        except Exception as e:
            logger.error(f"Failed to initialize local adapter: {e}")

        # Initialize simulator adapter
        if self.simulator_enabled:
            try:
                self.simulator_adapter = InfrastructureSimulatorAdapter()
                logger.info("Simulator adapter initialized")
            except Exception as e:
                logger.error(f"Failed to initialize simulator adapter: {e}")

        # Initialize Prometheus adapter for real metrics
        if self.data_mode in ("prometheus", "docker", "real"):
            try:
                self.prometheus_adapter = PrometheusAdapter(prometheus_url=self.prometheus_url)
                logger.info(f"Prometheus adapter initialized: {self.prometheus_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Prometheus adapter: {e}")

        try:
            self.mock_adapter = MockSolarWindsAdapter()
            logger.info("Mock adapter initialized")
        except Exception as e:
            logger.error(f"Failed to initialize mock adapter: {e}")

    def get_primary_adapter(self):
        """Get the primary data source adapter based on DATA_MODE."""
        if self.data_mode == "mock":
            return self._get_mock_adapter()
        elif self.data_mode in ("prometheus", "docker"):
            if self.prometheus_adapter and self.prometheus_adapter.is_available():
                return self.prometheus_adapter
            logger.warning("Prometheus not available, falling back to local adapter")
            return self._get_local_adapter()
        elif self.data_mode == "simulated":
            return self._get_simulator_adapter()
        elif self.data_mode == "local":
            return self._get_local_adapter()
        else:
            # Default: try Prometheus first, then local
            if self.prometheus_adapter and self.prometheus_adapter.is_available():
                return self.prometheus_adapter
            return self._get_local_adapter()

    def _get_mock_adapter(self):
        """Get or create mock adapter."""
        if not self.mock_adapter:
            self.mock_adapter = MockSolarWindsAdapter()
        return self.mock_adapter

    def _get_local_adapter(self):
        """Get or create local adapter."""
        if not self.local_adapter:
            self.local_adapter = LocalInfrastructureAdapter()
        return self.local_adapter

    def _get_simulator_adapter(self):
        """Get or create simulator adapter."""
        if not self.simulator_adapter:
            self.simulator_adapter = InfrastructureSimulatorAdapter()
        return self.simulator_adapter

    def discover_components(self) -> List[Dict]:
        """Discover components from all available data sources."""
        components = []

        # Always include local adapter (local PC metrics)
        if self.local_adapter and self.local_adapter.is_available():
            try:
                local_components = self.local_adapter.get_components()
                for comp in local_components:
                    comp["provider"] = "local"
                    comp["source"] = "local"
                    if not any(c.get("id") == comp.get("id") for c in components):
                        components.append(comp)
                logger.info(f"Discovered {len(local_components)} components from local")
            except Exception as e:
                logger.error(f"Error discovering from local: {e}")

        # Include simulator adapter
        if self.simulator_enabled and self.simulator_adapter and self.simulator_adapter.is_available():
            try:
                sim_components = self.simulator_adapter.get_components()
                for comp in sim_components:
                    comp["provider"] = "simulated"
                    comp["source"] = "simulated"
                    if not any(c.get("id") == comp.get("id") for c in components):
                        components.append(comp)
                logger.info(f"Discovered {len(sim_components)} components from simulator")
            except Exception as e:
                logger.error(f"Error discovering from simulator: {e}")

        # Include mock/simulated data
        try:
            mock_components = self._get_mock_adapter().get_components()
            for comp in mock_components:
                comp["provider"] = "simulated"
                comp["source"] = "simulated"
                if not any(c.get("id") == comp.get("id") for c in components):
                    components.append(comp)
            logger.info(f"Discovered {len(mock_components)} components from simulated")
        except Exception as e:
            logger.error(f"Error discovering from simulated: {e}")

        # Prometheus/Docker mode - add metrics from Prometheus adapter
        # Always include Prometheus components (even if real Prometheus is unavailable)
        logger.info(f"Data mode: {self.data_mode}, Prometheus adapter: {self.prometheus_adapter}")
        if self.data_mode in ("prometheus", "docker", "real") and self.prometheus_adapter:
            try:
                prom_components = self.prometheus_adapter.get_components()
                logger.info(f"Prometheus adapter returned {len(prom_components)} components")
                for comp in prom_components:
                    comp["provider"] = "prometheus"
                    comp["source"] = "prometheus"
                    if not any(c.get("id") == comp.get("id") for c in components):
                        components.append(comp)
                logger.info(f"Discovered {len(prom_components)} components from Prometheus")
            except Exception as e:
                logger.error(f"Error discovering from Prometheus: {e}")

        return components

    def get_component(self, component_id: str) -> Optional[Dict]:
        """Get a specific component."""
        adapter = self.get_primary_adapter()
        return adapter.get_component(component_id)

    def get_metrics(self, component_id: str, metric_names: List[str],
                   start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get time-series metrics for a component."""
        adapter = self.get_primary_adapter()
        return adapter.get_metrics(component_id, metric_names, start_time, end_time)

    def get_latest_metrics(self, component_id: str) -> Dict[str, float]:
        """Get latest metrics for a component."""
        adapter = self.get_primary_adapter()
        return adapter.get_latest_metrics(component_id)

    def get_all_latest_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get latest metrics for all components."""
        adapter = self.get_primary_adapter()
        return adapter.get_all_latest_metrics()

    def get_status(self) -> Dict:
        """Get status of all data sources."""
        status = {
            "data_mode": self.data_mode,
            "cloud_provider": self.cloud_provider,
            "prometheus_url": self.prometheus_url,
            "timestamp": datetime.utcnow().isoformat(),
            "sources": {}
        }

        if self.prometheus_adapter:
            prom_status = self.prometheus_adapter.get_status()
            status["sources"]["prometheus"] = {
                "available": prom_status.get("available", False),
                "type": "prometheus",
                "url": self.prometheus_url,
                "components": prom_status.get("components", 0),
                "description": "Real-time metrics from Prometheus"
            }

        if self.local_adapter:
            status["sources"]["local"] = {
                "available": self.local_adapter.is_available(),
                "type": "local",
                "description": "Local PC/Server metrics"
            }

        if self.simulator_adapter:
            scenario_info = self.simulator_adapter.get_scenario_info()
            status["sources"]["simulator"] = {
                "available": True,
                "enabled": self.simulator_enabled,
                "type": "simulator",
                "current_scenario": scenario_info.get("current_scenario", "normal"),
                "component_count": scenario_info.get("component_count", 0),
                "description": "Realistic infrastructure simulator"
            }

        if self.mock_adapter:
            status["sources"]["simulated"] = {
                "available": True,
                "type": "solarwinds",
                "description": "Simulated infrastructure data"
            }

        return status

    def set_simulator_scenario(self, scenario: str) -> Dict:
        """Set the simulator scenario."""
        if self.simulator_adapter:
            self.simulator_adapter.set_scenario(scenario)
            return {"success": True, "scenario": scenario}
        return {"success": False, "error": "Simulator not available"}

    def get_simulator_scenario(self) -> str:
        """Get current simulator scenario."""
        if self.simulator_adapter:
            return self.simulator_adapter.get_scenario()
        return "unavailable"

    def is_available(self) -> bool:
        """Check if any data source is available."""
        return True


_manager = None


def get_data_source_manager() -> DataSourceManager:
    """Get the singleton DataSourceManager instance."""
    global _manager
    if _manager is None:
        _manager = DataSourceManager()
    return _manager