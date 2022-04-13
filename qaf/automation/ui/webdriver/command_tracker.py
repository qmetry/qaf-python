from enum import Enum

from typing import Union


class Stage(Enum):
    executing_before_method = 1
    executing_method = 2
    executing_after_method = 3
    executing_on_failure = 4


class CommandTracker:
    def __init__(self, command: str, parameters: dict) -> None:
        self.exception = None
        self.stage = -1
        self.retry = False
        self.start_time = None
        self.end_time = None
        self.response = None
        self.command = command
        self.__parameters = {}
        self.parameters = parameters

    @property
    def exception(self) -> Exception:
        return self.__exception

    @exception.setter
    def exception(self, value: Exception) -> None:
        self.__exception = value

    def has_exception(self) -> bool:
        return self.__exception is not None

    def get_exception_type(self) -> Union[None, Exception]:
        return None if self.__exception is None else type(self.__exception).__name__

    @property
    def stage(self) -> int:
        return self.__stage

    @stage.setter
    def stage(self, value: int) -> None:
        self.__stage = value

    @property
    def retry(self) -> bool:
        return self.__retry

    @retry.setter
    def retry(self, value: bool) -> None:
        self.__retry = value

    @property
    def start_time(self) -> str:
        return self.__start_time

    @start_time.setter
    def start_time(self, value: str) -> None:
        self.__start_time = value

    @property
    def end_time(self) -> str:
        return self.__end_time

    @end_time.setter
    def end_time(self, value: str) -> None:
        self.__end_time = value

    @property
    def response(self) -> dict:
        return self.__response

    @response.setter
    def response(self, value: dict) -> None:
        self.__response = value

    @property
    def command(self) -> str:
        return self.__command

    @command.setter
    def command(self, value: str) -> None:
        self.__command = value

    @property
    def parameters(self) -> dict:
        return self.__parameters

    @parameters.setter
    def parameters(self, value: str) -> None:
        if value is not None:
            self.__parameters.update(value)

    @property
    def message(self) -> str:
        return "" if self.__exception is None else "{0}: {1!r}".format(type(self.__exception).__name__,
                                                                       self.__exception.args)
