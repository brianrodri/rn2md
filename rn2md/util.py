#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""TODO(brianrodri): Better module doc string."""
from typing import List

import datetime as dt
import time

import isoweek
import parsedatetime as pdt


def ParseDates(date_str: str, workdays_only: bool = False) -> List[dt.date]:
    """Returns the inferred dates described by the given date str.

    Args:
        date_str: A string parseable by parsedatetime.
        workdays_only: Whether to return only workdays (Mon-Fri)
    Returns:
        The list of datetime.date objects interpreted from the string.
    """
    noon_time_struct = dt.datetime.today().replace(hour=12).timetuple()
    # I use "today at noon" as the source time for `parsedatetime` to avoid
    # rounding errors in unit tests. Without it, date arithemtic is 1-day off.
    # This does not effect actual usage because Rednotebook can only be indexed
    # by DD-MM-YYYY anyway; HH-MM-SS is ignored.
    time_struct, result = pdt.Calendar().parse(date_str, noon_time_struct)
    if not result:
        raise ValueError(f'{date_str} could not be parsed into a date')
    parsed_date = dt.datetime(*time_struct[:6]).date()
    if 'week' in date_str:
        days = _GetWeekDays(parsed_date)
        return days[:5] if workdays_only else days
    else:
        return [_RoundToWorkday(parsed_date) if workdays_only else parsed_date]


def _GetWeekDays(date):
    week_number = date.isocalendar()[1]
    return isoweek.Week(date.year, week_number).days()


def _RoundToWorkday(date):
    if date.weekday() not in range(5):
        if dt.date.today() < date:
            workday_delta = date.weekday() - 7  # round to Monday.
        else:
            workday_delta = date.weekday() - 4  # round to Friday.
    else:
        workday_delta = 0
    return date - dt.timedelta(days=workday_delta)
