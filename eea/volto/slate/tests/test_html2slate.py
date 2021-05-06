""" test html2slate """
# -*- coding: utf-8 -*-
# pylint: disable=import-error,no-name-in-module,too-few-public-methods,
# pylint: disable=not-callable,no-self-use,unused-argument,invalid-name

import json
import os
import unittest

from pkg_resources import resource_filename

from eea.volto.slate.html2slate import merge_adjacent_text_nodes, text_to_slate


def read_data(filename):
    """read_data.

    :param filename:
    """
    fpath = resource_filename("eea.volto.slate", os.path.join("tests/data",
                                                              filename))

    with open(fpath) as f:
        return f.read()


def read_json(filename):
    """read_json.

    :param filename:
    """
    fpath = resource_filename("eea.volto.slate", os.path.join("tests/data",
                                                              filename))

    with open(fpath) as f:
        return json.load(f)


class TestConvertHTML2Slate(unittest.TestCase):
    """TestConvertHTML2Slate."""

    maxDiff = None

    def test_convert_simple_string(self):
        """test_convert_simple_string."""
        res = text_to_slate("Hello world")
        self.assertEqual(res, [{"children": [{"text": "Hello world"}],
                                "type": "p"}])

    def test_convert_simple_paragraph(self):
        """test_convert_simple_paragraph."""
        res = text_to_slate("<p>Hello world</p>")
        self.assertEqual(res, [{"children": [{"text": "Hello world"}],
                                "type": "p"}])

    def test_convert_text_and_a_tag(self):
        """test_convert_simple_paragraph."""
        res = text_to_slate(
            "Hello <strong>world</strong> mixed <i>content</i>.")

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
        """test_merge_text_nodes."""
        q = [{"text": "a"}, {"text": "b"}, {"text": "c"}]
        res = merge_adjacent_text_nodes(q)
        self.assertEqual(res, [{"text": "abc"}])

        q = [{"text": "a"}, {"type": "m"}, {"text": "b"}, {"text": "c"}]
        res = merge_adjacent_text_nodes(q)
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
        res = merge_adjacent_text_nodes(q)
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
        """test_convert_case_simple_p."""
        text = read_data("1.html")
        res = text_to_slate(text)

        self.assertEqual(
            res,
            read_json("1.json"),
        )

    def test_convert_case_multiple_p(self):
        """test_convert_case_multiple_p."""
        text = read_data("2.html")
        res = text_to_slate(text)

        self.assertEqual(
            res,
            read_json("2.json"),
        )

    # def test_one_list_item(self):
    #     """test_one_list_item."""
    #    text = """<li>      <a
    #    href="/case-study-hub/CS-brown-bears-Italy"
    #    >Brown bear (<em>ursus arctos</em>) in Italy</a>
    #    </li>
    #    </ul>"""
    #    res = text_to_slate(text)

    #    self.assertEqual(
    #        res,
    #        [{"children": [
    #            {"text": ""},
    #            {"children": [
    #                {"text": "Brown bear ("},
    #                {"children": [{"text": "ursus arctos"}], "type": "em"},
    #                {"text": ") in Italy"}, ],
    #             "data": {
    #                 "link": {
    #                     "internal": {
    #                         "internal_link": [
    #                             {"@id":
    #                              "/case-study-hub/CS-brown-bears-Italy"}
    #                         ]
    #                     }
    #                 }},
    #             "type": "a", },
    #            {"text": ""}, ],
    #          "type": "li", }],
    #    )

    # def test_convert_slate_output_markup(self):
    #    """test_convert_slate_output_markup."""
    #    text = read_data("5.html")
    #    res = text_to_slate(text)

    #    self.assertEqual(
    #        res,
    #        read_json("5.json"),
    #    )

    # def test_slate_list(self):
    #    """test_slate_list."""
    #    text = read_data("6.html")
    #    res = text_to_slate(text)

    #    self.assertEqual(
    #        res,
    #        read_json("6.json"),
    #    )

    # def test_slate_data(self):
    #    """test_slate_list."""
    #    text = read_data("7.html")
    #    res = text_to_slate(text)
    #    self.assertEqual(
    #        res,
    #        read_json("7.json"),
    #    )

    # def test_wrapped_slate_data(self):
    #    """test_wrapped_slate_data."""
    #    text = read_data("8.html")
    #    res = text_to_slate(text)
    #    self.assertEqual(
    #        res,
    #        read_json("8.json"),
    #    )
