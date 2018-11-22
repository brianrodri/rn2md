#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""TODO(brianrodri): Better module doc string."""
from typing import List

import datetime as dt

import isoweek
import parsedatetime as pdt


def ParseDates(date_str: str, workdays_only: bool = False) -> List[dt.date]:
    """Returns the dates interpreted from the given string.

    Args:
        date_str: A string parseable by parsedatetime.
        workdays_only: Whether to return only workdays (Mon-Fri)
    Returns:
        List of datetime.date objects interpreted from the string.
    Raises:
        ValueError: date_str could not be parsed.
    """
    noon_time_struct = dt.datetime.today().replace(hour=12).timetuple()
    # I use "today at noon" as the source time for `parsedatetime` to avoid
    # rounding errors in unit tests. Without it, date arithemtic is 1-day off.
    # This does not effect actual usage because Rednotebook can only be indexed
    # by DD-MM-YYYY anyway, HH-MM-SS gets ignored.
    time_struct, result = pdt.Calendar().parse(date_str, noon_time_struct)
    if not result:
        raise ValueError(f'{date_str} could not be parsed into a date')
    parsed_date = dt.datetime(*time_struct[:6]).date()
    if 'week' in date_str:
        return _GetWeekDays(parsed_date, workdays_only)
    else:
        return [_RoundToWorkday(parsed_date) if workdays_only else parsed_date]


def _GetWeekDays(date: dt.date, workdays_only: bool):
    week_number = date.isocalendar()[1]
    week = isoweek.Week(date.year, week_number).days()
    return week[:5] if workdays_only else week


def _RoundToWorkday(date: dt.date):
    if date.weekday() in (5, 6):  # Sat, Sun = 5, 6
        if date > dt.date.today():
            workday_delta = 7 - date.weekday()  # round to next Mon
        else:
            workday_delta = 4 - date.weekday()  # round to last Fri
    else:
        workday_delta = 0
    return date + dt.timedelta(days=workday_delta)
