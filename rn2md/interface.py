#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import datetime
import isoweek
import parsedatetime
import sys


def ParseDates(date_str, workdays_only=True):
    """Returns the inferred dates described by the given date str."""
    struct_time, _ = parsedatetime.Calendar().parse(date_str)
    parsed_date = datetime.date(*struct_time[:3])
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
        if date < datetime.date.today():
            workday_delta = date.weekday() - 4  # round to Friday
        else:
            workday_delta = date.weekday() - 7  # round to Monday
    else:
        workday_delta = 0
    return date - datetime.timedelta(days=workday_delta)


if __name__ == "__main__":
    print(ParseDates(" ".join(sys.argv[1:]) or "today"))
