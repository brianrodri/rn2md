#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Test cases for the transformers module."""
import unittest

from rn2md import transformers


class TransformerTestCase(unittest.TestCase):
    """Provides convienience method to build a transformer class instance.

    Assumes derived classes are named after a class in the transformers module
    in the format: f'{cls.__name__}Test'.
    """

    @classmethod
    def new_transformer(cls, *args, **kwargs):
        """Convienience method to build the transformer class under-test."""
        transformer_name = cls.__name__[:-4]
        transformer_generator = getattr(transformers, transformer_name)
        transformer = transformer_generator(*args, **kwargs)
        # Transformers are generators, so they need an initial call to `.next()`
        # to prepare them.
        # NOTE: This is the main motivation behind this helper method; all of
        # the `next(transformer)` calls would bloat test code.
        next(transformer)
        return transformer


class ItalicTransformerTest(TransformerTestCase):
    """Test transforming Rednotebook-style italics to markdown-style."""

    def test_transformation(self):
        """Test expected usage"""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('Text with //italicized// content.'),
                         'Text with _italicized_ content.')

    def test_ignores_non_paired_markers(self):
        """Tests solitary markers are left alone."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('//italic1//, //italic2//, unused //'),
                         '_italic1_, _italic2_, unused //')

    def test_ignores_urls(self):
        """Tests urls do not have their dashes changed."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('http://github.com/brianrodri'),
                         'http://github.com/brianrodri')

    def test_ignores_backticked_data(self):
        """Tests that backticked data do not get changed."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('//italic//, `//escaped italic//`'),
                         '_italic_, `//escaped italic//`')


class LinkTransformerTest(TransformerTestCase):
    """Test transforming Rednotebook-style links to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('[sample text ""go/somewhere""]'),
                         '[sample text](go/somewhere)')


class StrikethroughTransformerTest(TransformerTestCase):
    """Test transforming Rednotebook-style strikethroughs to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('--text--'), '**OBSOLETE**(text)')

    def test_punctuation_gets_stripped(self):
        """Tests punctuation is removed from parenthesized text."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('--a complete sentence.--'),
                         '**OBSOLETE**(a complete sentence)')

    def test_ignores_non_paired_markers(self):
        """Tests solitary markers are left alone."""
        transformer = self.new_transformer()
        self.assertEqual(
            transformer.send('--changed--, --this too--, not here--or here.'),
            '**OBSOLETE**(changed), **OBSOLETE**(this too), not here--or here.')

    def test_ignores_urls(self):
        """Tests urls are not changed."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('http://do/something--weird'),
                         'http://do/something--weird')

    def test_ignores_backticked_data(self):
        """Tests backticked data is left alone."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('--hit--, `--not hit--`'),
                         '**OBSOLETE**(hit), `--not hit--`')

    def test_ignores_lines_with_only_backticks(self):
        """Tests that data with only backticks are not changed."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('-' * 12), '-' * 12)


class HeaderTransformerTest(TransformerTestCase):
    """Test transforming Rednotebook-style header to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('=Level One='), '# Level One')
        self.assertEqual(transformer.send('===Level Three==='),
                         '### Level Three')

    def test_base_level_is_respected(self):
        """Tests changes to default base level create different headings."""
        transformer = self.new_transformer(base_level=2)
        self.assertEqual(transformer.send('===Only 3==='), '##### Only 3')

    def test_inner_markers_are_ignored(self):
        """Tests header markings are only interpreted when surrounding line."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('Not at =start= of text'),
                         'Not at =start= of text')

    def test_only_markers_are_ignored(self):
        """Tests lines with only markers aren't affected."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('=' * 6), '=' * 6)
        self.assertEqual(transformer.send('=' * 7), '=' * 7)

    def test_un_balanced_markers_are_ignored(self):
        """Tests that lines must use balanced markers."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('==Unbalanced==='), '==Unbalanced===')


class ListTransformerTest(TransformerTestCase):
    """Test transforming Rednotebook-style lists to markdown-style."""

    def test_unordered_list(self):
        """Tests expected usage for unordered lists."""
        transformer = self.new_transformer()
        input_lines = [
            '- A',
            ' - B',
            '- A',
        ]
        self.assertEqual([transformer.send(l) for l in input_lines], [
            '- A',
            ' - B',
            '- A',
        ])

    def test_ordered_list(self):
        """Tests expected usage for ordered lists."""
        transformer = self.new_transformer()
        input_lines = [
            '+ A',
            ' + B',
            '+ A',
        ]
        self.assertEqual([transformer.send(l) for l in input_lines], [
            '1. A',
            ' 1. B',
            '2. A',
        ])

    def test_two_blank_lines_reset_numbering(self):
        """Tests two blank lines starts separate ordered lists."""
        transformer = self.new_transformer()
        input_lines = [
            '+ A',
            '+ B',
            '',
            '',
            '+ C'
        ]
        self.assertEqual([transformer.send(l) for l in input_lines], [
            '1. A',
            '2. B',
            '',
            '',
            '1. C',
        ])

    def test_content_between_ordered_list_resets_numbering(self):
        """Tests content between ordered lists restarts numbering."""
        transformer = self.new_transformer()
        input_lines = [
            '+ A',
            '+ B',
            'Content',
            '+ C',
        ]
        self.assertEqual([transformer.send(l) for l in input_lines], [
            '1. A',
            '2. B',
            'Content',
            '1. C',
        ])

    def test_nested_levels_are_reset_once_passed(self):
        """Tests that nested levels are respected."""
        transformer = self.new_transformer()
        input_lines = [
            '+ A',
            ' + B',
            ' + C',
            '  + D',
            '+ E',
            ' + F',
            '  + G',
        ]
        self.assertEqual([transformer.send(l) for l in input_lines], [
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
        transformer = self.new_transformer()
        input_lines = [
            '+ A',
            ' - B',
            '+ C',
        ]
        self.assertEqual([transformer.send(l) for l in input_lines], [
            '1. A',
            ' - B',
            '2. C',
        ])


class InnerUnderscoreEscaperTest(TransformerTestCase):
    """Test transforming Rednotebook-style underscores to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('underscore_delimited_word'),
                         r'underscore\_delimited\_word')

    def test_trailing_underscores_ignored(self):
        """Tests trailing underscores are left alone."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('_with_trailing_underscores_'),
                         r'_with\_trailing\_underscores_')

    def test_ignores_urls(self):
        """Tests that underscores in urls are left alone."""
        transformer = self.new_transformer()
        self.assertEqual(
            transformer.send('[test_thing ""http://github.com/test_thing""]'),
            r'[test\_thing ""http://github.com/test_thing""]')

    def test_ignores_backticked_data(self):
        """Tests that underscores between backticks are left alone."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('gets_escaped, `no_escape`'),
                         r'gets\_escaped, `no_escape`')


class CodeBlockTransformerTest(TransformerTestCase):
    """Test transforming Rednotebook-style code blocks to markdown-style."""

    def test_transformation(self):
        """Tests expected usage."""
        transformer = self.new_transformer()
        self.assertEqual(transformer.send('``code encoded stuff``'),
                         '`code encoded stuff`')

    def test_only_two_backticks_are_transformed(self):
        """Tests that multi-line code blocks are left alone."""
        transformer = self.new_transformer()
        input_lines = [
            '```py',
            '# Python code',
            '```',
        ]
        self.assertEqual([transformer.send(l) for l in input_lines], [
            '```py',
            '# Python code',
            '```',
        ])


if __name__ == '__main__':
    unittest.main()
