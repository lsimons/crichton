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

from prodmgmt.models import Person, Product, Application
from package.models import PackageName, Package, Version, PackageRepository
from frontend.models import FollowedProduct
from issue.models import Issue
from system.models import Node, crichtonCronJobStatus

from django.utils import simplejson

def json_response(data):
    return HttpResponse(simplejson.dumps(data), mimetype="application/json")

def json_response_not_found(mydata={}):
    return HttpResponseNotFound(simplejson.dumps(mydata), mimetype="application/json")

from django import forms

cookie_defaults = {
    "filter_level": "followed",
    "show_deleted": False
    }

FILTER_LEVEL_CHOICES = (
    ('none', 'No filtering by user, show everything'),
    ('followed', "Show my projects, plus those I'm following"),
    ('mine', 'Show just my projects'),
    )
class OptionsForm(forms.Form):
    filter_level = forms.ChoiceField(choices=FILTER_LEVEL_CHOICES)
    show_deleted = forms.BooleanField(required=False)
    
@csrf_protect
def load_tab_options(request):
    for x in cookie_defaults.keys():
        if x not in request.session.keys():
            request.session[x] = cookie_defaults[x]
            
    prefilled = {
        'filter_level': request.session["filter_level"],
        'show_deleted': request.session["show_deleted"]
        }
    options_form = OptionsForm(initial=prefilled)
    
    mydict = {
        'options_form': options_form,
        }
    return render_to_response('tab-options.html',
                              mydict,
                              context_instance=RequestContext(request)
                              )

@csrf_protect
def load_tab_package(request):
    repositories = PackageRepository.objects.all()
    try:
        last_yum_index = crichtonCronJobStatus.objects.get(name='index_yum_repo', status='Successful').date
    except crichtonCronJobStatus.DoesNotExist:
        last_yum_index = 'never'
    mydict = {
        'all_repositories': [x.name for x in repositories],
        'last_indexrpm_success': last_yum_index
        }
    return render_to_response('tab-package.html',
                              mydict,
                              context_instance=RequestContext(request)
                              )

@csrf_protect
def add_followed_products(request):
    if request.method != 'POST':
        return HttpResponseRedirect('/#tab-options')

    try:
        person = Person.objects.get(username=request.user.username)
    except Person.DoesNotExist:
        logging.error("add_followed_products: Can't find person '%s'" % request.user.username)

    for x in request.POST:
        if not x.startswith("add_followed_product_"):
            continue
        
        product_id = request.POST[x]
        try:
            product = Product.objects.get(id=product_id)
        except:
            logging.error("add_followed_products: Can't find product id='%s'" % product_id)
            return HttpResponseRedirect('/#tab-options')

        followed_product, new = \
                          FollowedProduct.objects.get_or_create(product=product, user=person)
        if new:
            logging.info("Added FollowedProduct %s" % followed_product)

    return HttpResponseRedirect('/#tab-options')
    
@csrf_protect
def del_followed_products(request):

    if request.method != 'POST':
        return HttpResponseRedirect('/#tab-options')

    try:
        person = Person.objects.get(username=request.user.username)
    except Person.DoesNotExist:
        logging.error("del_followed_products: Can't find person '%s'" % request.user.username)

    for x in request.POST:
        if not x.startswith("del_followed_product_"):
            continue
        
        product_id = request.POST[x]
        try:
            product = Product.objects.get(id=product_id)
        except:
            logging.error("del_followed_products: Can't find product id='%s'" % product_id)
            return HttpResponseRedirect('/#tab-options')

        try:
            followed_product = FollowedProduct.objects.get(product=product, user=person)
        except FollowedProduct.DoesNotExist:
            logging.error("del_followed_products: Can't find FollowedProduct to delete for '%s', '%s'" % (product, person))
            return HttpResponseRedirect('/#tab-options')
        logging.info("Deleted FollowedProduct %s" % followed_product)
        followed_product.delete()

    return HttpResponseRedirect('/#tab-options')
    
@csrf_protect
def set_tab_options(request):
    options_form = OptionsForm()
    if request.method == 'POST':
        options_form = OptionsForm(request.POST)
        if options_form.is_valid():
            request.session["filter_level"] = options_form.cleaned_data["filter_level"]
            request.session["show_deleted"] = options_form.cleaned_data["show_deleted"]
        # todo else: return error

    return HttpResponseRedirect('/#tab-options')
    
@csrf_protect
def get_node_details(request, name):
    rtn = {}
    try:
        node = Node.objects.get(name=name)
    except Node.DoesNotExist:
        return json_response_not_found()

    data = {
        "is_virtual": node.is_virtual,
        "environment": node.environment.name,
        "deleted": node.deleted,
        "api_link": node.get_api_url("json"),
        "node_addresses": node.internet_address_list(),
        "pools": node.pool_list_urls(),
        }
    return json_response(data)

@csrf_protect
def get_node_apps(request, name):
    rtn = {}
    try:
        node = Node.objects.get(name=name)
    except Node.DoesNotExist:
        return json_response_not_found()

    node_deployments = [{"app_deploy_name": "%s" % nd.application_deployment.get_name(),
                         "app_deploy_date": nd.application_deployment.get_date(),
                         "prod_deploy": "%s" % nd.application_deployment.product_deployment,
                         "succeeded": nd.succeeded,
                         "started": "%s" % nd.started,
                         "finished":" %s" % nd.finished} for nd in node.deployments.all()]
    
    data = {
        "node_deployments": node_deployments,
        }
    return json_response(data)

@csrf_protect
def get_package_versions(request, name):
    rtn = {}
    try:
        packages = Package.objects.filter(name=name)
    except Package.DoesNotExist:
        return json_response_not_found()

    data = { 
        "name": name, 
        "versions": []
    }
    for pkg in packages:
        pkg_data = {
            "version": pkg.version.name,
            "deleted": pkg.deleted,
            "repositories": {}
            }
        for location in pkg.locations.all():
            pkg_data["repositories"][location.repository.name] = 1
        data["versions"].append(pkg_data)
    return json_response(data)

def list_filtered_products(request):
    set_trace()
    nodes = Node.objects.all()
    if not request.session.get("show_deleted", False):
        nodes = nodes.filter(deleted=False)
    names = [n.name for n in nodes]
    return json_response(names)

def list_node_names(request):
    nodes = Node.objects.all()
    if not request.session.get("show_deleted", False):
        nodes = nodes.filter(deleted=False)
    names = [n.name for n in nodes]
    return json_response(names)

def list_pipeline_issues(request):
    issues = [{"label": i.longname(), "value": i.id} for i in Issue.pipeline.all()]
    return json_response(issues)
    
def list_people(request):
    people = [{"label": p.username, "value": p.id} for p in Person.objects.all()]
    return json_response(people)
    
def _list_generic(Thing):
    things = [{"label": u"%s" % me, "value": me.id} for me in Thing.objects.all()]
    return json_response(things)

def list_packagenames(request):
    things = [{"label": me.name, "value": me.name} for me in PackageName.objects.all()]
    return json_response(things)
    
def list_versions(request):
    return _list_generic(Version)
    
def list_applications(request):
    return _list_generic(Application)
    
# eof
