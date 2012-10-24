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
from optparse import make_option

from django.core import serializers
from django.core.management.base import CommandError
from django import db
from django.utils.encoding import iri_to_uri

from crichtoncli.apihelpers import *
from crichtoncli.commands import ApiCommand
from crichtonweb.api.services import camel_to_url, url_to_camel

def print_list(iterable):
    """Print a list of django objects to stdout."""
    printed_header = False
    total_width = 0
    for des_obj in iterable:
        obj = des_obj.object
        if not printed_header:
            meta = obj._meta
            for f in meta.fields:
                if f.name.endswith("id"):
                    continue
                length = min(20, max(len(f.name), f.max_length)+2)
                if f.rel:
                    length = 25
                total_width += length + 1
                setattr(f, 'display_length', length)
                fmt_string = "%-" + str(f.display_length) + "s"
                if len(f.name) > f.display_length:
                    print fmt_string % (f.name[:f.display_length],),
                else:
                    print fmt_string % (f.name,),
            print
            print "-" * total_width
            printed_header = True
        for f in meta.fields:
            if f.name.endswith("id"):
                continue
            if f.rel and isinstance(f.rel, db.models.ManyToManyRel):
                val = des_obj.m2m_data[f.name]
            elif f.rel and isinstance(f.rel, db.models.ManyToOneRel):
                val = getattr(obj, f.attname, "")
            else:
                val = unicode(getattr(obj, f.name, ""))
            if val is None:
                val = ""
            val = unicode(val)
            if len(val) > f.display_length:
                val = val[:f.display_length-3]
                fmt_string = "%-" + str(f.display_length - 3) + "s..."
                print (fmt_string % (val,)).encode("UTF-8"),
            else:
                fmt_string = "%-" + str(f.display_length) + "s"
                print (fmt_string % (val,)).encode("UTF-8"),
        print
    
    if not printed_header:
        print "No results."

def list_all(model, selector="list/all", xml=False, http_client=None, api_url=None, **kwargs):
    url_base = api_url
    format = "xml"
    deserialize_format = "xml_no_db"

    meta = model._meta
    url_name = camel_to_url(meta.object_name)

    url = "%(url_base)s%(url_name)s/%(selector)s.%(format)s" % locals()
    resp, content = http_client.request(iri_to_uri(url), "GET")

    expect_ok(resp, content)
    expect_xml(resp, content)
    if xml:
        print content.encode("UTF-8")
    else:
        deserialized = serializers.deserialize(deserialize_format, content)
        print_list(deserialized)

def list_all_by_datatype(datatype_name, **kwargs):
    model = model_from_datatype(datatype_name)
    list_all(model, **kwargs)

class Command(ApiCommand):
    help = ("Retrieve lists of entities from the crichton server "
            "that are of the specified data type.")
    args = "<datatype> [datatypes]"

    option_list = ApiCommand.option_list + (
        make_option("--xml", action="store_true", dest="xml",
            default=False, help="Produce raw xml rather than "
                "formatted text. Defaults to false."),
    )
    
    def print_help(self, prog_name, subcommand):
        super(ApiCommand, self).print_help(prog_name, subcommand)
        print_datatype_help()

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("You must provide at least one model type")
        
        http_client = self.get_api_client(**options)
        
        for datatype_name in args:
            # check all types before fetching one
            model_from_datatype(datatype_name)
        
        for url_name in args:
            list_all_by_datatype(datatype_name, http_client=http_client, **options)
