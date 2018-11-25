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


def LinkTransformer():  # pylint: disable=invalid-name
    """Makes coroutine to transform links from RedNotebook to Markdown."""
    return _build_transformer(_link_transformer)


def ItalicTransformer():  # pylint: disable=invalid-name
    """Makes coroutine to transform italics from RedNotebook to Markdown."""
    return _build_transformer(_italic_transformer)


def StrikethroughTransformer():  # pylint: disable=invalid-name
    """Makes coroutine to transform strikethroughs from RedNotebook to Markdown.
    """
    return _build_transformer(_strikethrough_transformer)


def CodeBlockTransformer():  # pylint: disable=invalid-name
    """Makes coroutine to code blocks links from RedNotebook to Markdown."""
    return _build_transformer(_code_block_transformer)


def HeaderTransformer(init_level=0):  # pylint: disable=invalid-name
    """Makes coroutine to transform headers from RedNotebook to Markdown."""
    return _build_transformer(_header_transformer, init_level=init_level)


def ListTransformer():  # pylint: disable=invalid-name
    """Makes coroutine to transform underscores from RedNotebook to Markdown."""
    return _build_transformer(_list_transformer)


def InnerUnderscoreEscaper():  # pylint: disable=invalid-name
    """Returns coroutine to transform links from RedNotebook to Markdown."""
    return _build_transformer(_inner_underscore_escaper)


def _build_transformer(transformer_fun, *args, **kwargs):
    """Construct the given transformer.

    Transformers are implemented via generators. We call `next` once to prepare
    them for usage.
    """
    transformer = transformer_fun(*args, **kwargs)
    _ = next(transformer, None)
    return transformer


def _link_transformer():
    """Transforms '[[text ""url""]]' to '[text](url)'."""
    line = ''
    while True:
        line = yield re.sub(r'\[([^\]]*?) ""(.*?)""\]', r'[\1](\2)', line)


def _italic_transformer():
    """Transforms '//text//' to '_text_'."""
    line = ''
    while True:
        line = yield _sub_balanced_delims('//', '_', line)


def _strikethrough_transformer():
    """Transforms '--text--' to '**OBSOLETE**(text)'."""
    line = ''
    while True:
        line = yield (
            line if set(line) == {'-'} else
            _sub_balanced_delims('--', ['**OBSOLETE**(', ')'], line,
                                 data_op=lambda d: d.rstrip('.?!')))


def _header_transformer(init_level=0):
    """Transforms '=TEXT=' into '# TEXT'.

    Args:
        init_level: additional levels to add to all headers.
    """
    line = ''
    while True:
        line = yield line
        start_delim = re.search(r'^=+', line)
        if not start_delim or start_delim.group() == line:
            continue
        end_delim = re.search(r'=+$', line)
        if not end_delim or end_delim.group() != start_delim.group():
            continue
        lvl = len(start_delim.group())
        line = ' '.join(['#' * (init_level + lvl), line[lvl:-lvl].lstrip()])


def _list_transformer():
    """Transforms ordered and unordered lists into markdown syntax."""
    line = ''
    ordered_list_history = defaultlist.defaultlist(lambda: 1)
    sequential_empty_lines = 0
    while True:
        line = yield line
        li_match = re.match(r'^\s*([-|\+])\s', line)
        if li_match:
            i = li_match.start(1)
            # Always clear sub-items so they restart their numbering.
            del ordered_list_history[i + 1:]
            # Unordered lists do not use a different format in markdown.
            if line[i] == '-':
                continue
            # Ordered lists should change to their actual number.
            line = ''.join([
                line[:i], str(ordered_list_history[i]) + '.', line[i + 1:]
            ])
            ordered_list_history[i] += 1
        elif line.strip():
            sequential_empty_lines = 0
            ordered_list_history.clear()
        else:
            sequential_empty_lines += 1
            if sequential_empty_lines >= 2:
                ordered_list_history.clear()


def _inner_underscore_escaper():
    """Transforms underscores which need to be escaped."""
    line = ''
    while True:
        line = yield line
        for match in reversed(list(_filter_matches(r'(?<=\w)_(?=\w)', line))):
            line = ''.join([line[:match.start()], r'\_', line[match.end():]])


def _code_block_transformer():
    """Transforms codeblocks into markdown syntax."""
    line = ''
    while True:
        line = yield _sub_balanced_delims('``', '`', line, preds=[_not_in_link])


def _sub_balanced_delims(delim_pattern, sub, string, data_op=str, **kwargs):
    """We don't use a bigger regex because avoiding link urls is messy."""
    try:
        sub_start, sub_end = sub
    except ValueError:
        sub_start = sub_end = sub
    delims = _filter_matches(delim_pattern, string, **kwargs)
    balanced_delims = list(zip(delims, delims))
    # NOTE: Always do delim substitutions in reverse so the indices found remain
    # valid.
    for start_delim, end_delim in reversed(balanced_delims):
        start = string[:start_delim.start()]
        data = string[start_delim.end():end_delim.start()]
        end = string[end_delim.end():]
        string = ''.join([start, sub_start, data_op(data), sub_end, end])
    return string


def _filter_matches(pattern, string, preds=None):
    if preds is None:
        preds = (_not_in_link, _not_in_backticks)
    return (m for m in re.finditer(pattern, string) if all(p(m) for p in preds))


def _not_in_link(match):
    links = re.finditer(r'\[([^\]]*?) ""(.*?)""\]', match.string)
    return not any(_spans_intersect(match.span(), m.span(2)) for m in links)


def _not_in_backticks(match):
    backticks = re.finditer(r'`.*?`', match.string)
    return not any(_spans_intersect(match.span(), m.span()) for m in backticks)


def _spans_intersect(span1, span2):
    (lo1, hi1), (lo2, hi2) = span1, span2
    return hi1 >= lo2 and hi2 >= lo1
