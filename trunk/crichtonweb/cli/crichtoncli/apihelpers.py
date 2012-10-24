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
from crichtonweb.core.httpshelpers import *
from crichtonweb.api.services import camel_to_url, url_to_camel
from package import models as package
from django.db.models import Model, get_model
from django.db.models.base import ModelBase
from django.core.management.base import CommandError
from django.conf import settings
from django.utils.importlib import import_module

_exposed_models = None
def get_exposed_models():
    global _exposed_models
    if _exposed_models == None:
        result = []
        app_list = settings.API_EXPOSED_APPS
        for app in app_list:
            model = import_module(app + ".models")
            result.append(model)
        _exposed_models = result
        return result
    return _exposed_models

def model_from_datatype(datatype_name):
    model_name = url_to_camel(datatype_name)
    found_model = None
    for app in settings.API_EXPOSED_APPS:
        m = get_model(app, model_name)
        if m is not None:
            return m
    raise CommandError("Unknown data type %s" % (datatype_name,))

def get_datatypes(model=None):
    result = []
    if model != None:
        keys = model.__dict__.keys()[:]
        keys.sort()
        for k in keys:
            v = getattr(model, k)
            if isinstance(v, Model) or isinstance(v, ModelBase):
                if hasattr(v, "_meta") and hasattr(v._meta, "abstract") and v._meta.abstract == True:
                    continue
                if hasattr(v, "__name__") and v.__name__ in ["crichtonCronJobStatus", "FollowedProduct"]:
                    continue
                result.append(k)
    else:
        for models in get_exposed_models():
            result.extend(get_datatypes(models))
    return result

def print_datatype_help():
    print
    print "Available models:"
    for model in get_datatypes():
        print " ", camel_to_url(model)
