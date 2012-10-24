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
from django.db.models import Q
from django.db.models import fields

class BaseLookup(object):
    # set in subclass
    model = None
    
    # override in subclass:
    def get_filter(self, term):
        raise Exception("Must define get_filter in subclass")
    
    # override in subclass:
    def order(self, qs):
        return qs
    
    # override in subclass
    def limit(self, qs):
        return qs
    
    # override if primary key is weird
    def value_from_data(self, data):
        if self.integer_pk:
            return long(data)
        else:
            return unicode(data)
    
    # you can override this to determine if there is a '+' icon
    # the default behavior is to show it if django would show it
    # def can_add(self, *args, **kwargs):
    #     return True
    
    def __init__(self):
        if not self.model:
            raise Exception("Must define model in subclass")
        
        pk_field = self.model._meta.pk
        for t in [fields.AutoField, fields.IntegerField]:
            if isinstance(pk_field, t):
                self.integer_pk = True
            else:
                self.integer_pk = False
    
    def filter_deleted(self, request, qs):
        if hasattr(self.model, '_do_soft_delete') \
                and callable(self.model._do_soft_delete) \
                and self.model._do_soft_delete():
            show_deleted = request.session.get("show_deleted", False)
            if not show_deleted:
                qs = qs.filter(deleted=False)
        return qs

    def get_query(self, term, request):
        return self.limit(self.order(self.filter_deleted(request, self.get_filter(term))))
    
    def format_result(self, item):
        return getattr(item, "autocomplete_result", unicode(item))
        # todo support longname, but should make that a property first

    def format_item(self, item):
        return getattr(item, "autocomplete_html", self.format_result(item))

    def get_objects(self,ids):
        return self.order(self.model.objects.filter(pk__in=ids))

class NamedLookup(BaseLookup):
    # still need to set model in subclass
    
    def get_filter(self, term):
        return self.model.objects.filter(
            Q(name__icontains=term)
        )
    
    def order(self, qs):
        return qs.order_by('name')

class NameStartLookup(NamedLookup):
    # still need to set model in subclass
    
    def get_filter(self, term):
        return self.model.objects.filter(
            Q(name__istartswith=term)
        )
