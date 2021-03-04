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


class HTML2SlateParser(HTMLParser):
    def __init__(self, log=False):
        super(HTML2SlateParser, self).__init__()
        self.log = log
        self.result = []
        self.stack = deque([])  # used to determine the current wrapping element
        self.level = 0  # used to determine if an element is top level or not

    def slate_element_builder(self, tag, attrs):
        """A slate element builder"""

        element = {"type": tag, "children": []}

        if self.stack:
            current = self.stack[-1]
            current["children"].append(element)

        print("---Placing element in stack", tag)
        self.stack.append(element)
        return element, True

    def handle_tag_a(self, tag, attrs):
        attrs = dict(attrs)
        link = attrs.get("href", "")

        element, is_block_element = self.slate_element_builder(tag, attrs)
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

        return element, True

    def handle_tag_br(self, tag, attrs):
        self.add_text("\n")
        return None, False

    def handle_tag_b(self, tag, attrs):
        # <b> needs special handling
        # TODO: implement me

        return self.slate_element_builder(tag, attrs)

    def handle_tag_span(self, tag, attrs):
        # TODO: implement me
        return None, False

    def handle_some_block(self, tag, attrs):
        if tag not in KNOWN_BLOCK_TYPES:
            tag = DEFAULT_BLOCK_TYPE

        return self.slate_element_builder(tag, attrs)

    def handle_starttag(self, tag, attrs):
        if self.log:
            print("---Encountered a start tag:", tag, self.level)

        attributes = dict(attrs)

        if attributes.get("data-slate-data"):
            handler = self.handle_slate_data
        else:
            handler = getattr(self, "handle_tag_{}".format(tag), self.handle_some_block)

        element, is_block_element = handler(tag, attrs)

        if element is not None:
            if self.level == 0:
                self.result.append(element)
            if is_block_element:
                self.level += 1

    def handle_endtag(self, tag):
        if self.log:
            print("---Encountered an end tag :", tag, self.level)
        self.level -= 1
        self.stack.pop()

    def handle_slate_data(self, tag, attrs):
        if self.log:
            print("---Handling Slate data tag:", tag, self.level)

        attributes = dict(attrs)

        element = json.loads(attributes["data-slate-data"])
        if "children" not in element:
            element["children"] = []

        if self.stack:
            current = self.stack[-1]
            current["children"].append(element)

        print("---Placing slate data element in stack", tag)
        self.stack.append(element)

        return element, True

    def handle_data(self, data):
        """ Generic text handler, native HTML parser API """
        if is_whitespace(data):
            return

        text = clean_whitespace(data)
        self.add_text(text)
        if self.log:
            print("---Encountered some data  :", text)

    def add_text(self, text):
        current = self.stack[-1]
        if current["children"] and "text" in current["children"][-1]:
            current["children"][-1]["text"] += text
        else:
            current["children"].append({"text": text})

    def end(self):
        q = deque(self.result)

        while len(q):
            child = q.pop()
            children = child.get("children", None)
            if children is not None:
                q.extend(child["children"])
                self.pad_with_space(child["children"])

        return self.result

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

    def handle_tag_body(self):
        # TODO: implement me
        pass

    def handle_tag_code(self):
        # TODO: implement me
        pass


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


def html_fragment_to_slate(text, log=False):
    # element = fragment_fromstring(text)
    parser = HTML2SlateParser(log)
    parser.feed(text)

    return parser.end()


# def html_page_to_slate(text):
#     # element = document_fromstring(text)
#     dom = parseString(text)
#     return deserialize(element.find("body"))

# if (el.getAttribute('data-slate-data')) {
#   return typeDeserialize(editor, el);
# }
#
# const { nodeName } = el;
#
# if (htmlTagsToSlate[nodeName]) {
#   return htmlTagsToSlate[nodeName](editor, el);
# }
#
# return deserializeChildren(el, editor); // fallback deserializer
