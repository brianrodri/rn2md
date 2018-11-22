#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Test cases for the transformers module."""
from rn2md import transformers

import unittest


class TransformerBaseTest(unittest.TestCase):
    """Provides convienience method to build a transformer_class instance.

    Assumes that derived classes are named after some class in the modules
    transformers in the format: f'{cls.__name__}Test'
    """

    @classmethod
    def BuildTransformer(cls, *args, **kwargs):
        """Convienience method to build the transformer class under-test."""
        transformer_name = cls.__name__[:-4]
        transformer_class = getattr(transformers, transformer_name)
        t = transformer_class(*args, **kwargs)

        # Transformers are generators, so they need an initial call to `.next()`
        # to prepare them.
        next(t)
        return t


class ItalicTransformerTest(TransformerBaseTest):

    def testTransformation(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('Text with //italicized// content.'),
                         'Text with _italicized_ content.')

    def testIgnoresNonPairedMarkers(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('//italic1//, //italic2//, unused //'),
                         '_italic1_, _italic2_, unused //')

    def testIgnoresUrls(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('http://github.com/brianrodri'),
                         'http://github.com/brianrodri')

    def testIgnoresBacktickedData(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('//italic//, `//escaped italic//`'),
                         '_italic_, `//escaped italic//`')


class LinkTransformerTest(TransformerBaseTest):

    def testTransformation(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('[sample text ""go/somewhere""]'),
                         '[sample text](go/somewhere)')


class StrikethroughTransformerTest(TransformerBaseTest):

    def testTransformation(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('--text--'), '**OBSOLETE**(text)')

    def testPunctuationGetsStripped(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('--a complete sentence.--'),
                         '**OBSOLETE**(a complete sentence)')

    def testIgnoresNonPairedMarkers(self):
        t = self.BuildTransformer()
        self.assertEqual(
            t.send('--changed--, --this too--, not here--or here.'),
            '**OBSOLETE**(changed), **OBSOLETE**(this too), not here--or here.')

    def testIgnoresUrls(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('http://do/something--weird'),
                         'http://do/something--weird')

    def testIgnoresBacktickedData(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('--hit--, `--not hit--`'),
                         '**OBSOLETE**(hit), `--not hit--`')

    def testIgnoresLinesWithOnlyBackticks(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('-' * 12), '-' * 12)


class HeaderTransformerTest(TransformerBaseTest):

    def testTransformation(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('=Level One='), '# Level One')
        self.assertEqual(t.send('===Level Three==='),
                         '### Level Three')

    def testBaseLevelIsRespected(self):
        t = self.BuildTransformer(base_level=2)
        self.assertEqual(t.send('===Only 3==='), '##### Only 3')

    def testInnerMarkersAreIgnored(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('Not at =start= of text'),
                         'Not at =start= of text')

    def testOnlyMarkersAreIgnored(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('=' * 6), '=' * 6)
        self.assertEqual(t.send('=' * 7), '=' * 7)

    def testUnBalancedMarkersAreIgnored(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('==Unbalanced==='), '==Unbalanced===')


class ListTransformerTest(TransformerBaseTest):

    def testUnorderedList(self):
        t = self.BuildTransformer()
        input_lines = [
            '- A',
            ' - B',
            '- A',
        ]
        self.assertEqual([t.send(l) for l in input_lines], [
            '- A',
            ' - B',
            '- A',
        ])

    def testOrderedList(self):
        t = self.BuildTransformer()
        input_lines = [
            '+ A',
            ' + B',
            '+ A',
        ]
        self.assertEqual([t.send(l) for l in input_lines], [
            '1. A',
            ' 1. B',
            '2. A',
        ])

    def testTwoBlankLinesResetNumbering(self):
        t = self.BuildTransformer()
        input_lines = [
            '+ A',
            '+ B',
            '',
            '',
            '+ C'
        ]
        self.assertEqual([t.send(l) for l in input_lines], [
            '1. A',
            '2. B',
            '',
            '',
            '1. C',
        ])

    def testContentBetweenOrderedListResetsNumbering(self):
        t = self.BuildTransformer()
        input_lines = [
            '+ A',
            '+ B',
            'Content',
            '+ C',
        ]
        self.assertEqual([t.send(l) for l in input_lines], [
            '1. A',
            '2. B',
            'Content',
            '1. C',
        ])

    def testNestedLevelsAreResetOncePassed(self):
        t = self.BuildTransformer()
        input_lines = [
            '+ A',
            ' + B',
            ' + C',
            '  + D',
            '+ E',
            ' + F',
            '  + G',
        ]
        self.assertEqual([t.send(l) for l in input_lines], [
            '1. A',
            ' 1. B',
            ' 2. C',
            '  1. D',
            '2. E',
            ' 1. F',
            '  1. G',
        ])

    def testNestedLevelsAreNotInterruptedByUnorderedLists(self):
        t = self.BuildTransformer()
        input_lines = [
            '+ A',
            ' - B',
            '+ C',
        ]
        self.assertEqual([t.send(l) for l in input_lines], [
            '1. A',
            ' - B',
            '2. C',
        ])


class InnerUnderscoreEscaperTest(TransformerBaseTest):

    def testTransformation(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('underscore_delimited_word'),
                         r'underscore\_delimited\_word')

    def testTrailingUnderscoresIgnored(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('_with_trailing_underscores_'),
                         r'_with\_trailing\_underscores_')

    def testIgnoresUrls(self):
        t = self.BuildTransformer()
        self.assertEqual(
            t.send('[test_thing ""http://github.com/test_thing""]'),
            r'[test\_thing ""http://github.com/test_thing""]')

    def testIgnoresBacktickedData(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('gets_escaped, `no_escape`'),
                         r'gets\_escaped, `no_escape`')


class CodeBlockTransformerTest(TransformerBaseTest):

    def testTransformation(self):
        t = self.BuildTransformer()
        self.assertEqual(t.send('``code encoded stuff``'),
                         '`code encoded stuff`')

    def testOnlyTwoBackticksAreTransformed(self):
        t = self.BuildTransformer()
        input_lines = [
            '```py',
            '# Python code',
            '```',
        ]
        self.assertEqual([t.send(l) for l in input_lines], [
            '```py',
            '# Python code',
            '```',
        ])


if __name__ == '__main__':
    unittest.main()
