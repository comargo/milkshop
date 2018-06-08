from datetime import date
from unittest import TestCase

import helpers.url_converters as converters


class IsoDateConverterTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.converter = converters.IsoDateConverter()

    def test_regex(self):
        values = [
            ('2000-01-01', True),
            ('00-01-01', False),
            ('2000-01-02', True),
            ('abc', False)
        ]
        for value in values:
            with self.subTest(value[0]):
                assertfn = self.assertRegex if value[1] else self.assertNotRegex
                assertfn(value[0], self.converter.regex)

    def test_to_python(self):
        values = [
            ('2000-01-01', date(2000, 1, 1)),
            ('00-01-01', None),
            ('2000-01-02', date(2000, 1, 2)),
            ('abc', None)
        ]
        for value in values:
            with self.subTest(value):
                self.assertEqual(value[1], self.converter.to_python(value[0]))

    def test_to_url(self):
        values = [
            (None, AssertionError),
            (date(2000, 1, 1), '2000-01-01'),
            (date(2000, 1, 2), '2000-01-02'),
            ('abc', AssertionError)
        ]
        for value in values:
            with self.subTest(value):
                if isinstance(value[1], str):
                    self.assertEqual(value[1], self.converter.to_url(value[0]))
                elif issubclass(value[1], Exception):
                    self.assertRaises(value[1], self.converter.to_url, value[0])
