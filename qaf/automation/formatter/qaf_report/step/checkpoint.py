#  Copyright (c) .2022 Infostretch Corporation
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
