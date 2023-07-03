import re
from dataclasses import dataclass, field
from typing import List
from typing import Union

import pytest
from _pytest import nodes
from simpleeval import NameNotDefined, EvalWithCompoundTypes

from qaf.automation.bdd2.bdd2parser import parse
from qaf.automation.bdd2.bdd_keywords import STEP_TYPES
from qaf.pytest import metadata, OPT_METADATA_FILTER, OPT_DRYRUN

"""
@author: Chirag Jayswal
"""


# load_step_modules()
@dataclass
class Bdd2Step:
    name: str
    scenario: object = None
    line_number: int = 0
    keyword: str = ""

    def __init__(self, name: str, line_number: int = 0, scenario=None) -> None:
        self.name = name
        self.line_number = line_number
        self.scenario = scenario

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        match = re.match(
            "|".join(STEP_TYPES)
            , value,
            re.I)
        self.keyword = match.group() if match else ""
        self._name = value.replace(self.keyword, "").strip()

    def __str__(self):
        return self.keyword + ' ' + self.name


@dataclass
class BDD2Scenario:
    name: str
    line_number: int
    steps: list[Bdd2Step] = field(default_factory=list)
    metadata: dict[str] = field(default_factory=dict)
    testdata: dict[str] = field(default_factory=dict)
    description: list[str] = field(default_factory=list)
    background = None
    is_dryrun_mode: bool = False
    exception = None
    file: str = ""

    @property
    def has_dataprovider(self):
        return "JSON_DATA_TABLE" in self.metadata or "datafile" in self.metadata

    def add_step(self, name, line_number):
        self.steps.append(Bdd2Step(name=name, line_number=line_number, scenario=self))

    def get_test_func(self):
        from qaf.automation.bdd2.bddstep_executor import execute_step
        if self.has_dataprovider:
            @metadata(**self.metadata)
            def test_secario(testdata):
                for bdd_step in self.steps.copy():
                    try:
                        execute_step(bdd_step, testdata, self.is_dryrun_mode, self.exception is not None)
                    except BaseException or Exception as e:
                        self.exception = e
                if self.exception:
                    raise self.exception

            return test_secario
        else:
            @metadata(**self.metadata)
            def test_secario():
                for bdd_step in self.steps.copy():
                    try:
                        execute_step(bdd_step, {}, self.is_dryrun_mode, self.exception is not None)
                    except BaseException or Exception as e:
                        self.exception = e
                if self.exception:
                    raise self.exception

            return test_secario


def update_item(items: list, scenario):
    for item in items:
        item.scenario = scenario
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


class BDD2File(pytest.Module):
    def collect(self):
        #self.add_marker("metadata")
        values: List[Union[nodes.Item, nodes.Collector]] = []
        scenarios = parse(self.path)

        is_dryrun_mode = self.config.getoption(OPT_DRYRUN)
        meta_filter = self.config.getoption(OPT_METADATA_FILTER, "")
        dict_values: List[List[Union[nodes.Item, nodes.Collector]]] = []
        self.obj = self
        for scenario in scenarios:
            # apply filter when collecting
            if not should_include(meta_filter, scenario):
                continue

            #self.obj = scenario
            scenario.is_dryrun_mode = is_dryrun_mode
            fun = scenario.get_test_func()
            #setattr(scenario, scenario.name, fun)
            setattr(self, scenario.name, fun)

            res = self.ihook.pytest_pycollect_makeitem(
                collector=self, name=scenario.name, obj=fun
            )
            if res is None:
                continue
            elif isinstance(res, list):
                update_item(res,scenario)
                values.extend(res)
            else:
                update_item([res],scenario)
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
