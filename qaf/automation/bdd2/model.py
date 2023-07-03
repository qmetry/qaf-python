import re
from dataclasses import field, dataclass
from typing import TypeVar

from qaf.automation.bdd2.bdd_keywords import *
from qaf.automation.bdd2.bddstep_executor import execute_step
from qaf.automation.core.qaf_exceptions import ParseError
from qaf.automation.util.csv_util import get_list_of_map

Bdd2Node = TypeVar("Bdd2Node", bound="Bdd2Node")
T = TypeVar('T')


@dataclass
class Bdd2Node:
    name: str = ""
    lineNo: int = 0
    parent: Bdd2Node = None
    exception = None


@dataclass
class SupportsBdd2DataTable:
    _data_rows: list[str] = field(default_factory=list)
    header_cnt: int = 0

    def add_data_row(self, row: str):
        col_cnt = len(re.findall(r'(\s+)?\|(\s+)?', row))
        data_row = re.sub(r'(\s+)?\|(\s+)?', "|", row[1:-1])  # to csv
        if self.header_cnt > 0:
            if self.header_cnt != col_cnt:
                raise ParseError(f"col count mismatch in data table")
            self._data_rows.append(data_row)
        else:
            self.header_cnt = col_cnt
            self._data_rows = [data_row]

    @property
    def data_table(self):
        return get_list_of_map(self._data_rows, '|') if self._data_rows else None


@dataclass
class SupportsBdd2Metadata:
    metadata: dict = field(default_factory=dict)


@dataclass
class Bdd2MultiLineComment(Bdd2Node): ...


@dataclass
class Bdd2Examples(Bdd2Node, SupportsBdd2DataTable, SupportsBdd2Metadata): ...


@dataclass
class Bdd2Step(Bdd2Node, SupportsBdd2DataTable):
    @property
    def name(self):
        if self.data_table:
            return f'{self._name} {self.data_table}'
        return self._name

    @property
    def keyword(self):
        return self._keyword

    @property
    def display_name(self):
        return self._displayName

    @name.setter
    def name(self, value):
        self._displayName = value
        match = re.match("|".join(STEP_TYPES), value, re.I)
        self._keyword = match.group() if match else ""
        self._name = value.replace(self.keyword, "").strip()

    def execute(self, testdata={}, is_dryrun_mode: bool = False, should_skip=False):
        return execute_step(self, testdata, is_dryrun_mode, should_skip)

    def __deepcopy__(self, memo):
        # Exclude the parent reference during deepcopy
        new_obj = type(self)(name=self.display_name, lineNo=self.lineNo, data_table=self.data_table)
        memo[id(self)] = new_obj
        # new_obj.parent=self.parent
        return new_obj


@dataclass
class Bdd2StepCollection(Bdd2Node):
    steps: list[Bdd2Step] = field(default_factory=list)
    is_dryrun_mode: bool = False
    supports_background = False

    def execute(self, testdata={}):
        self.exception = None
        steps = self.steps.copy()
        for bdd_step in steps:
            try:
                execute_step(bdd_step, testdata, self.is_dryrun_mode, self.exception is not None)
            except BaseException or Exception as e:
                self.exception = e
        if self.exception:
            raise self.exception
        if isinstance(self, Bdd2Background): return steps


@dataclass
class Bdd2Scenario(Bdd2StepCollection, SupportsBdd2Metadata):
    examples: Bdd2Examples = None

    @property
    def has_dataprovider(self):
        if self.examples:
            self.metadata.update({"JSON_DATA_TABLE": self.examples.data_table})
            self.examples = None
        return "datafile" in self.metadata or "JSON_DATA_TABLE" in self.metadata

    @property
    def supports_background(self):
        return True


@dataclass
class Bdd2Background(Bdd2StepCollection, SupportsBdd2Metadata): ...


@dataclass
class Bdd2StepDefinition(Bdd2StepCollection, SupportsBdd2Metadata):
    def __call__(self, *args, **kwargs):
        self.execute(testdata=kwargs)


@dataclass
class Bdd2Feature(Bdd2Node, SupportsBdd2Metadata):
    backgrounds: list[Bdd2Background] = field(default_factory=list)
    scenarios: list[Bdd2Scenario] = field(default_factory=list)
