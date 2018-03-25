#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""Test cases for the transformers module."""
import unittest

import transformers


class ItalicTransformerTest(unittest.TestCase):

    def setUp(self):
        self.tfmr = transformers.ItalicTransformer()
        next(self.tfmr)

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


class LinkTransformer(unittest.TestCase):

    def setUp(self):
        self.tfmr = transformers.LinkTransformer()
        next(self.tfmr)

    def testTransformation(self):
        self.assertEqual(
            self.tfmr.send('[[sample text ""go/somewhere""]]'),
            '[sample text](go/somewhere)')


if __name__ == '__main__':
    unittest.main()