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
from crichtoncli.apihelpers import *

from django.core.management.base import CommandError
from crichtoncli.commands import ApiCommand
    
class Command(ApiCommand):
    help = ("get_https_request: requires url, cert_file, key_file and ca_file options set.")

    def handle(self, *args, **options):
        """ if the required options aren't available then return as an error.
        """
        
        if options['url'] == None:
          raise CommandError("You need to specify the url for the request with --url")        
                    
        if options['cert_file'] == None:
          raise CommandError("You need to specify the path to the certificate with --cert_file")
            
        if options['key_file'] == None:
          raise CommandError("You need to specify the path to the key (it can be the same as the cert pem file) with --key_file")        
          
        if options['ca_file'] == None:
          raise CommandError("You need to specify the path to the ca cert file with --ca_file")        
          
        url = options['url']
            
        h = self.get_api_client()
        response, content = h.request(iri_to_uri(url), "GET")
        
        if not ok(response):
          print "Error in requesting %s %s\n" % (url, response.status)
        else:
          print content
          
