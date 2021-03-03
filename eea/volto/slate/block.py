import os

from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import path2uid
from plone.restapi.interfaces import (IBlockFieldDeserializationTransformer,
                                      IBlockFieldSerializationTransformer)
from plone.restapi.serializer.blocks import uid_to_url
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

from .utils import iterate_children


class SlateBlockTransformer(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        for child in iterate_children(block["value"] or []):
            node_type = child.get("type")
            if node_type:
                handler = getattr(self, "handle_{}".format(node_type), None)
                if handler:
                    handler(child)

        return block


class SlateBlockSerializerBase(SlateBlockTransformer):
    order = 100
    block_type = "slate"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def _uid_to_url(self, context, path):
        portal = api.portal.get()
        return uid_to_url(path).replace(portal.absolute_url(), "")

    def handle_a(self, child):
        transform_links(self.context, child, transformer=self._uid_to_url)


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateBlockSerializer(SlateBlockSerializerBase):
    """ Serializer for content-types with IBlocks behavior """


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateBlockSerializerRoot(SlateBlockSerializerBase):
    """ Serializer for site root """


def transform_links(context, value, transformer):
    # Convert absolute links to resolveuid
    #   http://localhost:55001/plone/link-target
    #   ->
    #   ../resolveuid/023c61b44e194652804d05a15dc126f4
    data = value.get("data", {})
    if data.get("link", {}).get("internal", {}).get("internal_link"):
        internal_link = data["link"]["internal"]["internal_link"]
        for link in internal_link:
            link["@id"] = transformer(context, link["@id"])


class SlateBlockDeserializerBase(SlateBlockTransformer):
    order = 100
    block_type = "slate"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def handle_a(self, child):
        transform_links(self.context, child, transformer=path2uid)


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateBlockDeserializer(SlateBlockDeserializerBase):
    """ Deserializer for content-types that implements IBlocks behavior """


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateBlockDeserializerRoot(SlateBlockDeserializerBase):
    """ Deserializer for site root """