# -*- coding: utf-8 -*-

import json
import os
import unittest

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


class TestConvertSlate2HTML(unittest.TestCase):
    maxDiff = None

    def test_convert_simple_string(self):
        res = slate_to_html([{"children": [{"text": "Hello world"}], "type": "p"}])
        self.assertEqual(res, "<p>Hello world</p>")
