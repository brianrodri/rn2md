#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import unittest

import dateutil
import freezegun

from rn2md import util


def StrToDate(date_str):
    """Interprets a pretty date_str into datetime.date"""
    return dateutil.parser.parse(date_str).date()


class ParseDatesTest(unittest.TestCase):
    """TODO(brianrodri).

    NOTE: Times are added to the freeze_time decorators to ensure that
    parsedateutil interprets the correct date (without them, parsedatetime lags
    by one day).
    """

    @freezegun.freeze_time('Mar 24th, 2018 5pm')
    def testToday(self):
        self.assertListEqual(util.ParseDates('today'), [
            StrToDate('Mar 24th, 2018'),
        ])

    @freezegun.freeze_time('Fri Mar 23rd, 2018 5pm')
    def testThisWeek(self):
        self.assertListEqual(util.ParseDates('this week'), [
            StrToDate('Mon Mar 19th, 2018'),
            StrToDate('Tue Mar 20th, 2018'),
            StrToDate('Wed Mar 21st, 2018'),
            StrToDate('Thu Mar 22nd, 2018'),
            StrToDate('Fri Mar 23rd, 2018'),
            StrToDate('Sat Mar 24th, 2018'),
            StrToDate('Sun Mar 25th, 2018'),
        ])

    @freezegun.freeze_time('Mon Mar 26th, 2018 9am')
    def testLastWeek(self):
        self.assertListEqual(util.ParseDates('last week'), [
            StrToDate('Mon Mar 19th, 2018'),
            StrToDate('Tue Mar 20th, 2018'),
            StrToDate('Wed Mar 21st, 2018'),
            StrToDate('Thu Mar 22nd, 2018'),
            StrToDate('Fri Mar 23rd, 2018'),
            StrToDate('Sat Mar 24th, 2018'),
            StrToDate('Sun Mar 25th, 2018'),
        ])

    @freezegun.freeze_time('Sat Mar 24th, 2018 12pm')
    def testTodayOnSaturdayRoundsToFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('today', workdays_only=True), [
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Sun Mar 25th, 2018 12pm')
    def testTodayOnSundayRoundsToFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('today', workdays_only=True), [
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Sat Mar 24th, 2018 12pm')
    def testWorkWeekReturnedInWorkdayOnlyMode(self):
        self.assertListEqual(util.ParseDates('this week', workdays_only=True), [
            StrToDate('Mon Mar 19th, 2018'),
            StrToDate('Tue Mar 20th, 2018'),
            StrToDate('Wed Mar 21st, 2018'),
            StrToDate('Thu Mar 22nd, 2018'),
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Sun Mar 25th, 2018 12pm')
    def testYesterdayOnSundayReturnsFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('yesterday', workdays_only=True), [
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Mon Mar 26th, 2018 9am')
    def testYesterdayOnMondayReturnsFridayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('yesterday', workdays_only=True), [
            StrToDate('Fri Mar 23rd, 2018'),
        ])

    @freezegun.freeze_time('Fri Mar 23rd, 2018 5pm')
    def testTomorrowOnFridayReturnsMondayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('tomorrow', workdays_only=True), [
            StrToDate('Mon Mar 26th, 2018'),
        ])

    @freezegun.freeze_time('Sat Mar 24th, 2018 12pm')
    def testTomorrowOnSaturdayReturnsMondayInWorkdaysOnlyMode(self):
        self.assertListEqual(util.ParseDates('tomorrow', workdays_only=True), [
            StrToDate('Mon Mar 26th, 2018'),
        ])


if __name__ == '__main__':
    unittest.main()
