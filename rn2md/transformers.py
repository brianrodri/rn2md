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
import os
import re

import iterutils
import defaultlist


URL_PATTERN = re.compile(
    r'^(?:http|file|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
    r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    r'(?::\d+)?',
    re.IGNORECASE)
LINK_PATTERN = re.compile(r'\[.*?\]\(.*?\)')
BACKTICK_PATTERN = re.compile(r'`.*?`')
LIST_PATTERN = re.compile(r'^\s*([-|\+])\s')
HEADER_TOKEN_END_PATTERN = re.compile(r'[^=]')


def _Grouper(iterable, n):
    "Collect data into fixed-length chunks or blocks"
    # _Grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return list(zip(*args))


def _SpansIntersect(span1, span2):
    (lo1, hi1), (lo2, hi2) = span1, span2
    assert lo1 <= hi1; assert lo2 <= hi2
    return hi1 >= lo2 and hi2 >= lo1


def _OccursInUrl(match):
    """Check if regexp `match` occurs in some URL."""
    occurrences = URL_PATTERN.finditer(match.string)
    return any(_SpansIntersect(match.span(), m.span()) for m in occurrences)


def _OccursInBacktick(match):
    """Check if `match` occurs in backticks."""
    occurrences = BACKTICK_PATTERN.finditer(match.string)
    return any(_SpansIntersect(match.span(), m.span()) for m in occurrences)


def _FindNonEscapedPattens(pattern, s):
    matches = re.finditer(pattern, s)
    matches = filter(lambda m: not _OccursInUrl(m), matches)
    matches = filter(lambda m: not _OccursInBacktick(m), matches)
    return matches


def ItalicTransformer():
    """Transforms '//text//' to '_text_'."""
    line = None
    while True:
        line = yield line
        matches = _FindNonEscapedPattens(r'//', line)
        for mlo, mhi in reversed(_Grouper(matches, 2)):
            line = ''.join([
                line[:mlo.start()],
                '_%s_' % line[mlo.end():mhi.start()],
                line[mhi.end():]
            ])


def LinkTransformer():
    """Transforms '[[text ""url""]]' to '[text](url)'."""
    line = None
    while True:
        line = yield line
        line = re.sub(r'\[\[([^\]]*?) ""(.*?)""\]\]', r'[\1](\2)', line)


def StrikethroughTransformer():
    """Transforms '--text--' to '**OBSOLETE**(text)'."""
    line = None
    while True:
        line = yield line
        matches = _FindNonEscapedPattens(r'--', line)
        for mlo, mhi in reversed(_Grouper(matches, 2)):
            line = ''.join([
                line[:mlo.start()],
                '**OBSOLETE**(%s)' % line[mlo.end():mhi.start()].rstrip('.!?'),
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
        if not line.startswith('=') or not line.endswith('='):
            continue
        header_token_end = HEADER_TOKEN_END_PATTERN.search(line)
        if header_token_end is None:
            continue
        if (header_token_end.start() !=
                HEADER_TOKEN_END_PATTERN.search(line[::-1]).start()):
            continue
        level = header_token_end.start()
        if base_level + level > 0:
            line = ' '.join(
                ['#' * (base_level + level), line[level:-level].lstrip()])


def ListTransformer():
    line = None
    empty_line_counter = 0
    ordered_list_counter = defaultlist.defaultlist(lambda: 0)
    while True:
        line = yield line
        if not line.strip():
            empty_line_counter += 1
            if empty_line_counter >= 2:
                ordered_list_counter.clear()
            continue
        empty_line_counter = 0
        list_match = LIST_PATTERN.match(line)
        if not list_match:
            del ordered_list_counter[:]
        else:
            index = list_match.start(1)
            del ordered_list_counter[index + 1:]
            if list_match.group(1) == '+':
                ordered_list_counter[index] += 1
                line = ''.join([
                    line[:list_match.start(1)],
                    '%d.' % ordered_list_counter[index],
                    line[list_match.end(1):]
                ])


def InnerUnderscoreEscaper():
    line = None
    while True:
        line = yield line
        for m in reversed(_FindNonEscapedPattens(r'(<=\w)_(?=\w)', line)):
            line = ''.join([line[:m.start()], r'\_', line[m.end():]])


def BacktickTransformer():
    line = None
    while True:
        line = yield line
        for m in reversed(re.finditer('``.*?``', line)):
            if not _OccursInUrl(m):
                line = ''.join(
                    [line[:m.start()], m.group()[1:-1], line[m.end():]])
