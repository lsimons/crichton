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
from django.forms import ModelForm, ModelChoiceField
from django.core.exceptions import ValidationError
from django.db.models import Q

from ajax_select.fields import AutoCompleteSelectField

import crichtonweb.prodmgmt.models as pm
from crichtonweb.prodmgmt.models import Product
from crichtonweb.issue.models import Issue

class ProductField(AutoCompleteSelectField):
    
    # ReleaseForm, ApplicationForm has the cutandpaste magic turned on. So we need to
    # handle a product name, as well as the standard product pk

    def to_python(self, value):
        if value is None:
            return value

        # 'value' might be a id (user chose something from the autocomplete dropdown)
        # or it might be a name (user typed or cut'n'pasted but didn't select)
        # There is an edge case where a product has a name which could also be an id,
        # but its id is different. Can't see a way round that. Post an error if it occurs.
        try:
            int(value)
            objs = Product.objects.filter(Q(name=value) | Q(id=int(value)))
        except ValueError:
            objs = Product.objects.filter(Q(name=value))

        if len(objs) == 1:
            value = objs[0].id
        elif len(objs) == 0:
            raise ValidationError("Can't find Product '%s'" % value)
        elif len(objs) > 1:
            raise ValidationError("EdgeCase: ambiguous answers available for '%s'" % value)

        return int(value)
    
    def clean(self, value):

        # to_python() might normally be a better place for this code
        # but the AutoCompleteSelectField.clean() doesn't call it
        
        value = self.to_python(value)
        
        return super(ProductField, self).clean(value)

class ApplicationForm(ModelForm):
    product = ProductField('product', label='Product')

    class Meta:
        model = pm.Application

class ProductForm(ModelForm):
    owner = AutoCompleteSelectField('person', label='Person')
    pipeline_issue = AutoCompleteSelectField('pipeline_issue', label='Pipeline ticket')

    class Meta:
        model = pm.Product
        
# eof
