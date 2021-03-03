# -*- coding: utf-8 -*-
import os
import unittest

from pkg_resources import resource_filename

from eea.volto.slate.convert import html_fragment_to_slate


def read_data(filename):
    fpath = resource_filename("eea.volto.slate", os.path.join("tests/data", filename))
    return open(fpath).read()


class TestConvert(unittest.TestCase):
    maxDiff = None

    def test_convert_slate_output_markup(self):
        text = read_data("5.txt")
        res = html_fragment_to_slate(text)

        self.assertEqual(
            res,
            [
                {
                    "children": [
                        {"text": "Paragraph "},
                        {
                            "children": [
                                {"text": ""},
                                {
                                    "children": [{"text": "with bold and slate "}],
                                    "data": {
                                        "link": {
                                            "internal": {
                                                "internal_link": [
                                                    {
                                                        "@id": "/front-page",
                                                    }
                                                ]
                                            }
                                        }
                                    },
                                    "type": "a",
                                },
                                {"text": ""},
                            ],
                            "type": "strong",
                        },
                        {"text": "link"},
                    ],
                    "type": "p",
                }
            ],
        )

    def test_convert_case_simple_p(self):
        text = read_data("1.txt")
        res = html_fragment_to_slate(text)
        self.assertEqual(
            res,
            [
                {
                    "children": [
                        {
                            "text": "Since version 2.0, lxml comes with a dedicated Python "
                            "package for dealing with HTML: lxml.html. \n"
                            "It is based on lxml's HTML parser, but provides a "
                            "special Element API for HTML elements, as well as a "
                            "number of utilities for common HTML processing "
                            "tasks."
                        }
                    ],
                    "type": "p",
                }
            ],
        )

    def test_convert_case_multiple_p(self):
        text = read_data("2.txt")
        res = html_fragment_to_slate(text)

        self.assertEqual(
            res,
            [
                {
                    "children": [
                        {
                            "text": "Since version 2.0, lxml comes with a dedicated Python "
                            "package for dealing with HTML: lxml.html. \n"
                            "It is based on lxml's HTML parser, but provides a "
                            "special Element API for HTML elements, as well as a "
                            "number of utilities for common HTML processing "
                            "tasks."
                        }
                    ],
                    "type": "p",
                },
                {
                    "children": [
                        {
                            "text": "The normal HTML parser is capable of handling broken "
                            "HTML, but for pages that are far enough from HTML to "
                            "call them 'tag soup', it may still fail to parse the "
                            "page in a useful way. A way to deal with this is "
                            "ElementSoup, which deploys the well-known "
                            "BeautifulSoup parser to build an lxml HTML tree."
                        }
                    ],
                    "type": "p",
                },
                {
                    "children": [
                        {
                            "text": "However, note that the most common problem with web "
                            "pages is the lack of (or the existence of incorrect) "
                            "encoding declarations. It is therefore often "
                            "sufficient to only use the encoding detection of "
                            "BeautifulSoup, called UnicodeDammit, and to leave the "
                            "rest to lxml's own HTML parser, which is several "
                            "times faster."
                        }
                    ],
                    "type": "p",
                },
            ],
        )
