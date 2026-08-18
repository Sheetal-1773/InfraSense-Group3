import os
import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from .models.database import engine, Base, SessionLocal
from .models.models import Category, Component
from .routers import components, alerts, predictions, categories, correlations, metrics, thresholds, anomalies, websocket, simulator, prometheus_metrics
from .services.health_service import update_component_metrics, calculate_overall_health
from .services.seed_service import run_full_seed
from .services.alert_service import AlertService
from .services.prediction_service import run_prediction_engine
from .services.collectors import start_collector, stop_collector, get_collector_status
from .services.data_source_manager import get_data_source_manager
from .services.websocket_manager import notify_health_update, notify_new_alert, notify_prediction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_MODE = os.getenv("DATA_MODE", "real").lower()
ENABLE_SEED_DATA = os.getenv("ENABLE_SEED_DATA", "false").lower() == "true"
ENABLE_REAL_COLLECTION = os.getenv("ENABLE_REAL_COLLECTION", "true").lower() == "true"
UPDATER_INTERVAL = int(os.getenv("UPDATER_INTERVAL", "5"))


def alert_to_dict(alert) -> dict:
    return {
        "id": alert.id,
        "component_id": alert.component_id,
        "component_name": alert.component.name if alert.component else None,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "description": alert.description,
        "current_value": alert.current_value,
        "predicted_value": alert.predicted_value,
        "threshold": alert.threshold,
        "time_to_breach": alert.time_to_breach,
        "confidence": alert.confidence,
        "status": alert.status,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
    }


def prediction_to_dict(prediction) -> dict:
    return {
        "id": prediction.id,
        "component_id": prediction.component_id,
        "component_name": prediction.component.name if prediction.component else None,
        "metric_id": prediction.metric_id,
        "prediction_type": prediction.prediction_type,
        "current_value": prediction.current_value,
        "predicted_value": prediction.predicted_value,
        "predicted_threshold": prediction.predicted_threshold,
        "threshold_direction": prediction.threshold_direction,
        "time_to_breach_minutes": prediction.time_to_breach_minutes,
        "confidence": prediction.confidence,
        "severity": prediction.severity,
        "probability": prediction.probability,
        "status": prediction.status,
        "prediction_time": prediction.prediction_time.isoformat() if prediction.prediction_time else None,
        "created_at": prediction.created_at.isoformat() if prediction.created_at else None,
    }


def initialize_database():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)

        existing_categories = db.query(Category).count()
        if existing_categories == 0:
            if ENABLE_SEED_DATA or DATA_MODE == "mock":
                run_full_seed(db)
                logger.info("Database initialized with seed data")
            else:
                seed_categories_only(db)
                logger.info("Database initialized with categories only")

        components_list = db.query(Component).all()
        for comp in components_list:
            update_component_metrics(db, comp)

    finally:
        db.close()


def seed_categories_only(db: Session):
    """Seed only categories without components for real data mode."""
    categories_data = [
        {"name": "Network", "type": "network", "description": "Network infrastructure components"},
        {"name": "Applications", "type": "application", "description": "Application services and APIs"},
        {"name": "Databases", "type": "database", "description": "Database servers and clusters"},
        {"name": "Servers", "type": "server", "description": "Physical and virtual servers"},
    ]

    for cat_data in categories_data:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            db.add(Category(**cat_data))

    db.commit()


background_running = True
main_event_loop = None


def schedule_websocket(coro):
    """Schedule a WebSocket broadcast on the main event loop from a background thread."""
    if main_event_loop and not main_event_loop.is_closed():
        try:
            asyncio.run_coroutine_threadsafe(coro, main_event_loop)
        except Exception as e:
            logger.error(f"WebSocket notification error: {e}")


def background_updater():
    while background_running:
        time.sleep(UPDATER_INTERVAL)
        db = SessionLocal()
        try:
            if ENABLE_REAL_COLLECTION:
                data_source_manager = get_data_source_manager()
                discovered_components = data_source_manager.discover_components()

                for comp_data in discovered_components:
                    register_or_update_component(db, comp_data)

            components_list = db.query(Component).all()
            for comp in components_list:
                old_score = comp.health_score
                old_status = comp.status
                update_component_metrics(db, comp)
                if old_score != comp.health_score or old_status != comp.status:
                    schedule_websocket(notify_health_update(
                        comp.id,
                        comp.health_score,
                        comp.status
                    ))

            alert_service = AlertService(db)
            new_alerts = alert_service.check_and_create_alerts()
            for alert in new_alerts:
                schedule_websocket(notify_new_alert(alert_to_dict(alert)))

            new_predictions = run_prediction_engine(db)
            for prediction in new_predictions:
                schedule_websocket(notify_prediction(prediction_to_dict(prediction)))

            db.commit()
        except Exception as e:
            logger.error(f"Background update error: {e}")
        finally:
            db.close()


def register_or_update_component(db, comp_data: dict):
    """Register or update a component from discovered data."""
    component_id = comp_data.get("id")
    if not component_id:
        return

    existing = db.query(Component).filter(Component.id == component_id).first()

    category_type = comp_data.get("type", "server")
    category = db.query(Category).filter(Category.type == category_type).first()

    if not category:
        category = db.query(Category).filter(Category.type == "server").first()

    if existing:
        existing.name = comp_data.get("name", existing.name)
        existing.hostname = comp_data.get("hostname", existing.hostname)
        parsed_last_seen = _parse_datetime(comp_data.get("last_seen"))
        if parsed_last_seen:
            existing.last_seen = parsed_last_seen
        if "status" in comp_data:
            existing.status = comp_data["status"]
    else:
        component = Component(
            id=component_id,
            name=comp_data.get("name", component_id),
            hostname=comp_data.get("hostname"),
            category_id=category.id if category else None,
            environment=comp_data.get("environment", "production"),
            status=comp_data.get("status", "healthy"),
            health_score=100,
            criticality=comp_data.get("criticality", "medium"),
            owner=comp_data.get("owner"),
            description=comp_data.get("description"),
            last_seen=_parse_datetime(comp_data.get("last_seen")),
        )
        db.add(component)

    db.commit()


def _parse_datetime(value):
    """Coerce a value into a naive UTC datetime for SQLite columns."""
    if value is None or isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()

    global background_running, main_event_loop
    background_running = True
    main_event_loop = asyncio.get_running_loop()
    thread = threading.Thread(target=background_updater, daemon=True)
    thread.start()

    if ENABLE_REAL_COLLECTION:
        await start_collector()

    yield

    background_running = False
    if ENABLE_REAL_COLLECTION:
        await stop_collector()


app = FastAPI(
    title="InfraSense API",
    description="Real-Time Cloud Infrastructure Monitoring and Predictive Analytics Platform",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(components.router)
app.include_router(alerts.router)
app.include_router(predictions.router)
app.include_router(categories.router)
app.include_router(correlations.router)
app.include_router(metrics.router)
app.include_router(thresholds.router)
app.include_router(anomalies.router)
app.include_router(websocket.router, tags=["websocket"])
app.include_router(simulator.router)
app.include_router(prometheus_metrics.router)


@app.get("/api/health")
def api_health():
    prometheus_url = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
    return {
        "status": "healthy",
        "service": "infrasense-api",
        "data_mode": DATA_MODE,
        "real_collection": ENABLE_REAL_COLLECTION,
        "prometheus_url": prometheus_url
    }


@app.get("/")
def root():
    return {
        "message": "InfraSense API",
        "version": "2.0.0",
        "docs": "/docs",
        "data_mode": DATA_MODE
    }


@app.get("/api/dashboard/health")
def get_dashboard_health():
    db = SessionLocal()
    try:
        health = calculate_overall_health(db)
        return health
    finally:
        db.close()


@app.get("/api/data-sources/status")
def get_data_sources_status():
    """Get status of all data sources."""
    data_source_manager = get_data_source_manager()
    return data_source_manager.get_status()


@app.get("/api/components/discover")
def discover_components():
    """Manually trigger component discovery."""
    data_source_manager = get_data_source_manager()
    components = data_source_manager.discover_components()
    return {
        "discovered": len(components),
        "components": components
    }


@app.post("/api/data-mode")
def set_data_mode(mode: str):
    """Switch between data modes: mock, simulated, local, prometheus, docker"""
    global DATA_MODE, ENABLE_REAL_COLLECTION
    valid_modes = ["mock", "simulated", "local", "prometheus", "docker", "real"]
    if mode not in valid_modes:
        return {"error": f"Invalid mode. Use one of: {', '.join(valid_modes)}"}
    DATA_MODE = mode
    ENABLE_REAL_COLLECTION = mode in ("real", "prometheus", "docker", "local")
    return {"mode": DATA_MODE, "real_collection": ENABLE_REAL_COLLECTION}