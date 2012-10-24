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
import re

from crichtonweb.core.lookups import BaseLookup, NamedLookup, NameStartLookup
from crichtonweb.package.models import Package, PackageName, Version
from django.db.models import Q

from django.conf import settings

class PackageLookup(BaseLookup):
    model = Package
    
    def get_filter(self, term):
        if term is not None:
            query = None
            
            # if we happen to do a query when the user is just typing "<stuff>-" and hasn't typed
            # the version yet, it should work...
            if term.endswith("-"):
                term = term[:-1]
            
            term_parts = re.split(r"[ -]", term)
            if len(term_parts) > 1:
                probable_version = term_parts[-1]
                if re.match(r"^[0-9._]+$", probable_version): # yeah that looks like a version number
                    query = Q(version__name__istartswith=probable_version)
                    # since we matched on "<stuff>( |-)<version>", don't look for "( |-)<version>"
                    # in the package name...
                    term = term[:-len(probable_version)]
                    if term.endswith("-"):
                        term = term[:-1]
            
            term_parts = term.split(" ")
            for term in term_parts:
                query_part = Q(name__icontains=term)
                if query is None:
                    query = query_part
                else:
                    query = query & query_part
            
            f = self.model.objects.filter(query)
        else:
            f = self.model.objects.all()
        return f
    
    def limit(self, qs):
        return qs[:settings.MAX_LOOKUP_RESULTS]
    
    def order(self, qs):
        return qs.order_by('name', '-version__name')

class PackageNameLookup(NamedLookup):
    model = PackageName

class VersionLookup(NameStartLookup):
    model = Version
