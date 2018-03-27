#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import os
import unittest

from pyfakefs import fake_filesystem_unittest

import config


class ConfigOptionsTest(fake_filesystem_unittest.TestCase):

    def CreateFakeConfigFile(self, lines):
        config_path = os.path.expanduser('~/.rn2mdrc')
        config_content = '\n'.join(lines)
        self.fs.create_file(config_path, contents=config_content)

    def setUp(self):
        self.setUpPyfakefs()

    def testDefaultBehavior(self):
        argv = ['config_test.py', 'command', 'line', 'args']
        options, remaining_argv = config.BuildConfigOptions(argv)
        self.assertFalse(options.WorkdaysOnly())
        self.assertEqual(options.DataPath(),
                         os.path.expanduser('~/.rednotebook/data'))
        self.assertListEqual(remaining_argv, ['command', 'line', 'args'])

    def testWorkOptions(self):
        self.CreateFakeConfigFile([
            '[DEFAULT]',
            'workday mode=on',
        ])
        options = config.BuildConfigOptions()[0]
        self.assertTrue(options.WorkdaysOnly())


if __name__ == '__main__':
    unittest.main()
