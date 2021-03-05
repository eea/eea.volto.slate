from zope.interface import implementer

from .html2slate import text_to_slate
from .interfaces import ISlateConverter
from .slate2html import slate_to_html


@implementer(ISlateConverter)
class SlateConverter(object):
    """"""

    def html2slate(self, text):
        return text_to_slate(text)

    def slate2html(self, value):
        return slate_to_html(value)
