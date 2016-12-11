#!/usr/bin/env python3
import functools
from interface import DatesFromArgv
from storage import BuildDailyLogDict
from transformers import (EscapeInnerUnderscores, TranslateBackticks,
                          TranslateHeaders, TranslateImages,
                          TranslateItalics, TranslateLinks,
                          TranslateLists, TranslateStrikethroughs)


def FormatDay(day, database):
  def ComposeL(*iterable):
    def Compose2(f, g):
      return lambda x: g(f(x))
    return functools.reduce(Compose2, iterable, lambda x: x)
  rn2md = ComposeL(TranslateHeaders(padding=1), TranslateBackticks(),
                   TranslateImages(), TranslateLinks(), TranslateItalics(),
                   TranslateLists(), TranslateStrikethroughs(),
                   EscapeInnerUnderscores())
  head = day.strftime("%b %d, %Y")
  body = (line.rstrip() for line in database[day].split("\n"))
  formatted_head = "# " + head.rstrip()
  formatted_body = "\n".join(map(rn2md, body)).rstrip()
  if formatted_body:
    return formatted_head + "\n" + formatted_body
  else:
    return formatted_head


def main():
  database = BuildDailyLogDict()
  prettify = lambda day: FormatDay(day, database)
  print("\n\n\n".join(prettify(d) for d in DatesFromArgv() if d in database))


if __name__ == "__main__":
  main()
