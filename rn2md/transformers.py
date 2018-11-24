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


def _replace_balanced_delimiters(
        delim_patt, new_delim, s, transform=str, **kwargs):
    try:
        delim_start, delim_end = new_delim
    except ValueError:
        delim_start = delim_end = new_delim
    delimiters = _filtered_matches(delim_patt, s, **kwargs)
    balanced_delimiters = list(zip(delimiters, delimiters))
    # NOTE: Must always do delimiter replacements in reverse so the indicies
    # found remain valid.
    for delimiter_start, delimiter_end in reversed(balanced_delimiters):
        s_start = s[:delimiter_start.start()]
        s_data = s[delimiter_start.end():delimiter_end.start()]
        s_end = s[delimiter_end.end():]
        s = ''.join([s_start, delim_start, transform(s_data), delim_end, s_end])
    return s


def _filtered_matches(patt, s, negative_predicates=None):
    if negative_predicates is None:
        negative_predicates = (_occurs_in_link, _occurs_in_backtick)
    for match in patt.finditer(s):
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
        line = yield _replace_balanced_delimiters(ITALIC_PATTERN, '_', line)


def StrikethroughTransformer():  # pylint: disable=invalid-name
    """Transforms '--text--' to '**OBSOLETE**(text)'."""
    line = ''
    while True:
        line = yield line
        if set(line) == {'-'}:
            continue
        line = _replace_balanced_delimiters(STRIKETHROUGH_PATTERN,
                                            ('**OBSOLETE**(', ')'),
                                            line,
                                            transform=lambda c: c.rstrip('.!?'))


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
        line = yield _replace_balanced_delimiters(
                CODE_BLOCK_PATTERN, '`', line, negative_predicates=[_occurs_in_link])
