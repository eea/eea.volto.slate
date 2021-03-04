# -*- coding: utf-8 -*-
import json
import os
import unittest

from pkg_resources import resource_filename

from eea.volto.slate.convert import (Parser,  # convert_jsx_to_json,
                                     text_to_slate)


def read_data(filename):
    fpath = resource_filename("eea.volto.slate", os.path.join("tests/data", filename))

    with open(fpath) as f:
        return f.read()


def read_json(filename):
    fpath = resource_filename("eea.volto.slate", os.path.join("tests/data", filename))

    with open(fpath) as f:
        return json.load(f)


class TestConvert(unittest.TestCase):
    maxDiff = None

    def test_convert_simple_string(self):
        parser = Parser()
        res = parser.to_slate("Hello world")
        self.assertEqual(res, [{"children": [{"text": "Hello world"}], "type": "p"}])

    def test_convert_simple_paragraph(self):
        parser = Parser()

        res = parser.to_slate("<p>Hello world</p>")
        self.assertEqual(res, [{"children": [{"text": "Hello world"}], "type": "p"}])

    def test_convert_text_and_a_tag(self):
        parser = Parser()
        res = parser.to_slate("Hello <strong>world</strong> mixed <i>content</i>.")

        self.assertEqual(
            res,
            [
                {
                    "children": [
                        {"text": "Hello "},
                        {"children": [{"text": "world"}], "type": "strong"},
                        {"text": " mixed "},
                        {"children": [{"text": "content"}], "type": "i"},
                        {"text": "."},
                    ],
                    "type": "p",
                }
            ],
        )

    def test_merge_text_nodes(self):
        p = Parser()

        q = [{"text": "a"}, {"text": "b"}, {"text": "c"}]
        res = p.merge_adjacent_text_nodes(q)
        self.assertEqual(res, [{"text": "abc"}])

        q = [{"text": "a"}, {"type": "m"}, {"text": "b"}, {"text": "c"}]
        res = p.merge_adjacent_text_nodes(q)
        self.assertEqual(
            res,
            [
                {"text": "a"},
                {"type": "m"},
                {"text": "bc"},
            ],
        )

        q = [
            {"text": "a"},
            {"type": "m"},
            {"text": "b"},
            {"text": "c"},
            {"type": "m"},
            {"text": "d"},
            {"text": "e"},
        ]
        res = p.merge_adjacent_text_nodes(q)
        self.assertEqual(
            res,
            [
                {"text": "a"},
                {"type": "m"},
                {"text": "bc"},
                {"type": "m"},
                {"text": "de"},
            ],
        )

    def test_convert_case_simple_p(self):
        text = read_data("1.html")
        res = text_to_slate(text)

        self.assertEqual(
            res,
            read_json("1.json"),
        )

    #
    # def test_convert_case_multiple_p(self):
    #     text = read_data("2.html")
    #     res = html_fragment_to_slate(text)
    #
    #     self.assertEqual(
    #         res,
    #         read_json("2.json"),
    #     )
    #
    # def test_convert_slate_output_markup(self):
    #     text = read_data("5.html")
    #     res = html_fragment_to_slate(text)
    #
    #     self.assertEqual(
    #         res,
    #         read_json("5.json"),
    #     )
    #
    # def test_slate_list(self):
    #     text = read_data("6.html")
    #     res = html_fragment_to_slate(text)
    #
    #     self.assertEqual(
    #         res,
    #         read_json("6.json"),
    #     )

    # def test_slate_data(self):
    #     text = read_data("7.html")
    #     res = html_fragment_to_slate(text, log=True)
    #     import pdb
    #
    #     pdb.set_trace()
