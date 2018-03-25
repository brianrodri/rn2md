#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Test cases for the transformers module."""
import unittest

import transformers


class ItalicTransformerTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.ItalicTransformer(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(
            self.trans.send('Text with //italicized// content.'),
            'Text with _italicized_ content.')

    def testIgnoresNonPairedMarkers(self):
        self.assertEqual(
            self.trans.send('//italic1//, //italic2//, unused //'),
            '_italic1_, _italic2_, unused //')

    def testIgnoresUrls(self):
        self.assertEqual(
            self.trans.send('http://github.com/brianrodri'),
            'http://github.com/brianrodri')

    def testIgnoresBacktickedData(self):
        self.assertEqual(
            self.trans.send('//italic//, `//escaped italic//`'),
            '_italic_, `//escaped italic//`')


class LinkTransformerTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.LinkTransformer(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(
            self.trans.send('[[sample text ""go/somewhere""]]'),
            '[sample text](go/somewhere)')


class StrikethroughTransformerTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.StrikethroughTransformer(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(self.trans.send('--text--'), '**OBSOLETE**(text)')

    def testPunctuationGetsStripped(self):
        self.assertEqual(
            self.trans.send('--a complete sentence.--'),
            '**OBSOLETE**(a complete sentence)')

    def testIgnoresNonPairedMarkers(self):
        self.assertEqual(
            self.trans.send('--changed--, --this too--, not here--or here.'),
            '**OBSOLETE**(changed), **OBSOLETE**(this too), not here--or here.')

    def testIgnoresUrls(self):
        self.assertEqual(
            self.trans.send('http://do/something--weird'),
            'http://do/something--weird')

    def testIgnoresBacktickedData(self):
        self.assertEqual(
            self.trans.send('--hit--, `--not hit--`'),
            '**OBSOLETE**(hit), `--not hit--`')


class HeaderTransformerTest(unittest.TestCase):

    def setUp(self):
        self.trans = transformers.HeaderTransformer(); next(self.trans)

    def testTransformation(self):
        self.assertEqual(self.trans.send('=Level One='), '# Level One')
        self.assertEqual(
            self.trans.send('===Level Three==='), '### Level Three')

    def testBaseLevelIsRespected(self):
        trans = transformers.HeaderTransformer(base_level=2); next(trans)
        self.assertEqual(trans.send('===Only 3==='), '##### Only 3')

    def testInnerMarkersAreIgnored(self):
        self.assertEqual(
            self.trans.send('Not at =start= of text'),
            'Not at =start= of text')

    def testOnlyMarkersAreIgnored(self):
        self.assertEqual(self.trans.send('=' * 6), '=' * 6)
        self.assertEqual(self.trans.send('=' * 7), '=' * 7)

    def testUnBalancedMarkersAreIgnored(self):
        self.assertEqual(self.trans.send('==Unbalanced==='), '==Unbalanced===')


if __name__ == '__main__':
    unittest.main()
