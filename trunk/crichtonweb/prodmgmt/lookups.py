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
from crichtonweb.prodmgmt.models import Application, Person, Product
from django.db.models import Q

class ApplicationLookup(BaseLookup):
    model = Application

    def get_filter(self, term):
        return self.model.objects.filter(
            Q(name__icontains=term) | \
            Q(display_name__icontains=term)
        )

    def order(self, qs):
        return qs.order_by('name')

class PersonLookup(BaseLookup):
    model = Person

    def get_filter(self, term):
        return self.model.objects.filter(
            Q(username__icontains=term) | \
            Q(first_name__icontains=term) | \
            Q(last_name__icontains=term) | \
            Q(email__icontains=term)
        )
    
    def order(self, qs):
        return qs.order_by('username')

class ProductLookup(BaseLookup):
    model = Product

    def get_objects(self, ids):
        # some of these 'ids' might actually be names, due to ajax_select autocomplete
        # so turn these back to ids

        # this use of ProductField probably isn't the best way to do it, but
        # I don't want to duplicate code and it's not clear where else to do this
        from crichtonweb.prodmgmt.forms import ProductField
        pf = ProductField('product')

        print "before: ids: %s" % ids
        ids = [pf.to_python(id) for id in ids]
        print "after: ids: %s" % ids
        return super(ProductLookup, self).get_objects(ids)
        
    def get_filter(self, term):
        return self.model.objects.filter(
            Q(name__icontains=term) | \
            Q(display_name__icontains=term)
        )

    def order(self, qs):
        return qs.order_by('name')
