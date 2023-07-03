from typing import List, Iterator
from typing import Union

import pytest
from _pytest import nodes, fixtures
from simpleeval import NameNotDefined, EvalWithCompoundTypes

from qaf.automation.bdd2.model import Bdd2Scenario, Bdd2Background
from qaf.automation.bdd2.parser import parse
from qaf.pytest import metadata, OPT_METADATA_FILTER, OPT_DRYRUN

"""
@author: Chirag Jayswal
"""


def update_item(items: list, background_names: list, scenario):
    for item in items:
        item.fixturenames.extend(background_names)
        scenario.node = item
        for marker in item.own_markers:
            groups = marker.kwargs.pop("groups") if "groups" in marker.kwargs else []
            for group in groups:
                item.add_marker(group)


def should_include(expr, scenario):
    if not expr:
        return True
    try:
        evaluator = EvalWithCompoundTypes(names=scenario.metadata)
        return evaluator.eval(expr)
    except NameNotDefined:
        False


def get_test_func(scenario: Bdd2Scenario):
    if scenario.has_dataprovider:
        @metadata(**scenario.metadata)
        def test_secario(testdata):
            return scenario.execute(testdata)

        return test_secario
    else:
        @metadata(**scenario.metadata)
        def test_secario():
            return scenario.execute()

        return test_secario


def get_background_func(bdd2background: Bdd2Background):
    allowed_scopes = {"scenario": "function", "feature": "module"}
    scope = allowed_scopes[bdd2background.metadata.get("scope", "scenario").lower()]

    @fixtures.fixture(scope=scope, name=f"{bdd2background.id}")
    @actualName(bdd2background.name or bdd2background.id)
    def background():
        if bdd2background.parent.exception:
            raise bdd2background.parent.exception
        try:
            return bdd2background.execute()
        except BaseException as e:
            if scope == "module":
                bdd2background.parent.exception = e
            pytest.skip(f'Precondition "{bdd2background.name}" failed!')

    # background.__name__ = bdd2background.name
    return background


def actualName(newname):
    def decorator(f):
        f.__name__ = newname
        return f
    return decorator


class BDD2File(pytest.Module):
    def collect(self):
        # self.add_marker("metadata")
        values: List[Union[nodes.Item, nodes.Collector]] = []
        self.feature = parse(self.path)
        self.feature.node = self
        self.is_dryrun_mode = self.config.getoption(OPT_DRYRUN)
        meta_filter = self.config.getoption(OPT_METADATA_FILTER, "")

        dict_values: List[List[Union[nodes.Item, nodes.Collector]]] = []
        self.obj = self

        background_names = []
        for index, background in enumerate(self.feature.backgrounds):
            background.is_dryrun_mode = self.is_dryrun_mode
            name = background.name or index
            background.id = f'Background:{self.feature.name}-{name}'
            fun = get_background_func(background)
            setattr(self, background.name, fun)
            background_names.append(background.id)

        self.session._fixturemanager.parsefactories(self, self.nodeid)

        for scenario in self.feature.scenarios:
            # apply filter when collecting
            if not should_include(meta_filter, scenario):
                continue

            scenario.is_dryrun_mode = self.is_dryrun_mode
            fun = get_test_func(scenario)
            setattr(self, scenario.name, fun)

            res = self.ihook.pytest_pycollect_makeitem(
                collector=self, name=scenario.name, obj=fun
            )
            if res is None:
                continue
            elif isinstance(res, list):
                update_item(res, background_names, scenario)
                values.extend(res)
            else:
                update_item([res], background_names, scenario)
                values.append(res)
        dict_values.append(values)
        # Between classes in the class hierarchy, reverse-MRO order -- nodes
        # inherited from base classes should come before subclasses.
        result = []
        for values in reversed(dict_values):
            result.extend(values)
        return result

    def istestfunction(self, obj: object, name: str) -> bool:
        return True

    def _genfunctions(self, name: str, funcobj) -> Iterator["Function"]:
        return super()._genfunctions(name, funcobj)
