#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""TODO(brianrodri): Better module doc string."""
import datetime as dt
import os
import yaml


def LoadDailyEntries(data_path):
    all_daily_entries = {}
    for month_date, month_path in _LoadMonthPaths(data_path):
        with open(month_path, 'rb', encoding='utf-8') as month_file:
            all_daily_entries.update(_LoadDailyEntries(month_date, month_file))
    return all_daily_entries


def _LoadMonthPaths(data_path):
    for dir_entry in os.scandir(data_path):
        if dir_entry.is_file():
            file_root = os.path.splitext(dir_entry.name)[0]
            try:
                month_date = dt.datetime.strptime(file_root, '%Y-%m').date()
                yield (month_date, dir_entry.path)
            except ValueError:
                continue


def _LoadDailyEntries(month_date, month_file):
    try:
        month_file_content = yaml.safe_load(month_file)
    except yaml.YAMLError:
        return {}
    daily_entries = {}
    for day_of_month, month_content in month_file_content.items():
        day_key = month_date.replace(day=day_of_month)
        day_entry = month_content['text'].rstrip()
        if day_entry:
            daily_entries[day_key] = day_entry
    return daily_entries
