from collections import deque

from qaf.automation.formatter.qaf_report.step.checkpoint import CheckPoint


class SubCheckPoints:
    __sub_check_points = deque()

    def add_check_point(self, check_point: CheckPoint) -> None:
        SubCheckPoints.__sub_check_points.append(check_point.to_json_dict())

    def get_all_sub_check_points(self) -> list:
        arr_sub_check_points = []
        while SubCheckPoints.__sub_check_points:
            check_point = SubCheckPoints.__sub_check_points.popleft()
            arr_sub_check_points.append(check_point)
        return arr_sub_check_points
