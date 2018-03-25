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


def _OccursInUrl(match):
    """Check if regexp `match` occurs in some URL."""
    occurrences = itertools.chain(
        URL_PATTERN.finditer(match.string),
        LINK_PATTERN.finditer(match.string))
    return any(SpanOf(match) & SpanOf(m) for m in occurrences)


def _OccursInBacktick(match):
    """Check if `match` occurs in backticks."""
    occurrences = BACKTICK_PATTERN.finditer(match.string)
    return any(SpanOf(match) & SpanOf(m) for m in occurrences)


def _FindNonEscapedPattens(pattern, s):
    matches = re.finditer(pattern, s)
    matches = filter(lambda m: not _OccursInUrl(m), matches)
    matches = filter(lambda m: not _OccursInBacktick(m), matches)
    return matches


def ItalicTransformer():
    line = None
    while True:
        line = yield line
        matches = _FindNonEscapedPattens(r'//', line)
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
        matches = _FindNonEscapedPattens(r'--', line)
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
            line = ''.join(
                ['#' * (base_level + level), ' ', line[level:-level].lstrip()])


def ListTransformer():
    line = None
    empty_line_counter = 0
    ordered_list_counter = defaultlist(lambda: 0)
    while True:
        line = yield line

        if not line.strip():
            empty_line_counter += 1
            if empty_line_counter >= 2:
                ordered_list_counter.clear()
            continue
        empty_line_counter = 0

        m = LIST_PATTERN.match(line)
        if not m:
            del ordered_list_counter[:]
        else:
            index = m.start(1)
            del ordered_list_counter[index + 1:]
            if m.group(1) == '+':
                ordered_list_counter[index] += 1
                line = ''.join([
                    line[:m.begin(1)],
                    '%d.' % ordered_list_counter[index],
                    line[m.end(1):]
                ])


def InnerUnderscoreEscaper():
    line = None
    while True:
        line = yield line
        for m in reversed(re.finditer(r'(?<=\w)_(?=\w)', line)):
            if not _OccursInUrl(m) and not _OccursInBacktick(m):
                line = ''.join([line[:m.start()], r'\_', line[m.end():]])


def BacktickTransformer():
    line = None
    while True:
        line = yield line
        for m in reversed(re.finditer('``.*?``', line)):
            if not _OccursInUrl(m):
                line = ''.join(
                    [line[:m.start()], m.group()[1:-1], line[m.end():]])
