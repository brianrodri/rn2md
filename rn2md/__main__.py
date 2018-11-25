"""Entry point for rn2md tool."""
import sys

from . import config
from . import storage
from . import transformers
from . import util


def _fmt(lines):
    """Transform given lines from Markdown syntax to RedNotebook syntax."""
    transformer_sequence = [
        transformers.InnerUnderscoreEscaper(),
        transformers.LinkTransformer(),
        transformers.HeaderTransformer(init_level=1),
        transformers.CodeBlockTransformer(),
        transformers.ItalicTransformer(),
        transformers.StrikethroughTransformer(),
        transformers.ListTransformer(),
    ]
    for line in lines:
        for transformer in transformer_sequence:
            line = transformer.fmt(line)
        yield line


def main():
    """Prints RedNotebook entries in markdown syntax."""
    options, remaining_argv = config.build_config_options(sys.argv)
    date_arg = ' '.join(remaining_argv) or 'today'
    dates = util.parse_dates(date_arg, workdays_only=options.workdays_only)

    day_entries = storage.load_daily_entries(options.data_path)
    def _fmt_day_entry(date):
        """Returns the given date's entry in Markdown format."""
        entry_lines = [_fmt(l.rstrip()) for l in day_entries[date].split('\n')]
        entry_lines.insert(0, date.strftime('# %a %b %d, %Y'))  # Date header.
        return '\n'.join(entry_lines)

    print('\n\n\n'.join(_fmt_day_entry(d) for d in dates if d in day_entries))


if __name__ == '__main__':
    main()
