from enum import Enum
import six
import inspect


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
