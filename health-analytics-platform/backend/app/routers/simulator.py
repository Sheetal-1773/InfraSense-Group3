from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from ..services.data_source_manager import get_data_source_manager
from ..services.data_sources.simulator_adapter import Scenario

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


class ScenarioRequest(BaseModel):
    scenario: str


class ScenarioResponse(BaseModel):
    success: bool
    scenario: str
    message: Optional[str] = None


@router.get("/status")
def get_simulator_status():
    """Get current simulator status."""
    manager = get_data_source_manager()
    status = manager.get_status()
    
    if "simulator" in status.get("sources", {}):
        return {
            "available": True,
            "scenario": manager.get_simulator_scenario(),
            "details": status["sources"]["simulator"]
        }
    
    return {
        "available": False,
        "message": "Simulator is not enabled"
    }


@router.post("/scenario", response_model=ScenarioResponse)
def set_scenario(request: ScenarioRequest):
    """Set the simulator scenario."""
    valid_scenarios = [
        Scenario.NORMAL,
        Scenario.CPU_SPIKE,
        Scenario.MEMORY_LEAK,
        Scenario.DISK_PRESSURE,
        Scenario.NETWORK_CONGESTION,
        Scenario.DATABASE_SLOWDOWN,
        Scenario.DATABASE_CONNECTION_EXHAUSTION,
        Scenario.API_LATENCY,
        Scenario.API_ERROR_SPIKE,
        Scenario.SERVICE_DEGRADATION,
        Scenario.CASCADING_FAILURE,
    ]
    
    if request.scenario not in valid_scenarios:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario. Valid scenarios: {', '.join(valid_scenarios)}"
        )
    
    manager = get_data_source_manager()
    result = manager.set_simulator_scenario(request.scenario)
    
    if result.get("success"):
        logger.info(f"[SIMULATOR] Scenario set to: {request.scenario}")
        return ScenarioResponse(
            success=True,
            scenario=request.scenario,
            message=f"Scenario changed to {request.scenario}"
        )
    
    raise HTTPException(status_code=500, detail=result.get("error", "Failed to set scenario"))


@router.get("/scenarios")
def get_available_scenarios():
    """Get list of available scenarios."""
    return {
        "scenarios": [
            {"id": Scenario.NORMAL, "name": "Normal", "description": "Normal operation"},
            {"id": Scenario.CPU_SPIKE, "name": "CPU Spike", "description": "High CPU usage on servers"},
            {"id": Scenario.MEMORY_LEAK, "name": "Memory Leak", "description": "Increasing memory usage"},
            {"id": Scenario.DISK_PRESSURE, "name": "Disk Pressure", "description": "High disk usage"},
            {"id": Scenario.NETWORK_CONGESTION, "name": "Network Congestion", "description": "Network latency and packet loss"},
            {"id": Scenario.DATABASE_SLOWDOWN, "name": "Database Slowdown", "description": "Database performance degradation"},
            {"id": Scenario.DATABASE_CONNECTION_EXHAUSTION, "name": "DB Connection Exhaustion", "description": "Max database connections reached"},
            {"id": Scenario.API_LATENCY, "name": "API Latency", "description": "High API response times"},
            {"id": Scenario.API_ERROR_SPIKE, "name": "API Error Spike", "description": "High error rates"},
            {"id": Scenario.SERVICE_DEGRADATION, "name": "Service Degradation", "description": "Multiple metrics degrading"},
            {"id": Scenario.CASCADING_FAILURE, "name": "Cascading Failure", "description": "Database affects dependent services"},
        ]
    }


@router.post("/reset")
def reset_simulator():
    """Reset simulator to normal operation."""
    manager = get_data_source_manager()
    result = manager.set_simulator_scenario(Scenario.NORMAL)
    
    if result.get("success"):
        return {"success": True, "message": "Simulator reset to normal"}
    
    raise HTTPException(status_code=500, detail="Failed to reset simulator")


@router.get("/components")
def get_simulator_components():
    """Get components from simulator only."""
    manager = get_data_source_manager()
    
    if not manager.simulator_adapter:
        raise HTTPException(status_code=404, detail="Simulator not available")
    
    components = manager.simulator_adapter.get_components()
    return {"components": components, "count": len(components)}


@router.get("/metrics/{component_id}")
def get_simulator_component_metrics(component_id: str):
    """Get latest metrics for a specific simulator component."""
    manager = get_data_source_manager()
    
    if not manager.simulator_adapter:
        raise HTTPException(status_code=404, detail="Simulator not available")
    
    metrics = manager.simulator_adapter.get_latest_metrics(component_id)
    return {"component_id": component_id, "metrics": metrics}