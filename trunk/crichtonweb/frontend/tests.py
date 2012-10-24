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
from django.test import TestCase
from django.utils import unittest

from frontend import BBCRemoteUserBackend

class FrontendTestCase(TestCase):

    def test_parse_cert(self):
        backend = BBCRemoteUserBackend()
        username = backend.clean_username("Email=john.doe@domain.local,CN=John Doe,OU=BBC - FMT - Online Media Group,O=British Broadcasting Corporation,L=London,C=GB")
        self.assertEqual(username, "John.Doe")
        self.assertEqual(backend.email, "john.doe@domain.local")
        self.assertEqual(backend.first_name, "John")
        self.assertEqual(backend.last_name, "Doe")

    def test_parse_cert_no_last_name(self):
        backend = BBCRemoteUserBackend()
        backend.clean_username("Email=john.doe@domain.local,CN=John,OU=BBC - FMT - Online Media Group,O=British Broadcasting Corporation,L=London,C=GB")
        self.assertEqual(backend.first_name, "John")
        self.assertEqual(backend.last_name, "")

    def test_parse_cert_complex_last_name(self):
        backend = BBCRemoteUserBackend()
        backend.clean_username("Email=john.doe@domain.local,CN=John long Last-Name,OU=BBC - FMT - Online Media Group,O=British Broadcasting Corporation,L=London,C=GB")
        self.assertEqual(backend.first_name, "John")
        self.assertEqual(backend.last_name, "long Last-Name")

