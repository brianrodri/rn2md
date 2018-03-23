#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Translates text in RedNotebook syntax to Markdown syntax.

Given a sequence of lines from stdin, this script will print out the same
sequence of lines but with any RedNotebook discovered syntax converted to
Markdown.

Here is a list of the currently supported transformations:

    RedNotebook                         Markdown
    ===========                         ========
    [name ""url""]                    [name](url)
    //text//                                _text_
    --text--                                ~text~
    =Text=                                    # Text
    [""url""]                             ![...](url)
"""
import codecs
import collections
from datetime import datetime
import itertools
import os
import yaml


def GetMonthsData(data_path):
    try:
        for basename in os.listdir(data_path):
            root, unused_ext = os.path.splitext(basename)
            try:
                month_date = datetime.strptime(root, "%Y-%m").date()
                month_path = os.path.join(data_path, basename)
                yield (month_date, month_path)
            except ValueError:
                continue
    except FileNotFoundError:
        pass


def LoadDailyEntries(month_data):
    month_data = (month_date, month_path)
    daily_entries = dict()
    with codecs.open(month_path, "rb", encoding="utf-8") as month_file:
        contents = yaml.load(month_file)
        for day_of_month in contents:
            day_key = month_date.replace(day=day_of_month)
            day_entry = contents[day_of_month]["text"].rstrip()
            if day_entry:
                daily_entries[day_key] = day_entry
    return daily_entries


def BuildDailyEntriesDict(data_path):
    all_daily_entries = dict()
    for daily_entries in map(LoadDailyEntries, GetMonthsData(data_path)):
        all_daily_entries.update(daily_entries)
    return all_daily_entries


def main():
    daily_entries = (
            BuildDailyEntriesDict(os.path.expanduser('~/.rednotebook/data')))
    def PrintEntry(day):
        return str(day) + "\n" + daily_entries[day]
    print("\n\n\n".join(map(PrintEntry, itertools.islice(daily_entries, 3))))


if __name__ == "__main__":
    main()
