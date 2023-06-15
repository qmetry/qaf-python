# -*- coding: utf-8 -*-
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

# @Author: Chirag Jayswal
# module settings
__version__ = '1.0.0'
__all__ = [
    'get_testdata',
]

import json
import re

from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from qaf.automation.util import csv_util


def get_testdata(dataprovider: dict, params: dict):
    dataprovider = {k.upper(): v for k, v in dataprovider.items()}
    # TODO: validate data provider
    if "DATAFILE" in dataprovider or "_DATAFILE" in dataprovider:
        datafile = CM.get_bundle().resolve(dataprovider.get("DATAFILE",dataprovider.get("_DATAFILE")), params)
        if re.search(r'(?i)\.csv$|\.txt$', datafile):
            _testdata = csv_util.get_csvdata_as_map(datafile)
        elif datafile.lower().endswith(".json"):
            with open(datafile) as f:
                _testdata = json.load(f)
        else:
            raise NotImplemented
    elif "SQLQUERY" in dataprovider:
        raise NotImplemented
    else:
        raise ValueError
    testdata = _process(dataprovider,params, _testdata)
    return testdata


def _process(dataprovider: dict, params: dict, testdata):
    # FILTER, FROM, TO, INDICES
    if "FROM" in dataprovider or "TO" in dataprovider:
        _from = _toInt(dataprovider.get("FROM"), 1)
        to = _toInt(dataprovider.get("TO"))
        return testdata[_from:to]
    if "INDICES" in dataprovider:
        return [testdata[index] for index in dataprovider.get("INDICES")]
    if "FILTER" in dataprovider:
        _filter = CM.get_bundle().resolve(dataprovider.get("FILTER"), params)
        return list(filter(lambda rec: eval(_filter,None, rec), testdata))
    return testdata


def _toInt(val, base=0):
    return int(val)-base if val else None
