#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""TODO(brianrodri): Better module doc string."""
import datetime
import itertools
import sys

import functional

import config
import interface
import storage
import transformers


def RedNotebookToMarkDown(line):
    transformer = functional.compose(
            transformers.HeaderTransformer(start_level=1),
            transformers.BacktickTransformer(),
            transformers.ImageTransformer(),
            transformers.LinkTransformer(),
            transformers.ItalicTransformer(),
            transformers.ListTransformer(),
            transformers.StrikethroughTransformer(),
            transformers.InnerUnderscoreEscaper())
    return transformer(line)


def main():
    options, remaining_argv = config.BuildConfigOptions()
    entries = storage.BuildDailyEntriesDict(options.DataPath())
    dates = interface.ParseDates(
            ' '.join(remaining_argv), workdays_only=options.WorkdaysOnly())
    def FormatDate(date):
        output_lines = [date.strftime('# %a %b %d, %Y')]
        output_lines.extend(line.rstrip() for line in entries[date].split('\n'))
        return '\n'.join(map(RedNotebookToMarkDown, output_lines))

    print('\n\n\n'.join(FormatDate(d) for d in dates if d in entries))


if __name__ == '__main__':
    main()
