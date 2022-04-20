#  Copyright (c) .2022 Infostretch Corporation
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  #
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import os
import plistlib
from configparser import ConfigParser, ExtendedInterpolation

from qaf.automation.keys.application_properties import ApplicationProperties as AP
from qaf.automation.core.configurations_manager import ConfigurationsManager as CM
from typing import (
    Optional,
)


class ResourcesManager:
    """
    This class will load application properties and save values in configurations manager.
    """

    default_language = None

    def set_up(self) -> None:
        """
        Load Application Properties

        Returns:
            None
        """
        application_properties_path = os.path.join('resources', 'application_properties.ini')
        if os.path.exists(application_properties_path):
            config = ConfigParser(interpolation=ExtendedInterpolation())
            config.read(application_properties_path)

            for each_section in config.sections():
                for each_key, each_val in config.items(each_section):
                    CM().set_object_for_key(value=each_val, key=each_key)

        if ResourcesManager.default_language is None and CM().get_str_for_key(
                AP.ENV_DEFAULT_LANGUAGE) is not None:
            ResourcesManager.default_language = CM().get_str_for_key(
                AP.ENV_DEFAULT_LANGUAGE)

        self.__load_resources(CM().get_str_for_key(AP.RESOURCES))

    def __load_resources(self, resources_path: str) -> None:
        all_resources_path = resources_path.split(";")
        for each_resource_path in all_resources_path:
            if os.path.isdir(each_resource_path):
                for root, dirs, files in os.walk(each_resource_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        self.__load_files(file_path)

            elif os.path.isfile(each_resource_path):
                self.__load_files(each_resource_path)

    def __load_files(self, file: str) -> None:
        extension = os.path.splitext(file)[1]
        if extension == '.ini':
            self.__load_ini_file(file)
        elif extension == '.plist':
            self.__load_plist_file(file)
        elif extension in ('.properties', '.loc', '.wsc'):
            self.__load_properties_file(file)

    @staticmethod
    def __load_ini_file(file_path: str) -> None:
        """
        This method will load key-value pairs store in ini file and stores them in configuration manager.

        Args:
            file_path(str): Path of ini file.

        Returns:
            None
        """
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read(file_path)

        for each_section in config.sections():
            for key, value in config.items(each_section):
                CM().set_object_for_key(value=value, key=key)

    @staticmethod
    def __load_plist_file(file_path: str) -> None:
        """
        This method will load key-value pairs store in plist file and stores them in configuration manager.

        Args:
            file_path(str): Path of plist file.

        Returns:
            None
        """
        with open(file_path, 'rb') as fp:
            _dict = plistlib.load(fp)

        for key, value in _dict.items():
            CM().set_object_for_key(value=value, key=key)

    def __load_properties_file(self, file_path: str) -> None:
        """
        This method will load key-value pairs store in plist file and stores them in configuration manager.

        Args:
            file_path(str): Path of plist file.

        Returns:
            None
        """
        _dict = self.__load_properties(file_path, "=", "#")

        for key, value in _dict.items():
            CM().set_object_for_key(value=value, key=key)

    def __load_properties(self, filepath: str, sep: Optional[str] = '=', comment_char: Optional[str] = '#') -> dict:
        props = {}
        with open(filepath, "rt", encoding="UTF-8") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"')
                    props[key] = value
        return props
