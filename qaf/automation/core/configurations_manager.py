import json

from qaf.automation.core.singleton import Singleton
from qaf.automation.util.string_util import to_boolean
from typing import (
    Optional,
)


class ConfigurationsManager(metaclass=Singleton):
    """
    This class will store the values of all property files.
    """

    def __init__(self):
        self.__dict = {}

    def contains_key(self, key: str) -> bool:
        """
        Check that configurations manager contains key.

        Args:
            key (str): Key name to verify key is exist or not.

        Returns:
            bool: Returns True If dict contains key else returns False

        """
        return True if key in self.__dict else False

    def set_object_for_key(self, key: str, value=object) -> None:
        """
        Set object for key into the dict

        Args:
            key (str): Key name to store value
            value (str): Value which needs to be store

        Returns:
            None
        """
        self.__dict[key] = value

    def get_object_for_key(self, key: str, default_value: Optional[object] = None) -> object:
        """
        Returns object for key.

        Args:
            key (str): Key name to store value
            default_value (Optional(object)): This will default value for key

        Returns:
            Optional(object): Stored value for key
        """
        return self.__dict[key] if self.contains_key(key) else default_value

    def get_str_for_key(self, key: str, default_value=None) -> str:
        """
        Returns object for key.

        Args:
            key (str): Key name to store value
            default_value (Optional(str)): This will default value for key

        Returns:
            Optional(str): Stored value for key
        """
        return str(self.__dict[key]) if self.contains_key(key) else default_value

    def get_int_for_key(self, key: str, default_value=None) -> int:
        """
        Returns object for key.

        Args:
            key (str): Key name to store value
            default_value (Optional(int)): This will default value for key

        Returns:
            Optional(int): Stored value for key
        """
        return int(self.__dict[key]) if self.contains_key(key) else default_value

    def get_bool_for_key(self, key: str, default_value=False) -> bool:
        """
        Returns object for key.

        Args:
            key (str): Key name to store value
            default_value (Optional(bool)): This will default value for key

        Returns:
            Optional(bool): Stored value for key
        """
        return to_boolean(self.__dict[key]) if self.contains_key(key) else default_value

    def get_list_for_key(self, key: str, default_value=None) -> list:
        """
        Returns object for key.

        Args:
            key (str): Key name to store value
            default_value (Optional(list)): This will default value for key

        Returns:
            Optional(list): Stored value for key
        """
        if default_value is None:
            default_value = []
        if self.contains_key(key) and isinstance(self.__dict[key], str):
            return self.__dict[key].split(";")
        return default_value

    def get_dict_for_key(self, key: str, default_value=None) -> dict:
        """
        Returns object for key.

        Args:
            key (str): Key name to store value
            default_value (Optional(dict)): This will default value for key

        Returns:
            Optional(dict): Stored value for key
        """
        if default_value is None:
            default_value = {}
        if self.contains_key(key) and isinstance(self.__dict[key], str):
            return json.loads(self.__dict[key])
        return default_value
