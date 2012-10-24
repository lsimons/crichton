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
import logging

from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from django import forms

from crichtonweb.prodmgmt.models import Person, Product
from crichtonweb.prodmgmt.forms import ProductForm

@csrf_protect
def frm_product(request, action, id=None):
    """
    action = create, edit, view, save
    """
    print "%s, %s, %s" % (request.method, action, id)
    from pdb import set_trace
    #set_trace()

    if id == "None":
        id = None
    finished = False
    
    # check for valid combinations of call
    def _is_call_ok(request, action, id):
        if action == "view" and request.method == "GET" and id is not None:
            return True
        if action == "edit" and request.method == "GET" and id is not None:
            return True
        if action == "create" and request.method == "GET" and id is None:
            return True
        if action == "save" and request.method == "POST":
            return True
        return False
    
    try:
        if not _is_call_ok(request, action, id):
            logging.debug("frm_product: params are invalid(method=%s, action=%s, id=%s)" % (request.method, action, id))
            raise

        if action == 'create':
            me = Person.objects.get(username=request.user.username)
            defaults = {
                'owner': me, 
                }
            frm = ProductForm(initial=defaults)

        elif action == 'view' or action == 'edit':
            # jquery will apply the 'readonly' attributes for 'view'
            try:
                product = Product.objects.get(id=id)
            except Product.DoesNotExist:
                logging.debug("frm_product: product %s does not exist" % id)
                raise
            frm = ProductForm(instance=product)

        elif action == "save":
            if id:
                try:
                    product = Product.objects.get(id=id)
                    frm = ProductForm(request.POST, instance=product)
                except Product.DoesNotExist:
                    logging.debug("frm_product: product %s does not exist" % id)
                    raise
            else:
                frm = ProductForm(request.POST)

            if frm.is_valid():
                frm.save()
                finished = True
                
        else:
            raise RuntimeError("invalid action: %s" % action)
        
        mydict = {
            "id": id, # Django form doesn't include id because it's auto-generated.
            "form": frm,
            "finished": finished,
            }

        resp = render_to_response('frm_create_product.html',
                                  mydict,
                                  context_instance=RequestContext(request)
                                  )
        return resp

    except:
        return ERROR
                              
# eof
