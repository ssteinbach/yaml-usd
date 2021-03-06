#!/usr/bin/env python

import unittest
import usda_writer


NONE_TEST = """#usda 1.0
(
    endFrame = 1
    startFrame = 1
)

def Scope "root"
{

}
"""


class TestYaml(unittest.TestCase):
    def test_requires_dict(self):
        with self.assertRaises(ValueError):
            usda_writer.to_usda(12)

    def test_int(self):
        self.assertIn(
            "int test = 12",
            usda_writer.to_usda({'test': 12}),
        )

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

    def test_none(self):
        self.assertEqual(NONE_TEST, usda_writer.to_usda({'test': None}))

    def test_list(self):
        self.assertIn(
            'token[] test = ["first","second"]',
            usda_writer.to_usda({'test': ["first", "second"]}),
        )

        # test that the first item sets the type for the list
        self.assertIn(
            'token[] test = ["asdf","1"]',
            usda_writer.to_usda({'test': ["asdf", 1]}),
        )

        # test non-string lists
        self.assertIn(
            'int[] test = [1,2,3,4]',
            usda_writer.to_usda({'test': [1, 2, 3, 4]}),
        )

    def test_map(self):
        self.assertIn(
            'def Scope "test"',
            usda_writer.to_usda({'test': {"test_int": 1}}),
        )

    def test_commandline(self):
        usda_writer.main(["test.yml"])


if __name__ == '__main__':
    unittest.main()
