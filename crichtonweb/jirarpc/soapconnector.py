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
"""This implements a single instance of a SOAP connection to Jira
over SSL with certificates. Please ensure the following variables are
specified in your config file:

CA_CERT_FILE
SSL_CERT_FILE
SSL_KEY_FILE
JIRA_SOAP_ROOT
JIRA_USER
JIRA_PASS

Usage:
client = soapconnector.get_client()
# returned_data = client.service.someSoapMethod()
# new_local_var = client.factory.create('SomeObjectFromWsdl')
# See python-suds documentation

"""

import httplib
import urllib2
from suds.transport.http import HttpTransport
from suds.client import Client
from suds.options import Options

from django.conf import settings

# Maintain a single instance
_jira = None

def get_client():
    """Returns a soap client."""
    transport = HttpClientAuthTransport(settings.SSL_KEY_FILE, settings.SSL_CERT_FILE,)
    global _jira
    if not _jira:
        _jira = Client(settings.JIRA_SOAP_ROOT, transport=transport)
    return _jira

# The following two classes are taken from
# http://www.threepillarglobal.com/https-client-authentication-solution-for-the-suds-soap-library
# They allow suds to work over https with certs.
# TODO - replace this with something using M2Crypto or httplib2 so
# that we get server cert verification as well. Suggestions welcome!

class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert
    def https_open(self, req):
        #Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)
    def getConnection(self, host, *args, **kwargs):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert, *args, **kwargs)

class HttpClientAuthTransport(HttpTransport):
    def __init__(self, key, cert, options = Options()):
        HttpTransport.__init__(self)
        self.urlopener = urllib2.build_opener(HTTPSClientAuthHandler(key, cert))

