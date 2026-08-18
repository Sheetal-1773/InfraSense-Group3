import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """Generates correlations between components based on metrics and dependencies."""
    
    # Define component dependencies
    DEPENDENCIES = {
        # Database -> Application dependencies
        "postgres": ["payment", "order", "customer", "auth", "api"],
        "mysql": ["payment", "order", "customer", "auth", "api"],
        "redis": ["payment", "order", "customer", "auth", "api"],
        
        # Network -> All
        "gateway": ["api", "payment", "order", "customer", "auth"],
        "load-balancer": ["api", "payment", "order", "customer", "auth"],
        "router": ["api", "payment", "order", "customer", "auth"],
        "switch": ["api", "payment", "order", "customer", "auth"],
        
        # Server -> Applications
        "web-server": ["api", "payment", "order", "customer", "auth"],
        "app-server": ["api", "payment", "order", "customer", "auth"],
        "compute": ["api", "payment", "order", "customer", "auth"],
    }
    
    def generate_correlations(self, components: List[Dict]) -> List[Dict]:
        """Generate correlations between components."""
        correlations = []
        
        # Group components by type
        databases = [c for c in components if c.get("category") == "database" or c.get("type") == "database" or "db" in c.get("id", "").lower()]
        applications = [c for c in components if c.get("category") == "application" or c.get("type") == "application" or "app" in c.get("id", "").lower()]
        networks = [c for c in components if c.get("category") == "network" or c.get("type") == "network" or any(x in c.get("id", "").lower() for x in ["router", "switch", "gateway", "firewall", "load-balancer"])]
        servers = [c for c in components if c.get("category") == "server" or c.get("type") == "server" or "server" in c.get("id", "").lower() or "srv" in c.get("id", "").lower()]
        
        logger.info(f"Correlation check: {len(databases)} databases, {len(applications)} applications, {len(networks)} networks, {len(servers)} servers")
        
        # If we have databases and applications, create correlations based on latency
        for db in databases:
            db_id = db.get("id")
            db_name = db.get("name")
            db_metrics = db.get("metrics", {})
            db_health = db.get("health_score", 100)
            db_status = db.get("status", "healthy")
            db_latency = db_metrics.get("query_latency", db_metrics.get("db_query_latency", 0))
            
            for app in applications:
                app_id = app.get("id")
                app_name = app.get("name")
                app_metrics = app.get("metrics", {})
                app_health = app.get("health_score", 100)
                app_latency = app_metrics.get("api_latency", app_metrics.get("response_time", app_metrics.get("latency", 0)))
                
                # Always check for latency correlation if both have latency metrics
                if db_latency > 0 and app_latency > 0:
                    # Calculate correlation based on latency
                    correlation_score = min(0.9, (db_latency / 1000) + (app_latency / 1000))
                    if correlation_score > 0.1:
                        correlations.append({
                            "id": f"corr-latency-{db_id}-{app_id}",
                            "source_component_id": db_id,
                            "source_component_name": db_name,
                            "target_component_id": app_id,
                            "target_component_name": app_name,
                            "correlation_type": "latency_propagation",
                            "correlation_score": correlation_score,
                            "direction": "upstream",
                            "evidence": f"Database query latency ({db_latency:.1f}ms) correlates with API latency ({app_latency:.1f}ms)",
                            "detected_at": datetime.utcnow().isoformat(),
                            "status": "active"
                        })
        
        logger.info(f"Generated {len(correlations)} correlations")
        
        # Check database -> application correlations
        for db in databases:
            db_id = db.get("id")
            db_name = db.get("name")
            db_metrics = db.get("metrics", {})
            db_health = db.get("health_score", 100)
            db_status = db.get("status", "healthy")
            
            for app in applications:
                app_id = app.get("id")
                app_name = app.get("name")
                app_metrics = app.get("metrics", {})
                app_health = app.get("health_score", 100)
                app_status = app.get("status", "healthy")
                
                # Check if database issues affect application
                if db_status not in ["healthy", "good"] or db_health < 90:
                    # Database is unhealthy, check if app is affected
                    if app_status not in ["healthy", "good"] or app_health < 90:
                        correlation_score = self._calculate_correlation_score(db, app)
                        if correlation_score > 0.3:
                            correlations.append({
                                "id": f"corr-db-app-{db_id}-{app_id}",
                                "source_component_id": db_id,
                                "source_component_name": db_name,
                                "target_component_id": app_id,
                                "target_component_name": app_name,
                                "correlation_type": "performance_degradation",
                                "correlation_score": correlation_score,
                                "direction": "upstream",
                                "evidence": f"Database {db_name} is {db_status} (health: {db_health:.1f}%), affecting {app_name} (health: {app_health:.1f}%)",
                                "detected_at": datetime.utcnow().isoformat(),
                                "status": "active"
                            })
                
                # Check latency correlation
                db_latency = db_metrics.get("query_latency", db_metrics.get("db_query_latency", 0))
                app_latency = app_metrics.get("api_latency", app_metrics.get("response_time", 0))
                if db_latency > 30 and app_latency > 100:
                    correlation_score = min(1.0, (db_latency / 100) * (app_latency / 500))
                    if correlation_score > 0.3:
                        correlations.append({
                            "id": f"corr-latency-{db_id}-{app_id}",
                            "source_component_id": db_id,
                            "source_component_name": db_name,
                            "target_component_id": app_id,
                            "target_component_name": app_name,
                            "correlation_type": "latency_propagation",
                            "correlation_score": correlation_score,
                            "direction": "upstream",
                            "evidence": f"Database query latency ({db_latency:.1f}ms) correlates with API latency ({app_latency:.1f}ms)",
                            "detected_at": datetime.utcnow().isoformat(),
                            "status": "active"
                        })
        
        # Check network -> application correlations
        for net in networks:
            net_id = net.get("id")
            net_name = net.get("name")
            net_metrics = net.get("metrics", {})
            net_health = net.get("health_score", 100)
            net_status = net.get("status", "healthy")
            
            for app in applications:
                app_id = app.get("id")
                app_name = app.get("name")
                app_metrics = app.get("metrics", {})
                app_health = app.get("health_score", 100)
                
                # Check network latency impact
                net_latency = net_metrics.get("latency", 0)
                app_latency = app_metrics.get("api_latency", app_metrics.get("response_time", 0))
                
                if net_latency > 10 and app_latency > 200:
                    correlation_score = min(1.0, (net_latency / 20) * (app_latency / 500))
                    if correlation_score > 0.2:
                        correlations.append({
                            "id": f"corr-net-{net_id}-{app_id}",
                            "source_component_id": net_id,
                            "source_component_name": net_name,
                            "target_component_id": app_id,
                            "target_component_name": app_name,
                            "correlation_type": "network_latency",
                            "correlation_score": correlation_score,
                            "direction": "upstream",
                            "evidence": f"Network latency ({net_latency:.1f}ms) affecting API response time ({app_latency:.1f}ms)",
                            "detected_at": datetime.utcnow().isoformat(),
                            "status": "active"
                        })
        
        # Check server -> application correlations
        for server in servers:
            server_id = server.get("id")
            server_name = server.get("name")
            server_metrics = server.get("metrics", {})
            server_health = server.get("health_score", 100)
            server_status = server.get("status", "healthy")
            
            for app in applications:
                app_id = app.get("id")
                app_name = app.get("name")
                app_health = app.get("health_score", 100)
                
                # Check if server issues affect application
                if server_status != "healthy" or server_health < 70:
                    if app_health < 90:
                        correlation_score = self._calculate_correlation_score(server, app)
                        if correlation_score > 0.3:
                            correlations.append({
                                "id": f"corr-srv-{server_id}-{app_id}",
                                "source_component_id": server_id,
                                "source_component_name": server_name,
                                "target_component_id": app_id,
                                "target_component_name": app_name,
                                "correlation_type": "resource_contention",
                                "correlation_score": correlation_score,
                                "direction": "upstream",
                                "evidence": f"Server {server_name} health ({server_health:.1f}%) affecting {app_name} (health: {app_health:.1f}%)",
                                "detected_at": datetime.utcnow().isoformat(),
                                "status": "active"
                            })
        
        # Check for cascading failures
        critical_components = [c for c in components if c.get("health_score", 100) < 40]
        for critical in critical_components:
            critical_id = critical.get("id")
            critical_name = critical.get("name")
            critical_type = critical.get("category", "")
            
            # Find dependent components
            dependents = self._find_dependents(critical_id, critical_name, components)
            
            for dependent in dependents:
                dep_health = dependent.get("health_score", 100)
                if dep_health < 80:
                    correlations.append({
                        "id": f"corr-cascade-{critical_id}-{dependent.get('id')}",
                        "source_component_id": critical_id,
                        "source_component_name": critical_name,
                        "target_component_id": dependent.get("id"),
                        "target_component_name": dependent.get("name"),
                        "correlation_type": "cascading_failure",
                        "correlation_score": 0.9,
                        "direction": "downstream",
                        "evidence": f"Cascading failure from {critical_name} affecting {dependent.get('name')}",
                        "detected_at": datetime.utcnow().isoformat(),
                        "status": "active"
                    })
        
        return correlations
    
    def _calculate_correlation_score(self, source: Dict, target: Dict) -> float:
        """Calculate correlation score between two components."""
        source_health = source.get("health_score", 100)
        target_health = target.get("health_score", 100)
        
        # If both are unhealthy, there's likely a correlation
        if source_health < 70 and target_health < 80:
            # Calculate based on health difference
            health_diff = abs(source_health - target_health)
            return max(0.3, 1.0 - (health_diff / 100))
        
        return 0.0
    
    def _find_dependents(self, component_id: str, component_name: str, 
                        components: List[Dict]) -> List[Dict]:
        """Find components that depend on the given component."""
        dependents = []
        
        # Check component name/type for dependency hints
        comp_lower = component_name.lower()
        comp_id_lower = component_id.lower()
        
        for comp in components:
            if comp.get("id") == component_id:
                continue
            
            dep_name = comp.get("name", "").lower()
            dep_id = comp.get("id", "").lower()
            
            # Check if this component might depend on the source
            # Database dependencies
            if "postgres" in comp_id_lower or "mysql" in comp_id_lower or "redis" in comp_id_lower:
                if any(x in dep_id or x in dep_name for x in ["payment", "order", "customer", "auth", "api"]):
                    dependents.append(comp)
            
            # Network dependencies
            elif "gateway" in comp_id_lower or "load-balancer" in comp_id_lower or "router" in comp_id_lower:
                if "api" in dep_id or "api" in dep_name:
                    dependents.append(comp)
            
            # Server dependencies
            elif "server" in comp_id_lower:
                if "api" in dep_id or "api" in dep_name:
                    dependents.append(comp)
        
        return dependents


_correlation_engine = None


def get_correlation_engine() -> CorrelationEngine:
    global _correlation_engine
    if _correlation_engine is None:
        _correlation_engine = CorrelationEngine()
    return _correlation_engine