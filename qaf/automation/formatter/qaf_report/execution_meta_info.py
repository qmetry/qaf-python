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


class ExecutionMetaInfo:
    def __init__(self) -> None:
        path_to_write = os.path.join(os.getenv('REPORT_DIR'), 'json')
        self.__meta_info_file_path = os.path.join(path_to_write, 'meta-info.json')

        if os.path.exists(self.__meta_info_file_path):
            with open(self.__meta_info_file_path) as f:
                _dict = json.load(f)

            self.name = str(_dict['name'])
            self.status = str(_dict['status'])
            self.__tests = _dict['tests']
            self.total_count = int(_dict['total'])
            self.pass_count = int(_dict['pass'])
            self.fail_count = int(_dict['fail'])
            self.skip_count = int(_dict['skip'])
            self.startTime = _dict['startTime']
            self.endTime = _dict['endTime']

        else:
            self.name = ''
            self.status = ''
            self.__tests = []
            self.total_count = 0
            self.pass_count = 0
            self.fail_count = 0
            self.skip_count = 0
            self.startTime = ''
            self.endTime = ''

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value

    @property
    def status(self) -> str:
        return self.__status

    @status.setter
    def status(self, value: str) -> None:
        self.__status = value

    @property
    def tests(self) -> list:
        return self.__tests

    def add_test(self, test_name: str) -> None:
        self.__tests.append(test_name)
        self._close()

    @property
    def total_count(self) -> int:
        return self.__total_count

    @total_count.setter
    def total_count(self, value: int) -> None:
        self.__total_count = value

    @property
    def pass_count(self) -> int:
        return self.__pass_count

    @pass_count.setter
    def pass_count(self, value: int) -> None:
        self.__pass_count = value

    @property
    def fail_count(self) -> int:
        return self.__fail_count

    @fail_count.setter
    def fail_count(self, value: int) -> None:
        self.__fail_count = value

    @property
    def skip_count(self) -> int:
        return self.__skip_count

    @skip_count.setter
    def skip_count(self, value: int) -> None:
        self.__skip_count = value

    @property
    def startTime(self) -> str:
        return self.__startTime

    @startTime.setter
    def startTime(self, value: str) -> None:
        self.__startTime = value
        self._close()

    @property
    def endTime(self) -> str:
        return self.__endTime

    @endTime.setter
    def endTime(self, value: str) -> None:
        self.__endTime = value
        self._close()

    def _close(self) -> None:
        self.__dump_into_json()

    def __dump_into_json(self) -> None:
        try:
            _dict = {
                "name": self.name,
                "status": self.status,
                "tests": self.tests,
                "total": self.total_count,
                "pass": self.pass_count,
                "fail": self.fail_count,
                "skip": self.skip_count,
                "startTime": self.startTime,
                "endTime": self.endTime
            }
            with open(self.__meta_info_file_path, 'w') as fp:
                json.dump(_dict, fp, sort_keys=True, indent=4)
        except:
            pass

    def update_status(self, scenario_status: str) -> None:
        if scenario_status.lower() == 'passed':
            self.pass_count += 1
        elif scenario_status.lower() == 'failed':
            self.fail_count += 1
        else:
            self.skip_count += 1

        self.total_count += 1

        if self.fail_count > 0:
            self.status = 'fail'
        else:
            self.status = 'pass'

        self._close()
