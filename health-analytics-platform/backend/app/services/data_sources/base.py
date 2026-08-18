from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime


class DataSourceAdapter(ABC):
    """Base interface for data source adapters."""
    
    @property
    def cloud_provider(self) -> str:
        """Return the cloud provider name (local, simulated, etc)."""
        return "local"
    
    @abstractmethod
    def get_components(self) -> List[Dict]:
        """Get list of all components from the data source."""
        pass
    
    @abstractmethod
    def get_component(self, component_id: str) -> Optional[Dict]:
        """Get a specific component by ID."""
        pass
    
    @abstractmethod
    def get_metrics(self, component_id: str, metric_names: List[str], 
                    start_time: datetime, end_time: datetime) -> List[Dict]:
        """Get time-series metrics for a component."""
        pass
    
    @abstractmethod
    def get_latest_metrics(self, component_id: str) -> Dict[str, float]:
        """Get the latest metric values for a component."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the data source is available."""
        pass