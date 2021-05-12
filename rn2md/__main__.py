"""Entry point for the rn2md tool."""

import dataclasses
import datetime as dt
import sys

from . import config, formatters, storage, util

ENTRY_SEP = '\n\n\n'


@dataclasses.dataclass
class RedNotebook:
    entries: dict[dt.date, str]

    @classmethod
    def from_file(cls, data_path):
        return cls(storage.load_rednotebook_entries(data_path))

    def to_markdown(self, date_range):
        """Yields the specified RedNotebook entries in Markdown format."""
        for date in date_range:
            if date in self.entries:
                rn_lines = self.entries[date].split('\n')
                formatter = formatters.format_rednotebook_as_markdown()
                md_lines = [formatter.send(line.rstrip()) for line in rn_lines]
                yield '\n'.join(md_lines)


def main():
    """Prints RedNotebook entries in markdown syntax."""
    options, remaining_argv = config.Options.from_argv(sys.argv)

    red_notebook = RedNotebook.from_file(options.data_path)
    date_range = (
        util.parse_date_range(' '.join(remaining_argv), options.workdays_only)
        if remaining_argv else options.default_date_range)

    print(ENTRY_SEP.join(red_notebook.to_markdown(date_range)))


if __name__ == '__main__':
    main()
