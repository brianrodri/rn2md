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


BACKTICK_PATTERN = re.compile(r'`.*?`')
CODE_BLOCK_PATTERN = re.compile(r'``')
HEADER_TOKEN_END_PATTERN = re.compile(r'[^=]')
INNER_UNDERSCORE_PATTERN = re.compile(r'(?<=\w)_(?=\w)')
ITALIC_PATTERN = re.compile(r'//')
LINK_PATTERN = re.compile(r'\[([^\]]*?) ""(.*?)""\]')
LIST_PATTERN = re.compile(r'^\s*([-|\+])\s')
STRIKETHROUGH_PATTERN = re.compile(r'--')


def _sub_balanced_delims(delim_pattern, sub, string, data_fun=str, **kwargs):
    try:
        sub_start, sub_end = sub
    except ValueError:
        sub_start = sub_end = sub
    delims = _filtered_matches(delim_pattern, string, **kwargs)
    balanced_delims = list(zip(delims, delims))
    # NOTE: Always do delimiter replacements in reverse so the indicies found
    # remain valid.
    for start_delim, end_delim in reversed(balanced_delims):
        s_start = string[:start_delim.start()]
        s_data = string[start_delim.end():end_delim.start()]
        s_end = string[end_delim.end():]
        string = ''.join([s_start, sub_start, data_fun(s_data), sub_end, s_end])
    return string


def _filtered_matches(patt, string, negative_predicates=None):
    if negative_predicates is None:
        negative_predicates = (_occurs_in_link, _occurs_in_backtick)
    for match in patt.finditer(string):
        if any(p(match) for p in negative_predicates):
            continue
        yield match


def _occurs_in_link(match):
    """Check if regexp `match` occurs in some URL."""
    occurrences = LINK_PATTERN.finditer(match.string)
    return any(_spans_intersect(match.span(), m.span(2)) for m in occurrences)


def _occurs_in_backtick(match):
    """Check if `match` occurs in backticks."""
    occurrences = BACKTICK_PATTERN.finditer(match.string)
    return any(_spans_intersect(match.span(), m.span()) for m in occurrences)


def _spans_intersect(span1, span2):
    (lo1, hi1), (lo2, hi2) = span1, span2
    return hi1 >= lo2 and hi2 >= lo1


def LinkTransformer():  # pylint: disable=invalid-name
    """Transforms '[[text ""url""]]' to '[text](url)'."""
    line = ''
    while True:
        line = yield LINK_PATTERN.sub(r'[\1](\2)', line)


def ItalicTransformer():  # pylint: disable=invalid-name
    """Transforms '//text//' to '_text_'."""
    line = ''
    while True:
        line = yield _sub_balanced_delims(ITALIC_PATTERN, '_', line)


def StrikethroughTransformer():  # pylint: disable=invalid-name
    """Transforms '--text--' to '**OBSOLETE**(text)'."""
    line = ''
    while True:
        line = yield line if set(line) == {'-'} else (
            _sub_balanced_delims(
                STRIKETHROUGH_PATTERN, ('**OBSOLETE**(', ')'), line,
                data_fun=lambda d: d.rstrip('.?!')))


def HeaderTransformer(base_level=0):  # pylint: disable=invalid-name
    """Transforms '=TEXT=' into '# TEXT'.

    Always holds that:
        >>> input.count('=') == (output.count('#') - base_level) * 2
    """
    line = ''
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


def ListTransformer():  # pylint: disable=invalid-name
    """Transforms unordered and ordered lists into markdown syntax."""
    line = ''
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


def InnerUnderscoreEscaper():  # pylint: disable=invalid-name
    """Transforms underscores which need to be escaped."""
    line = ''
    while True:
        line = yield line
        matches = _filtered_matches(INNER_UNDERSCORE_PATTERN, line)
        for match in reversed(list(matches)):
            line = ''.join([line[:match.start()], r'\_', line[match.end():]])


def CodeBlockTransformer():  # pylint: disable=invalid-name
    """Transforms codeblocks into markdown syntax."""
    line = ''
    while True:
        line = yield _sub_balanced_delims(CODE_BLOCK_PATTERN, '`', line,
                                          negative_predicates=[_occurs_in_link])
