#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Test cases for the transformers module."""
import unittest

import transformers


class ItalicTransformerTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.ItalicTransformer(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(self.trans.send('Text with //italicized// content.'),
                         'Text with _italicized_ content.')

    def testIgnoresNonPairedMarkers(self):
        self.assertEqual(self.trans.send('//italic1//, //italic2//, unused //'),
                         '_italic1_, _italic2_, unused //')

    def testIgnoresUrls(self):
        self.assertEqual(self.trans.send('http://github.com/brianrodri'),
                         'http://github.com/brianrodri')

    def testIgnoresBacktickedData(self):
        self.assertEqual(self.trans.send('//italic//, `//escaped italic//`'),
                         '_italic_, `//escaped italic//`')


class LinkTransformerTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.LinkTransformer(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(self.trans.send('[sample text ""go/somewhere""]'),
                         '[sample text](go/somewhere)')


class StrikethroughTransformerTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.StrikethroughTransformer(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(self.trans.send('--text--'), '**OBSOLETE**(text)')

    def testPunctuationGetsStripped(self):
        self.assertEqual(self.trans.send('--a complete sentence.--'),
                         '**OBSOLETE**(a complete sentence)')

    def testIgnoresNonPairedMarkers(self):
        self.assertEqual(
            self.trans.send('--changed--, --this too--, not here--or here.'),
            '**OBSOLETE**(changed), **OBSOLETE**(this too), not here--or here.')

    def testIgnoresUrls(self):
        self.assertEqual(self.trans.send('http://do/something--weird'),
                         'http://do/something--weird')

    def testIgnoresBacktickedData(self):
        self.assertEqual(self.trans.send('--hit--, `--not hit--`'),
                         '**OBSOLETE**(hit), `--not hit--`')

    def testIgnoresLinesWithOnlyBackticks(self):
        self.assertEqual(self.trans.send('-' * 12), '-' * 12)


class HeaderTransformerTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.HeaderTransformer(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(self.trans.send('=Level One='), '# Level One')
        self.assertEqual(self.trans.send('===Level Three==='),
                         '### Level Three')

    def testBaseLevelIsRespected(self):
        trans = transformers.HeaderTransformer(base_level=2); next(trans)
        self.assertEqual(trans.send('===Only 3==='), '##### Only 3')

    def testInnerMarkersAreIgnored(self):
        self.assertEqual(self.trans.send('Not at =start= of text'),
                         'Not at =start= of text')

    def testOnlyMarkersAreIgnored(self):
        self.assertEqual(self.trans.send('=' * 6), '=' * 6)
        self.assertEqual(self.trans.send('=' * 7), '=' * 7)

    def testUnBalancedMarkersAreIgnored(self):
        self.assertEqual(self.trans.send('==Unbalanced==='), '==Unbalanced===')


class ListTransformerTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.ListTransformer(); next(self.trans)

    def testUnorderedList(self):
        input_lines = [
            '- A',
            ' - B',
            '- A',
        ]
        self.assertListEqual([self.trans.send(l) for l in input_lines], [
            '- A',
            ' - B',
            '- A',
        ])

    def testOrderedList(self):
        input_lines = [
            '+ A',
            ' + B',
            '+ A',
        ]
        self.assertListEqual([self.trans.send(l) for l in input_lines], [
            '1. A',
            ' 1. B',
            '2. A',
        ])

    def testTwoBlankLinesResetNumbering(self):
        input_lines = [
            '+ A',
            '+ B',
            '',
            '',
            '+ C'
        ]
        self.assertListEqual([self.trans.send(l) for l in input_lines], [
            '1. A',
            '2. B',
            '',
            '',
            '1. C',
        ])

    def testContentBetweenOrderedListResetsNumbering(self):
        input_lines = [
            '+ A',
            '+ B',
            'Content',
            '+ C',
        ]
        self.assertListEqual([self.trans.send(l) for l in input_lines], [
            '1. A',
            '2. B',
            'Content',
            '1. C',
        ])

    def testNestedLevelsAreResetOncePassed(self):
        input_lines = [
            '+ A',
            ' + B',
            ' + C',
            '  + D',
            '+ E',
            ' + F',
            '  + G',
        ]
        self.assertListEqual([self.trans.send(l) for l in input_lines], [
            '1. A',
            ' 1. B',
            ' 2. C',
            '  1. D',
            '2. E',
            ' 1. F',
            '  1. G',
        ])

    def testNestedLevelsAreNotInterruptedByUnorderedLists(self):
        input_lines = [
            '+ A',
            ' - B',
            '+ C',
        ]
        self.assertListEqual([self.trans.send(l) for l in input_lines], [
            '1. A',
            ' - B',
            '2. C',
        ])


class InnerUnderscoreEscaperTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.InnerUnderscoreEscaper(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(self.trans.send('underscore_delimited_word'),
                         r'underscore\_delimited\_word')

    def testTrailingUnderscoresIgnored(self):
        self.assertEqual(self.trans.send('_with_trailing_underscores_'),
                         r'_with\_trailing\_underscores_')

    def testIgnoresUrls(self):
        self.assertEqual(
            self.trans.send('[test_thing ""http://github.com/test_thing""]'),
            r'[test\_thing ""http://github.com/test_thing""]')

    def testIgnoresBacktickedData(self):
        self.assertEqual(self.trans.send('gets_escaped, `no_escape`'),
                         r'gets\_escaped, `no_escape`')


class CodeBlockTransformer(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.CodeBlockTransformer(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(self.trans.send('``code encoded stuff``'),
                         '`code encoded stuff`')

    def testOnlyTwoBackticksAreTransformed(self):
        input_lines = [
            '```py',
            '# Python code',
            '```',
        ]
        self.assertListEqual([self.trans.send(l) for l in input_lines], [
            '```py',
            '# Python code',
            '```',
        ])


if __name__ == '__main__':
    unittest.main()
