""" Convert HTML to slate, slate to HTML

A port of volto-slate' deserialize.js module
"""

import json
import re
from collections import deque

import six
from lxml.html import html5parser

from .config import DEFAULT_BLOCK_TYPE, KNOWN_BLOCK_TYPES


def is_whitespace(text):
    " Returns true if the text is only whitespace characters"

    if not isinstance(text, six.string_types):
        return False

    return len(re.sub(r"\s|\t|\n", "", text)) == 0


def clean_whitespace(c):
    """Cleans up non-significant whitespace text.

    - remove tabs, they're not usable in html
    - replace new lines with a whitespace (this is how browsers would render)
    """

    funcs = [
        lambda t: re.sub(r"\n$", " ", t),
        lambda t: re.sub(r"\n", " ", t),
        lambda t: re.sub(r"\t", "", t),
    ]
    for f in funcs:
        c = f(c)

    # TODO: collapse multiple \n to a single space?
    return c


def tag_name(el):
    return el.tag.replace("{%s}" % el.nsmap["html"], "")


def is_inline(el):
    """Returns true if the element is a text node

    Some richtext editors provide support for "inline elements", which is to say they
    mark some portions of text and add flags for that, like "bold:true,italic:true",
    etc.

    From experience, this is a bad way to go when the output is intended to be HTML. In
    HTML DOM there is only markup and that markup is semantic. So keeping it purely
    markup greately simplifies the number of cases that need to be covered.
    """

    if isinstance(el, dict) and "text" in el:
        return True

    return False


def merge_adjacent_text_nodes(children):
    " Given a list of Slate elements, it combines adjacent texts nodes"

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
                {"text": u"".join([c["text"] for c in children[i : range_dict[i] + 1]])}
            )
    return result


class HTML2Slate(object):
    """A parser for HTML to slate conversion

    If you need to handle some custom slate markup, inherit and extend
    """

    def to_slate(self, text):
        " Convert text to a slate value. A slate value is a list of elements "

        fragments = html5parser.fragments_fromstring(text)
        nodes = []
        for f in fragments:
            nodes += self.deserialize(f)

        return self.normalize(nodes)

    def deserialize_children(self, node):
        nodes = [node.text]
        for child in node.iterchildren():
            nodes.append(child)
            if is_whitespace(child.tail):
                nodes.append(child.tail)

        res = []
        for x in nodes:
            if x is not None:
                res += self.deserialize(x)

        return res

    def handle_tag_a(self, node):
        attrs = node.attrib
        link = attrs.get("href", "")

        element = {"type": "a", "children": self.deserialize_children(node)}
        if link:
            if link.startswith("http") or link.startswith("//"):
                # TODO: implement external link
                pass
            else:
                element["data"] = {
                    "link": {
                        "internal": {
                            "internal_link": [
                                {
                                    "@id": link,
                                }
                            ]
                        }
                    }
                }

        return element

    def handle_tag_br(self, node):
        return {"text": "\n"}

    def handle_block(self, node):
        return {"type": tag_name(node), "children": self.deserialize_children(node)}

    # def handle_tag_b(self, node):
    #     # TODO: implement <b> special cases
    #     return self.handle_block(node)

    def handle_slate_data_element(self, node):
        element = json.loads(node.attrib["data-slate-data"])
        element["children"] = self.deserialize_children(node)
        return element

    def deserialize(self, node):
        " Deserialize a node into a _list_ of slate elements"

        if node is None:
            return []

        if isinstance(node, six.string_types):
            if is_whitespace(node):
                return []
            return [{"text": clean_whitespace(node)}]

        tagname = tag_name(node)

        handler = None

        if node.attrib.get("data-slate-data"):
            handler = self.handle_slate_data_element
        else:
            handler = getattr(self, "handle_tag_{}".format(tagname), None)
            if not handler and tagname in KNOWN_BLOCK_TYPES:
                handler = self.handle_block

        if handler:
            element = handler(node)
            if node.tail and clean_whitespace(node.tail):
                return [element] + self.deserialize(node.tail)
            return [element]

        # fallback, "skips" the node
        return self.handle_fallback(node)

    def handle_fallback(self, node):
        " Unknown tags (for example span) are handled as pipe-through "

        nodes = self.deserialize_children(node) + self.deserialize(node.tail)
        return nodes

    def normalize(self, value):
        " Normalize value to match Slate constraints "

        assert isinstance(value, list)
        value = [v for v in value if v is not None]

        # all top-level elements in the value need to be block tags
        if value and [x for x in value if is_inline(value[0])]:
            value = [{"type": DEFAULT_BLOCK_TYPE, "children": value}]

        stack = deque(value)

        while len(stack):
            child = stack.pop()
            children = child.get("children", None)
            if children is not None:
                children = [c for c in children if c]
                # merge adjacent text nodes
                child["children"] = merge_adjacent_text_nodes(children)
                stack.extend(child["children"])

                # self._pad_with_space(child["children"])

        return value

    def _pad_with_space(children):
        """Mutate the children array in-place. It pads them with 'empty spaces'.

        Extract from Slate docs:
        https://docs.slatejs.org/concepts/02-nodes#blocks-vs-inlines

        You can define which nodes are treated as inline nodes by overriding the
        editor.isInline function. (By default it always returns false.) Note that inline
        nodes cannot be the first or last child of a parent block, nor can it be next to
        another inline node in the children array. Slate will automatically space these
        with { text: '' } children by default with normalizeNode.

        Elements can either contain block elements or inline elements intermingled with
        text nodes as children. But elements cannot contain some children that are
        blocks and some that are inlines.
        """

        # TODO: needs reimplementation according to above info
        if len(children) == 0:
            children.append({"text": ""})
            return

        if not children[0].get("text"):
            children.insert(0, {"text": ""})
        if not children[-1].get("text"):
            children.append({"text": ""})


def text_to_slate(text):
    return HTML2Slate().to_slate(text)
