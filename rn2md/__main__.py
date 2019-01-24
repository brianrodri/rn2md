"""Entry point for rn2md tool."""
import sys

from . import config
from . import formatters
from . import storage
from . import util


def main():
    """Prints RedNotebook entries in markdown syntax."""
    options, remaining_argv = config.Options.from_argv(sys.argv)
    rednotebook = storage.load_rednotebook_entries(options.data_path)
    def rednotebook_to_markdown(date):
        """Returns the given date's RedNotebook entry in Markdown format."""
        rn_lines = rednotebook[date].split('\n') if date in rednotebook else []
        formatter = formatters.format_rednotebook_as_markdown()
        md_lines = [formatter.send(line.rstrip()) for line in rn_lines]
        return '\n'.join(md_lines)
    if remaining_argv:
        try:
            date_range = util.parse_date_range(
                ' '.join(remaining_argv), options.workdays_only)
        except ValueError as e:
            print(f'Error: {e}')
            sys.exit(1)
    else:
        date_range = options.default_date_range
    print('\n\n\n'.join(rednotebook_to_markdown(d) for d in date_range))


if __name__ == '__main__':
    main()
