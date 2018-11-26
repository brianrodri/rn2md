"""Entry point for rn2md tool."""
import sys

from . import config
from . import storage
from . import transformers
from . import util


def main():
    """Prints RedNotebook entries in markdown syntax."""
    options, remaining_argv = config.build_config_options(sys.argv)
    date_arg = ' '.join(remaining_argv) or 'today'
    dates = util.parse_dates(date_arg, workdays_only=options.workdays_only)
    rednotebook = storage.load_rednotebook_entries(options.data_path)

    def entry_to_markdown(date):
        """Returns the given date's RedNotebook entry in Markdown format."""
        sequenced_transformers = [
            transformers.InnerUnderscoreEscaper(),
            transformers.LinkTransformer(),
            transformers.HeaderTransformer(init_level=1),
            transformers.CodeBlockTransformer(),
            transformers.ItalicTransformer(),
            transformers.StrikethroughTransformer(),
            transformers.ListTransformer(),
        ]
        rn_lines = rednotebook[date].split('\n') if date in rednotebook else []
        # Start with a date header to help visually separate entries.
        md_lines = [date.strftime('# %a %b %d, %Y')]
        for rn_line in rn_lines:
            md_line = rn_line.rstrip()
            for transformer in sequenced_transformers:
                md_line = transformer.fmt(md_line)
            md_lines.append(md_line)
        return '\n'.join(md_lines)

    print('\n\n\n'.join(entry_to_markdown(d) for d in dates))


if __name__ == '__main__':
    main()
