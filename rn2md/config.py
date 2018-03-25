#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Builds configuration options with nice default behavior."""
import configparser
import os
import sys


class ConfigOptions():
    """Encapsulates rn2md options; they can be configured through ~/.rn2mdrc."""

    DEFAULT_CONFIG_VALUES = {
        'data path': os.path.expanduser('~/.rednotebook/data'),
        'worday mode': 'on',
    }

    def __init__(self, section='DEFAULT'):
        config = configparser.ConfigParser(self.DEFAULT_CONFIG_VALUES)
        config.read(os.path.expanduser('~/.rn2mdrc'))
        self._config = config[section]

    def WorkdaysOnly(self):
        return self._config.getboolean('workday mode')

    def DataPath(self):
        return self._config.get('data path')


def BuildConfigOptions():
    # TODO(brianrodri): Add command-line configuration options.
    return ConfigOptions(), sys.argv[1:]
