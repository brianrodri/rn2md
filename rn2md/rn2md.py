#!/usr/local/bin/python3
from __future__ import print_function

import functools
import itertools
from interface import DatesFromArgv
from storage import BuildDailyLogDict
from transformers import EscapeInnerUnderscores
from transformers import TranslateBackticks
from transformers import TranslateHeaders
from transformers import TranslateImages
from transformers import TranslateItalics
from transformers import TranslateLinks
from transformers import TranslateLists
from transformers import TranslateStrikethroughs


def ComposeL(*iterable):
  def Compose2(f, g):
    return lambda x: g(f(x))
  return functools.reduce(Compose2, iterable, lambda x: x)


def FormatDay(day, database):
  rn2md = ComposeL(TranslateHeaders(padding=1), TranslateBackticks(),
                   TranslateImages(), TranslateLinks(), TranslateItalics(),
                   TranslateLists(), TranslateStrikethroughs(),
                   EscapeInnerUnderscores())
  header = day.strftime("# %b %d, %Y")
  body_as_lines = (line.rstrip() for line in database[day].split("\n"))
  return "\n".join(rn2md(l) for l in itertools.chain([header], body_as_lines))


def main():
  database = BuildDailyLogDict()
  prettify = lambda day: FormatDay(day, database)
  print("\n\n\n".join(prettify(d) for d in DatesFromArgv() if d in database))


if __name__ == "__main__":
  main()
