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
