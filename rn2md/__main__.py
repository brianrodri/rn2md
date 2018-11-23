"""Entry point for rn2md tool."""
import sys

from . import config_options
from . import rn2md_util as util
from . import rednotebook_storage as storage
from . import rn2md_transformers as transformers


def rn2md(lines):
    """Transform given lines from Markdown syntax to RedNotebook syntax."""
    required_transformer_sequence = [
        transformers.InnerUnderscoreEscaper(),
        transformers.LinkTransformer(),
        transformers.HeaderTransformer(base_level=1),
        transformers.CodeBlockTransformer(),
        transformers.ItalicTransformer(),
        transformers.StrikethroughTransformer(),
        transformers.ListTransformer(),
    ]
    # Transformers are generators with meanginful state, so they need to be
    # prepared with an initial call to `next`.
    for transformer in required_transformer_sequence:
        next(transformer, None)
    for line in lines:
        for transformer in required_transformer_sequence:
            line = transformer.send(line)
        yield line


def main():
    """Business-logic."""
    options, remaining_argv = config_options.build_config_options(sys.argv)
    daily_entries = storage.load_daily_entries(options.data_path)
    target_date = ' '.join(remaining_argv) or 'today'
    dates = util.parse_dates(target_date, workdays_only=options.workdays_only)

    def _format_day_entry(date):
        entry_lines = [l.rstrip() for l in daily_entries[date].split('\n')]
        # Add header for date.
        entry_lines.insert(0, date.strftime('# %a %b %d, %Y'))
        return '\n'.join(rn2md(entry_lines))

    print('\n\n\n'.join(_format_day_entry(d) for d in dates if d in daily_entries))


if __name__ == '__main__':
    main()