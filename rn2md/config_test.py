#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import os
import unittest

from pyfakefs import fake_filesystem_unittest

import config


class ConfigOptionsTest(fake_filesystem_unittest.TestCase):

    def setUp(self):
        self.setUpPyfakefs()

    def testDefaultBehavior(self):
        argv = ['config_test.py', 'command', 'line', 'args']
        options, remaining_argv = config.BuildConfigOptions(argv)
        self.assertFalse(options.WorkdaysOnly())
        self.assertEqual(options.DataPath(),
                         os.path.expanduser('~/.rednotebook/data'))
        self.assertListEqual(remaining_argv, ['command', 'line', 'args'])


if __name__ == '__main__':
    unittest.main()
