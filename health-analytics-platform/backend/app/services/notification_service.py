import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from ..models.models import Alert, Component

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications (email, webhook, etc.)."""

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.recipients = os.getenv("ALERT_EMAIL_RECIPIENTS", "").split(",")
        self.enabled = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"

        self._notification_cooldown = {}
        self._cooldown_minutes = int(os.getenv("NOTIFICATION_COOLDOWN_MINUTES", "30"))

    def send_alert_notification(self, alert: Alert, component: Component = None) -> bool:
        """Send notification for an alert."""
        if not self.enabled:
            logger.debug("Email notifications disabled")
            return False

        if alert.severity not in ["high", "critical"]:
            logger.debug(f"Skipping notification for {alert.severity} severity alert")
            return False

        if self._is_in_cooldown(alert.id):
            logger.debug(f"Alert {alert.id} is in cooldown period")
            return False

        try:
            self._send_email(alert, component)
            self._update_cooldown(alert.id)
            logger.info(f"Sent notification for alert {alert.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def _send_email(self, alert: Alert, component: Component = None):
        """Send email notification."""
        if not self.smtp_host or not self.recipients:
            logger.warning("SMTP not configured, skipping email")
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[{alert.severity.upper()}] InfraSense Alert: {alert.title}"
        msg["From"] = self.smtp_user
        msg["To"] = ", ".join(self.recipients)

        html_content = self._build_html_email(alert, component)
        text_content = self._build_text_email(alert, component)

        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

    def _build_html_email(self, alert: Alert, component: Component = None) -> str:
        """Build HTML email content."""
        severity_colors = {
            "critical": "#dc2626",
            "high": "#ea580c",
            "medium": "#ca8a04",
            "low": "#16a34a",
            "info": "#2563eb"
        }

        color = severity_colors.get(alert.severity, "#6b7280")

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; border-radius: 0 0 5px 5px; }}
                .alert-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .alert-details {{ margin: 15px 0; }}
                .alert-details dt {{ font-weight: bold; color: #4b5563; }}
                .alert-details dd {{ margin-left: 0; margin-bottom: 10px; }}
                .severity {{ display: inline-block; padding: 4px 12px; border-radius: 3px; color: white; font-weight: bold; }}
                .action {{ background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>InfraSense Alert</h2>
                </div>
                <div class="content">
                    <div class="alert-title">{alert.title}</div>
                    <span class="severity" style="background-color: {color};">{alert.severity.upper()}</span>

                    <dl class="alert-details">
                        <dt>Component</dt>
                        <dd>{component.name if component else alert.component_id}</dd>

                        <dt>Description</dt>
                        <dd>{alert.description or "No description"}</dd>

                        <dt>Current Value</dt>
                        <dd>{alert.current_value}</dd>

                        <dt>Threshold</dt>
                        <dd>{alert.threshold}</dd>
        """

        if alert.predicted_value:
            html += f"""
                        <dt>Predicted Value</dt>
                        <dd>{alert.predicted_value}</dd>

                        <dt>Time to Breach</dt>
                        <dd>{alert.time_to_breach} minutes</dd>

                        <dt>Confidence</dt>
                        <dd>{alert.confidence}%</dd>
            """

        if alert.impact:
            html += f"""
                        <dt>Potential Impact</dt>
                        <dd>{alert.impact}</dd>
            """

        if alert.recommended_action:
            html += f"""
                        <dt>Recommended Action</dt>
                        <dd>{alert.recommended_action}</dd>
            """

        html += f"""
                    </dl>

                    <p><a href="#" class="action">View in Dashboard</a></p>
                </div>
                <div class="footer">
                    <p>This is an automated alert from InfraSense monitoring platform.</p>
                    <p>Generated at {datetime.utcnow().isoformat()}</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _build_text_email(self, alert: Alert, component: Component = None) -> str:
        """Build plain text email content."""
        text = f"""
InfraSense Alert: {alert.title}

Severity: {alert.severity.upper()}
Component: {component.name if component else alert.component_id}
Description: {alert.description or "No description"}
Current Value: {alert.current_value}
Threshold: {alert.threshold}
"""

        if alert.predicted_value:
            text += f"""
Predicted Value: {alert.predicted_value}
Time to Breach: {alert.time_to_breach} minutes
Confidence: {alert.confidence}%
"""

        if alert.impact:
            text += f"\nPotential Impact: {alert.impact}\n"

        if alert.recommended_action:
            text += f"\nRecommended Action: {alert.recommended_action}\n"

        text += f"\nGenerated at: {datetime.utcnow().isoformat()}"
        return text

    def _is_in_cooldown(self, alert_id: str) -> bool:
        """Check if alert is in cooldown period."""
        if alert_id not in self._notification_cooldown:
            return False

        last_notification = self._notification_cooldown[alert_id]
        return (datetime.utcnow() - last_notification).total_seconds() < (self._cooldown_minutes * 60)

    def _update_cooldown(self, alert_id: str):
        """Update cooldown timestamp for alert."""
        self._notification_cooldown[alert_id] = datetime.utcnow()

    def send_digest(self, alerts: List[Alert]) -> bool:
        """Send a digest of alerts."""
        if not self.enabled or not alerts:
            return False

        critical_alerts = [a for a in alerts if a.severity == "critical"]
        high_alerts = [a for a in alerts if a.severity == "high"]

        if not critical_alerts and not high_alerts:
            return False

        try:
            self._send_digest_email(critical_alerts, high_alerts)
            logger.info(f"Sent digest with {len(critical_alerts)} critical and {len(high_alerts)} high alerts")
            return True
        except Exception as e:
            logger.error(f"Failed to send digest: {e}")
            return False

    def _send_digest_email(self, critical_alerts: List[Alert], high_alerts: List[Alert]):
        """Send digest email."""
        if not self.smtp_host or not self.recipients:
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[InfraSense] Alert Digest - {len(critical_alerts)} Critical, {len(high_alerts)} High"
        msg["From"] = self.smtp_user
        msg["To"] = ", ".join(self.recipients)

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .critical {{ color: #dc2626; font-weight: bold; }}
                .high {{ color: #ea580c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h2>InfraSense Alert Digest</h2>
            <p>{len(critical_alerts)} Critical alerts, {len(high_alerts)} High alerts</p>
        """

        if critical_alerts:
            html += "<h3 class='critical'>Critical Alerts</h3><ul>"
            for alert in critical_alerts:
                html += f"<li>{alert.title} - {alert.component_id}</li>"
            html += "</ul>"

        if high_alerts:
            html += "<h3 class='high'>High Priority Alerts</h3><ul>"
            for alert in high_alerts:
                html += f"<li>{alert.title} - {alert.component_id}</li>"
            html += "</ul>"

        html += f"<p>Generated at {datetime.utcnow().isoformat()}</p></body></html>"

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)


_notification_service = None


def get_notification_service() -> NotificationService:
    """Get the notification service singleton."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service


def send_alert_notification(alert: Alert, component: Component = None) -> bool:
    """Send notification for an alert."""
    service = get_notification_service()
    return service.send_alert_notification(alert, component)


def send_digest(alerts: List[Alert]) -> bool:
    """Send alert digest."""
    service = get_notification_service()
    return service.send_digest(alerts)