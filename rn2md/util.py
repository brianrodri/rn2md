"""Arbitrary utility functions for the rn2md tool."""
import enum
import datetime as dt

import isoweek
import parsedatetime as pdt


def prime_coroutine_generator(coroutine_generator):
    """Call `next()` on the coroutine generator so it can accept `send()`."""
    @functools.wraps(coroutine_generator)
    def primed_coroutine_generator(*args, **kwargs):
        gen = coroutine_generator(*args, **kwargs)
        _ = next(gen, None)
        return gen
    return primed_coroutine_generator


_Weekdays = (  # pylint: disable=invalid-name
    enum.Enum('_Weekdays', 'Mon Tue Wed Thu Fri Sat Sun', start=0))


def parse_dates(date_str, workdays_only=False):
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
    # by DD-MM-YYYY anyway; HH-MM-SS gets ignored.
    parsed_time_struct, result = pdt.Calendar().parse(date_str, noon_tuple)
    if not result:
        raise ValueError(f'{date_str} could not be parsed into a date')
    parsed_date = dt.datetime(*parsed_time_struct[:6]).date()
    get_days = _get_week_days if 'week' in date_str else _get_single_day
    return get_days(parsed_date, workdays_only)


def strict_parse_date(date_str):
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
    fmt_with_dow = '%a %b %d, %Y'
    try:
        parsed_date = dt.datetime.strptime(date_str, fmt_with_dow).date()
    except ValueError:
        pass
    else:
        date_str_weekday = date_str[:3].capitalize()
        parsed_date_weekday = _Weekdays(parsed_date.weekday()).name
        if date_str_weekday != parsed_date_weekday:
            raise ValueError(
                f'{date_str!r} does not have the same weekday as the date '
                f'parsed from it. (expected: {date_str_weekday!r}, '
                f'actual: {parsed_date_weekday!r})')
        return parsed_date

    fmt_without_dow = '%b %d, %Y'
    try:
        parsed_date = dt.datetime.strptime(date_str, fmt_without_dow).date()
    except ValueError:
        pass
    else:
        return parsed_date

    raise ValueError(f'{date_str!r} is not a valid format (expected formats: '
                     f'[{fmt_with_dow!r}, {fmt_without_dow!r}])')


def _get_week_days(date, workdays_only):
    """Expand date to the surrounding days in that week.

    Args:
        date: the date which will be expanded into a week.
        workdays_only: whether to only return workdays (Mon - Fri).

    Returns:
        list of date objects that fall in the week of given date.
    """
    week_number = date.isocalendar()[1]
    week = isoweek.Week(date.year, week_number).days()
    return week[:5] if workdays_only else week


def _get_single_day(date, workdays_only):
    """Wrap given date in a list.

    Args:
        date: the date to wrap in a list.
        workdays_only: whether to round the date to the nearest workday.

    Returns:
        list with the single given date, optionally rounded to a workday.
    """
    if workdays_only and date.weekday() in (5, 6):  # Sat, Sun = 5, 6
        if date > dt.date.today():
            daydelta = dt.timedelta(days=7 - date.weekday())  # until next Mon
        else:
            daydelta = dt.timedelta(days=4 - date.weekday())  # since last Fri
    else:
        daydelta = dt.timedelta()
    return [date + daydelta]
