"""Test cases for the transformers module."""
import unittest

from rn2md import transformers


class ItalicTransformerTest(unittest.TestCase):
    """Test transforming Rednotebook-style italics to markdown-style."""

    def test_transformation(self):
        """Test expected usage"""
        transformer = transformers.ItalicTransformer()
        self.assertEqual(transformer.fmt('Text with //italicized// content.'),
                         'Text with _italicized_ content.')

    def test_ignores_non_paired_markers(self):
        """Tests solitary markers are left alone."""
        transformer = transformers.ItalicTransformer()
        self.assertEqual(transformer.fmt('//italic1//, //italic2//, unused //'),
                         '_italic1_, _italic2_, unused //')

    def test_ignores_urls(self):
        """Tests urls do not have their dashes changed."""
        transformer = transformers.ItalicTransformer()
        self.assertEqual(transformer.fmt('http://github.com/brianrodri'),
                         'http://github.com/brianrodri')

    def test_ignores_backticked_data(self):
        """Tests that backticked data do not get changed."""
        transformer = transformers.ItalicTransformer()
        self.assertEqual(transformer.fmt('//italic//, `//escaped italic//`'),
                         '_italic_, `//escaped italic//`')


class LinkTransformerTest(unittest.TestCase):
    """Test transforming Rednotebook-style links to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = transformers.LinkTransformer()
        self.assertEqual(transformer.fmt('[sample text ""go/somewhere""]'),
                         '[sample text](go/somewhere)')


class StrikethroughTransformerTest(unittest.TestCase):
    """Test transforming Rednotebook-style strikethroughs to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = transformers.StrikethroughTransformer()
        self.assertEqual(transformer.fmt('--text--'), '**OBSOLETE**(text)')

    def test_punctuation_gets_stripped(self):
        """Tests punctuation is removed from parenthesized text."""
        transformer = transformers.StrikethroughTransformer()
        self.assertEqual(transformer.fmt('--a complete sentence.--'),
                         '**OBSOLETE**(a complete sentence)')

    def test_ignores_non_paired_markers(self):
        """Tests solitary markers are left alone."""
        transformer = transformers.StrikethroughTransformer()
        self.assertEqual(
            transformer.fmt('--changed--, --this too--, not here--or here.'),
            '**OBSOLETE**(changed), **OBSOLETE**(this too), not here--or here.')

    def test_ignores_urls(self):
        """Tests urls are not changed."""
        transformer = transformers.StrikethroughTransformer()
        self.assertEqual(transformer.fmt('http://do/something--weird'),
                         'http://do/something--weird')

    def test_ignores_backticked_data(self):
        """Tests backticked data is left alone."""
        transformer = transformers.StrikethroughTransformer()
        self.assertEqual(transformer.fmt('--hit--, `--not hit--`'),
                         '**OBSOLETE**(hit), `--not hit--`')

    def test_ignores_lines_with_only_backticks(self):
        """Tests that data with only backticks are not changed."""
        transformer = transformers.StrikethroughTransformer()
        self.assertEqual(transformer.fmt('-' * 12), '-' * 12)


class HeaderTransformerTest(unittest.TestCase):
    """Test transforming Rednotebook-style header to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = transformers.HeaderTransformer()
        self.assertEqual(transformer.fmt('=Level One='), '# Level One')
        self.assertEqual(transformer.fmt('===Level Three==='),
                         '### Level Three')

    def test_base_level_is_respected(self):
        """Tests changes to init level."""
        transformer = transformers.HeaderTransformer(init_level=2)
        self.assertEqual(transformer.fmt('===Only 3==='), '##### Only 3')

    def test_inner_markers_are_ignored(self):
        """Tests header markings are only interpreted when surrounding line."""
        transformer = transformers.HeaderTransformer()
        self.assertEqual(transformer.fmt('Not at =start= of text'),
                         'Not at =start= of text')

    def test_only_markers_are_ignored(self):
        """Tests lines with only markers aren't affected."""
        transformer = transformers.HeaderTransformer()
        self.assertEqual(transformer.fmt('=' * 6), '=' * 6)
        self.assertEqual(transformer.fmt('=' * 7), '=' * 7)

    def test_un_balanced_markers_are_ignored(self):
        """Tests that lines must use balanced markers."""
        transformer = transformers.HeaderTransformer()
        self.assertEqual(transformer.fmt('==Unbalanced==='), '==Unbalanced===')


class ListTransformerTest(unittest.TestCase):
    """Test transforming Rednotebook-style lists to markdown-style."""

    def test_unordered_list(self):
        """Tests expected usage for unordered lists."""
        transformer = transformers.ListTransformer()
        input_lines = [
            '- A',
            ' - B',
            '- A',
        ]
        self.assertEqual([transformer.fmt(l) for l in input_lines], [
            '- A',
            ' - B',
            '- A',
        ])

    def test_ordered_list(self):
        """Tests expected usage for ordered lists."""
        transformer = transformers.ListTransformer()
        input_lines = [
            '+ A',
            ' + B',
            '+ A',
        ]
        self.assertEqual([transformer.fmt(l) for l in input_lines], [
            '1. A',
            ' 1. B',
            '2. A',
        ])

    def test_two_blank_lines_reset_numbering(self):
        """Tests two blank lines starts separate ordered lists."""
        transformer = transformers.ListTransformer()
        input_lines = [
            '+ A',
            '+ B',
            '',
            '',
            '+ C'
        ]
        self.assertEqual([transformer.fmt(l) for l in input_lines], [
            '1. A',
            '2. B',
            '',
            '',
            '1. C',
        ])

    def test_content_between_ordered_list_resets_numbering(self):
        """Tests content between ordered lists restarts numbering."""
        transformer = transformers.ListTransformer()
        input_lines = [
            '+ A',
            '+ B',
            'Content',
            '+ C',
        ]
        self.assertEqual([transformer.fmt(l) for l in input_lines], [
            '1. A',
            '2. B',
            'Content',
            '1. C',
        ])

    def test_nested_levels_are_reset_once_passed(self):
        """Tests that nested levels are respected."""
        transformer = transformers.ListTransformer()
        input_lines = [
            '+ A',
            ' + B',
            ' + C',
            '  + D',
            '+ E',
            ' + F',
            '  + G',
        ]
        self.assertEqual([transformer.fmt(l) for l in input_lines], [
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
        transformer = transformers.ListTransformer()
        input_lines = [
            '+ A',
            ' - B',
            '+ C',
        ]
        self.assertEqual([transformer.fmt(l) for l in input_lines], [
            '1. A',
            ' - B',
            '2. C',
        ])


class InnerUnderscoreEscaperTest(unittest.TestCase):
    """Test transforming Rednotebook-style underscores to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = transformers.InnerUnderscoreEscaper()
        self.assertEqual(transformer.fmt('underscore_delimited_word'),
                         r'underscore\_delimited\_word')

    def test_trailing_underscores_ignored(self):
        """Tests trailing underscores are left alone."""
        transformer = transformers.InnerUnderscoreEscaper()
        self.assertEqual(transformer.fmt('_with_trailing_underscores_'),
                         r'_with\_trailing\_underscores_')

    def test_ignores_urls(self):
        """Tests that underscores in urls are left alone."""
        transformer = transformers.InnerUnderscoreEscaper()
        self.assertEqual(
            transformer.fmt('[test_thing ""http://github.com/test_thing""]'),
            r'[test\_thing ""http://github.com/test_thing""]')

    def test_ignores_backticked_data(self):
        """Tests that underscores between backticks are left alone."""
        transformer = transformers.InnerUnderscoreEscaper()
        self.assertEqual(transformer.fmt('gets_escaped, `no_escape`'),
                         r'gets\_escaped, `no_escape`')


class CodeBlockTransformerTest(unittest.TestCase):
    """Test transforming Rednotebook-style code blocks to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = transformers.CodeBlockTransformer()
        self.assertEqual(transformer.fmt('``code encoded stuff``'),
                         '`code encoded stuff`')

    def test_only_two_backticks_are_transformed(self):
        """Tests that multi-line code blocks are left alone."""
        transformer = transformers.CodeBlockTransformer()
        input_lines = [
            '```py',
            '# Python code',
            '```',
        ]
        self.assertEqual([transformer.fmt(l) for l in input_lines], [
            '```py',
            '# Python code',
            '```',
        ])


if __name__ == '__main__':
    unittest.main()
