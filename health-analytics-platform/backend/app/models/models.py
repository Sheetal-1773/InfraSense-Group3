from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, Boolean, Index, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    components = relationship("Component", back_populates="category")

    __table_args__ = (
        Index('idx_category_type', 'type'),
    )


class Component(Base):
    __tablename__ = "components"

    id = Column(String, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    hostname = Column(String, nullable=True)
    environment = Column(String, default="production")
    status = Column(String, default="healthy")
    health_score = Column(Integer, default=100)
    criticality = Column(String, default="medium")
    owner = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="components")
    metrics = relationship("ComponentMetric", back_populates="component", cascade="all, delete-orphan")
    health_scores = relationship("HealthScoreHistory", back_populates="component")
    alerts = relationship("Alert", back_populates="component")
    anomalies = relationship("Anomaly", back_populates="component")
    predictions = relationship("Prediction", back_populates="component")

    __table_args__ = (
        Index('idx_component_category', 'category_id'),
        Index('idx_component_status', 'status'),
    )


class ComponentMetric(Base):
    __tablename__ = "component_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    component_id = Column(String, ForeignKey("components.id"), nullable=False)
    metric_type = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    labels = Column(JSON, nullable=True)
    warning_threshold = Column(Float, nullable=True)
    critical_threshold = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String, default="system")
    created_at = Column(DateTime, default=datetime.utcnow)

    component = relationship("Component", back_populates="metrics")

    __table_args__ = (
        Index('idx_metric_component', 'component_id'),
        Index('idx_metric_type', 'metric_type'),
        Index('idx_metric_timestamp', 'timestamp'),
    )


class HealthScoreHistory(Base):
    __tablename__ = "health_score_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    component_id = Column(String, ForeignKey("components.id"), nullable=False)
    score = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    component = relationship("Component", back_populates="health_scores")

    __table_args__ = (
        Index('idx_health_component', 'component_id'),
    )


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, index=True)
    component_id = Column(String, ForeignKey("components.id"), nullable=False)
    metric_id = Column(Integer, ForeignKey("component_metrics.id"), nullable=True)
    prediction_type = Column(String, nullable=False)
    current_value = Column(Float, nullable=False)
    predicted_value = Column(Float, nullable=False)
    predicted_threshold = Column(Float, nullable=False)
    threshold_direction = Column(String, default="above")
    time_to_breach_minutes = Column(Integer, nullable=False)
    time_to_breach_max = Column(Integer, nullable=True)
    time_to_breach_min = Column(Integer, nullable=True)
    confidence = Column(Integer, nullable=False)
    severity = Column(String, default="low")
    probability = Column(Float, nullable=True)
    impact = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)
    contributing_factors = Column(JSON, nullable=True)
    recommended_action = Column(Text, nullable=True)
    runbook_url = Column(String, nullable=True)
    prediction_time = Column(DateTime, default=datetime.utcnow)
    expected_breach_time = Column(DateTime, nullable=True)
    actual_breach_time = Column(DateTime, nullable=True)
    is_accurate = Column(Boolean, nullable=True)
    accuracy_error = Column(Float, nullable=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    component = relationship("Component", back_populates="predictions")

    __table_args__ = (
        Index('idx_prediction_component', 'component_id'),
        Index('idx_prediction_status', 'status'),
    )


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True)
    component_id = Column(String, ForeignKey("components.id"), nullable=False)
    metric_id = Column(Integer, ForeignKey("component_metrics.id"), nullable=True)
    prediction_id = Column(String, ForeignKey("predictions.id"), nullable=True)
    parent_alert_id = Column(String, ForeignKey("alerts.id"), nullable=True)
    alert_type = Column(String, default="reactive")
    severity = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    current_value = Column(Float, nullable=True)
    predicted_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    time_to_breach = Column(Integer, nullable=True)
    confidence = Column(Integer, nullable=True)
    impact = Column(String, nullable=True)
    recommended_action = Column(Text, nullable=True)
    status = Column(String, default="open")
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    escalation_cancelled_at = Column(DateTime, nullable=True)
    escalation_count = Column(Integer, default=0)
    escalation_timeout_minutes = Column(Integer, default=15)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    component = relationship("Component", back_populates="alerts")
    parent_alert = relationship("Alert", remote_side=[id], backref="child_alerts")

    __table_args__ = (
        Index('idx_alert_component', 'component_id'),
        Index('idx_alert_status', 'status'),
        Index('idx_alert_type', 'alert_type'),
        Index('idx_alert_parent', 'parent_alert_id'),
    )


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(String, primary_key=True, index=True)
    component_id = Column(String, ForeignKey("components.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    threshold_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)

    component = relationship("Component", back_populates="anomalies")

    __table_args__ = (
        Index('idx_anomaly_component', 'component_id'),
        Index('idx_anomaly_detected', 'detected_at'),
    )


class Correlation(Base):
    __tablename__ = "correlations"

    id = Column(String, primary_key=True, index=True)
    source_component_id = Column(String, ForeignKey("components.id"), nullable=False)
    target_component_id = Column(String, ForeignKey("components.id"), nullable=False)
    correlation_type = Column(String, nullable=False)
    correlation_score = Column(Float, nullable=False)
    direction = Column(String, default="bidirectional")
    evidence = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")

    __table_args__ = (
        Index('idx_correlation_source', 'source_component_id'),
        Index('idx_correlation_target', 'target_component_id'),
    )


class Threshold(Base):
    __tablename__ = "thresholds"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    component_type = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    warning_threshold = Column(Float, nullable=False)
    critical_threshold = Column(Float, nullable=False)
    is_dynamic = Column(Boolean, default=False)
    duration_minutes = Column(Integer, default=0)


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)