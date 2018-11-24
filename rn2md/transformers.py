"""Helpers to tranform data in RedNotebook syntax to Markdown syntax.

Here is a summary of the currently implemented transformers:

    RedNotebook                       Markdown
    ===========                       ========
    [name ""url""]                    [name](url)
    //text//                          _text_
    --text--                          ~text~
    =Text=                            # Text
    [""url""]                         ![...](url)
    + Ordered item                    1. Ordered item
    - Unordered item                  - Unordered item
    ``asdf``                          `asdf`
"""
import re

import defaultlist


def _spans_intersect(span1, span2):
    (lo1, hi1), (lo2, hi2) = span1, span2
    return hi1 >= lo2 and hi2 >= lo1


def _find_unescaped_patterns(pattern, target_str):
    matches = pattern.finditer(target_str)
    # Order matters.
    matches = filter(lambda m: not _occurs_in_link(m), matches)
    matches = filter(lambda m: not _occurs_in_backtick(m), matches)
    return matches


BACKTICK_PATTERN = re.compile(r'`.*?`')
def _occurs_in_backtick(match):
    """Check if `match` occurs in backticks."""
    occurrences = BACKTICK_PATTERN.finditer(match.string)
    return any(_spans_intersect(match.span(), m.span()) for m in occurrences)


LINK_PATTERN = re.compile(r'\[([^\]]*?) ""(.*?)""\]')
def LinkTransformer():  # pylint: disable=invalid-name
    """Transforms '[[text ""url""]]' to '[text](url)'."""
    line = None
    while True:
        line = yield line
        line = LINK_PATTERN.sub(r'[\1](\2)', line)


def _occurs_in_link(match):
    """Check if regexp `match` occurs in some URL."""
    occurrences = LINK_PATTERN.finditer(match.string)
    return any(_spans_intersect(match.span(), m.span(2)) for m in occurrences)


ITALIC_PATTERN = re.compile(r'//')
def ItalicTransformer():  # pylint: disable=invalid-name
    """Transforms '//text//' to '_text_'."""
    line = None
    while True:
        line = yield line
        matches = _find_unescaped_patterns(ITALIC_PATTERN, line)
        match_pairs = list(zip(iter(matches), iter(matches)))
        for mlo, mhi in reversed(match_pairs):
            line = ''.join([
                line[:mlo.start()],
                '_%s_' % line[mlo.end():mhi.start()],
                line[mhi.end():]
            ])


STRIKETHROUGH_PATTERN = re.compile(r'--')
def StrikethroughTransformer():  # pylint: disable=invalid-name
    """Transforms '--text--' to '**OBSOLETE**(text)'."""
    line = None
    while True:
        line = yield line
        if set(line) == {'-'}:
            continue
        matches = _find_unescaped_patterns(STRIKETHROUGH_PATTERN, line)
        match_pairs = list(zip(iter(matches), iter(matches)))
        for mlo, mhi in reversed(match_pairs):
            line = ''.join([
                line[:mlo.start()],
                '**OBSOLETE**(%s)' % line[mlo.end():mhi.start()].rstrip('.!?'),
                line[mhi.end():]
            ])


HEADER_TOKEN_END_PATTERN = re.compile(r'[^=]')
def HeaderTransformer(base_level=0):  # pylint: disable=invalid-name
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


LIST_PATTERN = re.compile(r'^\s*([-|\+])\s')
def ListTransformer():  # pylint: disable=invalid-name
    """Transforms unordered and ordered lists into markdown syntax."""
    line = None
    sequential_empty_lines = 0
    ordered_list_counter = defaultlist.defaultlist(lambda: 0)
    while True:
        line = yield line
        if not line.strip():
            sequential_empty_lines += 1
            if sequential_empty_lines >= 2:
                ordered_list_counter.clear()
            continue
        sequential_empty_lines = 0
        list_match = LIST_PATTERN.match(line)
        if not list_match:
            ordered_list_counter.clear()
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


INNER_UNDERSCORE_PATTERN = re.compile(r'(?<=\w)_(?=\w)')
def InnerUnderscoreEscaper():  # pylint: disable=invalid-name
    """Transforms underscores which need to be escaped."""
    line = None
    while True:
        line = yield line
        matches = list(_find_unescaped_patterns(INNER_UNDERSCORE_PATTERN, line))
        for match in reversed(matches):
            line = ''.join([line[:match.start()], r'\_', line[match.end():]])


CODE_BLOCK_PATTERN = re.compile(r'``')
def CodeBlockTransformer():  # pylint: disable=invalid-name
    """Transforms codeblocks into markdown syntax."""
    line = None
    while True:
        line = yield line
        matches = CODE_BLOCK_PATTERN.finditer(line)
        match_pairs = list(zip(iter(matches), iter(matches)))
        for mlo, mhi in reversed(match_pairs):
            line = ''.join([
                line[:mlo.start()],
                '`%s`' % line[mlo.end():mhi.start()].rstrip('.!?'),
                line[mhi.end():]
            ])
