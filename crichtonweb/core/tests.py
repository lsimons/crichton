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
from django.test.client import Client
from django.forms import Select, SelectMultiple

import unittest

from package.models import Version

from crichtonweb.core.models import crichtonModel
from crichtonweb.core.widgets import ReadOnlySelect, ReadOnlySelectMultiple

class crichtonTestCase(TestCase):
    def run_std_tsts(self, thing, test_admin=True):
        
        self.assertTrue(isinstance(thing, crichtonModel))
        
        if thing.has_api:
            # check that we can get at it through the REST API endpoint
            response = self.client.get(thing.get_api_url("xml"))
            self.assertEqual(response.status_code, 200)
            
        # Check it has the other standard methods and they are callable
        thing.get_link()
        thing.get_absolute_url()
        thing.get_view_url()
        
        if test_admin:
            #  create user
            from django.contrib.auth.models import User
            USERNAME = 'testuser'
            USEREMAIL = 'test@user.com'
            USERPW = 'testpw'
            
            if not User.objects.filter(username=USERNAME).exists():
                User.objects.create_superuser(USERNAME, USEREMAIL, USERPW)
            
            HTTP_SSLCLIENTCERTSUBJECT="Email=%s, CN=%s," % (USEREMAIL, USERNAME)
            
            # login
            c = Client()
            # SOCOM-160 this bit doesn't work:
            # c.login(username=USERNAME, password=USERPW)
            
            # and the Admin interface
            response = c.get(thing.get_absolute_url(), HTTP_SSLCLIENTCERTSUBJECT=HTTP_SSLCLIENTCERTSUBJECT)
            #self.assertEqual(response.content, "XX")
            self.assertEqual(response.status_code, 200)

class CoreWidgetsTest(crichtonTestCase):
    def test_readonlyselect_widget(self):
        choices = (("key1","val1"), ("key2","val2"),("key3","val3"))
        widg = ReadOnlySelect(Select(choices=choices))
        # Single choice (regular select widget)
        output = widg.render(name="testname", value="key2")
        self.assertEqual(output, u'<input type="hidden" value="key2"  name="testname" />\n<input type="text" value="val2"  readonly="readonly" name="testname_readonlyselectlabel" id="testname_readonlyselectlabel" />')
        # Multiple choices:
        multiwidg = ReadOnlySelectMultiple(SelectMultiple(choices=choices))
        output = multiwidg.render(name="testname", value=("key2", "key3"))
        self.assertEqual(output, u'<input type="hidden" value="key2"  name="testname" />\n<input type="hidden" value="key3"  name="testname" />\n<input type="text" value="val2, val3"  readonly="readonly" name="testname_readonlyselectlabel" id="testname_readonlyselectlabel" />')

# eof
