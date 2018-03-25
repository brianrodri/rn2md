#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Translates text in RedNotebook syntax to Markdown syntax.

Given a sequence of lines from stdin, this script will print out the same
sequence of lines but with any RedNotebook discovered syntax converted to
Markdown.

Here is a list of the currently supported transformations:

    RedNotebook                       Markdown
    ===========                       ========
    [name ""url""]                    [name](url)
    //text//                          _text_
    --text--                          ~text~
    =Text=                            # Text
    [""url""]                         ![...](url)
"""
import itertools
import iterutils
import os
import re
import string
import sys


URL_PATTERN = re.compile(
    r'^(?:http|file|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?',
    re.IGNORECASE)
LINK_PATTERN = re.compile(r'\[.*?\]\(.*?\)')
BACKTICK_PATTERN = re.compile(r'`.*?`')


def OccursInUrl(match):
    """Check if regexp `match` occurs in some URL."""
    occurrences = itertools.chain(
        URL_PATTERN.finditer(match.string),
        LINK_PATTERN.finditer(match.string))
    return any(SpanOf(match) & SpanOf(m) for m in occurrences)


def OccursInBacktick(match):
    """Check if `match` occurs in backticks."""
    occurrences = BACKTICK_PATTERN.finditer(match.string)
    return any(SpanOf(match) & SpanOf(m) for m in occurrences)


def FindNonEscapedPattens(pattern, s):
    matches = re.finditer(pattern, s)
    matches = filter(lambda m: not OccursInUrl(m), matches)
    matches = filter(lambda m: not OccursInBacktick(m), matches)
    return matches


def ItalicTransformer():
    line = None
    while True:
        line = yield line
        matches = FindNonEscapedPattens(r'//', line)
        for mlo, mhi in reversed(iterutils.grouper(matches, 2)):
            line = ''.join([
                line[:mlo.start()],
                '_',
                line[mlo.end():mhi.start()],
                '_',
                line[mhi.end():]
            ])


def LinkTransformer():
    line = None
    while True:
        line = yield line
        line = re.sub(r'\[([^\]]*?) ""(.*?)""\]', r'[\1](\2)')


def StrikethroughTransformer():
    line = None
    while True:
        line = yield line
        matches = FindNonEscapedPattens(r'--', line)
        for mlo, mhi in reversed(iterutils.grouper(matches, 2)):
            line = ''.join([
                line[:mlo.start()],
                '**IRRELEVANT**(',
                line[mlo.end():mhi.start()].rstrip('.!?'),
                ')',
                line[mhi.end():]
            ])


def HeaderTransformer(base_level=0):
    """Transforms '=TEXT=' into '# TEXT'.

    Always holds that:
        >>> input.count('=') == (output.count('#') - base_level) * 2
    """
    line = None
    while True:
        line = yield line
        if not line.startswith('='):
            continue
        affix = os.path.commonprefix([line, line[::-1]])
        if affix == line:
            continue
        m = re.search('[^=]', affix)
        level = m.start() if m else len(affix)
        if base_level + level > 0:
            line = ''.join([
                '#' * (base_level + level),
                ' ',
                line[level:-level].lstrip(),
            ])


def ListTransformer():
    levels = []
    missed_lines = 0

    line = None
    while True:
        line = yield line
        if not line.strip():
            missed_lines += 1
            continue
        m = re.match(r'^\s*(\+|-)\s', line)
        if not m


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

    def Transform(self, substr):
        # `substr` is `+`
        self.history[-1] += 1
        return str(self.history[-1]) + '.'

    def _UpdateHistory(self, i):
        self.history = [iterutils.nth(self.history[:i+1], n, 0) for n in range(i+1)]


class InnerUnderscoreEscaper(Morpher):

    def FindRanges(self, s):
        return [m.span() for m in re.finditer(r'(?<=\w)_(?=\w)', s)
                if not OccursInUrl(m) and not OccursInBacktick(m)]

    def Transform(self, substr):
        return '\\_'


class BacktickTransformer(Morpher):

    def __init__(self):
        self.line_num = 0

    def FindRanges(self, s):
        return [m.span() for m in re.finditer('``.*?``', s)
                if not OccursInUrl(m)]

    def Transform(self, substr):
        return substr[1:-1]  # Trim off the outermost ticks.


def main():
    for key, val in sys.modules[__name__].__dict__.items():
        if isinstance(val, type) and issubclass(val, Morpher):
            print(key)
            _ = val()  # Make sure it can be initialized.


if __name__ == '__main__':
    main()
