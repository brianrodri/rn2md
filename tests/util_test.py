#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import unittest

import enum
import datetime as dt
import dateutil
import freezegun
import itertools

from rn2md import util


Weekdays = enum.Enum('Weekdays', 'Mon Tue Wed Thu Fri Sat Sun', start=0)


def StrictParseDate(date_str: str) -> dt.date:
    """Parses date with strict requirements on the output.

    Asserts that when a weekday ('%a') is provided, the parsed date's weekday
    matches it. Normally, mismatches are ignored by date parsers.

    Args:
        date_str: Format must be: '%a %b %d, %Y' or '%b %d, %Y'.
    Returns:
        The parsed datetime.date instance.
    Raises:
        ValueError:
            - none of the formats could parse date_str
            - weekday provided in date_str was not the same as the weekday
              parsed from it
    """
    try:
        parsed_date = dt.datetime.strptime(date_str, '%a %b %d, %Y').date()
    except ValueError:
        pass
    else:
        date_str_weekday = date_str[:3].capitalize()
        parsed_weekday = Weekdays(parsed_date.weekday()).name
        if date_str_weekday != parsed_weekday:
            raise ValueError(
                f'weekday provided in {repr(date_str)} was not the same as the '
                f'weekday parsed from it ('
                f'got: {parsed_weekday}, want: {date_str_weekday})')
        return parsed_date

    try:
        parsed_date = dt.datetime.strptime(date_str, '%b %d, %Y').date()
    except ValueError:
        pass
    else:
        return parsed_date

    raise ValueError(
        f'{repr(date_str)} did not match any of the expected formats: '
        f'[\'%b %d, %Y\', \'%a %b %d, %Y\']')


class ParseDatesTest(unittest.TestCase):
    """Tests for the rn2md.util.ParseDates function."""

    @freezegun.freeze_time(StrictParseDate('Mar 24, 2018'))
    def testToday(self):
        self.assertEqual(util.ParseDates('today'), [
            StrictParseDate('Mar 24, 2018'),
        ])

    @freezegun.freeze_time(StrictParseDate('Fri Mar 23, 2018'))
    def testThisWeek(self):
        self.assertEqual(util.ParseDates('this week'), [
            StrictParseDate('Mon Mar 19, 2018'),
            StrictParseDate('Tue Mar 20, 2018'),
            StrictParseDate('Wed Mar 21, 2018'),
            StrictParseDate('Thu Mar 22, 2018'),
            StrictParseDate('Fri Mar 23, 2018'),
            StrictParseDate('Sat Mar 24, 2018'),
            StrictParseDate('Sun Mar 25, 2018'),
        ])

    @freezegun.freeze_time(StrictParseDate('Mon Mar 26, 2018'))
    def testLastWeek(self):
        self.assertEqual(util.ParseDates('last week'), [
            StrictParseDate('Mon Mar 19, 2018'),
            StrictParseDate('Tue Mar 20, 2018'),
            StrictParseDate('Wed Mar 21, 2018'),
            StrictParseDate('Thu Mar 22, 2018'),
            StrictParseDate('Fri Mar 23, 2018'),
            StrictParseDate('Sat Mar 24, 2018'),
            StrictParseDate('Sun Mar 25, 2018'),
        ])

    @freezegun.freeze_time(StrictParseDate('Sat Mar 24, 2018'))
    def testTodayOnSaturdayRoundsToFridayInWorkdaysOnlyMode(self):
        self.assertEqual(util.ParseDates('today', workdays_only=True), [
            StrictParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(StrictParseDate('Sun Mar 25, 2018'))
    def testTodayOnSundayRoundsToFridayInWorkdaysOnlyMode(self):
        self.assertEqual(util.ParseDates('today', workdays_only=True), [
            StrictParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(StrictParseDate('Sat Mar 24, 2018'))
    def testWorkWeekReturnedInWorkdayOnlyMode(self):
        self.assertEqual(util.ParseDates('this week', workdays_only=True), [
            StrictParseDate('Mon Mar 19, 2018'),
            StrictParseDate('Tue Mar 20, 2018'),
            StrictParseDate('Wed Mar 21, 2018'),
            StrictParseDate('Thu Mar 22, 2018'),
            StrictParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(StrictParseDate('Sun Mar 25, 2018'))
    def testYesterdayOnSundayReturnsFridayInWorkdaysOnlyMode(self):
        self.assertEqual(util.ParseDates('yesterday', workdays_only=True), [
            StrictParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(StrictParseDate('Mon Mar 26, 2018'))
    def testYesterdayOnMondayReturnsFridayInWorkdaysOnlyMode(self):
        self.assertEqual(util.ParseDates('yesterday', workdays_only=True), [
            StrictParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(StrictParseDate('Fri Mar 23, 2018'))
    def testTomorrowOnFridayReturnsMondayInWorkdaysOnlyMode(self):
        self.assertEqual(util.ParseDates('tomorrow', workdays_only=True), [
            StrictParseDate('Mon Mar 26, 2018'),
        ])

    @freezegun.freeze_time(StrictParseDate('Sat Mar 24, 2018'))
    def testTomorrowOnSaturdayReturnsMondayInWorkdaysOnlyMode(self):
        self.assertEqual(util.ParseDates('tomorrow', workdays_only=True), [
            StrictParseDate('Mon Mar 26, 2018'),
        ])


if __name__ == '__main__':
    unittest.main()
