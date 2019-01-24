"""Entry point for rn2md tool."""
import sys

from . import config
from . import formatters
from . import storage
from . import util


def main():
    """Prints RedNotebook entries in markdown syntax."""
    config, remaining_argv = config.Config.from_argv(sys.argv)
    rednotebook = storage.load_rednotebook_entries(config.data_path)
    date_arg = ' '.join(remaining_argv) if remaining_argv else 'today'
    dates = util.parse_dates(date_arg, config.workdays_only)
    def rednotebook_to_markdown(date):
        """Returns the given date's RedNotebook entry in Markdown format."""
        rn_lines = rednotebook[date].split('\n') if date in rednotebook else []
        formatter = formatters.format_rednotebook_as_markdown()
        md_lines = [formatter.send(line.rstrip()) for line in rn_lines]
        return '\n'.join(md_lines)
    print('\n\n\n'.join(rednotebook_to_markdown(d) for d in dates))


if __name__ == '__main__':
    main()
