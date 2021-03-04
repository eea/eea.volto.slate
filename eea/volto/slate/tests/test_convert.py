# -*- coding: utf-8 -*-
import json
import os
import unittest

from pkg_resources import resource_filename

from eea.volto.slate.convert import html_fragment_to_slate


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

    # def test_convert_case_simple_p(self):
    #     text = read_data("1.html")
    #     res = html_fragment_to_slate(text)
    #
    #     self.assertEqual(
    #         res,
    #         read_json("1.json"),
    #     )
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

    def test_self_closed_element(self):
        text = "<span />"
        res = html_fragment_to_slate(text, log=True)
        import pdb

        pdb.set_trace()
        pass
