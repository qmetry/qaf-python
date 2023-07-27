# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Infostretch Corporation
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

import json
import os
import re

from simpleeval import NameNotDefined, EvalWithCompoundTypes

from qaf.automation.util.string_util import to_boolean, decode_base64, rnd


class PropertyUtil(dict):
    """
    @Author: Chirag Jayswal

    This class is represents similar features as PropertyUtil in qaf-java version.
    It supports
    - parameter-interpolation: https://qmetry.github.io/qaf/latest/properties_configuration.html#parameter-interpolation
    - encryption: https://qmetry.github.io/qaf/latest/different_ways_of_providing_prop.html#encryption-support
    - file types: properties, wsc, wscj, loc, locj, ini

    """

    def __init__(self, *args, **kw):
        super(PropertyUtil, self).__init__(*args, **kw)
        self.loading_resources = False
        self.resource_path = ""
        self.evaluator = EvalWithCompoundTypes()

    def load(self, resources_path: str) -> None:

        if self.resource_path == resources_path: return
        self.loading_resources = True
        self.resource_path = resources_path
        all_resources_path = resources_path.split(";") if resources_path else []
        for each_resource_path in all_resources_path:
            if os.path.isdir(each_resource_path):
                for root, dirs, files in os.walk(each_resource_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        self.__load_file(file_path)

            elif os.path.isfile(each_resource_path):
                # self.__load_files(each_resource_path)
                self.__load_file(each_resource_path)
        self.loading_resources = False  # mark done
        if self.resource_path != self.get_string("env.resources", self.resource_path):
            self.load(self.get_string("env.resources", self.resource_path))

    def __load_file(self, file):
        extension = os.path.splitext(file)[1]
        if extension in ('.properties', '.loc', '.wsc', '.ini'):
            with open(file, 'r', encoding='UTF-8') as file:
                while line := file.readline():
                    kv = line.strip()
                    if kv and not kv.startswith("#"):
                        while kv.endswith("\\"):
                            kv = kv[:-1]
                            part = file.readline().strip()
                            if part and not part.startswith("#"):
                                kv = kv + part

                        kv = kv.split("=", 1)
                        if len(kv) == 2:
                            self.set_property(key=kv[0].strip(), value=kv[1].strip())
        elif extension in ('.wscj', '.locj'):
            with open(file, 'r', encoding='UTF-8') as json_file:
                data = json.load(json_file)
                for key, value in data.items():
                    self.set_property(key=key, value=json.dumps(value))

    def contains_key(self, key: str) -> bool:
        """
        Check if contains key.

        Args:
            key (str): Key name to verify key is exist or not.

        Returns:
            bool: Returns True If contains key else returns False

        """
        return self.__contains__(key)

    def get_string(self, key: str, default: str = None) -> str:
        """
        Returns object for key.

        Args:
            key (str): Key name to store value
            default (Optional(str)): This will default value for key, if not provided default value will be None

        Returns:
            Optional(str): Stored value for key or default
        """
        val = self.get(key, default)
        return str(val) if val is not None else None

    def get_boolean(self, key: str, default: bool = None) -> bool:
        """
        Returns boolean value for key or None.

        Args:
            key (str): Key name to store value
            default (Optional(bool)): This will default value for key if not provided default is None

        Returns:
            Optional(bool): Stored value for key or default
        """
        val = self.get_string(key, default)
        return to_boolean(val) if val is not None else None

    def get_int(self, key, default: int = None) -> int:
        val = self.get(key, default)
        return int(val) if val is not None else None

    def set_property(self, key: str, value):
        if key in os.environ:
            value = os.environ[key]
        self.__setitem__(key, value)
        if key.startswith("encrypted."):
            dkey = key.split(".", 1)[1]
            decrypt = self._decrypt_impl()
            d_val = decrypt(value)
            self.__setitem__(dkey, d_val)
        # do we need to reload resources?
        if not (self.loading_resources or self.resource_path == self.get_string("env.resources", self.resource_path)):
            self.load(self.get_string("env.resources"))

    def get_property(self, key: str, default=None):
        return self.get(key, default)

    def __getitem__(self, key, default=None):
        return super(PropertyUtil, self).__getitem__(key) if self.__contains__(key) else default

    def get(self, key: str, default=None):
        value = self.get_raw_value(key)
        return self.resolve(value) if value is not None else default

    def get_or_set(self, key: str, default):
        if key not in self:
            self.set_property(key, default)
        return self.get(key)

    def get_raw_value(self, key: str, default=None):
        return self.__getitem__(key, default)

    def interpolate(self, rest, prefix, suffix, pattern, ext_dict=None):
        if ext_dict is None:
            ext_dict = {}
        accum = []
        while rest:
            p = rest.find(prefix)
            if p < 0:
                accum.append(rest)
                return ''.join(accum)
            if p >= 0:
                accum.append(rest[:p])
                rest = rest[p:]
            # p is no longer used
            c = rest[1:2]
            if c == prefix[0]:
                accum.append(prefix[0])
                rest = rest[2:]
            elif c == prefix[1]:
                m = pattern.match(rest)
                if m is None:
                    raise Exception(
                        "bad interpolation variable reference %r" % rest)
                path = m.group(1).split(':')
                rest = rest[m.end():]
                try:
                    if len(path) == 1:
                        opt = path[0]
                        v = ext_dict.get(opt, self.get(opt, prefix + opt + suffix))
                    elif len(path) == 2:
                        sect = path[0]
                        opt = path[1]
                        if sect == 'expr':
                            v = str(self._evalexpr(opt, ext_dict))
                        elif sect == 'rnd':
                            v = rnd(opt)
                        else:
                            v = ext_dict.get(opt, self.get(opt, prefix + opt + suffix))
                    accum.append(str(v))
                except Exception as e:
                    raise e
            else:
                accum.append(rest)

        return ''.join(accum)

    def resolve(self, value, disc=None):
        if disc is None:
            disc = {}
        if value and isinstance(value, str):
            pattern = re.compile(r"<%([^>]+)%>")
            value = self.interpolate(value, "<%", "%>", pattern, disc)
            pattern = re.compile(r"\$\{([^}]+)\}")
            value = self.interpolate(value, "${", "}", pattern, disc)
            return value
        return value

    def _evalexpr(self, expr, vars):
        self.evaluator.names = vars if vars else {}
        try:
            return self.evaluator.eval(expr)
        except NameNotDefined:
            return False

    def _decrypt_impl(self):
        return self.get("password.decryptor.impl", decode_base64)
