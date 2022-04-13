from typing import (
    Optional,
)


class ValidationError(Exception):
    def __init__(self, message: Optional[str] = "") -> None:
        """
        Thrown when validation will fail.
        
        Note:
            Do not include the `self` parameter in the ``Args`` section.
        Args:
            message (str): Human readable string describing the exception
        """
        super(ValidationError, self).__init__(message)


class ServerError(Exception):
    def __init__(self, message: Optional[str] = "") -> None:
        """
        Thrown when Proteus server will response with error.

        Note:
            Do not include the `self` parameter in the ``Args`` section.
        Args:
            message (str): Human readable string describing the exception
        """
        super(ServerError, self).__init__(message)


class DataError(Exception):
    def __init__(self, message: Optional[str] = "") -> None:
        """
        Thrown when expected data will not present in the application UI.

        Note:
            Do not include the `self` parameter in the ``Args`` section.
        Args:
            message (str): Human readable string describing the exception
        """
        super(DataError, self).__init__(message)


class ApplicationError(Exception):
    def __init__(self, message: Optional[str] = "") -> None:
        """
        Thrown when application will behave like unexpected.

        Note:
            Do not include the `self` parameter in the ``Args`` section.
        Args:
            message (str): Human readable string describing the exception
        """
        super(ApplicationError, self).__init__(message)


class AutomationError(Exception):
    def __init__(self, message: Optional[str] = "") -> None:
        """
        Thrown when there will any automation script error.

        Note:
            Do not include the `self` parameter in the ``Args`` section.
        Args:
            message (str): Human readable string describing the exception
        """
        super(AutomationError, self).__init__(message)


class ElementNotFoundError(Exception):
    def __init__(self, message: Optional[str] = "") -> None:
        """
        Thrown when element could not be found.

        Note:
            Do not include the `self` parameter in the ``Args`` section.
        Args:
            message (str): Human readable string describing the exception
        """
        super(ElementNotFoundError, self).__init__(message)


class KeyNotFoundError(Exception):
    def __init__(self, message: Optional[str] = "") -> None:
        """
        Thrown when element could not be found.

        Note:
            Do not include the `self` parameter in the ``Args`` section.
        Args:
            message (str): Human readable string describing the exception
        """
        super(KeyNotFoundError, self).__init__(message)