# -*- coding: utf-8 -*-

import json
import os
import re
import unittest

import six
from bs4 import BeautifulSoup
from lxml.html import fragments_fromstring, tostring
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


def clean_whitespace(html):
    html = html.replace("\n", " ")
    html = re.sub(r"\s+", " ", html)
    html = html.replace("> <", "><")
    return html


#
#
# def is_html_equal(proba_a, proba_b, debug=False):
#     a = clean_whitespace(proba_a)
#     b = clean_whitespace(proba_b)
#     if debug:
#         import pdb
#
#         pdb.set_trace()
#     return a == b


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
        self.assertEqual(
            html,
            "<p>Since version 2.0, lxml comes with a dedicated Python package "
            "for dealing with HTML: lxml.html. <br>It is based on lxml's HTML parser, "
            "but provides a special Element API for HTML elements, as well as a number "
            "of utilities for common HTML processing tasks.</p>",
        )

    def test_convert_case_multiple_p(self):
        slate = read_json("2.json")
        html = slate_to_html(slate)
        self.assertEqual(
            html,
            "<p>Since version 2.0, lxml comes with a dedicated Python package "
            "for dealing with HTML: lxml.html. <br>It is based on lxml's HTML parser, "
            "but provides a special Element API for HTML elements, as well as a number "
            "of utilities for common HTML processing tasks.</p><p>The normal HTML "
            "parser is capable of handling broken HTML, but for pages that are far "
            "enough from HTML to call them 'tag soup', it may still fail to parse the "
            "page in a useful way. A way to deal with this is ElementSoup, which "
            "deploys the well-known BeautifulSoup parser to build an lxml HTML tree."
            "</p><p>However, note that the most common problem with web pages is the "
            "lack of (or the existence of incorrect) encoding declarations. It is "
            "therefore often sufficient to only use the encoding detection of "
            "BeautifulSoup, called UnicodeDammit, and to leave the rest to lxml's own "
            "HTML parser, which is several times faster.</p>",
        )

    def test_one_list_item(self):
        slate = [
            {
                "children": [
                    {"text": ""},
                    {
                        "children": [
                            {"text": "Brown bear ("},
                            {"children": [{"text": "ursus arctos"}], "type": "em"},
                            {"text": ") in Italy"},
                        ],
                        "data": {
                            "link": {
                                "internal": {
                                    "internal_link": [
                                        {"@id": "/case-study-hub/CS-brown-bears-Italy"}
                                    ]
                                }
                            }
                        },
                        "type": "a",
                    },
                    {"text": ""},
                ],
                "type": "li",
            }
        ]
        text = clean_whitespace(
            """<li><a
        href="/case-study-hub/CS-brown-bears-Italy">Brown bear (<em>ursus arctos</em>) in Italy</a>
        </li>"""
        )
        res = slate_to_html(slate)

        self.assertEqual(
            res,
            text,
        )
