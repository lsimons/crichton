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
from crichtonweb.core.lookups import BaseLookup
from crichtonweb.release.models import Release
from django.db.models import Q

class ReleaseLookup(BaseLookup):
    model = Release

    def get_filter(self, term):
        MAX = 50
        truncated = self.model.objects.filter(
            Q(product__name=term) | \
            Q(product__name__icontains=term) | \
            Q(version__icontains=term)
        )[:MAX]

        # we can't return 'truncated' as-is, since this will generate an
        # "Cannot filter a query once a slice has been taken" error.
        # Rebuild it as a QuerySet
        qset = self.model.objects.none()
        for x in truncated:
            qset = qset | self.model.objects.filter(id=x.id)
        return qset
    
    def order(self, qs):
        return qs.order_by('product', 'version')
