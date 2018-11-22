#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""TODO(brianrodri): Better module doc string."""
import collections
import sys

import config
import util
import storage
import transformers


def rn2md(lines):
    """Transform given lines from Markdown syntax to RedNotebook syntax."""
    required_transformer_sequence = [
        transformers.InnerUnderscoreEscaper(),
        transformers.LinkTransformer(),
        transformers.HeaderTransformer(base_level=1),
        transformers.CodeBlockTransformer(),
        transformers.ItalicTransformer(),
        transformers.StrikethroughTransformer(),
        transformers.ListTransformer(),
    ]
    # Transformers are generators, so they need to be prepared with an initial
    # call to `next`.
    for t in required_transformer_sequence:
        next(t)
    for line in lines:
        for t in required_transformer_sequence:
            line = t.send(line)
        yield line


if __name__ == '__main__':
    options, remaining_argv = config.BuildConfigOptions(sys.argv)
    daily_entries = storage.LoadDailyEntries(options.DataPath())
    target_date =' '.join(remaining_argv) or 'today'
    dates = util.ParseDates(target_date , workdays_only=options.WorkdaysOnly())

    def FormatDate(date):
        entry_lines = [date.strftime('# %a %b %d, %Y')]
        entry_lines.extend(l.rstrip() for l in daily_entries[date].split('\n'))
        return '\n'.join(rn2md(entry_lines))

    print('\n\n\n'.join(FormatDate(d) for d in dates if d in daily_entries))
