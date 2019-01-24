"""Test cases for the rn2md.config module."""
import datetime
import os
import unittest

from pyfakefs import fake_filesystem_unittest
import freezegun

from rn2md import config
from rn2md import util


class OptionsTest(fake_filesystem_unittest.TestCase):
    """Tests for the Options class"""

    def setUp(self):
        self.setUpPyfakefs()

    def test_default_behavior(self):
        """Tests nothing special happens when arbitrary args are passed."""
        argv = ['config_test.py', 'command', 'line', 'args']
        options, remaining_argv = config.Options.from_argv(argv)
        self.assertFalse(options.workdays_only)
        self.assertEqual(options.data_path,
                         os.path.expanduser('~/.rednotebook/data'))
        self.assertEqual(options.default_date_range, [datetime.date.today()])
        self.assertEqual(remaining_argv, ['command', 'line', 'args'])

    def test_change_work_options(self):
        """Tests workday changes made in the config_options file."""
        self.fs.create_file(os.path.expanduser('~/.rn2mdrc'), contents="""
        [DEFAULT]
        workday mode=on
        """)
        options, unused_remaining_argv = config.Options.from_argv([])
        self.assertTrue(options.workdays_only)

    def test_change_data_path(self):
        """Test data changes made in the config file."""
        self.fs.create_file(os.path.expanduser('~/.rn2mdrc'), contents="""
        [DEFAULT]
        data path=/test
        """)
        options, unused_remaining_argv = config.Options.from_argv([])
        self.assertEqual(options.data_path, '/test')

    @freezegun.freeze_time(util.strict_parse_date('Mon Mar 26, 2018'))
    def test_change_default_date_range(self):
        """Test date range changes made in the config file."""
        self.fs.create_file(os.path.expanduser('~/.rn2mdrc'), contents="""
        [DEFAULT]
        default date range=last week
        """)
        options, unused_remaining_argv = config.Options.from_argv([])
        self.assertEqual(options.default_date_range, [
            util.strict_parse_date('Mon Mar 19, 2018'),
            util.strict_parse_date('Tue Mar 20, 2018'),
            util.strict_parse_date('Wed Mar 21, 2018'),
            util.strict_parse_date('Thu Mar 22, 2018'),
            util.strict_parse_date('Fri Mar 23, 2018'),
            util.strict_parse_date('Sat Mar 24, 2018'),
            util.strict_parse_date('Sun Mar 25, 2018'),
        ])


if __name__ == '__main__':
    unittest.main()
