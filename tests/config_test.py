#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import os
import unittest

from pyfakefs import fake_filesystem_unittest

from rn2md import config


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

    def testChangeWorkOptions(self):
        self.fs.create_file(os.path.expanduser('~/.rn2mdrc'), contents="""
        [DEFAULT]
        workday mode=on
        """)
        options = config.BuildConfigOptions()[0]
        self.assertTrue(options.WorkdaysOnly())

    def testChangeDataPath(self):
        self.fs.create_file(os.path.expanduser('~/.rn2mdrc'), contents="""
        [DEFAULT]
        data path=/test
        """)
        options = config.BuildConfigOptions()[0]
        self.assertEqual(options.DataPath(), '/test')


if __name__ == '__main__':
    unittest.main()
