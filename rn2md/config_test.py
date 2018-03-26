#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import os
import unittest

from pyfakefs import fake_filesystem_unittest

import config


class ConfigOptionsTest(fake_filesystem_unittest.TestCase):

    def CreateFakeConfigFile(self, options):
        config_path = os.path.expanduser('~/.rn2mdrc')
        config_lines = []
        for sect in options:
            config_content.append('[%s]\n' % sect)
            for option in options[sect]:
                config_lines.append('%s=%s' % (option, options[sect][option]))
            config_content.append('')
        self.fs.create_file(config_path, contents='\n'.join(config_lines))

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
        self.CreateFakeConfigFile({
            'WORK': {
                'workday mode': 'on',
                'selected': 'true',
            },
        })
        options = config.BuildConfigOptions()[0]
        self.assertTrue(options.WorkdaysOnly())


if __name__ == '__main__':
    unittest.main()
