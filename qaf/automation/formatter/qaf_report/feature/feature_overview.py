import json
import os


class FeatureOverView:
    def __init__(self) -> None:
        path_to_write = os.getenv('CURRENT_FEATURE_DIR')
        self.__overview_file_path = os.path.join(path_to_write, 'overview.json')

        if os.path.exists(self.__overview_file_path):
            with open(self.__overview_file_path) as f:
                _dict = json.load(f)

            self.total_count = int(_dict['total'])
            self.pass_count = int(_dict['pass'])
            self.fail_count = int(_dict['fail'])
            self.skip_count = int(_dict['skip'])
            self.startTime = str(_dict['startTime'])
            self.endTime = str(_dict['endTime'])
            self.__classes = _dict['classes']
            self.envInfo = _dict['envInfo']
        else:
            self.total_count = 0
            self.pass_count = 0
            self.fail_count = 0
            self.skip_count = 0
            self.startTime = ''
            self.endTime = ''
            self.__classes = []
            self.envInfo = {}

    @property
    def total_count(self) -> int:
        return self.__total_count

    @total_count.setter
    def total_count(self, value: int) -> None:
        self.__total_count = value

    @property
    def pass_count(self) -> int:
        return self.__pass_count

    @pass_count.setter
    def pass_count(self, value: int) -> None:
        self.__pass_count = value

    @property
    def fail_count(self) -> int:
        return self.__fail_count

    @fail_count.setter
    def fail_count(self, value: int) -> None:
        self.__fail_count = value

    @property
    def skip_count(self) -> int:
        return self.__skip_count

    @skip_count.setter
    def skip_count(self, value: int) -> None:
        self.__skip_count = value

    @property
    def startTime(self) -> str:
        return self.__startTime

    @startTime.setter
    def startTime(self, value: str) -> None:
        self.__startTime = value
        self.__dump_to_json()

    @property
    def endTime(self) -> str:
        return self.__endTime

    @endTime.setter
    def endTime(self, value: str) -> None:
        self.__endTime = value
        self.__dump_to_json()

    @property
    def classes(self) -> list:
        return self.__classes

    def add_class(self, class_name: str) -> None:
        self.__classes.append(class_name)
        self.__dump_to_json()

    @property
    def envInfo(self) -> dict:
        return self.__envInfo

    @envInfo.setter
    def envInfo(self, value: dict) -> None:
        self.__envInfo = value

    def update_status(self, scenario_status: str) -> None:
        if scenario_status.lower() == 'passed':
            self.pass_count += 1
        elif scenario_status.lower() == 'failed':
            self.fail_count += 1
        else:
            self.skip_count += 1

        self.total_count += 1
        self.__dump_to_json()

    def __dump_to_json(self) -> None:
        try:
            _dict = {
                "total": self.total_count,
                "pass": self.pass_count,
                "fail": self.fail_count,
                "skip": self.skip_count,
                "startTime": self.startTime,
                "endTime": self.endTime,
                "classes": self.classes,
                "envInfo": self.envInfo
            }
            with open(self.__overview_file_path, 'w') as fp:
                json.dump(_dict, fp, sort_keys=True, indent=4)
        except:
            pass
