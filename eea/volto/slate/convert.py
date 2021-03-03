""" Convert HTML to slate, slate to HTML

A port of volto-slate' deserialize.js module
"""

import re
from collections import deque
from html.parser import HTMLParser

import six

# from defusedxml.minidom import parseString
# from lxml.html import document_fromstring, fragment_fromstring

KNOWN_BLOCK_TYPES = [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "blockquote",
    "pre",
    "ol",
    "ul",
    "li",
    "strong",
    "del",
    "em",
    "i",
    "s",
    "sub",
    "sup",
    "u",
    "a",
]

DEFAULT_BLOCK_TYPE = "p"


class HTML2SlateParser(HTMLParser):
    def __init__(self):
        super(HTML2SlateParser, self).__init__()
        self.result = []
        self.stack = deque([])
        self.level = 0

    def _element(self, tag, attrs):
        element = {"type": tag, "children": []}

        if self.stack:
            current = self.stack[-1]
            current["children"].append(element)

        self.stack.append(element)
        return element

    def handle_a(self, tag, attrs):
        attrs = dict(attrs)
        link = attrs.get("href", "")

        element = self._element(tag, attrs)
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

    def handle_br(self, tag, attrs):
        self.add_text("\n")
        self.level -= 1

    def handle_b(self, tag, attrs):
        # <b> needs special handling

        return self._element(tag, attrs)

    def handle_code(self):
        pass

    def handle_span(self, tag, attrs):
        # do nothing for now
        pass

    def handle_generic_block(self, tag, attrs):
        if tag not in KNOWN_BLOCK_TYPES:
            tag = DEFAULT_BLOCK_TYPE

        return self._element(tag, attrs)

    def handle_starttag(self, tag, attrs):
        # print("---Encountered a start tag:", tag, self.level)
        handler = getattr(self, "handle_{}".format(tag), self.handle_generic_block)
        element = handler(tag, attrs)

        if self.level == 0 and element is not None:
            self.result.append(element)
        self.level += 1

    def handle_endtag(self, tag):
        self.level -= 1
        self.stack.pop()
        # print("---Encountered an end tag :", tag)

    def handle_data(self, data):
        if is_whitespace(data):
            return

        text = clean_whitespace(data)
        self.add_text(text)
        # print("---Encountered some data  :", text)

    def add_text(self, text):
        current = self.stack[-1]
        if current["children"] and "text" in current["children"][-1]:
            current["children"][-1]["text"] += text
        else:
            current["children"].append({"text": text})

    def end(self):
        # pad children with empty spaces. Slate requires the children array start and
        # end with "texts", even if empty, this allows Slate to place a cursor
        q = deque(self.result)

        while len(q):
            child = q.pop()
            children = child.get("children", None)
            if children is not None:
                q.extend(child["children"])
                self.pad_with_space(child["children"])

        return self.result

    def pad_with_space(self, children):
        if len(children) == 0:
            children.append({"text": ""})
            return

        if not children[0].get("text"):
            children.insert(0, {"text": ""})
        if not children[-1].get("text"):
            children.append({"text": ""})


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


def html_fragment_to_slate(text):
    # element = fragment_fromstring(text)
    parser = HTML2SlateParser()
    parser.feed(text)

    return parser.end()


# def html_page_to_slate(text):
#     # element = document_fromstring(text)
#     dom = parseString(text)
#     return deserialize(element.find("body"))

# if (el.nodeType == COMMENT) {
#   return null
# } else if (el.nodeType == TEXT_NODE) {
#   // instead of == '\n' we use isWhitespace for when deserializing tables
#   // from Calc and other similar cases
#   if (isWhitespace(el.textContent)) {
#     // if it's empty text between 2 tags, it should be ignored
#     return null
#   }
#   return el.textContent
#     .replace(/\n$/g, ' ')
#     .replace(/\n/g, ' ')
#     .replace(/\t/g, '');
# } else if (el.nodeType !== ELEMENT_NODE) {
#   return null;
# } else if (el.nodeName === 'BR') {
#   // TODO: handle <br> ?
#   return null;
# }
#
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
