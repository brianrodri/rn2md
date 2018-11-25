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


class TransformerBase():
    """Handles boilerplate required by all transformers."""

    def __init__(self, *args, **kwargs):
        self._transformer = self._transformer_generator(*args, **kwargs)
        _ = next(self._transformer, None)

    def send(self, line):
        """Transforms the RedNotebook formatted line into Markdown format."""
        return self._transformer.send(line)

    def _transformer_generator(self, *args, **kwargs):
        raise NotImplementedError


class LinkTransformer(TransformerBase):
    """Makes coroutine to transform links from RedNotebook to Markdown."""
    def _transformer_generator(self):
        """Transforms '[[text ""url""]]' to '[text](url)'."""
        line = ''
        while True:
            line = yield re.sub(r'\[([^\]]*?) ""(.*?)""\]', r'[\1](\2)', line)


class ItalicTransformer(TransformerBase):
    """Makes coroutine to transform italics from RedNotebook to Markdown."""
    def _transformer_generator(self):
        """Transforms '//text//' to '_text_'."""
        line = ''
        while True:
            line = yield _sub_balanced_delims('//', '_', line)


class StrikethroughTransformer(TransformerBase):
    """Makes coroutine to transform strikethroughs from RedNotebook to Markdown.
    """
    def _transformer_generator(self):
        """Transforms '--text--' to '**OBSOLETE**(text)'."""
        line = ''
        while True:
            line = yield (
                line if set(line) == {'-'} else
                _sub_balanced_delims('--', ['**OBSOLETE**(', ')'], line,
                                     data_op=lambda d: d.rstrip('.?!')))


class CodeBlockTransformer(TransformerBase):
    """Makes coroutine to code blocks links from RedNotebook to Markdown."""
    def _transformer_generator(self):
        """Transforms codeblocks into markdown syntax."""
        line = ''
        while True:
            line = yield _sub_balanced_delims('``', '`', line,
                                              preds=[_not_in_link])


class HeaderTransformer(TransformerBase):
    """Transform headers from RedNotebook syntax to Markdown syntax."""

    def _transformer_generator(self, init_level=0):
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


class ListTransformer(TransformerBase):
    """Makes coroutine to transform underscores from RedNotebook to Markdown."""
    def _transformer_generator(self):
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


class InnerUnderscoreEscaper(TransformerBase):
    """Returns coroutine to transform links from RedNotebook to Markdown."""
    def _transformer_generator(self):
        """Transforms underscores which need to be escaped."""
        line = ''
        while True:
            line = yield line
            inner_underscores = list(_filter_matches(r'(?<=\w)_(?=\w)', line))
            for match in reversed(inner_underscores):
                line = ''.join([
                    line[:match.start()],
                    r'\_',
                    line[match.end():]
                ])


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
