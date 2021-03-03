# -*- coding: utf-8 -*-
import json
import unittest

import transaction
from plone.app.testing import TEST_USER_ID, setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer, iterSchemata
from plone.restapi.interfaces import IDeserializeFromJson, IFieldSerializer
from plone.uuid.interfaces import IUUID
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter, queryUtility

from eea.volto.slate.tests.base import FUNCTIONAL_TESTING


class TestBlockTransformers(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

        self.doc = createContentInContainer(
            self.portal, u"Document", id=u"doc", title=u"A document"
        )
        transaction.commit()

    def deserialize(self, blocks=None, validate_all=False, context=None):
        blocks = blocks or ""
        context = context or self.portal.doc
        self.request["BODY"] = json.dumps({"blocks": blocks})
        deserializer = getMultiAdapter((context, self.request), IDeserializeFromJson)

        return deserializer(validate_all=validate_all)

    def serialize(self, context, blocks):
        fieldname = "blocks"
        for schema in iterSchemata(context):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter((context, field), IDataManager)
        dm.set(blocks)
        serializer = getMultiAdapter((field, context, self.request), IFieldSerializer)
        return serializer()

    def test_internal_link_deserializer(self):
        blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                    {
                                        "children": [{"text": "slate link"}],
                                        "data": {
                                            "link": {
                                                "internal": {
                                                    "internal_link": [
                                                        {
                                                            "@id": "/front-page",
                                                            "title": "Welcome to Plone",
                                                        }
                                                    ]
                                                }
                                            }
                                        },
                                        "type": "a",
                                    },
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }
        res = self.deserialize(blocks=blocks)
        value = res.blocks["2caef9e6-93ff-4edf-896f-8c16654a9923"]["value"]
        link = value[0]["children"][1]["children"][1]
        resolve_link = link["data"]["link"]["internal"]["internal_link"][0]["@id"]
        self.assertTrue(resolve_link.startswith("../resolveuid/"))

    def test_internal_link_serializer(self):
        doc_uid = IUUID(self.portal["front-page"])
        resolve_uid_link = {
            "@id": "../resolveuid/{}".format(doc_uid),
            "title": "Welcome to Plone",
        }
        blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                    {
                                        "children": [{"text": "slate link"}],
                                        "data": {
                                            "link": {
                                                "internal": {
                                                    "internal_link": [resolve_uid_link]
                                                }
                                            }
                                        },
                                        "type": "a",
                                    },
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }

        res = self.serialize(
            context=self.portal.doc,
            blocks=blocks,
        )

        value = res["2caef9e6-93ff-4edf-896f-8c16654a9923"]["value"]
        link = value[0]["children"][1]["children"][1]
        resolve_link = link["data"]["link"]["internal"]["internal_link"][0]["@id"]

        self.assertTrue(resolve_link == "/front-page")
