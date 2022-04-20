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

import json
import os

from qaf.automation.formatter.qaf_report.step.checkpoint import CheckPoint


class Scenario:
    def __init__(self, file_name: str) -> None:
        path_to_write = os.getenv('CURRENT_SCENARIO_DIR')
        self.__scenario_file_path = os.path.join(path_to_write, file_name + '.json')

        if os.path.exists(self.__scenario_file_path):
            with open(self.__scenario_file_path) as f:
                _dict = json.load(f)

            self.seleniumLog = _dict['seleniumLog']
            self.__checkPoints = _dict['checkPoints']
            self.errorTrace = _dict['errorTrace']
        else:
            self.seleniumLog = []
            self.__checkPoints = []
            self.errorTrace = ''

    @property
    def seleniumLog(self) -> list:
        return self.__seleniumLog

    @seleniumLog.setter
    def seleniumLog(self, value: list) -> None:
        self.__seleniumLog = value
        self.__dump_to_json()

    @property
    def checkPoints(self) -> list:
        return self.__checkPoints

    def add_checkPoints(self, value: CheckPoint) -> None:
        self.__checkPoints.append(value.to_json_dict())
        self.__dump_to_json()

    @property
    def errorTrace(self) -> str:
        return self.__errorTrace

    @errorTrace.setter
    def errorTrace(self, value: str) -> None:
        self.__errorTrace = "\n".join(value) if isinstance(value, list) else value
        self.__dump_to_json()

    def __dump_to_json(self) -> None:
        try:
            _dict = {
                "seleniumLog": self.seleniumLog,
                "checkPoints": self.checkPoints,
                "errorTrace": self.errorTrace,
            }
            with open(self.__scenario_file_path, 'w') as fp:
                json.dump(_dict, fp, sort_keys=True, indent=4)
        except:
            pass
