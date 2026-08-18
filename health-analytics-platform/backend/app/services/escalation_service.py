import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from ..models.models import Alert, Component, Settings

logger = logging.getLogger(__name__)


class EscalationService:
    def __init__(self, db: Session):
        self.db = db
        self._load_config()
    
    def _load_config(self):
        self.enabled = self._get_setting("escalation_enabled", "false").lower() == "true"
        self.default_timeout_minutes = int(self._get_setting("escalation_timeout_minutes", "15"))
        self.escalation_contacts = self._get_setting("escalation_contacts", "").split(",")
        self.max_escalations = int(self._get_setting("max_escalations", "3"))
    
    def _get_setting(self, key: str, default: str) -> str:
        setting = self.db.query(Settings).filter(Settings.key == key).first()
        return setting.value if setting else default
    
    def check_and_escalate(self) -> List[Alert]:
        """
        Check for unacknowledged critical alerts and escalate if needed.
        Returns list of escalated alerts.
        """
        if not self.enabled:
            return []
        
        escalated_alerts = []
        
        critical_alerts = self.db.query(Alert).filter(
            Alert.severity == 'critical',
            Alert.status.in_(['active', 'acknowledged']),
            Alert.acknowledged == False
        ).all()
        
        for alert in critical_alerts:
            if self._should_escalate(alert):
                if self._escalate_alert(alert):
                    escalated_alerts.append(alert)
        
        return escalated_alerts
    
    def _should_escalate(self, alert: Alert) -> bool:
        if not alert.created_at:
            return False
        
        timeout = self._get_alert_escalation_timeout(alert)
        elapsed = datetime.utcnow() - alert.created_at
        
        if elapsed < timedelta(minutes=timeout):
            return False
        
        escalation_count = self._get_escalation_count(alert)
        return escalation_count < self.max_escalations
    
    def _get_alert_escalation_timeout(self, alert: Alert) -> int:
        alert_timeout = getattr(alert, 'escalation_timeout_minutes', None)
        if alert_timeout:
            return alert_timeout
        return self.default_timeout_minutes
    
    def _get_escalation_count(self, alert: Alert) -> int:
        escalation_count = getattr(alert, 'escalation_count', None)
        return escalation_count if escalation_count else 0
    
    def _escalate_alert(self, alert: Alert) -> bool:
        try:
            alert.status = 'escalated'
            alert.escalated_at = datetime.utcnow()
            alert.escalation_count = self._get_escalation_count(alert) + 1
            
            self.db.commit()
            
            self._send_escalation_notification(alert)
            
            logger.info(f"Alert {alert.id} escalated (count: {alert.escalation_count})")
            return True
        except Exception as e:
            logger.error(f"Failed to escalate alert {alert.id}: {e}")
            self.db.rollback()
            return False
    
    def _send_escalation_notification(self, alert: Alert):
        """
        Send escalation notification to escalation contacts.
        """
        if not self.escalation_contacts or self.escalation_contacts == [""]:
            logger.warning("No escalation contacts configured")
            return
        
        component = self.db.query(Component).filter(
            Component.id == alert.component_id
        ).first()
        component_name = component.name if component else "Unknown"
        
        logger.info(
            f"Escalation notification for alert {alert.id} - "
            f"Component: {component_name}, Severity: {alert.severity}"
        )
    
    def cancel_escalation(self, alert_id: str) -> bool:
        """
        Cancel escalation when alert is acknowledged.
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return False
        
        if alert.status == 'escalated':
            alert.status = 'active'
            alert.escalation_cancelled_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Escalation cancelled for alert {alert_id}")
            return True
        
        return False
    
    def get_escalation_status(self, alert_id: str) -> Optional[Dict]:
        """
        Get escalation status for an alert.
        """
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        
        return {
            "alert_id": alert.id,
            "status": alert.status,
            "is_escalated": alert.status == 'escalated',
            "escalation_count": self._get_escalation_count(alert),
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "acknowledged": alert.acknowledged,
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
        }


def run_escalation_check(db: Session) -> List[Alert]:
    """
    Run escalation check for all alerts.
    """
    escalation_service = EscalationService(db)
    return escalation_service.check_and_escalate()