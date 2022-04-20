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

import uuid
from qaf.automation.formatter.qaf_report.step.checkpoint import CheckPoint
import os
from qaf.automation.formatter.qaf_report.step.sub_check_points import SubCheckPoints
from qaf.automation.ui.webdriver import base_driver
from qaf.automation.core.message_type import MessageType
from typing import (
    Optional,
)


class Reporter:
    """
    This class will handle log event
    """

    def add_check_point(self, message: str, message_type: MessageType, screen_shot: Optional[str] = '') -> None:
        check_point = CheckPoint()
        check_point.message = message
        check_point.type = message_type
        check_point.screenshot = screen_shot
        SubCheckPoints().add_check_point(check_point)

    @staticmethod
    def log(message: str, message_type: Optional[MessageType] = MessageType.Info) -> None:
        """
        Log message into log file.

        Args:
            message (str): Message needs to be log
            message_type (int): Message type

        Returns:
            None
        """
        Reporter().add_check_point(message, message_type)

    @staticmethod
    def info(message: str) -> None:
        """
        Log message into log file.

        Args:
            message (str): Message needs to be log

        Returns:
            None
        """
        Reporter().add_check_point(message, MessageType.Info)

    @staticmethod
    def debug(message: str) -> None:
        """
        Log message into log file.

        Args:
            message (str): Message needs to be log

        Returns:
            None
        """
        Reporter().add_check_point(message, MessageType.Info)

    @staticmethod
    def error(message: str) -> None:
        """
        Log message into log file.

        Args:
            message (str): Message needs to be log

        Returns:
            None
        """
        Reporter().add_check_point(message, MessageType.Fail)

    @staticmethod
    def critical(message: str) -> None:
        """
        Log message into log file.

        Args:
            message (str): Message needs to be log

        Returns:
            None
        """
        Reporter().add_check_point(message, MessageType.Warn)

    @staticmethod
    def warn(message: str) -> None:
        """
        Log message into log file.

        Args:
            message (str): Message needs to be log

        Returns:
            None
        """
        Reporter().add_check_point(message, MessageType.Warn)

    @staticmethod
    def log_with_screenshot(message: str, message_type: Optional[MessageType] = MessageType.Info) -> None:
        filename = os.path.join(os.getenv('REPORT_DIR'), 'img', str(uuid.uuid4()) + '.png')
        base_driver.BaseDriver().get_driver().save_screenshot(filename=filename)
        Reporter().add_check_point(message, message_type, screen_shot=filename)
