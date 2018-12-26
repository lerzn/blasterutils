from collections import abc
from functools import lru_cache
from keyword import iskeyword

import yaml
import json


@lru_cache(maxsize=32)
def open_yml(filename, frozen_js=True, top_key=None):
    """
    Opens a YML file and returns it's content either as dictionary or as instance of FrozenJSON. Cached by
    built-in lru_cache module.

    :param filename: filename to open
    :param frozen_js: True to return FrozenJSON, False to return dict
    :param top_key: if specified the returned instance will only include items from this key onwards.
    :return:
    """
    with open(filename, "r", encoding="UTF8") as f:
        if not top_key:
            yaml_file = yaml.load(f)
        else:
            yaml_file = yaml.load(f)[top_key]
    if not frozen_js:
        return yaml_file
    return FrozenJSON(yaml_file)


@lru_cache(maxsize=32)
def open_json(filename, frozen_js=True, top_key=None):
    """
    Opens a YML file and returns it's content either as dictionary or as instance of FrozenJSON. Cached by
    built-in lru_cache module.

    :param filename: filename to open
    :param frozen_js: True to return FrozenJSON, False to return dict
    :param top_key: if specified the returned instance will only include items from this key onwards.
    :return:
    """
    with open(filename, "r", encoding="UTF-8") as f:
        if not top_key:
            dic = json.load(f)
        else:
            dic = json.load(f)[top_key]
    if not frozen_js:
        return dic
    return FrozenJSON(dic)


class FrozenJSON:
    """
    Turns a dictionary-like object into an instance of FrozenJSON, which supports both
    variable['key'] and variable.key reference. Read-only!
    """

    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, mapping):
        self.__data = {}
        for key, value in mapping.items():
            if iskeyword(key):
                key += "_"
            self.__data[key] = value

    def __getattr__(self, name):
        if hasattr(self.__data, name):
            return getattr(self.__data, name)
        else:
            try:
                return FrozenJSON(self.__data[name])
            except KeyError:
                raise AttributeError(name)

    def __repr__(self):
        return f"FrozenJSON({self._FrozenJSON__data})"

    def __getitem__(self, arg):
        requested = self._FrozenJSON__data[arg]
        if isinstance(requested, abc.Mapping):
            return FrozenJSON(requested)
        elif isinstance(requested, abc.MutableSequence):
            return [FrozenJSON(item) for item in requested]
        else:
            return requested
