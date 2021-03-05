from lxml.html import builder as E
from lxml.html import tostring

from .config import DEFAULT_BLOCK_TYPE, KNOWN_BLOCK_TYPES


class Slate2HTML(object):
    def serialize(self, element):
        if "text" in element:
            return element["text"]

        tagname = element["type"]

        if element.get("data-slate-data"):
            handler = self.handle_slate_data_element
        else:
            handler = getattr(self, "handle_tag_{}".format(tagname), None)
            if not handler and tagname in KNOWN_BLOCK_TYPES:
                handler = self.handle_block

        return handler(element)

    def handle_slate_data_element(self, element):
        pass

    def handle_block(self, element):
        el = getattr(E, element["type"].upper())
        return el(*[self.serialize(child) for child in element["children"]])

    def to_html(self, value):
        fragments = [self.serialize(child) for child in value]

        # TODO: handle unicode properly
        return u"".join(tostring(f).decode("utf-8") for f in fragments)


def slate_to_html(value):
    convert = Slate2HTML()
    return convert.to_html(value)
