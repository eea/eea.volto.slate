# -*- coding: utf-8 -*-

import json
import os
import unittest

from lxml.html.clean import clean_html
from pkg_resources import resource_filename

from eea.volto.slate.slate2html import slate_to_html


def read_data(filename):
    fpath = resource_filename("eea.volto.slate", os.path.join("tests/data", filename))

    with open(fpath) as f:
        return f.read()


def read_json(filename):
    fpath = resource_filename("eea.volto.slate", os.path.join("tests/data", filename))

    with open(fpath) as f:
        return json.load(f)


def is_html_equal(proba_a, proba_b):
    a = clean_html(proba_a).replace("\n", " ").strip()
    b = clean_html(proba_b).replace("\n", " ").strip()
    return a == b


class TestConvertSlate2HTML(unittest.TestCase):
    maxDiff = None

    def test_convert_simple_string(self):
        res = slate_to_html([{"children": [{"text": "Hello world"}], "type": "p"}])
        self.assertEqual(res, "<p>Hello world</p>")

    def test_convert_simple_paragraph(self):
        res = slate_to_html([{"children": [{"text": "Hello world"}], "type": "p"}])
        self.assertEqual(res, "<p>Hello world</p>")

    def test_convert_simple_paragraph_multi_breaks(self):
        res = slate_to_html(
            [
                {
                    "children": [
                        {"text": "Hello \nworld \n in a multi line \nparagraph"}
                    ],
                    "type": "p",
                }
            ]
        )
        self.assertEqual(
            res, "<p>Hello <br>world <br> in a multi line <br>paragraph</p>"
        )

    def test_convert_text_and_a_tag(self):
        res = slate_to_html(
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
            ]
        )

        self.assertEqual(
            res,
            "<p>Hello <strong>world</strong> mixed <i>content</i>.</p>",
        )

    def test_convert_case_simple_p(self):
        slate = read_json("1.json")
        html = slate_to_html(slate)
        res = read_data("1.html")

        self.assertTrue(is_html_equal(res, html))
