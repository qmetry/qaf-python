import time

from qaf.automation.formatter.py_test_report.pystep_decorators import pystep
from qaf.automation.formatter.py_test_report.pytest_fixture import PyTestFixture
from qaf.automation.formatter.py_test_report.pytest_utils import PyTestStatus, del_all_attr


class PyTestSession:
    @staticmethod
    def _before_session(request):
        PyTestFixture().before_session()

    @staticmethod
    def _after_session(request):
        PyTestFixture().after_session()


class PyTestClass:
    name = ''
    filename = ''

    @staticmethod
    def _before_class(request):
        del_all_attr(PyTestClass)

        PyTestClass.name = request.cls.__name__
        PyTestClass.filename = request.node.nodeid

        PyTestFixture().before_class(PyTestClass)

    @staticmethod
    def _after_class(request):
        PyTestFixture().after_class(PyTestClass)

        del_all_attr(PyTestClass)


class PyTestFunction:
    clas = ''
    name = ''
    description = ''
    location = ''
    effective_tags = []
    exception = None
    status = ''

    @staticmethod
    def _before_function(request):
        del_all_attr(PyTestFunction)
        PyTestFunction.name = request.node.name
        PyTestFunction.description = request.node.name
        PyTestFunction.location = request.node.nodeid
        PyTestFunction.effective_tags = request.node.own_markers
        PyTestFunction.clas = PyTestClass

        PyTestFixture().before_function(PyTestFunction)

        pystep(keyword='Given', name=request.node.name).before_step()

    @staticmethod
    def _after_function(request):
        PyTestFunction.duration = request.node.rep_call.duration
        if request.node.rep_setup.failed:
            PyTestFunction.status = PyTestStatus.failed.name
            PyTestFunction.exception = request.node.rep_setup.longreprtext
        else:
            PyTestFunction.status = PyTestStatus.from_name(request.node.rep_call.outcome)
            PyTestFunction.exception = request.node.rep_call.longreprtext
        pystep().after_step(status=PyTestFunction.status.name, exception=PyTestFunction.exception)
        PyTestFixture().after_function(PyTestFunction)


class PyTestStep:
    start_time = time.time()
    name = ''
    keyword = ''
    active = False

    @staticmethod
    def _before_step(name, keyword, step):
        PyTestStep._after_step(status=PyTestStatus.passed.name, exception=None)

        PyTestStep.start_time = time.time()
        PyTestStep.name = step.__name__ if name is None else name
        PyTestStep.keyword = keyword
        PyTestStep.active = True
        PyTestFixture().before_step(PyTestStep)

    @staticmethod
    def _after_step(status, exception=None):
        if hasattr(PyTestStep, 'active') and getattr(PyTestStep, 'active'):
            PyTestStep.status = status
            PyTestStep.exception = exception
            PyTestStep.duration = time.time() - PyTestStep.start_time
            PyTestFixture().after_step(PyTestStep)
        # Delete the attributes of current step
        del_all_attr(PyTestStep)
