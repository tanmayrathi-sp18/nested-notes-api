class DomainError(Exception):
    """Base class for all domain-level exceptions."""

    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class EntityNotFoundError(DomainError):
    """Raised when a requested entity is not found."""

    pass


class PermissionDeniedError(DomainError):
    """Raised when a user does not have permission to access or modify an entity."""

    pass


class ValidationError(DomainError):
    """Raised when a business rule is violated."""

    pass
