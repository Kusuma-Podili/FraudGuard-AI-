"""Domain Exception Hierarchy and Problem Details (RFC 7807) Formatting."""

from typing import Any, Dict, Optional


class FraudGuardException(Exception):
    """Base domain exception for FraudGuard AI."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "FRAUDGUARD_GENERIC_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class EntityNotFoundException(FraudGuardException):
    """Raised when requested entity is missing."""

    def __init__(self, message: str = "Entity not found", entity_type: str = "Entity", entity_id: str = ""):
        super().__init__(
            message=message if message != "Entity not found" else f"{entity_type} with ID '{entity_id}' was not found.",
            status_code=404,
            error_code="ENTITY_NOT_FOUND",
            details={"entity_type": entity_type, "entity_id": entity_id}
        )


class DuplicateEntityException(FraudGuardException):
    """Raised when creating an entity with a duplicate unique constraint."""

    def __init__(self, message: str = "Entity already exists"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="DUPLICATE_ENTITY"
        )


class AuthenticationException(FraudGuardException):
    """Raised on invalid credentials or expired sessions."""

    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_FAILED"
        )


class PermissionDeniedException(FraudGuardException):
    """Raised on unauthorized role access."""

    def __init__(self, required_role: str):
        super().__init__(
            message=f"Access denied. Requires role '{required_role}'.",
            status_code=403,
            error_code="PERMISSION_DENIED",
            details={"required_role": required_role}
        )


class RuleSyntaxException(FraudGuardException):
    """Raised on invalid AST rule condition syntax."""

    def __init__(self, condition: str, error_detail: str):
        super().__init__(
            message=f"Invalid rule expression: '{condition}'. Detail: {error_detail}",
            status_code=422,
            error_code="RULE_SYNTAX_ERROR",
            details={"condition": condition, "error": error_detail}
        )


class InferenceException(FraudGuardException):
    """Raised when machine learning inference fails."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Inference failure: {reason}",
            status_code=500,
            error_code="MODEL_INFERENCE_FAILURE",
            details={"reason": reason}
        )
