"""Test cases for the rn2md.formatters module."""
import unittest

from rn2md import formatters


class FormatterTestBase(unittest.TestCase):
    """Provides convenience methods to make tests more readable."""

    def apply_formatter(self, f, lines):
        """Returns self.formatter's application on the given lines."""
        return [f.send(line) for line in lines]


class RednotebookToMarkdownFormatterTest(FormatterTestBase):
    """Test formatting RedNotebook-style data to markdown-style."""

    def test_constructor(self):
        """Basic test to ensure construction works."""
        _ = formatters.format_rednotebook_as_markdown()


class ItalicFormatterTest(FormatterTestBase):
    """Test formatting Rednotebook-style italics to markdown-style."""

    def test_common_format(self):
        """Test expected usage"""
        f = formatters.format_italic_text()
        self.assertEqual(
            self.apply_formatter(f, ['Text with //italicized// content.']),
            ['Text with _italicized_ content.'])

    def test_ignores_non_paired_markers(self):
        """Tests solitary markers are left alone."""
        f = formatters.format_italic_text()
        self.assertEqual(
            self.apply_formatter(f, ['//italic1//, //italic2//, unused //']),
            ['_italic1_, _italic2_, unused //'])

    def test_ignores_urls(self):
        """Tests that URL strings do not have their dashes changed."""
        f = formatters.format_italic_text()
        self.assertEqual(
            self.apply_formatter(f, ['http://github.com/brianrodri']),
            ['http://github.com/brianrodri'])

    def test_ignores_backticked_data(self):
        """Tests that back-ticked data do not get changed."""
        f = formatters.format_italic_text()
        self.assertEqual(
            self.apply_formatter(f, ['//italic//, `//escaped italic//`']),
            ['_italic_, `//escaped italic//`'])


class LinkFormatterTest(FormatterTestBase):
    """Test formatting Rednotebook-style links to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        f = formatters.format_links()
        self.assertEqual(
            self.apply_formatter(f, ['[sample text ""go/somewhere""]']),
            ['[sample text](go/somewhere)'])


class ImageFormatterTest(FormatterTestBase):
    """Test formatting Rednotebook-style links to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        f = formatters.format_images()
        self.assertEqual(
            self.apply_formatter(f, ['[""http://www.site.com/image.jpg""]']),
            ['![](http://www.site.com/image.jpg)'])


class StrikethroughFormatterTest(FormatterTestBase):
    """Test formatting Rednotebook-style strikethroughs to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        f = formatters.format_strikethrough_text()
        self.assertEqual(self.apply_formatter(f, ['--text--']), ['~text~'])

    def test_punctuation_gets_stripped(self):
        """Tests punctuation is removed from parenthesized text."""
        f = formatters.format_strikethrough_text()
        self.assertEqual(self.apply_formatter(f, ['--a complete sentence.--']),
                         ['~a complete sentence.~'])

    def test_ignores_non_paired_markers(self):
        """Tests solitary markers are left alone."""
        f = formatters.format_strikethrough_text()
        self.assertEqual(
            self.apply_formatter(f, [
                '--changed--, --this too--, not here--or here.',
            ]), [
                '~changed~, ~this too~, not here--or here.'
            ])

    def test_ignores_urls(self):
        """Tests urls are not changed."""
        f = formatters.format_strikethrough_text()
        self.assertEqual(
            self.apply_formatter(f, ['[x ""http://do/kinda--weird--thing""]']),
            ['[x ""http://do/kinda--weird--thing""]'])

    def test_ignores_backticked_data(self):
        """Tests backticked data is left alone."""
        f = formatters.format_strikethrough_text()
        self.assertEqual(self.apply_formatter(f, ['--hit--, `--not hit--`']),
                         ['~hit~, `--not hit--`'])

    def test_ignores_lines_with_only_backticks(self):
        """Tests that data with only backticks are not changed."""
        f = formatters.format_strikethrough_text()
        self.assertEqual(self.apply_formatter(f, ['-----']), ['-----'])


class HeaderFormatterTest(FormatterTestBase):
    """Test formatting Rednotebook-style header to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        f = formatters.format_headers()
        self.assertEqual(
            self.apply_formatter(f, ['=Level One=', '===Level Three===']),
            ['# Level One', '### Level Three'])

    def test_base_level_is_respected(self):
        """Tests changes to init level."""
        f = formatters.format_headers(padding=2)
        self.assertEqual(self.apply_formatter(f, ['===Only 3===']),
                         ['##### Only 3'])

    def test_inner_markers_are_ignored(self):
        """Tests header markings are only interpreted when surrounding line."""
        f = formatters.format_headers()
        self.assertEqual(self.apply_formatter(f, ['Not at =start= of text']),
                         ['Not at =start= of text'])

    def test_only_markers_are_ignored(self):
        """Tests lines with only markers aren't affected."""
        f = formatters.format_headers()
        self.assertEqual(self.apply_formatter(f, ['=' * 6]), ['=' * 6])
        self.assertEqual(self.apply_formatter(f, ['=' * 7]), ['=' * 7])

    def test_un_balanced_markers_are_ignored(self):
        """Tests that lines must use balanced markers."""
        f = formatters.format_headers()
        self.assertEqual(self.apply_formatter(f, ['==Unbalanced===']),
                         ['==Unbalanced==='])


class ListFormatterTest(FormatterTestBase):
    """Test formatting Rednotebook-style lists to markdown-style."""

    def test_unordered_list(self):
        """Tests expected usage for unordered lists."""
        f = formatters.format_lists()
        self.assertEqual(
            self.apply_formatter(f, [
                '- A',
                ' - B',
                '- A',
            ]), [
                '- A',
                ' - B',
                '- A',
            ])

    def test_ordered_list(self):
        """Tests expected usage for ordered lists."""
        f = formatters.format_lists()
        self.assertEqual(
            self.apply_formatter(f, [
                '+ A',
                ' + B',
                '+ A',
            ]), [
                '1. A',
                ' 1. B',
                '2. A',
            ])

    def test_two_blank_lines_reset_numbering(self):
        """Tests two blank lines starts separate ordered lists."""
        f = formatters.format_lists()
        self.assertEqual(
            self.apply_formatter(f, [
                '+ A',
                '+ B',
                '',
                '',
                '+ C'
            ]), [
                '1. A',
                '2. B',
                '',
                '',
                '1. C',
            ])

    def test_content_between_ordered_list_resets_numbering(self):
        """Tests content between ordered lists restarts numbering."""
        f = formatters.format_lists()
        self.assertEqual(
            self.apply_formatter(f, [
                '+ A',
                '+ B',
                'Content',
                '+ C',
            ]), [
                '1. A',
                '2. B',
                'Content',
                '1. C',
            ])

    def test_nested_levels_are_reset_once_passed(self):
        """Tests that nested levels are respected."""
        f = formatters.format_lists()
        self.assertEqual(
            self.apply_formatter(f, [
                '+ A',
                ' + B',
                ' + C',
                '  + D',
                '+ E',
                ' + F',
                '  + G',
            ]), [
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
        f = formatters.format_lists()
        self.assertEqual(
            self.apply_formatter(f, [
                '+ A',
                ' - B',
                '+ C',
            ]), [
                '1. A',
                ' - B',
                '2. C',
            ])


class InnerUnderscoreFormatterTest(FormatterTestBase):
    """Test formatting Rednotebook-style underscores to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        f = formatters.format_inner_underscores()
        self.assertEqual(self.apply_formatter(f, ['underscore_delimited_word']),
                         ['underscore\_delimited\_word'])

    def test_trailing_underscores_ignored(self):
        """Tests trailing underscores are left alone."""
        f = formatters.format_inner_underscores()
        self.assertEqual(
            self.apply_formatter(f, ['_with_trailing_underscores_']),
            ['_with\_trailing\_underscores_'])

    def test_ignores_urls(self):
        """Tests that underscores in urls are left alone."""
        f = formatters.format_inner_underscores()
        self.assertEqual(
            self.apply_formatter(f, [
                '[test_thing ""http://github.com/test_thing""]',
            ]), [
                '[test\_thing ""http://github.com/test_thing""]'
            ])

    def test_ignores_backticked_data(self):
        """Tests that underscores between backticks are left alone."""
        f = formatters.format_inner_underscores()
        self.assertEqual(self.apply_formatter(f, ['gets_escaped, `no_escape`']),
                         ['gets\_escaped, `no_escape`'])


class CodeBlockFormatterTest(FormatterTestBase):
    """Test formatting Rednotebook-style code blocks to markdown-style."""

    def test_common_format(self):
        """Tests expected usage."""
        f = formatters.format_code_blocks()
        self.assertEqual(self.apply_formatter(f, ['``code encoded stuff``']),
                         ['`code encoded stuff`'])

    def test_only_two_backticks_are_formated(self):
        """Tests that multi-line code blocks are left alone."""
        f = formatters.format_code_blocks()
        self.assertEqual(
            self.apply_formatter(f, [
                '```py',
                '# Python code',
                '```',
            ]), [
                '```py',
                '# Python code',
                '```',
            ])


if __name__ == '__main__':
    unittest.main()
