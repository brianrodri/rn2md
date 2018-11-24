"""Module for accessing existing RedNotebook data on a local computer."""
import datetime as dt
import io
import os

import yaml


def load_daily_entries(data_path):
    """Extracts the Rednotebook-styled data found in the given path."""
    daily_entries = {}
    for month_date, month_path in _load_month_paths(data_path):
        with open(month_path, encoding='utf-8') as month_file:
            daily_entries.update(_load_daily_entries(month_date, month_file))
    return daily_entries


def _load_month_paths(data_path):
    """Returns files from the data_path which contain RedNotebook data."""
    for dir_entry in os.scandir(data_path):
        if not dir_entry.is_file():
            pass
        file_root, unused_ext = os.path.splitext(dir_entry.name)
        try:
            month_date = dt.datetime.strptime(file_root, '%Y-%m').date()
        except ValueError:
            continue
        else:
            yield (month_date, dir_entry.path)


def _load_daily_entries(month_date, month_file):
    """Returns mapping of the month file's daily entries as strings."""
    try:
        month_file_content = yaml.safe_load(month_file)
    except yaml.YAMLError:
        return {}
    daily_entries = {}
    for day_of_month, content in month_file_content.items():
        day_date = month_date.replace(day=day_of_month)
        entry = content['text'].rstrip()
        if entry:
            daily_entries[day_date] = entry
    return daily_entries
