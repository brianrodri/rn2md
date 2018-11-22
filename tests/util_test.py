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


def ParseDate(date_str: str) -> dt.date:
    """Parses and validates the given date string.

    Args:
        date_str: Format must be: '%a %b %d, %Y' or '%b %d, %Y'.
    Returns:
        The parsed datetime.date instance.
    Raises:
        AssertionError: weekday provided in date_str was not the same as the
        weekday parsed from it.
    """
    try:
        parsed_datetime = dt.datetime.strptime(date_str, '%a %b %d, %Y')
    except ValueError:
        pass
    else:
        date_str_weekday = Weekdays[date_str[:3].capitalize()]
        parsed_weekday = Weekdays(parsed_datetime.weekday())
        if date_str_weekday != parsed_weekday:
            raise AssertionError(
                f'weekday provided in {repr(date_str)} was not the same as the '
                f'weekday parsed from it ('
                f'got: {parsed_weekday.name}, want: {date_str_weekday.name})')
        return parsed_datetime.date()

    try:
        parsed_datetime = dt.datetime.strptime(date_str, '%b %d, %Y')
    except ValueError:
        pass
    else:
        return parsed_datetime.date()

    raise ValueError(
        f'{repr(date_str)} did not match any of the expected formats: '
        f'[\'%b %d, %Y\', \'%a %b %d, %Y\']')


class ParseDatesTest(unittest.TestCase):
    """Tests for the rn2md.util.ParseDates function."""

    @freezegun.freeze_time(ParseDate('Mar 24, 2018'))
    def testToday(self):
        self.assertListEqual(util.ParseDates('today'), [
            ParseDate('Mar 24, 2018'),
        ])

    @freezegun.freeze_time(ParseDate('Fri Mar 23, 2018'))
    def testThisWeek(self):
        self.assertListEqual(util.ParseDates('this week'), [
            ParseDate('Mon Mar 19, 2018'),
            ParseDate('Tue Mar 20, 2018'),
            ParseDate('Wed Mar 21, 2018'),
            ParseDate('Thu Mar 22, 2018'),
            ParseDate('Fri Mar 23, 2018'),
            ParseDate('Sat Mar 24, 2018'),
            ParseDate('Sun Mar 25, 2018'),
        ])

    @freezegun.freeze_time(ParseDate('Mon Mar 26, 2018'))
    def testLastWeek(self):
        self.assertListEqual(util.ParseDates('last week'), [
            ParseDate('Mon Mar 19, 2018'),
            ParseDate('Tue Mar 20, 2018'),
            ParseDate('Wed Mar 21, 2018'),
            ParseDate('Thu Mar 22, 2018'),
            ParseDate('Fri Mar 23, 2018'),
            ParseDate('Sat Mar 24, 2018'),
            ParseDate('Sun Mar 25, 2018'),
        ])

    @freezegun.freeze_time(ParseDate('Sat Mar 24, 2018'))
    def testTodayOnSaturdayRoundsToFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('today', workdays_only=True), [
            ParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(ParseDate('Sun Mar 25, 2018'))
    def testTodayOnSundayRoundsToFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('today', workdays_only=True), [
            ParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(ParseDate('Sat Mar 24, 2018'))
    def testWorkWeekReturnedInWorkdayOnlyMode(self):
        self.assertListEqual(util.ParseDates('this week', workdays_only=True), [
            ParseDate('Mon Mar 19, 2018'),
            ParseDate('Tue Mar 20, 2018'),
            ParseDate('Wed Mar 21, 2018'),
            ParseDate('Thu Mar 22, 2018'),
            ParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(ParseDate('Sun Mar 25, 2018'))
    def testYesterdayOnSundayReturnsFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('yesterday', workdays_only=True), [
            ParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(ParseDate('Mon Mar 26, 2018'))
    def testYesterdayOnMondayReturnsFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('yesterday', workdays_only=True), [
            ParseDate('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(ParseDate('Fri Mar 23, 2018'))
    def testTomorrowOnFridayReturnsMondayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('tomorrow', workdays_only=True), [
            ParseDate('Mon Mar 26, 2018'),
        ])

    @freezegun.freeze_time(ParseDate('Sat Mar 24, 2018'))
    def testTomorrowOnSaturdayReturnsMondayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('tomorrow', workdays_only=True), [
            ParseDate('Mon Mar 26, 2018'),
        ])


if __name__ == '__main__':
    unittest.main()
