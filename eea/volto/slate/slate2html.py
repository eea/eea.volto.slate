from lxml.html import builder as E
from lxml.html import tostring

from .config import DEFAULT_BLOCK_TYPE, KNOWN_BLOCK_TYPES


def join(element, children):
    res = []
    for bit in children:
        res.append(bit)
        res.append(element)
    return res[:-1]  # remove the last break


class Slate2HTML(object):
    def serialize(self, element):
        if "text" in element:
            if "\n" not in element["text"]:
                return [element["text"]]

            return join(E.BR, element["text"].split("\n"))

        tagname = element["type"]

        if element.get("data-slate-data"):
            handler = self.handle_slate_data_element
        else:
            handler = getattr(self, "handle_tag_{}".format(tagname), None)
            if not handler and tagname in KNOWN_BLOCK_TYPES:
                handler = self.handle_block

        res = handler(element)
        if isinstance(res, list):
            return res
        return [res]

    def handle_tag_a(self, element):
        internal_link = (
            element.get("data", {})
            .get("link", {})
            .get("internal", {})
            .get("internal_link", [])
        )

        attributes = {}

        if internal_link:
            attributes["href"] = internal_link[0]["@id"]

        el = getattr(E, element["type"].upper())

        children = []
        for child in element["children"]:
            children += self.serialize(child)

        return el(*children, **attributes)

    def handle_slate_data_element(self, element):
        pass

    def handle_block(self, element):
        el = getattr(E, element["type"].upper())

        children = []
        for child in element["children"]:
            children += self.serialize(child)

        return el(*children)

    def to_html(self, value):
        children = []
        for child in value:
            children += self.serialize(child)

        # TODO: handle unicode properly
        return u"".join(tostring(f).decode("utf-8") for f in children)


def slate_to_html(value):
    convert = Slate2HTML()
    return convert.to_html(value)
