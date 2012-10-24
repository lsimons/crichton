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
import httplib2
from urlparse import urlparse

CONTENT_TYPES = {
    "xml" : "application/xml",
    "textxml" : "text/xml",
    "json" : "application/json",
    "javascript" : "application/javascript"
}

def makeHttps(url, cert_file=None, key_file=None, ca_file=None, **options):
    """ Use  cert_file and key_file
        to locate the cert files and make the https requests
        httplib2 uses its authority list to store certificates by domain

        By default, cache dir location is controlled in the settings file.
        This can be overridden by passing in a 'cache' parameter.
    """
    
    scheme, netloc, path, parameters, query, fragment = urlparse(url)
    if options.has_key('cache'):
        cache = options['cache']
    else:
        cache = None
    https = httplib2.Http(cache=cache, timeout=1000)
    if scheme == "https" and cert_file and key_file:
        https.add_certificate(key_file, cert_file, netloc)
        if ca_file:
            https.set_ca_file(ca_file)
    return https


class HttpError(Exception):
    def __init__(self, desc, response, content):
        self.response = response
        self.content = content
        
        data = "HttpError-Status_" + str(self.response.status) + "\n"
        data += "Description: " + desc + "\n"
        data += "Details:" + "\n"
        for line in self.content.split("\n"):
            data += "  " + line + "\n"

        Exception.__init__(self, data)

def ok(resp):
    return resp.status >= 200 and resp.status < 400

def is_of_type(resp, content_type):
    content_type = CONTENT_TYPES.get(content_type, content_type)
    return resp.get("content-type", content_type).find(content_type) != -1

def is_json(resp):
    # jenkins spits out application/javascript if you ask for json. Yes, really.
    return is_of_type(resp, "json") or is_of_type(resp, "javascript")

def is_xml(resp):
    return is_of_type(resp, "xml") or is_of_type(resp, "textxml")

def expect_ok(resp, content):
    if not ok(resp):
        raise HttpError("Status %s" % (resp.status,), resp, content)

def expect_json(resp, content):
    if not is_json(resp):
        raise HttpError("Expected json, got %s" % (resp.get("content-type", "")), resp, content)

def expect_xml(resp, content):
    if not is_xml(resp):
        raise HttpError("Expected xml, got %s" % (resp.get("content-type", "")), resp, content)

