import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.models import Component, ComponentMetric, Alert, Correlation, Category

logger = logging.getLogger(__name__)

CORRELATION_THRESHOLD = float(os.getenv("CORRELATION_THRESHOLD", "0.7"))


class CorrelationEngine:
    """Engine for detecting correlations between component issues."""

    DEPENDENCY_GRAPH = {
        "server": ["application"],
        "database": ["application"],
        "network": ["application", "server"],
    }

    def __init__(self, db: Session):
        self.db = db

    def discover_correlations(self) -> List[Correlation]:
        """Discover correlations between components based on alert patterns."""
        correlations = []

        recent_alerts = self.db.query(Alert).filter(
            Alert.created_at >= datetime.utcnow() - timedelta(hours=24),
            Alert.status.in_(["open", "acknowledged"])
        ).all()

        alert_groups = {}
        for alert in recent_alerts:
            if alert.component_id not in alert_groups:
                alert_groups[alert.component_id] = []
            alert_groups[alert.component_id].append(alert)

        components_with_alerts = list(alert_groups.keys())

        for i, comp_a in enumerate(components_with_alerts):
            for comp_b in components_with_alerts[i+1:]:
                correlation = self._analyze_correlation(
                    alert_groups[comp_a],
                    alert_groups[comp_b]
                )
                if correlation:
                    correlations.append(correlation)

        return correlations

    def _analyze_correlation(self, alerts_a: List[Alert], alerts_b: List[Alert]) -> Optional[Correlation]:
        """Analyze correlation between two components based on their alerts."""
        time_window = timedelta(minutes=15)

        coincident = 0
        for alert_a in alerts_a:
            for alert_b in alerts_b:
                time_diff = abs((alert_a.created_at - alert_b.created_at).total_seconds())
                if time_diff <= time_window.total_seconds():
                    coincident += 1

        if coincident == 0:
            return None

        total_alerts = max(len(alerts_a), len(alerts_b))
        correlation_score = coincident / total_alerts

        if correlation_score < CORRELATION_THRESHOLD:
            return None

        component_a = self.db.query(Component).filter(Component.id == alerts_a[0].component_id).first()
        component_b = self.db.query(Component).filter(Component.id == alerts_b[0].component_id).first()

        if not component_a or not component_b:
            return None

        direction = self._determine_direction(alerts_a, alerts_b)
        correlation_type = self._infer_correlation_type(component_a, component_b)

        existing = self.db.query(Correlation).filter(
            or_(
                and_(Correlation.source_component_id == component_a.id,
                     Correlation.target_component_id == component_b.id),
                and_(Correlation.source_component_id == component_b.id,
                     Correlation.target_component_id == component_a.id)
            )
        ).first()

        if existing:
            existing.correlation_score = correlation_score
            existing.detected_at = datetime.utcnow()
            return existing

        correlation = Correlation(
            id=f"corr-{component_a.id}-{component_b.id}-{int(datetime.utcnow().timestamp())}",
            source_component_id=component_a.id,
            target_component_id=component_b.id,
            correlation_type=correlation_type,
            correlation_score=correlation_score,
            direction=direction,
            evidence=f"{coincident} coincident alerts detected within {time_window.total_seconds() / 60} minutes",
            status="active"
        )

        self.db.add(correlation)
        return correlation

    def _determine_direction(self, alerts_a: List[Alert], alerts_b: List[Alert]) -> str:
        """Determine the direction of correlation."""
        avg_severity_a = sum(self._severity_to_int(a.severity) for a in alerts_a) / len(alerts_a)
        avg_severity_b = sum(self._severity_to_int(a.severity) for a in alerts_b) / len(alerts_b)

        if abs(avg_severity_a - avg_severity_b) < 0.5:
            return "bidirectional"
        elif avg_severity_a > avg_severity_b:
            return "unidirectional"
        else:
            return "unidirectional"

    def _severity_to_int(self, severity: str) -> int:
        """Convert severity to integer for comparison."""
        mapping = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        return mapping.get(severity.lower(), 0)

    def _infer_correlation_type(self, comp_a: Component, comp_b: Component) -> str:
        """Infer the type of correlation between components."""
        type_a = comp_a.category.type if comp_a.category else "unknown"
        type_b = comp_b.category.type if comp_b.category else "unknown"

        if type_a == "database" or type_b == "database":
            if type_a == "application" or type_b == "application":
                return "dependency"
        if type_a == "network" or type_b == "network":
            return "performance"
        if type_a == "server" or type_b == "server":
            if type_a == type_b:
                return "resource"
            return "dependency"

        return "performance"

    def get_impact_analysis(self, component_id: str) -> Dict:
        """Analyze the potential impact of a component failure."""
        component = self.db.query(Component).filter(Component.id == component_id).first()
        if not component:
            return {}

        affected = self._find_affected_components(component_id)
        root_cause_candidates = self._find_root_cause_candidates(component_id)

        return {
            "component_id": component_id,
            "component_name": component.name if component else "Unknown",
            "component_type": component.category.type if component and component.category else "unknown",
            "affected_components": affected,
            "root_cause_candidates": root_cause_candidates,
            "risk_level": self._calculate_risk_level(affected),
            "estimated_impact": self._estimate_impact(affected)
        }

    def _find_affected_components(self, component_id: str) -> List[Dict]:
        """Find components that might be affected by the given component."""
        affected = []

        correlations = self.db.query(Correlation).filter(
            Correlation.source_component_id == component_id,
            Correlation.status == "active"
        ).all()

        for corr in correlations:
            target = self.db.query(Component).filter(Component.id == corr.target_component_id).first()
            if target:
                affected.append({
                    "component_id": target.id,
                    "component_name": target.name,
                    "component_type": target.category.type if target.category else "unknown",
                    "correlation_type": corr.correlation_type,
                    "correlation_score": corr.correlation_score,
                    "direction": corr.direction
                })

        return affected

    def _find_root_cause_candidates(self, component_id: str) -> List[Dict]:
        """Find potential root cause candidates for issues in the given component."""
        candidates = []

        correlations = self.db.query(Correlation).filter(
            Correlation.target_component_id == component_id,
            Correlation.status == "active"
        ).all()

        for corr in correlations:
            source = self.db.query(Component).filter(Component.id == corr.source_component_id).first()
            if source:
                recent_alerts = self.db.query(Alert).filter(
                    Alert.component_id == source.id,
                    Alert.status.in_(["open", "acknowledged"])
                ).count()

                if recent_alerts > 0:
                    candidates.append({
                        "component_id": source.id,
                        "component_name": source.name,
                        "component_type": source.category.type if source.category else "unknown",
                        "correlation_type": corr.correlation_type,
                        "correlation_score": corr.correlation_score,
                        "active_alerts": recent_alerts
                    })

        candidates.sort(key=lambda x: (x["correlation_score"], x["active_alerts"]), reverse=True)
        return candidates

    def _calculate_risk_level(self, affected: List[Dict]) -> str:
        """Calculate risk level based on affected components."""
        if not affected:
            return "low"

        critical_count = sum(1 for a in affected if a.get("correlation_score", 0) > 0.8)
        if critical_count >= 3:
            return "critical"
        elif critical_count >= 1:
            return "high"
        return "medium"

    def _estimate_impact(self, affected: List[Dict]) -> str:
        """Estimate the business impact."""
        if not affected:
            return "No immediate impact expected"

        types = set(a.get("component_type") for a in affected)
        impact_parts = []

        if "application" in types:
            impact_parts.append("customer-facing services")
        if "database" in types:
            impact_parts.append("data access")
        if "network" in types:
            impact_parts.append("connectivity")

        if impact_parts:
            return f"Potential impact on: {', '.join(impact_parts)}"
        return "Limited impact expected"

    def get_dependency_graph(self) -> Dict:
        """Get the complete dependency graph."""
        graph = {
            "nodes": [],
            "edges": []
        }

        components = self.db.query(Component).all()
        for comp in components:
            graph["nodes"].append({
                "id": comp.id,
                "name": comp.name,
                "type": comp.category.type if comp.category else "unknown",
                "status": comp.status
            })

        correlations = self.db.query(Correlation).filter(
            Correlation.status == "active"
        ).all()

        for corr in correlations:
            graph["edges"].append({
                "source": corr.source_component_id,
                "target": corr.target_component_id,
                "type": corr.correlation_type,
                "score": corr.correlation_score
            })

        return graph


def run_correlation_engine(db: Session) -> List[Correlation]:
    """Run the correlation engine."""
    engine = CorrelationEngine(db)
    return engine.discover_correlations()


def get_impact(db: Session, component_id: str) -> Dict:
    """Get impact analysis for a component."""
    engine = CorrelationEngine(db)
    return engine.get_impact_analysis(component_id)