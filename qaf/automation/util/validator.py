from hamcrest.core.matcher import Matcher
from hamcrest.core.string_description import StringDescription

from qaf.automation.core.message_type import MessageType
from qaf.automation.core.reporter import Reporter


class Validator:

    @staticmethod
    def verify_that(arg1, matcher=None, reason=''):
        if isinstance(matcher, Matcher):
            return Validator._assert_match(actual=arg1, matcher=matcher, reason=reason)
        else:
            return Validator._assert_bool(assertion=arg1, reason=matcher)

    @staticmethod
    def assert_that(arg1, matcher=None, reason=''):
        if not Validator.verify_that(arg1=arg1, matcher=matcher, reason=reason):
            raise AssertionError

    @staticmethod
    def _assert_match(actual, matcher, reason):
        description = StringDescription()
        description.append_text(reason) \
            .append_text('\nExpected: ') \
            .append_description_of(matcher) \
            .append_text('\n     Actual: ')
        matcher.describe_mismatch(actual, description)
        description.append_text('\n')

        if not matcher.matches(actual):
            Reporter.log(str(description), MessageType.Fail)
            return False
        else:
            Reporter.log(str(description), MessageType.Pass)
            return True

    @staticmethod
    def _assert_bool(assertion, reason=None):
        if not assertion:
            if not reason:
                Reporter.log("Assertion failed", MessageType.Fail)
            return False
        return True
