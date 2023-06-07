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
class StatusCounter(object):
    """
    @author: Chirag Jayswal
    """
    def __init__(self, name):
        self.file = name
        self._pass = 0
        self._fail = 0
        self._skip = 0
        self.name = name

    def with_file(self, file_name):
        self.file = file_name
        return self

    def add(self, status):
        if "pass" in status.lower():
            self._pass += 1
        elif "fail" in status.lower():
            self._fail += 1
        else:
            self._skip += 1

    def get_pass(self):
        return self._pass

    def get_fail(self):
        return self._fail

    def get_skip(self):
        return self._skip

    def get_total(self):
        return self._pass + self._fail + self._skip

    def get_status(self):
        return "pass" if self.get_total() == self._pass else "fail"

    def get_pass_rate(self):
        return self._pass * 100 / (self._pass + self._fail + self._skip) if self._pass > 0 else 0

    def reset(self, staus):
        if "pass" in staus:
            self._pass = staus["pass"]
            self._skip = staus["skip"]
            self._fail = staus["fail"]