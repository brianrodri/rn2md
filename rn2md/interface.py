#!/usr/local/bin/python3
from __future__ import print_function

import sys

import argparse
import datetime


def ValidDate(s, fmt="%Y-%m-%d"):
  try:
    return datetime.date.strptime(s, fmt)
  except ValueError:
    raise argparse.ArgumentTypeError(
        "'{}' does not match the format: {}.".format(s, fmt))


def ExpandDateRange(lo, hi):
  """Inclusive."""
  return [lo + datetime.timedelta(n) for n in range((hi - lo).days + 1)]


def DatesFromArgv(argv=sys.argv[1:]):
  """Parses input to interpret a target date range."""
  parser = argparse.ArgumentParser()
  subparsers = parser.add_subparsers(dest="command")
  today_parser = subparsers.add_parser(  # pylint: disable=unused-variable
      "today", help="Print today's entry.")
  yesterday_parser = subparsers.add_parser(
      "yesterday", help="Print yesterday's entry.")
  yesterday_parser = yesterday_parser.add_argument(
      "-w", "--work_days", help="Interpret as `Fri` on Sun and Mon.",
      action="store_false")
  week_parser = subparsers.add_parser(
      "week", help="Print an entire week's entries.")
  week_parser.add_argument(
      "week_number", default=datetime.date.today().isocalendar()[1], type=int,
      help="Week number of year.  Defaults to this week.", nargs="?")
  week_parser.add_argument(
      "-y", "--year", default=datetime.date.today().year, type=int,
      help="The reference year for the week number.")
  week_parser.add_argument(
      "-o", "--offset", default=0, type=int,
      help="Offset number of weeks from this week.")
  range_parser = subparsers.add_parser(
      "range", help="Print entries within specified YYYY-MM-DD date range.")
  range_parser.add_argument(
      "-b", "--begin_date", dest="begin", type=ValidDate, required=True)
  range_parser.add_argument(
      "-e", "--end_date", dest="end", type=ValidDate, required=True)
  parser.set_defaults(command="today")

  args = parser.parse_args(argv)
  if args.command == "today":
    # This is the default option.
    dates = [datetime.date.today()]
  elif args.command == "week":
    # Determine members of a specified week number.
    d = "{}-W{}".format(args.year, args.week_number)
    start = datetime.datetime.strptime(d + "-1", "%Y-W%W-%w").date()
    start += datetime.timedelta(7*args.offset)
    end = start + datetime.timedelta(6)
    dates = ExpandDateRange(start, end)
  elif args.command == "yesterday":
    # Can be configured to use workdays.
    today = datetime.date.today()
    if not args.work_days or today.weekday() in range(1, 6):  # Tue - Sat.
      yesterday = today + datetime.timedelta(-1)
    elif today.weekday() == 6:                                # Sun.
      yesterday = today + datetime.timedelta(-2)
    else:                                                     # Mon.
      yesterday = today + datetime.timedelta(-3)
    dates = [yesterday]
  elif args.command == "range":
    # We've been given an explicit date-range.
    dates = ExpandDateRange(args.begin, args.end)
  return dates


def main():
  print("\n".join(str(date) for date in DatesFromArgv()))


if __name__ == "__main__":
  main()
