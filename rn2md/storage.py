#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""TODO(brianrodri): Better module doc string."""
import codecs
import collections
from datetime import datetime
import itertools
import os
import yaml


def _GetMonthsData(data_path):
    if not os.path.exists(data_path):
        return
    for dir_entry in os.scandir(data_path):
        if dir_entry.is_file():
            month_root, unused_ext = os.path.splitext(dir_entry)
            try:
                month_date = datetime.strptime(month_root, '%Y-%m').date()
                month_path = os.path.join(data_path, dir_entry)
                yield (month_date, month_path)
            except ValueError:
                continue


def _LoadDailyEntries(month_data):
    month_date, month_path = month_data
    daily_entries = dict()
    with codecs.open(month_path, 'rb', encoding='utf-8') as month_file:
        month_contents = yaml.load(month_file)
        for day_of_month, month_content in month_contents.iteritems():
            day_key = month_date.replace(day=day_of_month)
            day_entry = month_content['text'].rstrip()
            if day_entry:
                daily_entries[day_key] = day_entry
    return daily_entries


def BuildDailyEntriesDict(data_path):
    all_daily_entries = dict()
    for daily_entries in map(_LoadDailyEntries, _GetMonthsData(data_path)):
        all_daily_entries.update(daily_entries)
    return all_daily_entries


def main():
    daily_entries = (
        BuildDailyEntriesDict(os.path.expanduser('~/.rednotebook/data')))
    def PrintEntry(day):
        return str(day) + '\n' + daily_entries[day]
    print('\n\n\n'.join(map(PrintEntry, itertools.islice(daily_entries, 3))))


if __name__ == '__main__':
    main()
