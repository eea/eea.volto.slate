""" Transformers to store the slate HTML value serialized as HTML
"""


from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import (IBlockFieldDeserializationTransformer,
                                      IBlockFieldSerializationTransformer)
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter, getUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

from .interfaces import ISlateConverter


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateHTMLBlockSerializer(object):
    """ Serialize the content of an HTML block as Slate value """

    field = "value"
    order = 1000
    block_type = "slate"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):

        value = block[self.field]
        return getUtility(ISlateConverter).slate2html(value)


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateBlockSerializerRoot(SlateHTMLBlockSerializer):
    """ Serializer for site root """


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateHTMLBlockDeserializer(object):
    """ Store a slate value as an HTML """

    field = "value"
    order = 1000
    block_type = "slate"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):

        value = block[self.field]
        return getUtility(ISlateConverter).html2slate(value)


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateHTMLBlockDeserializerRoot(SlateHTMLBlockDeserializer):
    """ Deserializer for site root """
