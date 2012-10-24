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
from crichtoncli.apihelpers import *

from crichtonweb.prodmgmt.models import Person
from crichtonweb.issue.models import Issue
from crichtonweb.ci.models import BuildServer
from crichtonweb.package.models import Version

from django.utils.text import capfirst
from crichtoncli.commands import ApiCommand
from crichtoncli.commands.list import list_all
from crichtoncli.commands.get import list_one
from crichtoncli.commands.put import put_one
from crichtoncli.apihelpers import get_datatypes

def demo(**kwargs):
    print "-" * 60
    print "LISTING EVERYTHING"
    print "-" * 60
    for model_name in get_datatypes():
        model = model_from_datatype(camel_to_url(model_name))
        meta = model._meta
        print capfirst(meta.object_name) + "s:"
        list_all(model, **kwargs)
        print

    print "-" * 60
    print "SOME UPDATES"
    print "-" * 60

    print "put build_server hudson-ci-app-int sample-data/build_server_hudson-ci-app-int.xml"
    put_one(BuildServer, "hudson-ci-app-int", open("sample-data/build_server_hudson-ci-app-int.xml", "r").read(), **kwargs)

    print "put issue PIPELINE:PIPELINE-72@forge-jira sample-data/issue_PIPELINE__PIPELINE-72__forge-jira.xml.xml"
    put_one(Issue, "PIPELINE:PIPELINE-72@forge-jira", open("sample-data/issue_PIPELINE__PIPELINE-72__forge-jira.xml", "r").read(), **kwargs)

    print "-" * 60
    print "SOME SPECIFIC QUERIES"
    print "-" * 60

    print "get person matthew.wood"
    list_one(Person, "matthew.wood", **kwargs)
    print

    print "get person matthew.wood --audit"
    list_all(Person, "audit/matthew.wood", **kwargs)
    print

    print "get build_server hudson-ci-app-int"
    list_one(BuildServer, "hudson-ci-app-int", **kwargs)
    print

    print "get build_server hudson-ci-app-int --audit"
    list_all(BuildServer, "audit/hudson-ci-app-int", **kwargs)
    print

    print "get build_server hudson-ci-app-int --xml"
    list_one(BuildServer, "hudson-ci-app-int", xml=True, **kwargs)
    print
    
    print "list version"
    list_all(Version, **kwargs)
    print

    print "get issue PIPELINE:PIPELINE-72@forge-jira --xml"
    list_one(Issue, "PIPELINE:PIPELINE-72@forge-jira", xml=True, **kwargs)
    print


class Command(ApiCommand):
    help = ("Some example API invocations.")

    def handle(self, *args, **options):
        
        http_client = self.get_api_client(**options)
        
        demo(http_client=http_client, **options)
