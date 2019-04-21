"""Builds configuration options for rn2md tool with nice default behavior."""
import configparser
import os

from . import util


class Options():
    """Encapsulates rn2md options which are configurable through ~/.rn2mdrc."""

    DEFAULT_DATA_PATH = os.path.expanduser('~/.rednotebook/data')
    DEFAULT_CONFIG_VALUES = {
        'data path': DEFAULT_DATA_PATH,
        'workday mode': 'off',
        'default date range': 'today',
    }

    @classmethod
    def from_argv(cls, argv):
        """Make changes to the default options based on argv input."""
        return cls(), argv[1:]

    def __init__(self, section='DEFAULT'):
        self._config = configparser.ConfigParser(self.DEFAULT_CONFIG_VALUES)
        self._config.read(os.path.expanduser('~/.rn2mdrc'))
        self._section = section
        self._default_date_range = util.parse_date_range(
            self._config[section].get('default date range'))

    @property
    def workdays_only(self):
        """Read-only accessor for workday mode."""
        return self._config[self._section].getboolean('workday mode')

    @property
    def data_path(self):
        """Read-only accessor for data path."""
        return self._config[self._section].get('data path')

    @property
    def default_date_range(self):
        """Read-only accessor for default date range."""
        return self._default_date_range
