from .html2slate import text_to_slate
from .slate2html import slate_to_html


class SlateConverter(object):
    def html2slate(self, text):
        return text_to_slate(text)

    def slate2html(self, value):
        return slate_to_html(value)
