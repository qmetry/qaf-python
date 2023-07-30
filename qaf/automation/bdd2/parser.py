import re
from copy import deepcopy
from dataclasses import field, dataclass
from typing import TypeVar

from qaf.automation.bdd2.bdd_keywords import *
from qaf.automation.bdd2.bdd_keywords import TAG, SCENARIO_OUTLINE
from qaf.automation.bdd2.model import SupportsBdd2DataTable, Bdd2Scenario, Bdd2Background, Bdd2Examples, \
    Bdd2MultiLineComment, Bdd2Feature, Bdd2Step, Bdd2StepDefinition, Bdd2StepCollection
from qaf.automation.bdd2.qaf_teststep import QAFTestStep
from qaf.automation.core import get_bundle
from qaf.automation.core.qaf_exceptions import ParseError

BDD2StatementCollector = TypeVar("BDD2StatementCollector", bound="BDD2StatementCollector")


@dataclass
class BDD2StatementCollector:
    parent: BDD2StatementCollector

    def collect(self, stmt: str, line_no: int, _type: str) -> BDD2StatementCollector:
        pass


@dataclass
class BDD2MetadataCollector(BDD2StatementCollector):
    metadata: dict = field(default_factory=dict)

    def matches(self, target, default=True):
        if not self.metadata: return default
        for k, v in self.metadata:
            v != target.get(k)
            return False
        return True

    def collect(self, stmt: str, line_no: int, _type: str) -> BDD2StatementCollector:
        if TAG != _type:
            return self.parent.collect(stmt, line_no, _type)
        for tag in stmt.split("@"):
            tag = tag.strip()
            if ":" in tag:
                k, v = tag.split(":", 1)
                self.metadata.update({k: v})
            elif tag != "":
                if GROUPS in self.metadata and tag not in self.metadata[GROUPS]:
                    self.metadata[GROUPS].append(tag)
                else:
                    self.metadata[GROUPS] = [tag]
        return self


@dataclass
class BDD2DataTableCollector(BDD2StatementCollector):
    node: SupportsBdd2DataTable

    def collect(self, stmt: str, line_no: int, _type: str) -> BDD2StatementCollector:
        if stmt[0] == "|":
            self.node.add_data_row(stmt)
            return self
        if _type == MULTI_LINE_COMMENT:
            comment = Bdd2MultiLineComment(parent=self.node, name=stmt, lineNo=line_no)
            return BDD2MultilineCommentCollector(comment, parent=self)
        try:
            return self.parent.collect(stmt, line_no, _type)
        except:
            raise ParseError(f"Not supported statement in datatable @{line_no}")


@dataclass
class BDD2MultilineCommentCollector(BDD2StatementCollector):
    comment = Bdd2MultiLineComment

    def collect(self, stmt: str, line_no: int, _type: str) -> BDD2StatementCollector:
        self.comment.name = f'{self.comment.name}\n{stmt}'
        return self.parent if _type == MULTI_LINE_COMMENT_END or _type == MULTI_LINE_COMMENT else self


@dataclass
class BDD2ScenarioCollector(BDD2StatementCollector):
    scenario: Bdd2StepCollection

    def collect(self, stmt: str, line_no: int, _type: str) -> BDD2StatementCollector:
        if not _type and _is_step(stmt): #set parent at the time of execution to clone to avoid deepcopy cycling
            self.scenario.steps.append(Bdd2Step(name=stmt, lineNo=line_no, parent=None))
            return self
        if EXAMPLES.lower() == _type.lower():
            if type(self.scenario) == Bdd2Background or type(self.scenario) == Bdd2StepDefinition:
                raise ParseError("Examples not allowed with background or step definition.")
            self.scenario.examples = Bdd2Examples(lineNo=line_no, parent=self.scenario)
            return BDD2DataTableCollector(node=self.scenario.examples,
                                          parent=self.parent)  # after examples return to feature collector
        if stmt[0] == "|":
            step = self.scenario.steps[-1]
            return BDD2DataTableCollector(node=step, parent=self).collect(stmt, line_no, _type)
        if _type == MULTI_LINE_COMMENT:
            comment = Bdd2MultiLineComment(parent=self.scenario, name=stmt, lineNo=line_no)
            return BDD2MultilineCommentCollector(comment, parent=self)
        try:
            return self.parent.collect(stmt, line_no, _type)
        except:
            raise ParseError(f"Not supported statement for {type(self.scenario)} @{line_no}")


@dataclass
class FeatureCollector(BDD2StatementCollector):
    feature: Bdd2Feature
    _metadata_collector: BDD2MetadataCollector = None

    @property
    def metadata_collector(self):
        if self._metadata_collector is None:
            self._metadata_collector = BDD2MetadataCollector(parent=self)
        return self._metadata_collector

    def collect(self, stmt: str, line_no: int, _type: str) -> BDD2StatementCollector:
        if TAG == _type:
            return self.metadata_collector.collect(stmt, line_no, _type)
        if _type.lower() == FEATURE.lower():
            if self.feature.name != "":
                raise ParseError("Feature file can have at most one Feature.")
            self.feature.metadata = deepcopy(self.metadata_collector.metadata)
            self.metadata_collector.metadata.clear()
            self.feature.name = stmt.split(":", 1)[1].strip()
            self.feature.lineNo = line_no
            return self
        if SCENARIO.lower() in _type.lower():
            if "groups" in self.metadata_collector.metadata and "step" in self.metadata_collector.metadata["groups"]:
                _type = STEP_DEF
            else:
                scenario = Bdd2Scenario(parent=self.feature, name=stmt.split(":", 1)[1].strip(),
                                        lineNo=line_no,
                                        metadata=deepcopy(self.feature.metadata) | deepcopy(
                                            self.metadata_collector.metadata))
                self.metadata_collector.metadata.clear()
                self.feature.scenarios.append(scenario)
                return BDD2ScenarioCollector(parent=self, scenario=scenario)
        if STEP_DEF.lower() == _type.lower():
            step_def = Bdd2StepDefinition(parent=self.feature, name=stmt.split(":", 1)[1].strip(),
                                          lineNo=line_no,
                                          metadata=deepcopy(self.feature.metadata) | deepcopy(
                                              self.metadata_collector.metadata))
            self.metadata_collector.metadata.clear()
            # self.feature.scenarios.append(scenario)
            QAFTestStep(step_def.name)(step_def)
            return BDD2ScenarioCollector(parent=self, scenario=step_def)
        if BACKGROUND.lower() == _type.lower():
            background = Bdd2Background(parent=self.feature, name=stmt.split(":", 1)[1].strip(),
                                        lineNo=line_no)
            if "global" != self.metadata_collector.metadata.get("scope", "").lower():
                background.metadata = deepcopy(self.metadata_collector.metadata)
            else:
                background.metadata = deepcopy(self.feature.metadata) | deepcopy(
                    self.metadata_collector.metadata)
            self.metadata_collector.metadata.clear()
            self.feature.backgrounds.append(background)
            return BDD2ScenarioCollector(self, background)
        if EXAMPLES.lower() == _type.lower():
            scenario = self.feature.scenarios[-1]
            examples = Bdd2Examples(parent=scenario, lineNo=line_no)
            if len(self.metadata_collector.metadata) == 0 and scenario.examples is not None:
                raise ParseError(f"Unexpected Examples @{line_no}")
            elif scenario.examples is not None and self.metadata_collector.matches(target=get_bundle()):
                # env specific matched
                scenario.examples = examples
            self.metadata_collector.metadata.clear()
            return BDD2DataTableCollector(node=examples, parent=self)
        if _type == MULTI_LINE_COMMENT:
            comment = Bdd2MultiLineComment(parent=self.feature, name=stmt, lineNo=line_no)
            return BDD2MultilineCommentCollector(comment, parent=self).collect(stmt, line_no, _type)
        return ParseError(f"Unsupported statement @{line_no}")


def parse(path):
    feature = Bdd2Feature(path=path)
    with open(path) as fp:
        collector = FeatureCollector(None, feature=feature)
        for line_number, line in enumerate(fp):
            try:
                stmt = line.strip()
                if stmt == "" or stmt[0] in COMMENT_CHARS: continue
                _type: str = _getType(stmt)
                collector = collector.collect(stmt, line_number, _type)
            except ParseError as e:
                raise ParseError(f'bdd parsing error: {str(e)} in {path}@{line_number}')
    return feature


def _getType(line):
    if line.endswith(MULTI_LINE_COMMENT) and len(set(line)) > 1:  # contains other than comment char
        return MULTI_LINE_COMMENT_END
    match = re.match(
        "|".join([TAG, SCENARIO_OUTLINE, SCENARIO, STEP_DEF, EXAMPLES, FEATURE, BACKGROUND, MULTI_LINE_COMMENT])
        , line,
        re.I)
    return match.group() if match else ""


def _is_step(line):
    match = re.match("|".join(STEP_TYPES), line, re.I)
    return True if match else False
