"""Test cases for the rn2md.storage module."""
import datetime as dt
import os
import unittest

from pyfakefs import fake_filesystem_unittest
import yaml

from rn2md import storage


class LoadDailyEntriesTest(fake_filesystem_unittest.TestCase):
    """Test case for the load_daily_entries function."""

    def _create_month_test_file(self, month_filename, daily_entries):
        month_file_path = os.path.join('/data', month_filename)
        month_file_content = yaml.dump(
            {day: {'text': entry} for day, entry in daily_entries.items()})
        self.fs.create_file(
            month_file_path, contents=month_file_content, encoding='utf-8')

    def setUp(self):
        self.setUpPyfakefs()

    def test_gathering_data(self):
        """Tests the basic functionality expected from load_daily_entries."""
        self._create_month_test_file('1993-01.txt', {17: '🎂'})
        self._create_month_test_file('2017-12.txt', {25: '🎅'})
        self._create_month_test_file('2018-03.txt', {1: 'data', 24: 'info'})

        self.assertEqual(storage.load_daily_entries('/data'), {
            dt.date(1993, 1, 17): '🎂',
            dt.date(2017, 12, 25): '🎅',
            dt.date(2018, 3, 1): 'data',
            dt.date(2018, 3, 24): 'info',
        })

    def test_misnamed_files_are_ignored(self):
        """Tests that files are ignored if they aren't named correctly."""
        self._create_month_test_file('2018-01.txt', {17: 'from valid file'})
        self._create_month_test_file('2018-MAR.txt', {24: 'from invalid file'})

        self.assertEqual(storage.load_daily_entries('/data'), {
            dt.date(2018, 1, 17): 'from valid file',
        })

    def test_empty_entries_are_ignored(self):
        """Tests that only entries with data are part of the result."""
        self._create_month_test_file('2018-03.txt', {12: '', 24: 'non-empty'})

        self.assertEqual(storage.load_daily_entries('/data'), {
            dt.date(2018, 3, 24): 'non-empty',
        })

    def test_non_yaml_data_is_ignored(self):
        """Tests that files with non-yaml data are ignored."""
        self.fs.create_file(
            '2018-03.txt', contents='I AM }NOT{ YAML!', encoding='utf-8')

        self.assertFalse(storage.load_daily_entries('/data'))

    def test_non_utf8_data_is_ignored(self):
        """Tests that files without utf8-encoding are ignored."""
        self.fs.create_file(
            '2018-03.txt', contents=yaml.dump({24: {'text': '😂'}}),
            encoding='ascii')

        self.assertFalse(storage.load_daily_entries('/data'))


if __name__ == '__main__':
    unittest.main()
