import re
from copy import deepcopy

from qaf.automation.bdd2.bdd_keywords import *
from qaf.automation.core.qaf_exceptions import ParseError
from qaf.automation.util.csv_util import get_list_of_map

"""
@author: Chirag Jayswal
"""


def _parsTags(line, metadata):
    for tag in line.split("@"):
        tag = tag.strip()
        if ":" in tag:
            k, v = tag.split(":", 1)
            metadata.update({k: v})
        elif tag != "":
            if GROUPS in metadata and tag not in metadata[GROUPS]:
                metadata[GROUPS].append(tag)
            else:
                metadata[GROUPS] = [tag]


def parse(path):
    from qaf.automation.bdd2.bdd2test_factory import BDD2Scenario

    scenarios = []
    feature = None
    cur_scenario = BDD2Scenario(name="", line_number=0)
    data_table = None
    example_table = None

    with open(path) as f:
        mylist = [line.strip('\n') for line in f]

    for line_number, line in enumerate(mylist, start=1):
        stmt = line.strip()
        if not (stmt == "" or stmt[0] in COMMENT_CHARS):
            type = _getType(stmt)
            if type == "":
                if _is_step(stmt):
                    if data_table:
                        # append to last step
                        _set_data_table(cur_scenario, None, data_table)
                        data_table = None
                    cur_scenario.add_step(name=stmt, line_number=line_number)
                elif stmt[0] == "|" == stmt[-1]:
                    colcnt = len(re.findall(r'(\s+)?\|(\s+)?', stmt))
                    datarow = re.sub(r'(\s+)?\|(\s+)?', "|", stmt[1:-1])  # to csv
                    if example_table is not None:
                        if len(example_table)>0 :
                            if headercnt != colcnt:
                                raise ParseError(f"Column count mismatch in data table {path}@{line_number}")
                        else:
                            headercnt = colcnt
                        example_table.append(datarow)
                    elif data_table:
                        if headercnt != colcnt:
                            raise Exception(f"col count mismatch {path}@{line_number}",code=None)
                        data_table.append(datarow)
                    else:
                        headercnt = colcnt
                        data_table = [datarow]
                else:
                    raise ParseError(f'bdd parsing error in {path}@{line_number}')
            elif type == TAG:
                _set_data_table(cur_scenario, example_table, data_table)
                data_table = None  # reset
                example_table = None  # reset
                # start tarcking tags
                if cur_scenario is None or cur_scenario.name != "":  # tags can be multiline
                    cur_scenario = BDD2Scenario(name="", line_number=0,
                                                metadata=deepcopy(feature.metadata), file=str(path))
                _parsTags(stmt, cur_scenario.metadata)
            elif FEATURE.lower() == type.lower():
                cur_scenario.line_number = line_number
                cur_scenario.name = stmt.split(":", 1)[1].strip()
                cur_scenario.metadata.update({"feature": cur_scenario.name})
                feature = cur_scenario
            elif SCENARIO.lower() in type.lower() or BACKGROUND.lower() == type.lower():
                _set_data_table(cur_scenario, example_table, data_table)
                data_table = None  # reset
                example_table = None  # reset
                if cur_scenario.name != "":  # no tags create new and set current
                    cur_scenario = BDD2Scenario(name=stmt.split(":", 1)[1].strip(), line_number=line_number,
                                                metadata=deepcopy(feature.metadata), file=str(path))
                else:  # tags collected update name and location
                    cur_scenario.line_number = line_number
                    cur_scenario.name = stmt.split(":", 1)[1].strip()

                if BACKGROUND.lower() == type.lower():
                    feature.background = cur_scenario
                else:  # add scenario
                    cur_scenario.background = feature.background
                    scenarios.append(cur_scenario)
            elif EXAMPLES.lower() == type.lower():
                _set_data_table(cur_scenario, None, data_table)
                data_table = None  # reset
                example_table = []

    _set_data_table(cur_scenario, example_table, data_table)
    return scenarios


def _set_data_table(cur_scenario, example_table, data_table):
    if example_table:
        cur_scenario.metadata.update({"JSON_DATA_TABLE": _to_list(example_table)})
    if data_table:
        cur_scenario.steps[-1] = cur_scenario.steps[-1] + _to_list(data_table)


def _to_list(table_data):
    return get_list_of_map(table_data, '|')


def _getType(line):
    if line.endswith(MULTI_LINE_COMMENT):
        return MULTI_LINE_COMMENT_END

    match = re.match(
        "|".join([TAG, SCENARIO_OUTELINE, SCENARIO, STEP_DEF, EXAMPLES, FEATURE, BACKGROUND, MULTI_LINE_COMMENT])
        , line,
        re.I)
    return match.group() if match else ""

def _is_step(line):
    match = re.match(
        "|".join(STEP_TYPES)
        , line,
        re.I)
    return True if match else False
