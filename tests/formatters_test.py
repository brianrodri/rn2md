"""Test cases for the rn2md.formatters module."""
import unittest

from rn2md import formatters


class RednotebookToMarkdownFormatterTest(unittest.TestCase):
    """Test formatting RedNotebook-style data to markdown-style."""

    def test_constructor(self):
        """Basic test to ensure construction works."""
        with self.subTest():
            _ = formatters.RednotebookToMarkdownFormatter()


class ItalicFormatterTest(unittest.TestCase):
    """Test formatting Rednotebook-style italics to markdown-style."""

    def test_common_format(self):
        """Test expected usage"""
        formatter = formatters.ItalicFormatter()
        self.assertEqual(formatter.send('Text with //italicized// content.'),
                         'Text with _italicized_ content.')

    def test_ignores_non_paired_markers(self):
        """Tests solitary markers are left alone."""
        formatter = formatters.ItalicFormatter()
        self.assertEqual(formatter.send('//italic1//, //italic2//, unused //'),
                         '_italic1_, _italic2_, unused //')

    def test_ignores_urls(self):
        """Tests that URL strings do not have their dashes changed."""
        formatter = formatters.ItalicFormatter()
        self.assertEqual(formatter.send('http://github.com/brianrodri'),
                         'http://github.com/brianrodri')

    def test_ignores_backticked_data(self):
        """Tests that back-ticked data do not get changed."""
        formatter = formatters.ItalicFormatter()
        self.assertEqual(formatter.send('//italic//, `//escaped italic//`'),
                         '_italic_, `//escaped italic//`')


class LinkFormatterTest(unittest.TestCase):
    """Test formatting Rednotebook-style links to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        formatter = formatters.LinkFormatter()
        self.assertEqual(formatter.send('[sample text ""go/somewhere""]'),
                         '[sample text](go/somewhere)')


class ImageFormatterTest(unittest.TestCase):
    """Test formatting Rednotebook-style links to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        formatter = formatters.ImageFormatter()
        self.assertEqual(formatter.send('[""http://www.site.com/image.jpg""]'),
                         '![](http://www.site.com/image.jpg)')


class StrikethroughFormatterTest(unittest.TestCase):
    """Test formatting Rednotebook-style strikethroughs to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        formatter = formatters.StrikethroughFormatter()
        self.assertEqual(formatter.send('--text--'), '~text~')

    def test_punctuation_gets_stripped(self):
        """Tests punctuation is removed from parenthesized text."""
        formatter = formatters.StrikethroughFormatter()
        self.assertEqual(formatter.send('--a complete sentence.--'),
                         '~a complete sentence.~')

    def test_ignores_non_paired_markers(self):
        """Tests solitary markers are left alone."""
        formatter = formatters.StrikethroughFormatter()
        self.assertEqual(
            formatter.send('--changed--, --this too--, not here--or here.'),
            '~changed~, ~this too~, not here--or here.')

    def test_ignores_urls(self):
        """Tests urls are not changed."""
        formatter = formatters.StrikethroughFormatter()
        self.assertEqual(
            formatter.send('[x ""http://do/kinda--weird--thing""]'),
            '[x ""http://do/kinda--weird--thing""]')

    def test_ignores_backticked_data(self):
        """Tests backticked data is left alone."""
        formatter = formatters.StrikethroughFormatter()
        self.assertEqual(formatter.send('--hit--, `--not hit--`'),
                         '~hit~, `--not hit--`')

    def test_ignores_lines_with_only_backticks(self):
        """Tests that data with only backticks are not changed."""
        formatter = formatters.StrikethroughFormatter()
        self.assertEqual(formatter.send('-----'), '-----')


class HeaderFormatterTest(unittest.TestCase):
    """Test formatting Rednotebook-style header to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        formatter = formatters.HeaderFormatter()
        self.assertEqual(formatter.send('=Level One='), '# Level One')
        self.assertEqual(formatter.send('===Level Three==='),
                         '### Level Three')

    def test_base_level_is_respected(self):
        """Tests changes to init level."""
        formatter = formatters.HeaderFormatter(padding=2)
        self.assertEqual(formatter.send('===Only 3==='), '##### Only 3')

    def test_inner_markers_are_ignored(self):
        """Tests header markings are only interpreted when surrounding line."""
        formatter = formatters.HeaderFormatter()
        self.assertEqual(formatter.send('Not at =start= of text'),
                         'Not at =start= of text')

    def test_only_markers_are_ignored(self):
        """Tests lines with only markers aren't affected."""
        formatter = formatters.HeaderFormatter()
        self.assertEqual(formatter.send('=' * 6), '=' * 6)
        self.assertEqual(formatter.send('=' * 7), '=' * 7)

    def test_un_balanced_markers_are_ignored(self):
        """Tests that lines must use balanced markers."""
        formatter = formatters.HeaderFormatter()
        self.assertEqual(formatter.send('==Unbalanced==='), '==Unbalanced===')


class ListFormatterTest(unittest.TestCase):
    """Test formatting Rednotebook-style lists to markdown-style."""

    def test_unordered_list(self):
        """Tests expected usage for unordered lists."""
        formatter = formatters.ListFormatter()
        input_lines = [
            '- A',
            ' - B',
            '- A',
        ]
        self.assertEqual([formatter.send(l) for l in input_lines], [
            '- A',
            ' - B',
            '- A',
        ])

    def test_ordered_list(self):
        """Tests expected usage for ordered lists."""
        formatter = formatters.ListFormatter()
        input_lines = [
            '+ A',
            ' + B',
            '+ A',
        ]
        self.assertEqual([formatter.send(l) for l in input_lines], [
            '1. A',
            ' 1. B',
            '2. A',
        ])

    def test_two_blank_lines_reset_numbering(self):
        """Tests two blank lines starts separate ordered lists."""
        formatter = formatters.ListFormatter()
        input_lines = [
            '+ A',
            '+ B',
            '',
            '',
            '+ C'
        ]
        self.assertEqual([formatter.send(l) for l in input_lines], [
            '1. A',
            '2. B',
            '',
            '',
            '1. C',
        ])

    def test_content_between_ordered_list_resets_numbering(self):
        """Tests content between ordered lists restarts numbering."""
        formatter = formatters.ListFormatter()
        input_lines = [
            '+ A',
            '+ B',
            'Content',
            '+ C',
        ]
        self.assertEqual([formatter.send(l) for l in input_lines], [
            '1. A',
            '2. B',
            'Content',
            '1. C',
        ])

    def test_nested_levels_are_reset_once_passed(self):
        """Tests that nested levels are respected."""
        formatter = formatters.ListFormatter()
        input_lines = [
            '+ A',
            ' + B',
            ' + C',
            '  + D',
            '+ E',
            ' + F',
            '  + G',
        ]
        self.assertEqual([formatter.send(l) for l in input_lines], [
            '1. A',
            ' 1. B',
            ' 2. C',
            '  1. D',
            '2. E',
            ' 1. F',
            '  1. G',
        ])

    def test_nested_levels_are_not_interrupted_by_unordered_lists(self):
        """Tests that unordered lists do not restart ordered list numbering."""
        formatter = formatters.ListFormatter()
        input_lines = [
            '+ A',
            ' - B',
            '+ C',
        ]
        self.assertEqual([formatter.send(l) for l in input_lines], [
            '1. A',
            ' - B',
            '2. C',
        ])


class InnerUnderscoreFormatterTest(unittest.TestCase):
    """Test formatting Rednotebook-style underscores to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        formatter = formatters.InnerUnderscoreFormatter()
        self.assertEqual(formatter.send('underscore_delimited_word'),
                         r'underscore\_delimited\_word')

    def test_trailing_underscores_ignored(self):
        """Tests trailing underscores are left alone."""
        formatter = formatters.InnerUnderscoreFormatter()
        self.assertEqual(formatter.send('_with_trailing_underscores_'),
                         r'_with\_trailing\_underscores_')

    def test_ignores_urls(self):
        """Tests that underscores in urls are left alone."""
        formatter = formatters.InnerUnderscoreFormatter()
        self.assertEqual(
            formatter.send('[test_thing ""http://github.com/test_thing""]'),
            r'[test\_thing ""http://github.com/test_thing""]')

    def test_ignores_backticked_data(self):
        """Tests that underscores between backticks are left alone."""
        formatter = formatters.InnerUnderscoreFormatter()
        self.assertEqual(formatter.send('gets_escaped, `no_escape`'),
                         r'gets\_escaped, `no_escape`')


class CodeBlockFormatterTest(unittest.TestCase):
    """Test formatting Rednotebook-style code blocks to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        formatter = formatters.CodeBlockFormatter()
        self.assertEqual(formatter.send('``code encoded stuff``'),
                         '`code encoded stuff`')

    def test_only_two_backticks_are_formated(self):
        """Tests that multi-line code blocks are left alone."""
        formatter = formatters.CodeBlockFormatter()
        input_lines = [
            '```py',
            '# Python code',
            '```',
        ]
        self.assertEqual([formatter.send(l) for l in input_lines], [
            '```py',
            '# Python code',
            '```',
        ])


if __name__ == '__main__':
    unittest.main()
