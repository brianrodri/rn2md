"""Test cases for the rn2md.config module."""
import os
import unittest

from pyfakefs import fake_filesystem_unittest

from rn2md import config


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


if __name__ == '__main__':
    unittest.main()
