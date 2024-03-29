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

import inspect
from enum import Enum

import six

from qaf.automation.core.test_base import get_test_context


def del_all_attr(obj):
    for name in inspect.getmembers(obj):
        if not name[0].startswith('_') and not inspect.ismethod(name[1]):
            delattr(obj, name[0])


class PyTestStatus(Enum):
    untested = 0
    skipped = 1
    passed = 2
    failed = 3
    undefined = 4
    executing = 5

    def __eq__(self, other):
        if isinstance(other, six.string_types):
            return self.name == other
        return super(PyTestStatus, self).__eq__(other)

    @classmethod
    def from_name(cls, name):
        enum_value = cls.__members__.get(name, None)
        if enum_value is None:
            known_names = ", ".join(cls.__members__.keys())
            raise LookupError("%s (expected: %s)" % (name, known_names))
        return enum_value


def get_all_metadata(node):
    if hasattr(node, "metadata"):
        return node.metadata
    markers = node.parent.own_markers if hasattr(node.parent, "own_markers") else []
    if hasattr(node, "own_markers"):
        markers.extend(node.own_markers)
    node.metadata = get_metadata(markers)
    return node.metadata


def add_metadata(**kwargs):
    """
    add metadata to current testcase at runtime. Useful to link cloud session, video etc...
    """
    node = get_test_context()
    if node is not None:
        get_all_metadata(node).update(**kwargs)


def get_metadata(markers):
    metadata = {"groups": []}
    for marker in markers:
        if marker.name.lower() == "dataprovider":
            metadata.update(get_dp(marker))
        elif marker.args or marker.kwargs:
            metadata.update(marker.kwargs)
            if marker.args:
                if marker.name.lower() == "groups":
                    metadata["groups"] += list(marker.args)
                else:
                    metadata.update({marker.name: marker.args})
        else:
            metadata["groups"].append(marker.name)
    return metadata


def get_dp(marker):
    return {"_dataFile": marker.args[0]} | marker.kwargs if marker.args else marker.kwargs
