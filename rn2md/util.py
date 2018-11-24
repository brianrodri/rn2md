"""Arbitrary utility functions for the rn2md tool."""
from typing import List

import datetime as dt

import isoweek
import parsedatetime as pdt


def parse_dates(date_str: str, workdays_only: bool = False) -> List[dt.date]:
    """Returns the dates interpreted from the given string.

    Args:
        date_str: A string parseable by parsedatetime.
        workdays_only: Whether to return only workdays (Mon-Fri)
    Returns:
        List of datetime.date objects interpreted from the string.
    Raises:
        ValueError: date_str could not be parsed.
    """
    noon_tuple = dt.datetime.today().replace(hour=12).timetuple()
    # I use "today at noon" as the source-time for `parsedatetime` to avoid
    # rounding errors in unit tests. Without it, date arithmetic is 1-day off.
    # This does not effect actual usage because RedNotebook can only be indexed
    # by DD-MM-YYYY anyway, HH-MM-SS gets ignored.
    parsed_time_struct, result = pdt.Calendar().parse(date_str, noon_tuple)
    if not result:
        raise ValueError('%s could not be parsed into a date' % date_str)
    parsed_date = dt.datetime(*parsed_time_struct[:6]).date()
    get_days = (_get_week_days if 'week' in date_str else _get_single_day)
    return get_days(parsed_date, workdays_only)


def _get_week_days(date: dt.date, workdays_only: bool) -> List[dt.date]:
    week_number = date.isocalendar()[1]
    week = isoweek.Week(date.year, week_number).days()
    return week[:5] if workdays_only else week


def _get_single_day(date: dt.date, workdays_only: bool) -> List[dt.date]:
    if workdays_only and date.weekday() in (5, 6):  # Sat, Sun = 5, 6
        if date > dt.date.today():
            workday_delta = 7 - date.weekday()  # round to next Mon
        else:
            workday_delta = 4 - date.weekday()  # round to last Fri
    else:
        workday_delta = 0
    return [date + dt.timedelta(days=workday_delta)]
