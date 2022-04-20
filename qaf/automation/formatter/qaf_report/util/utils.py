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

from enum import Enum


class Status(object):
    FAILED = 'TestStepFail'
    BROKEN = 'TestStepFail'
    PASSED = 'TestStepPass'
    SKIPPED = 'TestStepSkip'


SCENARIO_STATUS = {
    'passed': 'pass',
    'failed': 'fail',
    'skipped': 'skip',
    'untested': 'skip',
    'undefined': 'broken'
}

STEP_STATUS = {
    'passed': 'TestStepPass',
    'failed': 'TestStepFail',
    'skipped': 'TestStepSkip',
    'untested': 'TestStepSkip',
    'undefined': 'TestStepFail'
}


def scenario_status(status: str) -> str:
    return SCENARIO_STATUS.get(status)


def step_status(result) -> str:
    if result.exception:
        return get_status(result.exception)
    else:
        if isinstance(result.status, Enum):
            return STEP_STATUS.get(result.status.name, None)
        else:
            return STEP_STATUS.get(result.status, None)


def get_status(exception: Exception):
    if exception and isinstance(exception, AssertionError):
        return Status.FAILED
    elif exception:
        return Status.BROKEN
    return Status.PASSED
