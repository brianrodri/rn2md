#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""TODO(brianrodri): Better module doc string."""
import sys

import config
import util
import storage
import transformers


def RedNotebookToMarkDown(day_entry_lines):
    generators = [
        transformers.InnerUnderscoreEscaper(),
        transformers.LinkTransformer(),
        transformers.HeaderTransformer(base_level=1),
        transformers.CodeBlockTransformer(),
        transformers.ItalicTransformer(),
        transformers.ListTransformer(),
        transformers.StrikethroughTransformer(),
    ]
    map(next, generators)  # Prepare each generator to begin receiving lines.
    for line in day_entry_lines:
        for generator in generators:
            line = generator.send(line)
        yield line


def main():
    options, remaining_argv = config.BuildConfigOptions(sys.argv)
    daily_entries = storage.LoadDailyEntries(options.DataPath())
    def FormatDate(date):
        day_entry_lines = [date.strftime('# %a %b %d, %Y')]
        day_entry_lines.extend(
            l.rstrip() for l in daily_entries[date].split('\n'))
        return '\n'.join(RedNotebookToMarkDown(day_entry_lines))

    dates = util.ParseDates(
        ' '.join(remaining_argv), workdays_only=options.WorkdaysOnly())
    print('\n\n\n'.join(FormatDate(d) for d in dates if d in daily_entries))


if __name__ == '__main__':
    main()
