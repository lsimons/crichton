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
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from crichtonweb.release.models import DeploymentRequest

from crichtonweb.hotjazz.utils import intercept_api_exceptions, HttpError

@csrf_exempt
@intercept_api_exceptions
def deployment_request(request, product_name, release_version, environment_name):
    if request.method != "GET" and request.method != "HEAD":
        return HttpResponse("Only GET is allowed here, not %s\n" % request.method,
                content_type='text/plain', status=405)
    
    try:
        dr = DeploymentRequest.objects.get(
                release__product__name=product_name,
                release__version=release_version,
                environment__name=environment_name)
    except ObjectDoesNotExist:
        raise HttpError("Object not found: " + product_name + "," + release_version + "," + environment_name,
                status=404)
    
    if dr.deleted or dr.release.deleted or dr.environment.deleted:
        raise HttpError("Object deleted", status=404)

    # TODO configure base_url
    base_url = "http://localhost:8000/"
    
    json = {}
    json["environment"] = dr.environment.name
    #json["admin_url"] = base_url + "admin/release/deploymentrequest/" + str(dr.id) + "/"
    json["admin_url"] = dr.get_absolute_url()
    if dr.ops_issue:
        json["ops_issue"] = dr.ops_issue.name
    json["release"] = {}
    #json["release"]["admin_url"] = base_url + "admin/release/release/" + str(dr.release.id) + "/"
    json["release"]["admin_url"] = dr.release.get_absolute_url()
    json["release"]["product"] = {}
    json["release"]["product"]["name"] = dr.release.product.name
    json["release"]["product"]["owner"] = unicode(dr.release.product.owner)
    json["release"]["product"]["pipeline_issue"] = dr.release.product.pipeline_issue.name
    #json["release"]["product"]["admin_url"] = base_url + "admin/prodmgmt/product/" + str(dr.release.product.id) + "/"
    json["release"]["product"]["admin_url"] = dr.release.product.get_absolute_url()
    json["release"]["packages"] = []
    for release_element in dr.release.elements.filter(deleted=False):
        pkg = {}
        pkg["name"] = release_element.package.name
        pkg["version"] = release_element.package_version.name
        pkg["rpm_version"] = release_element.package_version.rpm_version
        pkg["rpm_release"] = release_element.package_version.rpm_release
        if release_element.application:
            pkg["application"] = {}
            pkg["application"]["name"] = release_element.application.name
            pkg["application"]["display_name"] = release_element.application.display_name
        json["release"]["packages"].append(pkg)
    
    body = simplejson.dumps(json, indent=4)
    format = "json"
    content_type = "application/json"
    return HttpResponse(body, content_type=content_type, status=200)
