#!/usr/bin/env python3
"""Translates text in RedNotebook syntax to Markdown syntax.

Given a sequence of lines from stdin, this script will print out the same
sequence of lines but with any RedNotebook discovered syntax converted to
Markdown.

Here is a list of the currently supported transformations:

  RedNotebook             Markdown
  ===========             ========
  [name ""url""]          [name](url)
  //text//                _text_
  --text--                ~text~
  =Text=                  # Text
  [""url""]               ![...](url)
"""
import codecs
from datetime import datetime
import itertools
import os
import yaml

DATA_DIR = os.path.expanduser("~/.rednotebook/data")


def BuildMonthPaths():
  for basename in sorted(os.listdir(DATA_DIR)):
    root, _ = os.path.splitext(basename)
    try:
      yield (os.path.join(DATA_DIR, basename),
             datetime.strptime(root, "%Y-%m").date())
    except ValueError:
      pass


def LoadDaysFromPath(path_details):
  path, path_month = path_details
  days = dict()
  with codecs.open(path, "rb", encoding="utf-8") as month_file:
    contents = yaml.load(month_file, Loader=yaml.CLoader)
    for day_num in contents:
      day_log = contents[day_num]["text"].rstrip()
      if day_log:
        days[path_month.replace(day=day_num)] = day_log
  return days


def BuildDailyLogDict():
  collection = dict()
  for month in (LoadDaysFromPath(p) for p in BuildMonthPaths()):
    collection.update(month)
  return collection


def main():
  database = BuildDailyLogDict()
  print("\n\n\n".join(database[key] for key in itertools.islice(database, 5)))


if __name__ == "__main__":
  main()
