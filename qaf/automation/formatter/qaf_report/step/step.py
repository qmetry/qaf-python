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

import os
import uuid

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.core.message_type import MessageType
from qaf.automation.formatter.qaf_report.step.checkpoint import CheckPoint
from qaf.automation.formatter.qaf_report.step.sub_check_points import SubCheckPoints
from qaf.automation.formatter.qaf_report.util.utils import step_status, STEP_STATUS
from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.ui.webdriver import base_driver


class Step:
    def __init__(self) -> None:
        self.obj_check_point = None

    @property
    def obj_check_point(self) -> CheckPoint:
        if self.__obj_check_point is None:
            self.__obj_check_point = CheckPoint()
        return self.__obj_check_point

    @obj_check_point.deleter
    def obj_check_point(self) -> None:
        del self.__obj_check_point

    @obj_check_point.setter
    def obj_check_point(self, value: CheckPoint) -> None:
        self.__obj_check_point = value

    def start_behave_step(self, step) -> None:
        self.obj_check_point = CheckPoint()
        self.obj_check_point.message = step.keyword + ' ' + step.name

    def stop_behave_step(self, step) -> None:
        status = step_status(step)
        if 'Fail' in status and CM().get_bool_for_key(AP.FAILURE_SCREENSHOT):
            self.take_screen_shot()
        self.obj_check_point.type = status
        self.obj_check_point.subCheckPoints = SubCheckPoints().get_all_sub_check_points()
        for subCheckPoint in self.obj_check_point.subCheckPoints:
            if subCheckPoint['type'] == MessageType.Fail:
                self.obj_check_point.type = STEP_STATUS.get('failed')
                break
        self.obj_check_point.duration = step.duration * 1000

    def __del__(self) -> None:
        del self.obj_check_point
        self.obj_check_point = None

    def take_screen_shot(self) -> None:
        if base_driver.BaseDriver().has_driver():
            filename = os.path.join(os.getenv('REPORT_DIR'), 'img', str(uuid.uuid4()) + '.png')
            base_driver.BaseDriver().get_driver().save_screenshot(filename=filename)
            self.obj_check_point.screenshot = filename
