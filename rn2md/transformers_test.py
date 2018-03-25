#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Test cases for the transformers module."""
import unittest

import transformers


class ItalicTransformerTest(unittest.TestCase):

    def setUp(self):
        self.tfmr = transformers.ItalicTransformer(); next(self.tfmr)

    def testTransformation(self):
        self.assertEqual(
            self.tfmr.send('Text with //italicized// content.'),
            'Text with _italicized_ content.')

    def testIgnoresNonPairedMarkers(self):
        self.assertEqual(
            self.tfmr.send('//italic1//, //italic2//, unused //'),
            '_italic1_, _italic2_, unused //')

    def testIgnoresUrls(self):
        self.assertEqual(
            self.tfmr.send('http://github.com/brianrodri'),
            'http://github.com/brianrodri')

    def testIgnoresBacktickedData(self):
        self.assertEqual(
            self.tfmr.send('//italic//, `//escaped italic//`'),
            '_italic_, `//escaped italic//`')


class LinkTransformerTest(unittest.TestCase):

    def setUp(self):
        self.tfmr = transformers.LinkTransformer(); next(self.tfmr)

    def testTransformation(self):
        self.assertEqual(
            self.tfmr.send('[[sample text ""go/somewhere""]]'),
            '[sample text](go/somewhere)')


class StrikethroughTransformerTest(unittest.TestCase):

    def setUp(self):
        self.tfmr = transformers.StrikethroughTransformer(); next(self.tfmr)

    def testTransformation(self):
        self.assertEqual(self.tfmr.send('--text--'), '**OBSOLETE**(text)')

    def testPunctuationGetsStripped(self):
        self.assertEqual(
            self.tfmr.send('--a complete sentence.--'),
            '**OBSOLETE**(a complete sentence)')

    def testIgnoresNonPairedMarkers(self):
        self.assertEqual(
            self.tfmr.send('--changed--, --this too--, not here--or here.'),
            '**OBSOLETE**(changed), **OBSOLETE**(this too), not here--or here.')

    def testIgnoresUrls(self):
        self.assertEqual(
            self.tfmr.send('http://do/something--weird'),
            'http://do/something--weird')

    def testIgnoresBacktickedData(self):
        self.assertEqual(
            self.tfmr.send('--hit--, `--not hit--`'),
            '**OBSOLETE**(hit), `--not hit--`')


class HeaderTransformerTest(unittest.TestCase):

    def setUp(self):
        self.tfmr = transformers.HeaderTransformer(); next(self.tfmr)

    def testTransformation(self):
        self.assertEqual(self.tfmr.send('=TEXT='), '# TEXT')

    def testBaseLevelIsRespected(self):
        tfmr = transformers.HeaderTransformer(base_level=2); next(tfmr)
        self.assertEqual(tfmr.send('===Only 3==='), '##### Only 3')

    def testInnerMarkersAreIgnored(self):
        self.assertEqual(
            self.tfmr.send('Not at =start= of text'),
            'Not at =start= of text')

    def testOnlyMarkersAreIgnored(self):
        self.assertEqual(self.tfmr.send('=' * 6), '=' * 6)
        self.assertEqual(self.tfmr.send('=' * 7), '=' * 7)

    def testUnBalancedMarkersAreIgnored(self):
        self.assertEqual(self.tfmr.send('==Unbalanced==='), '==Unbalanced===')


if __name__ == '__main__':
    unittest.main()
