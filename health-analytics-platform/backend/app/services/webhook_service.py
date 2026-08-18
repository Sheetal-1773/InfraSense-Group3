import httpx
import logging
from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from ..models.models import Alert, Component, Settings

logger = logging.getLogger(__name__)


class WebhookService:
    def __init__(self, db: Session):
        self.db = db
        self._load_config()
    
    def _load_config(self):
        self.enabled = self._get_setting("webhook_enabled", "false").lower() == "true"
        self.endpoints = self._get_setting("webhook_endpoints", "").split(",")
        self.timeout = int(self._get_setting("webhook_timeout", "10"))
        self.max_retries = 3
    
    def _get_setting(self, key: str, default: str) -> str:
        setting = self.db.query(Settings).filter(Settings.key == key).first()
        return setting.value if setting else default
    
    def _build_payload(self, alert: Alert, component_name: str) -> dict:
        return {
            "id": alert.id,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "component": {
                "id": alert.component_id,
                "name": component_name
            },
            "metric": alert.metric,
            "current_value": alert.current_value,
            "threshold": alert.threshold,
            "time_to_breach": alert.time_to_breach,
            "confidence": alert.confidence,
            "recommended_action": alert.recommended_action,
            "status": alert.status,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def send_webhook(self, alert: Alert, endpoint: str, max_retries: int = None) -> bool:
        """
        Send webhook notification for an alert.
        Returns True if successful, False otherwise.
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        if not endpoint or endpoint.strip() == "":
            logger.warning(f"Empty webhook endpoint configured")
            return False
        
        endpoint = endpoint.strip()
        
        component = self.db.query(Component).filter(
            Component.id == alert.component_id
        ).first()
        component_name = component.name if component else "Unknown"
        
        payload = self._build_payload(alert, component_name)
        
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(endpoint, json=payload)
                    response.raise_for_status()
                    logger.info(f"Webhook sent successfully to {endpoint} for alert {alert.id}")
                    return True
            except httpx.TimeoutException:
                logger.warning(f"Webhook timeout attempt {attempt + 1} for {endpoint}")
            except httpx.HTTPStatusError as e:
                logger.warning(f"Webhook HTTP error attempt {attempt + 1}: {e.response.status_code}")
            except Exception as e:
                logger.warning(f"Webhook send attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                import time
                wait_time = 2 ** attempt
                logger.info(f"Retrying webhook in {wait_time} seconds...")
                time.sleep(wait_time)
        
        logger.error(f"Failed to send webhook to {endpoint} after {max_retries} attempts")
        return False
    
    def send_alert_webhooks(self, alert: Alert) -> Dict[str, int]:
        """
        Send webhook notifications to all configured endpoints.
        Returns a summary of results.
        """
        results = {
            "total_endpoints": len(self.endpoints),
            "successful": 0,
            "failed": 0
        }
        
        if not self.enabled:
            logger.info("Webhook notifications disabled")
            return results
        
        for endpoint in self.endpoints:
            if endpoint.strip():
                if self.send_webhook(alert, endpoint):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
        
        return results
    
    def send_batch_webhooks(self, alerts: List[Alert]) -> Dict[str, int]:
        """
        Send webhook notifications for multiple alerts.
        Returns a summary of results.
        """
        results = {
            "total_alerts": len(alerts),
            "total_endpoints": len(self.endpoints),
            "successful": 0,
            "failed": 0
        }
        
        if not self.enabled:
            logger.info("Webhook notifications disabled")
            return results
        
        for alert in alerts:
            alert_results = self.send_alert_webhooks(alert)
            results["successful"] += alert_results["successful"]
            results["failed"] += alert_results["failed"]
        
        return results
    
    def test_webhook(self, endpoint: str) -> dict:
        """
        Test a webhook endpoint with a sample payload.
        """
        test_alert = Alert(
            id="test-alert",
            component_id="test-component",
            alert_type="test",
            severity="info",
            title="Test Alert",
            description="This is a test webhook from InfraSense",
            status="active",
            created_at=datetime.utcnow()
        )
        
        success = self.send_webhook(test_alert, endpoint, max_retries=1)
        
        return {
            "endpoint": endpoint,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }


def send_webhook_notifications(db: Session, alerts: List[Alert]) -> dict:
    """
    Send webhook notifications for a list of alerts.
    Returns a summary of notification results.
    """
    webhook_service = WebhookService(db)
    return webhook_service.send_batch_webhooks(alerts)