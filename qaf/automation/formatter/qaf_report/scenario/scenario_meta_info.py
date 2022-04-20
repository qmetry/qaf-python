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

import json
import os

from typing import Union

from qaf.automation.formatter.qaf_report.util.utils import scenario_status


class ScenarioMetaInfo:
    def __init__(self) -> None:
        path_to_write = os.getenv('CURRENT_SCENARIO_DIR')
        self.__meta_info_file_path = os.path.join(path_to_write, 'meta-info.json')

        self.index = 1
        self.type = 'test'
        self.__args = []
        self.metaData = {}
        self.dependsOn = []
        self.startTime = 0
        self.duration = 0
        self.result = ''
        self.passPer = 0.0

    @property
    def index(self) -> int:
        return self.__index

    @index.setter
    def index(self, value: int) -> None:
        self.__index = value

    @property
    def type(self) -> str:
        return self.__type

    @type.setter
    def type(self, value: str) -> None:
        self.__type = value

    @property
    def args(self) -> list:
        return self.__args

    def add_args(self, arg: str) -> None:
        self.__args.append(arg)

    @property
    def metaData(self) -> dict:
        return self.__metaData

    @metaData.setter
    def metaData(self, value: dict) -> None:
        self.__metaData = value

    @property
    def dependsOn(self) -> list:
        return self.__dependsOn

    @dependsOn.setter
    def dependsOn(self, value: list) -> None:
        self.__dependsOn = value

    @property
    def startTime(self) -> None:
        return self.__startTime

    @startTime.setter
    def startTime(self, value) -> None:
        self.__startTime = value

    @property
    def duration(self) -> int:
        return self.__duration

    @duration.setter
    def duration(self, value: Union[int, str]) -> None:
        self.__duration = int(value)

    @property
    def result(self) -> str:
        return self.__result

    @result.setter
    def result(self, value: str) -> None:
        self.__result = scenario_status(value)

    @property
    def passPer(self) -> float:
        return self.__passPer

    @passPer.setter
    def passPer(self, value: float) -> None:
        self.__passPer = value

    def __dump_into_json(self) -> None:
        _dict = {
            "index": self.index,
            "type": self.type,
            "args": self.args,
            "metaData": self.metaData,
            "dependsOn": self.dependsOn,
            "startTime": self.startTime,
            "duration": self.duration,
            "result": self.result,
            "passPer": self.passPer
        }

        if os.path.exists(self.__meta_info_file_path):
            with open(self.__meta_info_file_path, "r") as jsonFile:
                data = json.load(jsonFile)
                methods = data['methods']
        else:
            methods = []
        methods.append(_dict)
        final_data = {'methods': methods}

        with open(self.__meta_info_file_path, 'w') as fp:
            json.dump(final_data, fp, sort_keys=True, indent=4)

    def close(self) -> None:
        try:
            self.__dump_into_json()
        except:
            pass


class MetaData:
    def __init__(self) -> None:
        self.description = ''
        self.groups = []
        self.lineNo = 0
        self.name = ''
        self.referece = ''
        self.sign = ''
        self.resultFileName = ''

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        self.__description = value

    @property
    def resultFileName(self) -> str:
        return self.__resultFileName

    @resultFileName.setter
    def resultFileName(self, value: str) -> None:
        self.__resultFileName = value

    @property
    def groups(self) -> list:
        return self.__groups

    @groups.setter
    def groups(self, value: list) -> None:
        self.__groups = value

    @property
    def lineNo(self) -> int:
        return self.__lineNo

    @lineNo.setter
    def lineNo(self, value: int) -> None:
        self.__lineNo = value

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    @property
    def referece(self) -> str:
        return self.__referece

    @referece.setter
    def referece(self, value: str) -> None:
        self.__referece = value

    @property
    def sign(self) -> str:
        return self.__sign

    @sign.setter
    def sign(self, value: str) -> None:
        self.__sign = value

    def to_json_dict(self) -> dict:
        _dict = {
            "description": self.description,
            "groups": self.groups,
            "lineNo": self.lineNo,
            "name": self.name,
            "referece": self.referece,
            "resultFileName": self.resultFileName,
            "sign": self.sign
        }
        return _dict