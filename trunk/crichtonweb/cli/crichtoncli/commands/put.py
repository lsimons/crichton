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
from django.core import serializers
from django.core.management.base import CommandError
from django.utils.encoding import iri_to_uri

from crichtoncli.apihelpers import *
from crichtoncli.commands import ApiCommand

def put_one(model, key, data, api_url=None, http_client=None, **kwargs):
    url_base = api_url
    format = "xml"

    # check deserialization works
    deserialized = serializers.deserialize("xml_no_db", data)
    found_one = False
    for x in deserialized:
        if found_one:
            raise "Deserialized more than one object" # TODO exception classes
        found_one = True
        if x.object._meta.object_name != model._meta.object_name:
            raise "Deserialized a %s, was expecting a %s" % (x.object._meta.object_name, model._meta.object_name)
    
    # TODO model should allow producing name-as-in-url??
    meta = model._meta
    url_name = camel_to_url(meta.object_name)

    url = "%(url_base)s%(url_name)s/one/%(key)s.%(format)s" % locals()
    
    resp, content = http_client.request(iri_to_uri(url), "POST",
        body=data,
        headers={"content-type":CONTENT_TYPES[format]})
    
    expect_ok(resp, content)
    print content.encode("UTF-8")

def put_one_by_datatype(datatype_name, key, data, **kwargs):
    model = model_from_datatype(datatype_name)
    put_one(model, key, data, **kwargs)

class Command(ApiCommand):
    help = ("Save data on the crichton server from the provided "
        "XML file.")
    args = "<datatype> <key> <xmlfile>"

    def print_help(self, prog_name, subcommand):
        super(ApiCommand, self).print_help(prog_name, subcommand)
        print_datatype_help()

    def handle(self, *args, **options):
        if len(args) < 3:
            raise CommandError("You must provide a datatype, a key and an xml file")
        
        http_client = self.get_api_client(**options)
        
        datatype = args[0]
        key = args[1]
        xmlfile = args[2]
        data = open(xmlfile, "r").read()
        put_one_by_datatype(datatype, key, data, http_client=http_client, **options)
