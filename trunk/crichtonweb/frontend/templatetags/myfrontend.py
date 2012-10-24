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
from django import template
from django.db.models import Q

from crichtonweb.frontend.models import FollowedProduct
import crichtonweb.ci.models as ci
import crichtonweb.release.models as release
import crichtonweb.prodmgmt.models as prodmgmt
import crichtonweb.system.models as system

register = template.Library()

def filter_deleted(qs, context):
    request = context["request"]
    show_deleted = request.session.get("show_deleted", False)
    if not show_deleted:
        return qs.filter(deleted=False)
    else:
        return qs

def filter_products(context):
    request = context["request"]
    filter_level = request.session.get("filter_level", "followed")
    username = context["user"].username
    
    products = prodmgmt.Product.objects.all()
    products = filter_deleted(products, context)
    if filter_level == "followed":
        # django does not do UNION so we have to do this in memory
        pset = set(products.filter(Q(owner__username=username)))
        products = pset.union(products.filter(Q(followers__user__username=username)))
        del pset
    elif filter_level == "mine":
        products = products.filter(Q(owner__username=username))
    return products

class ProductListNode(template.Node):
    """The products corresponding to the current filter."""
    
    def __init__(self, var_name):
        self.var_name = var_name
        
    def render(self, context):
        products = filter_products(context)
        for x in products:
            x.status = x.ownership_status(context["user"].username)
        context[self.var_name] = products
        return ''
        
@register.tag
def get_products_for_filter(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return ProductListNode(var_name)

class UnfollowedProductListNode(template.Node):
    """The products corresponding to the current filter that are not owned or followed."""

    def __init__(self, var_name):
        self.var_name = var_name
        
    def render(self, context):
        products = prodmgmt.Product.objects.all()
        products = filter_deleted(products, context)
        products = products.exclude(owner__username=context["user"].username)
        products = products.exclude(followers__user__username=context["user"].username)
        for x in products:
            x.status = x.ownership_status(context["user"].username)
        context[self.var_name] = products
        return ''
        
@register.tag
def get_unfollowed_products(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return UnfollowedProductListNode(var_name)

class FollowedProductListNode(template.Node):
    """The products corresponding to the current filter that are not owned or followed."""

    def __init__(self, var_name):
        self.var_name = var_name
        
    def render(self, context):
        products = prodmgmt.Product.objects.all()
        products = filter_deleted(products, context)
        products = products.filter(followers__user__username=context["user"].username)
        for x in products:
            x.status = x.ownership_status(context["user"].username)
        context[self.var_name] = products
        return ''
        
@register.tag
def get_followed_products(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return FollowedProductListNode(var_name)

class ThingListNode(template.Node):
    """The objects corresponding to the current filter."""
    
    def __init__(self, var_name, mymodel):
        self.var_name = var_name
        self.mymodel = mymodel
    
    def render(self, context):
        products = filter_products(context)
        mine = self.mymodel.objects.filter(product__in=products)
        mine = filter_deleted(mine, context)
        context[self.var_name] = mine
        return ''

@register.tag
def get_applications_for_filter(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return ThingListNode(var_name, prodmgmt.Application)

@register.tag
def get_releases_for_filter(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return ThingListNode(var_name, release.Release)

class DeploymentRequestListNode(template.Node):
    
    def __init__(self, var_name):
        self.var_name = var_name
        
    def render(self, context):
        products = filter_products(context)
        releases = release.Release.objects.filter(product__in=products)
        releases = filter_deleted(releases, context)
        mine = release.DeploymentRequest.objects.filter(release__in=releases)
        mine = filter_deleted(mine, context)
        context[self.var_name] = mine
        return ''
        
@register.tag
def get_deployment_requests_for_filter(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return DeploymentRequestListNode(var_name)

@register.tag
def get_build_jobs_for_filter(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return ThingListNode(var_name, ci.BuildJob)

class BuildResultListNode(template.Node):
    """The latest build results for the current filter."""

    def __init__(self, var_name):
        self.var_name = var_name
        
    def render(self, context):
        products = filter_products(context)
        
        mine = ci.BuildResult.objects.none()
        for fp in products:
            buildjobs = ci.BuildJob.objects.filter(product=fp)
            buildjobs = filter_deleted(buildjobs, context)
            for job in buildjobs:
                results = ci.BuildResult.objects.filter(job=job)
                results = filter_deleted(results, context)
                results = results.order_by("-finished_at")
                if len(results):
                    latest = results[0]
                    mine = mine | ci.BuildResult.objects.filter(id=latest.id)

        mine = mine.order_by('job__product')
        context[self.var_name] = mine
        return ''
        
@register.tag
def get_latest_build_results_for_filter(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return BuildResultListNode(var_name)

#

class OrphanBuildJobListNode(template.Node):
    """The latest build results for the current filter."""

    def __init__(self, var_name):
        self.var_name = var_name
        
    def render(self, context):
        
        mine = ci.BuildJob.objects.filter(product__isnull=True)
        context[self.var_name] = mine
        return ''
        
@register.tag
def get_build_jobs_without_product(parser, token):
    try:
        tag_name, var_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return OrphanBuildJobListNode(var_name)

class StatusNode(template.Node):
    def __init__(self, var_name, status_type, status_name):
        self.var_name = var_name
        self.status_type = status_type
        self.status_name = status_name

    def render(self, context):
        try:
            context[self.var_name] = getattr(system, self.status_type).objects.get(name = self.status_name)
        except AttributeError, e:
            raise template.TemplateSyntaxError, "Error: Asking for StatusType:%s StatusName:%s Error:%s" % (status_type, status_name, str(e))
        return ''

@register.tag
def get_status(parser, token):
    try:
        tag_name, var_name, status_type, status_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s: needs one arg, the variable for the results" % token
    return StatusNode(var_name, status_type, status_name)

# eof
