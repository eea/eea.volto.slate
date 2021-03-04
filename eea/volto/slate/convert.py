""" Convert HTML to slate, slate to HTML

A port of volto-slate' deserialize.js module
"""

import json
import re
from collections import deque
from html.parser import HTMLParser

import six

KNOWN_BLOCK_TYPES = [
    "a",
    "blockquote",
    "del",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "i",
    "li",
    "ol",
    "p",
    "pre",
    "s",
    "strong",
    "sub",
    "sup",
    "u",
    "ul",
]

DEFAULT_BLOCK_TYPE = "p"

from lxml.html import html5parser, tostring


def is_whitespace(c):
    if not isinstance(c, six.string_types):
        return False

    return len(re.sub(r"\s|\t|\n", "", c)) == 0


def clean_whitespace(c):
    funcs = [
        lambda t: re.sub(r"\n$", " ", t),
        lambda t: re.sub(r"\n", " ", t),
        lambda t: re.sub(r"\t", "", t),
    ]
    for f in funcs:
        c = f(c)

    return c


def tag_name(el):
    return el.tag.replace("{%s}" % el.nsmap["html"], "")


def deserialize(el):
    tag = tag_name(el)
    print(tag)
    pass


def is_inline(el):
    # if isinstance(el, six.string_types):
    #     return True
    if isinstance(el, dict) and "text" in el:
        return True

    return False


class Parser(object):
    """A parser for HTML to slate conversion"""

    def deserialize_children(self, node):
        nodes = [node.text]
        for child in node.iterchildren():
            nodes.append(child)
            nodes.append(child.tail)
        # nodes.append(node.tail)

        nodes = [self.deserialize(n) for n in nodes if n is not None]
        return nodes

    def handle_tag_br(self, node):
        return {"text": "\n"}

    def handle_block(self, node):
        tag = tag_name(node)
        # slate_data = node

        return {"type": tag, "children": self.deserialize_children(node)}

    def deserialize(self, node):
        if isinstance(node, six.string_types):
            if is_whitespace(node):
                return None
            return {"text": clean_whitespace(node)}

        tagname = tag_name(node)
        if tagname in KNOWN_BLOCK_TYPES:
            handler = self.handle_block
        else:
            handler = getattr(self, "handle_tag_{}".format(tagname), None)
        if handler:
            element = handler(node)
            # if node.tail:
            #     return [element, self.deserialize(node.tail)]
            return element

        return self.deserialize_children(node)

    def to_slate(self, text):
        fragments = html5parser.fragments_fromstring(text)
        nodes = []
        for f in fragments:
            if isinstance(f, six.string_types):
                nodes.append(f)
            else:
                nodes.append(f)
                if f.tail:
                    nodes.append(f.tail)

        value = list(filter(None, [self.deserialize(f) for f in nodes]))
        return self.normalize(value)

    def merge_adjacent_text_nodes(self, children):
        ranges = []
        for i, v in enumerate(children):
            if "text" in v:
                if ranges and ranges[-1][1] == i - 1:
                    ranges[-1][1] = i
                else:
                    ranges.append([i, i])
        text_positions = []
        range_dict = {}
        for start, end in ranges:
            text_positions.extend(list(range(start, end + 1)))
            range_dict[start] = end

        result = []
        for i, v in enumerate(children):
            if i not in text_positions:
                result.append(v)
            if i in range_dict:
                result.append(
                    {
                        "text": u"".join(
                            [c["text"] for c in children[i : range_dict[i] + 1]]
                        )
                    }
                )
        return result

    def normalize(self, value):
        # all top-level elements in the value should be block tags
        if value and is_inline(value[0]):
            value = [{"type": "p", "children": value}]

        q = deque(value)

        while len(q):
            child = q.pop()
            children = child.get("children", None)
            if children is not None:
                # merge adjancent text nodes
                child["children"] = self.merge_adjacent_text_nodes(child["children"])

                q.extend(child["children"])
                self.pad_with_space(child["children"])

        return value

    def pad_with_space(self, children):
        # pad children with empty spaces. Slate requires the children array start and
        # end with "texts", even if empty, this allows Slate to place a cursor
        if len(children) == 0:
            children.append({"text": ""})
            return

        if not children[0].get("text"):
            children.insert(0, {"text": ""})
        if not children[-1].get("text"):
            children.append({"text": ""})


def text_to_slate(text):
    parser = Parser()
    return parser.to_slate(text)
