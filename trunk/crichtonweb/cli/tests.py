# Crichton, Admirable Source Configuration Management
# Copyright 2012 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
import unittest

from django.test import TestCase
from django.test.client import Client

from django.db.models import Model
from django.db.models.base import ModelBase
from django.core.management.base import CommandError

from crichtoncli.apihelpers import makeHttps, get_exposed_models, model_from_datatype, get_datatypes, print_datatype_help

class crichtonApiHelpersTestCase(TestCase):
    def test_makeHttps(self):
        h = makeHttps("https://www.live.domain.local/", None, None, None)
        self.assertTrue(h is not None)
        self.assertTrue(hasattr(h, "request"))
        self.assertTrue(callable(h.request))
    
    def test_get_exposed_models(self):
        models = get_exposed_models()
        self.assertTrue(models.__iter__() is not None)
        has_a_model = False
        for model_module in models:
            self.assertTrue(model_module.__dict__ is not None)
    
    def test_model_from_datatype(self):
        model = model_from_datatype("Person")
        self.assertTrue(model is not None)
        self.assertRaises(CommandError, model_from_datatype, "SomeNonExistentModelName")
    
    def test_get_datatypes(self):
        types = get_datatypes()
        for t in types:
            m = model_from_datatype(t)
            self.assertTrue(m is not None)
    
    def test_print_datatype_help(self):
        print_datatype_help()

from crichtoncli.apihelpers import HttpError
import crichtoncli.apihelpers
import crichtoncli.commands.list
import crichtoncli.commands.put
from crichtoncli.commands.get import list_one_by_datatype
from crichtoncli.commands.list import list_all_by_datatype
from crichtoncli.commands.put import put_one_by_datatype


class MockErrorResponse(object):
    status = 500
    
    def get(self, header_name, default_value=None):
        if header_name.lower() == "content-type":
            return "application/xml"
        else:
            return default_value

class MockHttpClient(object):
    def __init__(self):
        self.http_requests = []

    def request(self, *args, **kwargs):
        self.http_requests.append((args, kwargs))
        return MockErrorResponse(), "Broken"

class MockHttpTestCase(TestCase):
    def setUp(self):
        # override the http client with ourselves to fake http requests
        self.orig_h = crichtoncli.apihelpers.h
        self.h = MockHttpClient()
        crichtoncli.apihelpers.h = self.h
        crichtoncli.commands.list.h = self.h
        crichtoncli.commands.put.h = self.h
    
    def tearDown(self):
        crichtoncli.apihelpers.h = self.orig_h
        crichtoncli.commands.list.h = self.orig_h
        crichtoncli.commands.put.h = self.orig_h

class GetCommandTestCase(MockHttpTestCase):
    def test_get_person(self):
        self.assertRaises(HttpError, list_one_by_datatype, "Person", "joe.tester")
        self.assertEqual(self.h.http_requests[0][0][0], "http://localhost:8000/api/person/one/joe.tester.xml")
        self.assertEqual(self.h.http_requests[0][0][1], "GET")

class ListCommandTestCase(MockHttpTestCase):
    def test_list_people(self):
        self.assertRaises(HttpError, list_all_by_datatype, "Person")
        self.assertEqual(self.h.http_requests[0][0][0], "http://localhost:8000/api/person/list/all.xml")
        self.assertEqual(self.h.http_requests[0][0][1], "GET")

class PutCommandTestCase(MockHttpTestCase):
    def test_put_person(self):
        self.assertRaises(HttpError, put_one_by_datatype, "Person", "joe.tester", """<?xml version="1.0" encoding="utf-8"?>
<core:person
        xmlns="urn:x-ns:hotjazz:prodmgmt"
        xmlns:hotjazz="urn:x-ns:hotjazz"
        hotjazz:type="model"
        xmlns:core="urn:x-ns:hotjazz:prodmgmt">
    <core:username hotjazz:type="CharField">joe.tester</core:username>
    <core:first_name hotjazz:type="CharField">Joe</core:first_name>
    <core:last_name hotjazz:type="CharField">Tester</core:last_name>
    <core:email hotjazz:type="CharField">joe.tester@example.com</core:email>
    <core:distinguished_name hotjazz:type="CharField"></core:distinguished_name>
</core:person>
""")
        self.assertEqual(self.h.http_requests[0][0][0], "http://localhost:8000/api/person/one/joe.tester.xml")
        self.assertEqual(self.h.http_requests[0][0][1], "POST")
