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
