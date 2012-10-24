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

from django.core.management.base import CommandError

from crichtoncli.apihelpers import print_datatype_help
from crichtoncli.commands import ApiCommand
from crichtoncli.commands.list import list_all, list_all_by_datatype
from crichtoncli.commands.list import Command as ListCommand

def list_one(model, key, **kwargs):
    selector = "one/" + key
    list_all(model, selector=selector, **kwargs)

def list_one_by_datatype(datatype_name, key, **kwargs):
    selector = "one/" + key
    list_all_by_datatype(datatype_name, selector=selector, **kwargs)

def audit_one_by_datatype(datatype_name, key, **kwargs):
    selector = "audit/" + key
    list_all_by_datatype(datatype_name, selector=selector, **kwargs)

class Command(ApiCommand):
    help = ("Retrieve an entity from the crichton server "
            "of the specified data type with the specified key.")
    args = "<datatype> <key>"

    option_list = ListCommand.option_list + (
        make_option("--audit", action="store_true", dest="audit",
            default=False, help="Get audit data rather than data "
                "itself. Defaults to false."),
    )

    def print_help(self, prog_name, subcommand):
        super(ApiCommand, self).print_help(prog_name, subcommand)
        print_datatype_help()

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError("You must provide a datatype and a key")
        datatype_name = args[0]
        key = args[1]
        
        http_client = self.get_api_client(**options)

        if options.get("audit", False):
            audit_one_by_datatype(datatype_name, key, http_client=http_client, **options)
        else:
            list_one_by_datatype(datatype_name, key, http_client=http_client, **options)
