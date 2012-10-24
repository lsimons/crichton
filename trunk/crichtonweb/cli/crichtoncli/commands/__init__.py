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
from optparse import make_option

from django.core.management.base import BaseCommand

from crichtonweb.core.httpshelpers import makeHttps

class ApiCommand(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--cert-file", action="store", dest="cert_file",
            default="/root/.yum/dev.domain.com.pem",
            help="The location of the certificate file used for https://"),
        make_option("--key-file", action="store", dest="key_file",
            default="/root/.yum/dev.domain.com.key",
            help="The location of the key file used for https://"),
        make_option("--ca-file", action="store", dest="ca_file",
            default="/etc/ca.pem",
            help="The location of the CA file used for https://"),
        make_option("--api-url", action="store", dest="api_url",
            default="http://localhost:8000/api/",
            help="The API endpoint URL to use. Defaults to "
                "http://localhost:8000/api/."),            
    )
    requires_model_validation = False
    
    def get_api_client(self, **options):
        return makeHttps(options['api_url'], options['cert_file'], options['key_file'], options['ca_file'])
