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
from crichtonweb.core.lookups import NamedLookup
from crichtonweb.ci.models import BuildJob

class BuildJobLookup(NamedLookup):
    model = BuildJob

class OrphanBuildJobLookup(BuildJobLookup):
    def get_query(self, q, request):
        qs = BuildJobLookup.get_query(self, q, request).filter(product__isnull=True)
        return qs

# eof
