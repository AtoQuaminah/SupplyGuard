"""Custom exceptions for SupplyGuard."""


class SupplyGuardError(RuntimeError):
    """Base exception for SupplyGuard."""


class RetrievalError(SupplyGuardError):
    """Raised when a package artifact cannot be retrieved."""


class ValidationError(SupplyGuardError):
    """Raised when a package artifact fails validation."""


class ExtractionError(SupplyGuardError):
    """Raised when extraction fails."""


class AnalysisError(SupplyGuardError):
    """Raised when analysis fails."""


class ConfigurationError(SupplyGuardError):
    """Raised when configuration is invalid."""
