#  Copyright (c) 2022 Infostretch Corporation
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  #
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
from typing import (
    Optional,
)


class QAFException(BaseException):
    """Generic Exception"""

    pass


class QuietError(BaseException):
    # All who inherit this shall not traceback, but be spoken of cleanly
    pass


class ParseError(QAFException, QuietError):
    "BDD2 parse error"
    pass


class StepNotFound(QAFException, QuietError):
    "BDD2 Step Not found"

    def __init__(self,step) -> None:
        """
        Thrown when validation will fail.

        Note:
            Do not include the `self` parameter in the ``Args`` section.
        Args:
            message (str): Human readable string describing the exception
        """
        self.message = f'step not found: {step.name}'
        super(StepNotFound, self).__init__()
        self.step=step

    def __repr__(self):
        return f"Step implementation not found: {self.step.name}\n" \
               f"called from {self.step.scenario.file}\n"\
               f"{self.step.keyword} {self.step.name} @{self.step.line_number}\n" \
               f"{self.step.scenario.name}@{self.step.scenario.line_number}\n" \


class DataProviderError(QAFException, QuietError):
    "Data provider error"

    pass


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
