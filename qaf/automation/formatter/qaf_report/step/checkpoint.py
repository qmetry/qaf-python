class CheckPoint:
    def __init__(self) -> None:
        self.message = ''
        self.type = ''
        self.duration = 0
        self.threshold = 0
        self.screenshot = ''
        self.subCheckPoints = []

    @property
    def message(self) -> str:
        return self.__message

    @message.setter
    def message(self, value: str) -> None:
        self.__message = value

    @property
    def type(self) -> str:
        return self.__type

    @type.setter
    def type(self, value: str) -> None:
        self.__type = value

    @property
    def duration(self) -> int:
        return self.__duration

    @duration.setter
    def duration(self, value: int) -> None:
        self.__duration = int(value)

    @property
    def threshold(self) -> int:
        return self.__threshold

    @threshold.setter
    def threshold(self, value: int) -> None:
        self.__threshold = value

    @property
    def screenshot(self) -> str:
        return self.__screenshot

    @screenshot.setter
    def screenshot(self, value: str) -> None:
        self.__screenshot = value

    @property
    def subCheckPoints(self) -> list:
        return self.__subCheckPoints

    @subCheckPoints.setter
    def subCheckPoints(self, value: list):
        self.__subCheckPoints = value

    def to_json_dict(self) -> dict:
        _dict = {
            "message": self.message,
            "type": self.type,
            "duration": self.duration,
            "threshold": self.threshold,
            "screenshot": self.screenshot,
            "subCheckPoints": self.subCheckPoints,
        }
        return _dict
