import os

from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import path2uid
from plone.restapi.interfaces import (IBlockFieldDeserializationTransformer,
                                      IBlockFieldSerializationTransformer,
                                      IFieldSerializer)
from plone.restapi.serializer.blocks import uid_to_url
from Products.CMFPlone.interfaces import IPloneSiteRoot


class SlateBlockSerializerBase(object):
    order = 100
    block_type = "slate"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        # Resolve UID links:
        #   ../resolveuid/023c61b44e194652804d05a15dc126f4
        #   ->
        #   http://localhost:55001/plone/link-target

        # import pdb
        # pdb.set_trace()

        entity_map = value.get("text", {}).get("entityMap", {})
        for entity in entity_map.values():
            if entity.get("type") == "LINK":
                url = entity.get("data", {}).get("url", "")
                entity["data"]["url"] = uid_to_url(url)
        return value


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateBlockSerializer(SlateBlockSerializerBase):
    """ Serializer for content-types with IBlocks behavior """


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateBlockSerializerRoot(SlateBlockSerializerBase):
    """ Serializer for site root """


class SlateBlockDeserializerBase(object):
    order = 100
    block_type = "slate"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        # Convert absolute links to resolveuid
        #   http://localhost:55001/plone/link-target
        #   ->
        #   ../resolveuid/023c61b44e194652804d05a15dc126f4
        entity_map = block.get("text", {}).get("entityMap", {})
        for entity in entity_map.values():
            if entity.get("type") == "LINK":
                href = entity.get("data", {}).get("url", "")
                entity["data"]["url"] = path2uid(context=self.context, link=href)
        return block


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateBlockDeserializer(SlateBlockDeserializerBase):
    """ Deserializer for content-types that implements IBlocks behavior """


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateBlockDeserializerRoot(SlateBlockDeserializerBase):
    """ Deserializer for site root """
