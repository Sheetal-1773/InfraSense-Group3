from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CategoryBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryWithHealth(CategoryResponse):
    health_score: Optional[int] = None
    health_status: Optional[str] = None
    total_components: int = 0
    healthy_components: int = 0
    warning_components: int = 0
    critical_components: int = 0
    unknown_components: int = 0


class ComponentMetricBase(BaseModel):
    metric_type: str
    metric_name: str
    current_value: float
    unit: str
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None


class ComponentMetricResponse(ComponentMetricBase):
    id: int
    component_id: str
    timestamp: datetime
    source: str

    class Config:
        from_attributes = True


class ComponentBase(BaseModel):
    name: str
    category_id: int
    hostname: Optional[str] = None
    environment: str = "production"
    criticality: str = "medium"
    owner: Optional[str] = None
    description: Optional[str] = None


class ComponentCreate(ComponentBase):
    pass


class ComponentUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    hostname: Optional[str] = None
    environment: Optional[str] = None
    status: Optional[str] = None
    health_score: Optional[int] = None
    criticality: Optional[str] = None
    owner: Optional[str] = None
    description: Optional[str] = None


class ComponentResponse(BaseModel):
    id: str
    category_id: int
    name: str
    hostname: Optional[str]
    environment: str
    status: str
    health_score: int
    criticality: str
    owner: Optional[str]
    description: Optional[str]
    last_seen: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComponentWithMetrics(ComponentResponse):
    metrics: List[ComponentMetricResponse] = []


class HealthScoreTrend(BaseModel):
    timestamp: datetime
    score: int


class CategoryHealthSummary(BaseModel):
    score: Optional[int] = None
    status: Optional[str] = None
    totalComponents: int = 0
    healthyComponents: int = 0
    warningComponents: int = 0
    criticalComponents: int = 0
    unknownComponents: int = 0


class OverallHealthResponse(BaseModel):
    overall: dict
    categories: dict


class PredictionBase(BaseModel):
    component_id: str
    prediction_type: str
    current_value: float
    predicted_value: float
    predicted_threshold: float
    time_to_breach_minutes: int
    confidence: int
    severity: str = "low"
    probability: Optional[float] = None
    impact: Optional[str] = None
    explanation: Optional[str] = None
    recommended_action: Optional[str] = None


class PredictionResponse(PredictionBase):
    id: str
    component_id: str
    metric_id: Optional[int]
    threshold_direction: str
    expected_breach_time: Optional[datetime]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AlertBase(BaseModel):
    component_id: str
    alert_type: str = "reactive"
    severity: str
    title: str
    description: Optional[str] = None
    current_value: Optional[float] = None
    predicted_value: Optional[float] = None
    threshold: Optional[float] = None
    time_to_breach: Optional[int] = None
    confidence: Optional[int] = None
    impact: Optional[str] = None
    recommended_action: Optional[str] = None


class AlertCreate(AlertBase):
    pass


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    acknowledged: Optional[bool] = None


class AlertResponse(AlertBase):
    id: str
    component_id: str
    metric_id: Optional[int]
    prediction_id: Optional[str]
    status: str
    acknowledged: bool
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CorrelationBase(BaseModel):
    source_component_id: str
    target_component_id: str
    correlation_type: str
    correlation_score: float
    direction: str = "bidirectional"
    evidence: Optional[str] = None


class CorrelationResponse(CorrelationBase):
    id: str
    detected_at: datetime
    status: str

    class Config:
        from_attributes = True


class ThresholdBase(BaseModel):
    component_type: str
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    is_dynamic: bool = False


class ThresholdCreate(ThresholdBase):
    pass


class ThresholdResponse(ThresholdBase):
    id: int

    class Config:
        from_attributes = True


class SettingsResponse(BaseModel):
    key: str
    value: str
    updated_at: datetime

    class Config:
        from_attributes = True