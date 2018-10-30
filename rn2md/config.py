#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Builds configuration options with nice default behavior."""
import configparser
import os
import sys


class ConfigOptions():
    """Encapsulates rn2md options; they can be configured through ~/.rn2mdrc."""

    DEFAULT_DATA_PATH = os.path.expanduser('~/.rednotebook/data')
    DEFAULT_CONFIG_VALUES = {
        'data path': DEFAULT_DATA_PATH,
        'workday mode': 'off',
    }

    def __init__(self, section='DEFAULT'):
        self._config = configparser.ConfigParser(self.DEFAULT_CONFIG_VALUES)
        self._config.read(os.path.expanduser('~/.rn2mdrc'))
        self._section = section

    def WorkdaysOnly(self):
        return self._config[self._section].getboolean('workday mode')

    def DataPath(self):
        return self._config[self._section].get('data path')


def BuildConfigOptions(argv=None):
    if argv is None:
        argv = []
    # TODO(brianrodri): Add more command-line configuration options.
    return ConfigOptions(), argv[1:]
