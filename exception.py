class BaseError(Exception):
    pass


class EntityNotFoundError(BaseError):
    pass


class IntegrityViolationError(BaseError):
    pass
