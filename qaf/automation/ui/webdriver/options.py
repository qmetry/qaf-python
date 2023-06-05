from typing import Dict, Any

from selenium.webdriver.common.options import BaseOptions


class GenericOptions(BaseOptions):
    """
    @author: Chirag Jayswal
    """
    def __init__(self, option={}) -> None:
        self.__dict__.update(option.__dict__)
        super().__init__()

    def to_capabilities(self):
        return self.capabilities

    @property
    def default_capabilities(self):
        return {}

    def load_capabilities(self, desired_caps: Dict[str, Any]):
        for name, value in desired_caps.items():
            try:
                self.set_capability(name, value)
            except:
                setattr(self._cap,name,value)
        return self
