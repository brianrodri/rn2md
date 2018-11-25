"""Test cases for the rn2md_util module."""
import unittest

import datetime as dt
import freezegun

from rn2md import util


class StrictParseDate(unittest.TestCase):
    pass


class ParseDatesTest(unittest.TestCase):
    """Tests for the rn2md.rn2md_util.parse_dates function."""

    @freezegun.freeze_time(util.strict_parse_date('Mar 24, 2018'))
    def test_today(self):
        """Tests that today returns a single-element list for today's date."""
        self.assertEqual(util.parse_dates('today'), [
            util.strict_parse_date('Mar 24, 2018'),
        ])

    @freezegun.freeze_time(util.strict_parse_date('Fri Mar 23, 2018'))
    def test_this_week(self):
        """Tests that this week returns all dates in the week."""
        self.assertEqual(util.parse_dates('this week'), [
            util.strict_parse_date('Mon Mar 19, 2018'),
            util.strict_parse_date('Tue Mar 20, 2018'),
            util.strict_parse_date('Wed Mar 21, 2018'),
            util.strict_parse_date('Thu Mar 22, 2018'),
            util.strict_parse_date('Fri Mar 23, 2018'),
            util.strict_parse_date('Sat Mar 24, 2018'),
            util.strict_parse_date('Sun Mar 25, 2018'),
        ])

    @freezegun.freeze_time(util.strict_parse_date('Mon Mar 26, 2018'))
    def test_last_week(self):
        """Tests that last week returns all dates from last week."""
        self.assertEqual(util.parse_dates('last week'), [
            util.strict_parse_date('Mon Mar 19, 2018'),
            util.strict_parse_date('Tue Mar 20, 2018'),
            util.strict_parse_date('Wed Mar 21, 2018'),
            util.strict_parse_date('Thu Mar 22, 2018'),
            util.strict_parse_date('Fri Mar 23, 2018'),
            util.strict_parse_date('Sat Mar 24, 2018'),
            util.strict_parse_date('Sun Mar 25, 2018'),
        ])

    @freezegun.freeze_time(util.strict_parse_date('Sat Mar 24, 2018'))
    def test_today_on_saturday_rounds_to_friday_in_workdays_only_mode(self):
        """Tests workday-mode rounds to friday on saturdays."""
        self.assertEqual(util.parse_dates('today', workdays_only=True), [
            util.strict_parse_date('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(util.strict_parse_date('Sun Mar 25, 2018'))
    def test_today_on_sunday_rounds_to_friday_in_workdays_only_mode(self):
        """Tests workday-mode rounds to friday on sundays."""
        self.assertEqual(util.parse_dates('today', workdays_only=True), [
            util.strict_parse_date('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(util.strict_parse_date('Sat Mar 24, 2018'))
    def test_work_week_returned_in_workday_only_mode(self):
        """Tests only workdays are returned in workday-mode."""
        self.assertEqual(util.parse_dates('this week', workdays_only=True), [
            util.strict_parse_date('Mon Mar 19, 2018'),
            util.strict_parse_date('Tue Mar 20, 2018'),
            util.strict_parse_date('Wed Mar 21, 2018'),
            util.strict_parse_date('Thu Mar 22, 2018'),
            util.strict_parse_date('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(util.strict_parse_date('Sun Mar 25, 2018'))
    def test_yesterday_on_sunday_returns_friday_in_workdays_only_mode(self):
        """Tests yesterday on sunday is friday for workday-mode."""
        self.assertEqual(util.parse_dates('yesterday', workdays_only=True), [
            util.strict_parse_date('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(util.strict_parse_date('Mon Mar 26, 2018'))
    def test_yesterday_on_monday_returns_friday_in_workdays_only_mode(self):
        """Tests yesterday on monday is friday for workday-mode."""
        self.assertEqual(util.parse_dates('yesterday', workdays_only=True), [
            util.strict_parse_date('Fri Mar 23, 2018'),
        ])

    @freezegun.freeze_time(util.strict_parse_date('Fri Mar 23, 2018'))
    def test_tomorrow_on_friday_returns_monday_in_workdays_only_mode(self):
        """Tests tomorrow on friday is monday for workday-only mode."""
        self.assertEqual(util.parse_dates('tomorrow', workdays_only=True), [
            util.strict_parse_date('Mon Mar 26, 2018'),
        ])

    @freezegun.freeze_time(util.strict_parse_date('Sat Mar 24, 2018'))
    def test_tomorrow_on_saturday_returns_monday_in_workdays_only_mode(self):
        """Tests tomorrow on saturday is monday for workday-only mode."""
        self.assertEqual(util.parse_dates('tomorrow', workdays_only=True), [
            util.strict_parse_date('Mon Mar 26, 2018'),
        ])


if __name__ == '__main__':
    unittest.main()
