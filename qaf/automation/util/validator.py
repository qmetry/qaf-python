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
