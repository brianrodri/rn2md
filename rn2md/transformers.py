#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Translates text in RedNotebook syntax to Markdown syntax.

Given a sequence of lines from stdin, this script will print out the same
sequence of lines but with any RedNotebook discovered syntax converted to
Markdown.

Here is a list of the currently supported transformations:

  RedNotebook             Markdown
  ===========             ========
  [name ""url""]          [name](url)
  //text//                _text_
  --text--                **IRRELEVANT**(text)
  =Text=                  # Text
  [""url""]               ![...](url)
"""
from __future__ import print_function

import itertools
import iterutils
import string
import re
import sys


URL_PATTERN = re.compile(r'^(?:http|file|ftp)s?://'
                         r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
                         r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                         r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
                         r'(?::\d+)?',
                         re.IGNORECASE)
LINK_PATTERN = re.compile(r'\[.*?\]\(.*?\)')
BACKTICK_PATTERN = re.compile(r'`.*?`')


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

    def __call__(self, s):
        """Find target substring(s), apply transformation, return result.

        Substrings are collected by the `FindRanges` method. Each one is
        describes the half-open ranges to transform:

        (lo, hi) -> s[lo:hi]

        Example:
        >>> class VowelsAs1337(Morpher):
        ...     TRANSLATOR = string.maketrans('aeiou', '43105')
        ...
        ...     def FindRanges(self, s):
        ...         return [m.span() for m in re.finditer('[aeiou]', s.lower())]
        ...
        ...     def Transform(self, old):
        ...         return old.lower().translate(TRANSLATOR)
        ...
        >>> morpher = VowelsAs1337()
        >>> print(morpher('I love sour patches!'))
        1 l0v3 s05r p4tch3s!

        Args:
            s: The string that is used as transformed according to the rules
                defined by self's FindRanges and Transform methods.

        Returns:
            transformed_piece: str. Substrs defined by self.FindRanges(s)
                are replaced with the result of self.Transform(substr).
        """
        ranges = self.FindRanges(s)
        output = ''
        bounds = zip(ranges[:-2], ranges[1:-1], ranges[2:])
        at_first = True
        for (_, prevhi), (currlo, currhi), (nextlo, _) in bounds:
            if at_first:
                output += s[prevhi:currlo]
                at_first = False
            output += self.Transform(s[currlo:currhi])
            output += s[currhi:nextlo]
        return output or s

    def FindRanges(self, s):  # pylint: disable=unused-argument
        """Get indicies of substrings that should have Transform applied to them.

        Args:
            s: string to analyze for transformation ranges.

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


class ItalicTransformer(Morpher):

    def FindRanges(self, s):
        matches = (
            m for m in re.finditer(r'//', s)
            if not OccursInUrl(m) and not OccursInBacktick(m))
        return [
            (lo.start(), hi.end())
            for lo, hi in iterutils.grouper(2, matches)
            if all((lo, hi))
        ]

    def Transform(self, old):
        return '_{}_'.format(old[2:-2])


class ImageTransformer(Morpher):

    def FindRanges(self, s):
        return [m.span() for m in
                re.finditer(r'\[""file://.*?""\.(jpg|tif|png|gif)\]', s)]

    def Transform(self, old):
        # `old` is: [""file://url"".ext]
        return '![]({})'.format(old[5:-7] + old[-5:-1])


class LinkTransformer(Morpher):

    def FindRanges(self, s):
        return [m.span() for m in re.finditer(r'\[[^"].*?""\]', s)]

    def Transform(self, old):
        # `old` is: [name ""url""]
        url_span = re.search(r'\s""', old).end(), len(old) - 3
        name_span = 1, re.search(r'\s""', old).start()
        name = old[name_span[0]:name_span[1]].strip()
        url = old[url_span[0]:url_span[1]].strip()
        return '[{}]({})'.format(name, url.replace('_', '\\_').replace('*', '\\*'))


class StrikethroughTransformer(Morpher):

    def FindRanges(self, s):
        matches = (m for m in re.finditer(r'--', s) if
                not OccursInUrl(m) and not OccursInBacktick(m))
        return [(lo.start(), hi.end())
                for lo, hi in iterutils.grouper(2, matches) if all((lo, hi))]

    def Transform(self, old):
        # `old` is: --text--
        return '**IRRELEVANT**({})'.format(old[2:-2].rstrip('.!:'))


class HeaderTransformer(Morpher):
    """'==TEXT==' to '## TEXT'; input.count('=') == output.count('#') * 2."""

    def __init__(self, start_level=0):
        self.start_level = start_level

    def FindRanges(self, s):
        affixes = re.search('[^=]', s), re.search('[^=]', s[::-1])
        if all(a and a.start() for a in affixes):
            if affixes[0].start() == affixes[1].start():
                return [Span(s)]
        return []

    def Transform(self, old):
        level = re.search(r'^=+', old).end()
        return '#'*(self.start_level + level) + ' ' + old[level:-level]


class ListTransformer(Morpher):
    """Enumerates syntactically sequential unordered and ordered lists."""

    def __init__(self):
        self.history = []
        self.missed_lines = 0

    def FindRanges(self, s):
        m = re.match(r'^\s*(\+|-)\s', s)
        if not s.strip():
            self.missed_lines += 1
            return []  # Do nothing
        elif not m:
            self.history.clear()
            return []  # Do nothing.
        elif m.group(1) == '-':
            self.missed_lines += 1
            return []  # Do nothing.
        elif m.group(1) == '+':
            self._UpdateHistory(m.start(1))
            return [m.span(1)]

    def Transform(self, old):
        # `old` is `+`
        self.history[-1] += 1
        return str(self.history[-1]) + '.'

    def _UpdateHistory(self, i):
        self.history = [iterutils.nth(self.history[:i+1], n, 0) for n in range(i+1)]


class InnerUnderscoreEscaper(Morpher):

    def FindRanges(self, s):
        return [m.span() for m in re.finditer(r'(?<=\w)_(?=\w)', s)
                if not OccursInUrl(m) and not OccursInBacktick(m)]

    def Transform(self, old):
        return '\\_'


class BacktickTransformer(Morpher):

    def __init__(self):
        self.line_num = 0

    def FindRanges(self, s):
        return [m.span() for m in re.finditer('``.*?``', s)
                if not OccursInUrl(m)]

    def Transform(self, old):
        return old[1:-1]  # Trim off the outermost ticks.


def main():
    for key, val in sys.modules[__name__].__dict__.items():
        if isinstance(val, type) and issubclass(val, Morpher):
            print(key)
            _ = val()  # Make sure it can be initialized.


if __name__ == '__main__':
    main()
