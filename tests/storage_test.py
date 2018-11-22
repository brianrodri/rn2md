#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from rn2md import storage

import datetime as dt
import os
import unittest

from pyfakefs import fake_filesystem_unittest
import yaml


class LoadDailyEntriesTest(fake_filesystem_unittest.TestCase):

    def CreateValidMonthFile(self, month_filename, daily_entries):
        month_file_path = os.path.join('/test', month_filename)
        month_file_content = yaml.dump(
            {day: {'text': entry} for day, entry in daily_entries.items()})
        self.fs.create_file(
            month_file_path, contents=month_file_content, encoding='utf-8')

    def setUp(self):
        self.setUpPyfakefs()

    def testGatheringData(self):
        self.CreateValidMonthFile('1993-01.txt', {17: '🎂'})
        self.CreateValidMonthFile('2017-12.txt', {25: '🎅'})
        self.CreateValidMonthFile('2018-03.txt', {1: 'data', 24: 'info'})

        self.assertEqual(storage.LoadDailyEntries('/test'), {
            dt.date(1993, 1, 17): '🎂',
            dt.date(2017, 12, 25): '🎅',
            dt.date(2018, 3, 1): 'data',
            dt.date(2018, 3, 24): 'info',
        })

    def testMisnamedFilesAreIgnored(self):
        self.CreateValidMonthFile('2018-01.txt', {17: 'from valid file'})
        self.CreateValidMonthFile('2018-MAR.txt', {24: 'from invalid file'})

        self.assertEqual(storage.LoadDailyEntries('/test'), {
            dt.date(2018, 1, 17): 'from valid file',
        })

    def testEmptyEntriesAreIgnored(self):
        self.CreateValidMonthFile('2018-03.txt', {12: '', 24: 'non-empty'})

        self.assertEqual(storage.LoadDailyEntries('/test'), {
            dt.date(2018, 3, 24): 'non-empty',
        })

    def testFilesWithNonYamlDataAreIgnored(self):
        self.fs.create_file(
            '2018-03.txt', contents='I AM }NOT{ YAML!', encoding='utf-8')

        self.assertFalse(storage.LoadDailyEntries('/test'))

    def testFilesWithoutUtf8EncodingAreIgnored(self):
        self.fs.create_file(
            '2018-03.txt', contents=yaml.dump({24: {'text': '😂'}}),
            encoding='ascii')

        self.assertFalse(storage.LoadDailyEntries('/test'))


if __name__ == '__main__':
    unittest.main()
