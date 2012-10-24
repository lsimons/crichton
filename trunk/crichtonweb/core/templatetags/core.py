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
from pdb import set_trace

from django import template

from crichtonweb.prodmgmt.models import Product

register = template.Library()

class ThingNode(template.Node):
    def __init__(self, model, var_name):
        self.model = model
        self.var_name = var_name
    def render(self, context):
        if self.model in [Product]:
            mine = self.model.objects.filter(owner__username=context["user"].username)
        else:
            raise template.TemplateSyntaxError, "ThingNode: model %s not yet supported" % self.model
            mine = self.model.objects.none()
        context[self.var_name] = mine
        return ''
        
@register.tag
def get_my_owned_products(parser, token):
    try:
        tag_name, arg = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return ThingNode(Product, arg)

# eof
