"""Entry point for rn2md tool."""
import collections
import sys

from . import config
from . import formatters
from . import storage
from . import util


def main():
    """Prints RedNotebook entries in markdown syntax."""
    options, remaining_argv = config.build_config_options(sys.argv)
    date_arg = ' '.join(remaining_argv) or 'today'
    dates = util.parse_dates(date_arg, workdays_only=options.workdays_only)
    rednotebook = storage.load_rednotebook_entries(options.data_path)
    def rednotebook_to_markdown(date):
        """Returns the given date's RedNotebook entry in Markdown format."""
        formatter = formatters.RednotebookToMarkdownFormatter()
        rn_lines = rednotebook[date].split('\n') if date in rednotebook else []
        md_lines = collections.deque(formatter.fmt(l) for l in rn_lines)
        # Prepend entry with a markdown-formatted date header to help
        # distinguish it from other entries.
        md_lines.appendleft(date.strftime('# %a %b %d, %Y'))
        return '\n'.join(md_lines)
    print('\n\n\n'.join(rednotebook_to_markdown(d) for d in dates))


if __name__ == '__main__':
    main()
