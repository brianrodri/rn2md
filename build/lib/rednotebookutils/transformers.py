#!/usr/bin/env python3
"""Translates text in RedNotebook syntax to Markdown syntax.

Given a sequence of lines from stdin, this script will print out the same
sequence of lines but with any RedNotebook discovered syntax converted to
Markdown.

Here is a list of the currently supported transformations:

  RedNotebook             Markdown
  ===========             ========
  [name ""url""]          [name](url)
  //text//                _text_
  --text--                ~text~
  =Text=                  # Text
  [""url""]               ![...](url)
"""
import itertools
import iterutils
import os
import re


URL_PATTERN = re.compile(r"^(?:http|file|ftp)s?://"
                         r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"
                         r"(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
                         r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})" r"(?::\d+)?",
                         re.IGNORECASE)
LINK_PATTERN = re.compile(r"\[.*?\]\(.*?\)")
BACKTICK_PATTERN = re.compile(r"`.*?`")


def IsIntersecting(v, u):
  return v[1] >= u[0] and u[1] >= v[0]


def Span(string):
  return (0, len(string))


def OccursInUrl(match):
  """Check if regexp `match` occurs in some URL."""
  occurrences = itertools.chain(URL_PATTERN.finditer(match.string),
                                LINK_PATTERN.finditer(match.string))
  return any(IsIntersecting(match.span(), m.span()) for m in occurrences)


def OccursInBacktick(match):
  """Check if `match` occurs in backticks."""
  occurrences = BACKTICK_PATTERN.finditer(match.string)
  return any(IsIntersecting(match.span(), m.span()) for m in occurrences)


class Morpher(object):
  """Applies changes to multiple points of a string."""

  def __call__(self, string):
    """Find target substring(s); apply transformation(s); return result.

    Substrings are collected by the `FindRanges` method.  Each one is encoded
    through the use of a half-open index-range pair:

      lo, hi -> string[lo:hi]

    Example:
      class VowelsAs1337(Morpher):
        TRANSLATOR = string.maketrans("aeiou", "43105")

        def FindRanges(self, string):
          return [m.span() for m in re.finditer("[aeiou]", string.lower())]

        def Transform(self, old):
          return old.lower().translate(TRANSLATOR)


      morpher = VowelsAs1337()
      print(morpher("I love sour patches!"))
      >> 1 l0v3 s05r p4tch3s!

    Args:
      string: The string that is used as transformed according to the rules
      defined by self's FindRanges and Transform methods.
    Returns:
      transformed_piece: string, with all substr defined by
      self.FindRanges(string) replaced with the result of
      self.Transform(substr).
    """
    ranges = [(0, 0)] + self.FindRanges(string) + [(len(string), len(string))]
    output = ""
    bounds = zip(ranges[:-2], ranges[1:-1], ranges[2:])
    is_first = True
    for (_, prevhi), (currlo, currhi), (nextlo, _) in bounds:
      if is_first:
        output += string[prevhi:currlo]
        is_first = False
      output += self.Transform(string[currlo:currhi])
      output += string[currhi:nextlo]
    return output or string

  def FindRanges(self, string):  # pylint: disable=unused-argument
    """Get indicies of substrings that should have Transform applied to them.

    Args:
      string: string to analyze for transformation ranges.
    Returns:
      ranges: A collection of index ranges that identify the substrings in
      string to be replaced with a transformation.
    """
    return []

  def Transform(self, old):
    """Transform string-string `old` as desired.

    Args:
      old: Input string to be transformed.
    Returns:
      new: The transformed string.
    """
    return old


class TranslateItalics(Morpher):

  def FindRanges(self, string):
    matches = (m for m in re.finditer(r"//", string) if
               not OccursInUrl(m) and not OccursInBacktick(m))
    return [(lo.start(), hi.end())
            for lo, hi in iterutils.grouper(2, matches) if all((lo, hi))]

  def Transform(self, old):
    return "_{}_".format(old[2:-2])


class TranslateImages(Morpher):

  def Transform(self, old):
    # `old` is: [""file://url"".ext]
    return "![]({})".format(old[5:-7] + old[-5:-1])

  def FindRanges(self, string):
    return [m.span() for m in
            re.finditer(r'\[""file://.*?""\.(jpg|tif|png|gif)\]', string)]


class TranslateLinks(Morpher):

  def Transform(self, old):
    # `old` is: [name ""url""]
    url_span = re.search(r'\s""', old).end(), len(old) - 3
    name_span = 1, re.search(r'\s""', old).start()
    name = old[name_span[0]:name_span[1]].strip()
    url = old[url_span[0]:url_span[1]].strip()
    return "[{}]({})".format(name, url.replace("_", "\\_").replace("*", "\\*"))

  def FindRanges(self, string):
    return [m.span() for m in re.finditer(r'\[[^"].*?""\]', string)]


class TranslateStrikethroughs(Morpher):

  def Transform(self, old):
    # `old` is: --text--
    return "~~{}~~".format(old[2:-2])

  def FindRanges(self, string):
    matches = (m for m in re.finditer(r"--", string) if
               not OccursInUrl(m) and not OccursInBacktick(m))
    return [(lo.start(), hi.end())
            for lo, hi in iterutils.grouper(2, matches) if all((lo, hi))]


class TranslateHeaders(Morpher):

  def __init__(self, padding=0):
    self.padding = padding

  def Transform(self, old):
    # `old` is: =text= (w/ non-zero number of wrapping ='s)
    level = re.search(r"^=+", old).end()
    return "#"*(self.padding + level) + " " + old[level:-level]

  def FindRanges(self, string):
    affixes = re.search("[^=]", string), re.search("[^=]", string[::-1])
    if all(a and a.start() for a in affixes):
      if affixes[0].start() == affixes[1].start():
        return [Span(string)]
    return []


class TranslateLists(Morpher):
  """Enumerates syntactically sequential numbered lists."""

  def __init__(self):
    self.history = []
    self.missed_one = False

  def Transform(self, old):
    # `old` is `+`
    return str(self.history[-1]) + "."

  def FindRanges(self, string):
    m = re.search(r"^\s*(\+|-)\s", string)
    if m is None:
      self._UpdateMisses()
    else:
      self._ResizeHistory(m.end(1))
      if m.group(1) == "+":
        self.history[-1] += 1
        return [m.span(1)]
    return []

  def _UpdateMisses(self):
    if self.missed_one:
      del self.history[:]
    else:
      self.missed_one = True

  def _ResizeHistory(self, size):
    self.missed_one = False
    self.history = self.history[:size] + [0]*(size - len(self.history))


class FirstLineToHeader(Morpher):

  def __init__(self):
    self.past_first_line = False

  def FindRanges(self, string):
    return [] if self.past_first_line else [Span(string)]

  def Transform(self, old):
    self.past_first_line = True
    return "# " + old


class EscapeInnerUnderscores(Morpher):

  def FindRanges(self, string):
    return [m.span() for m in re.finditer(r"(?<=\w)_(?=\w)", string)
            if not OccursInUrl(m) and not OccursInBacktick(m)]

  def Transform(self, old):
    return "\\_"


class TranslateBackticks(Morpher):

  def __init__(self):
    self.line_num = 0

  def FindRanges(self, string):
    return [m.span() for m in re.finditer("``.*?``", string)
            if not OccursInUrl(m)]

  def Transform(self, old):
    return old[1:-1]  # Trim off the outermost ticks.


def main():
  pass


if __name__ == "__main__":
  main()
