"""Builds configuration options for rn2md tool with nice default behavior."""
import configparser
import os


class ConfigOptions():
    """Encapsulates rn2md options which are configurable through ~/.rn2mdrc."""

    DEFAULT_DATA_PATH = os.path.expanduser('~/.rednotebook/data')
    DEFAULT_CONFIG_VALUES = {
        'data path': DEFAULT_DATA_PATH,
        'workday mode': 'off',
    }

    def __init__(self, section='DEFAULT'):
        self._config = configparser.ConfigParser(self.DEFAULT_CONFIG_VALUES)
        self._config.read(os.path.expanduser('~/.rn2mdrc'))
        self._section = section

    @property
    def workdays_only(self):
        """Read-only accessor for workday mode"""
        return self._config[self._section].getboolean('workday mode')

    @property
    def data_path(self):
        """Read-only accessor for data path"""
        return self._config[self._section].get('data path')


def build_config_options(argv=None):
    """Parses argv for any extra configuration requested via stdin."""
    if argv is None:
        argv = []
    return ConfigOptions(), argv[1:]
