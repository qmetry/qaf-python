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


class ReportsMetaInfo:
    def __init__(self, path_to_write: str) -> None:
        self.__meta_info_file_path = os.path.join(path_to_write, 'meta-info.json')

        self.name = ''
        self.dir = ''
        self.startTime = ''

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    @property
    def dir(self) -> str:
        return self.__dir

    @dir.setter
    def dir(self, value: str) -> None:
        self.__dir = value

    @property
    def startTime(self) -> str:
        return self.__startTime

    @startTime.setter
    def startTime(self, value: str) -> None:
        self.__startTime = value

    def __dump_into_json(self) -> None:
        _dict = {
            "name": self.name,
            "dir": self.dir,
            "startTime": self.startTime,
        }
        if os.path.exists(self.__meta_info_file_path):
            with open(self.__meta_info_file_path, "r") as jsonFile:
                data = json.load(jsonFile)
                reports = data['reports']
        else:
            reports = []
        reports.insert(0, _dict)
        final_data = {'reports': reports}

        with open(self.__meta_info_file_path, 'w') as fp:
            json.dump(final_data, fp, sort_keys=True, indent=4)

    def close(self) -> None:
        self.__dump_into_json()
