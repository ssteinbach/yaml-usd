#!/usr/bin/env python

import unittest
import usda_writer


class TestYaml(unittest.TestCase):
    def test_requires_dict(self):
        with self.assertRaises(ValueError):
            usda_writer.to_usda(12)

    def test_int(self):
        self.assertIn(
            "int test = 12",
            usda_writer.to_usda({'test': 12}),
        )

    # def test_bool(self):
    #     self.assertIn(
    #         "int test = 12",
    #         usda_writer.to_usda({'test': 12}),
    #     )

    def test_float(self):
        self.assertIn(
            "float test = 1.0",
            usda_writer.to_usda({'test': 1.0}),
        )

    def test_string(self):
        self.assertIn(
            'token test = "asdf"',
            usda_writer.to_usda({'test': "asdf"}),
        )

if __name__ == '__main__':
    unittest.main()
