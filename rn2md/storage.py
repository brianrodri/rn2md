"""Module for accessing existing RedNotebook data on a local computer."""
import datetime as dt
import os

import yaml


def load_rednotebook_entries(data_path):
    """Extracts the Rednotebook-styled data found in the given path."""
    rednotebook = {}
    for month_date, month_path in _load_month_paths(data_path):
        with open(month_path, encoding='utf-8') as month_file:
            rednotebook.update(_load_daily_entries(month_date, month_file))
    return rednotebook


def _load_month_paths(data_path):
    """Returns files from the data_path which contain RedNotebook data."""
    for item in os.scandir(data_path):
        if not item.is_file():
            continue
        file_root, unused_ext = os.path.splitext(item.name)
        try:
            month_date = dt.datetime.strptime(file_root, '%Y-%m').date()
        except ValueError:
            continue
        else:
            yield (month_date, item.path)


def _load_daily_entries(month_date, month_file):
    """Returns mapping of the month file's daily entries as strings."""
    month_file_content = yaml.safe_load(month_file)
    if not isinstance(month_file_content, dict):
        return {}
    return {
        month_date.replace(day=day): entry
        for day, day_content in month_file_content.items()
        if (entry := day_content['text'].rstrip())
    }
