import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class RemediationGuard:
    """
    Ensures the platform never automatically executes actions on external systems.
    All remediation actions must be human-initiated.
    """
    
    @staticmethod
    def prevent_auto_remediation(action_type: str, target_system: str, details: Dict[str, Any]) -> bool:
        """
        Log and prevent any auto-remediation attempts.
        Returns False (action blocked).
        """
        logger.warning(
            f"AUTO-REMEDIATION BLOCKED: Attempted to {action_type} on {target_system}. "
            f"Details: {details}. Humans must approve all remediation actions."
        )
        return False
    
    @staticmethod
    def log_remediation_request(action_type: str, target_system: str, details: Dict[str, Any], requested_by: str):
        """
        Log a remediation request for audit purposes.
        """
        logger.info(
            f"REMEDIATION REQUEST: {action_type} on {target_system} "
            f"requested by {requested_by}. Details: {details}"
        )


def prevent_auto_action(action_type: str, target_system: str, **kwargs):
    """
    Decorator/function to prevent auto-remediation.
    Use this before any code that would modify external systems.
    """
    return RemediationGuard.prevent_auto_remediation(action_type, target_system, kwargs)