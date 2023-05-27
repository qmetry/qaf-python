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
import random
import re
import string

from qaf.automation.util.string_util import to_boolean, decode_base64


class PropretyUtil(dict):
    """
    @Author: Chirag Jayswal

    This class is represents similar features as PropertyUtil in qaf-java version.
    It supports
    - parameter-interpolation: https://qmetry.github.io/qaf/latest/properties_configuration.html#parameter-interpolation
    - encryption: https://qmetry.github.io/qaf/latest/different_ways_of_providing_prop.html#encryption-support
    - file types: properties, wsc, wscj, loc, locj, ini

    """

    def __init__(self, *args, **kw):
        super(PropretyUtil, self).__init__(*args, **kw)

    def load(self, resources_path: str) -> None:

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

    def get_string(self, key, default=None):
        val = self.get(key, default)
        return str(val) if val is not None else None

    def get_boolean(self, key, default=None):
        val = self.get_string(key, default)
        return to_boolean(val) if val is not None else None

    def get_int(self, key, default=0):
        val = self.get(key, default)
        return int(val) if val is not None else None

    def set_property(self, key, value):
        self.__setitem__(key, value)
        if key.startswith("encrypted."):
            dkey = key.split(".", 1)[1]
            decrypt = self._decrypt_impl()
            d_val = decrypt(value)
            self.__setitem__(dkey, d_val)

    def get_property(self, key, default=None):
        return self.get(key, default)

    def __getitem__(self, key, default=None):
        return super(PropretyUtil, self).__getitem__(key) if self.__contains__(key) else default

    def get(self, key, default=None):
        value = self.get_raw_value(key)
        return self.resolve(value) if value is not None else default

    def get_or_set(self, key, default):
        if key not in self:
            self.set_property(key, default)
        return self.get(key)

    def get_raw_value(self, key, default=None):
        return self.__getitem__(key, default)

    def interpolate(self, rest, prefix, suffix, pattern, ext_dict={}):
        accum = []
        while rest:
            p = rest.find(prefix[0])
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
                            v = self._rnd(opt)
                        else:
                            v = ext_dict.get(opt, self.get(opt, prefix + opt + suffix))
                    accum.append(v)
                except Exception as e:
                    raise e
            else:
                accum.append(rest)

        return ''.join(accum)

    def resolve(self, value, disc={}):
        if value and isinstance(value, str):
            pattern = re.compile(r"<%([^>]+)%>")
            value = self.interpolate(value, "<%", "%>", pattern, disc)
            pattern = re.compile(r"\$\{([^}]+)\}")
            value = self.interpolate(value, "${", "}", pattern, disc)
            return value
        return value

    def _rnd(self, r_format):
        res_string = ""
        for char in r_format:
            res = char
            if char.isdigit():
                res = random.choice(string.digits)
            elif char.isalpha():
                res = random.choice(string.ascii_lowercase) if char.islower() else random.choice(string.ascii_uppercase)

            res_string += res
        return res_string

    def _evalexpr(self, expr, vars):
        try:
            return eval(str(expr), self, vars)
        except NameError as ne:
            arg_index = expr.index('(')
            if not expr.startswith('__import') and arg_index > 0:
                qualified_name = expr[:arg_index]
                arg = expr[arg_index:]
                m_index = qualified_name.rindex('.')
                class_name = qualified_name[:m_index]
                method_name = qualified_name[m_index:]
                m_expr = "__import__('{0}'){1}{2}".format(class_name, method_name, arg)
                try:
                    return eval(m_expr, self, vars)
                except Exception as ex:
                    raise ne

    def _decrypt_impl(self):
        return self.get("password.decryptor.impl", decode_base64)
