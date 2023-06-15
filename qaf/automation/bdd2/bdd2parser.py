import re
from typing import Match

from qaf.automation.util.csv_util import get_list_of_map

TAG: str = "@"
COMMENT_CHARS: str = "#!"
MULTI_LINE_COMMENT: str = "\"\"\""
MULTI_LINE_COMMENT_END: str = "COMMENT_END"
STEP_DEF: str = "STEP-DEF"
END: str = "END"
TEST_DATA: str = "TEST-DATA"
SCENARIO: str = "SCENARIO"
DESCRIPTION: str = "desc"
SCENARIO_OUTELINE: str = "Scenario Outline"
EXAMPLES: str = "EXAMPLES"
FEATURE: str = "Feature"
BACKGROUND: str = "Background"

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
            if "groups" in metadata:
                # metadata["groups"].add(tag)
                metadata["groups"].append(tag)
            else:
                # 'set' object has no attribute 'to_json_dict'
                # metadata["groups"] = set([tag])
                metadata["groups"] = [tag]


def parse(content):
    from qaf.automation.bdd2.bdd2test_factory import BDD2Scenario, Bdd2Step

    meta_data = {}
    scenarios = []
    feature = BDD2Scenario(name="", line_number=0)
    cur_scenario = feature
    data_table = None
    example_table = None

    with open(content) as f:
        mylist = [line.strip('\n') for line in f]

    for line_number, line in enumerate(mylist, start=1):
        stmt = line.strip()
        if not (stmt == "" or stmt[0] in COMMENT_CHARS):
            type = _getType(stmt)
            if type == "":
                if stmt[0] == "|":  # data table
                    # Todo: vaidate entry
                    datarow = re.sub(r'(\s+)?\|(\s+)?', "|", stmt.strip()[1:-1])
                    if example_table is not None:
                        example_table.append(datarow)
                    elif data_table:
                        data_table.append(datarow)
                    else:
                        data_table = [datarow]
                else:
                    if data_table:
                        # append to last step
                        _set_data_table(cur_scenario, None, data_table)
                        data_table = None
                    cur_scenario.steps.append(Bdd2Step(name=stmt, line_number=line_number))
            elif type == TAG:
                _set_data_table(cur_scenario, example_table, data_table)
                data_table = None  # reset
                example_table = None  # reset
                # start tarcking tags
                cur_scenario = BDD2Scenario(name="", line_number=0)
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
                if cur_scenario.name != "":
                    cur_scenario = BDD2Scenario(name=stmt.split(":", 1)[1].strip(), line_number=line_number)
                else:
                    cur_scenario.line_number = line_number
                    cur_scenario.name = stmt.split(":", 1)[1].strip()
                if BACKGROUND.lower() == type.lower():
                    feature.background = cur_scenario
                else:
                    cur_scenario.metadata.update(feature.metadata)
                    cur_scenario.background = feature.background
                    scenarios.append(cur_scenario)
            elif EXAMPLES.lower() == type.lower():
                _set_data_table(cur_scenario, None, data_table)
                data_table = None  # reset
                example_table = []

    _set_data_table(cur_scenario, example_table, data_table)
    example_table = None
    data_table = None

    return scenarios


def _set_data_table(cur_scenario, example_table, data_table):
    if example_table:
        cur_scenario.metadata.update({"JSON_DATA_TABLE": _to_list(example_table)})
    if data_table:
        cur_scenario.steps[-1] = cur_scenario.steps[-1] + _to_list(data_table)


def _to_list(table_data):
    # data_errors =  list(filter(lambda row: row[1] != "|" or row[-1]!="|" , table_data))
    # if data_errors:
    #     raise Exception("Data table must start and end with '|'", data_errors)
    # data = (data.strip()[1:-1] for data in table_data)
    return get_list_of_map(table_data, '|')


def _getType(line):
    if line.endswith(MULTI_LINE_COMMENT):
        return MULTI_LINE_COMMENT_END

    match: Match[bytes] | None | Match[str] = re.match(
        "|".join([TAG, SCENARIO_OUTELINE, SCENARIO, STEP_DEF, EXAMPLES, FEATURE, BACKGROUND, MULTI_LINE_COMMENT])
        , line,
        re.I)
    return match.group() if match else ""
