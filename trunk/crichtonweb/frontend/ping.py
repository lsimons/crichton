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
import datetime
from django.utils import simplejson
import socket
from _mysql_exceptions import OperationalError
from django.http import HttpResponse
from django.core import serializers

from system.models import crichtonCronJobStatus 

def index(request, format):
    """Performs a health check on the crichton app, and returns an page
    that can be picked up with urlmonitor.

    In addition, it will print out separate status check results for various 
    parts like last cron run, etc. The intention is for it to be human
    readable (format = html) but in theory can be picked up by a machine as 
    well.

    """

    json = {}
    json["currentstatus"] = {}
    json["currentstatus"]["hostname"] = socket.gethostname()
    json["recentactivity"] = {}

    # everything else from the db
    for cron_job in crichtonCronJobStatus.objects.all():
        json["recentactivity"]['Last cron job %s' % cron_job.name] = {
            'date' : cron_job.date.strftime("%d/%m/%Y %H:%M:%S"),
            'status' : cron_job.status,
            'comment' : cron_job.comment
        }

    body = simplejson.dumps(json, indent=4)
    if format == "html":
        # For lack of anything better to do, present the json data but
        # wrapped in a basic html page.
        body = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\"> \n\
<html><body><pre>%s</pre></body></html>" % body
        content_type = "text/html"
    elif format == "json":
        content_type = "application/json"
    else:
        raise Exception("Bad format %s provided" % format)

    return HttpResponse(body, content_type=content_type, status=200)
