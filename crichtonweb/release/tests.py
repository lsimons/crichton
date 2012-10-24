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
#from django.test import TestCase
from crichtonweb.core.tests import crichtonTestCase
from crichtonweb.prodmgmt.models import Product
import crichtonweb.release.models as release

from crichtonweb.prodmgmt.tests import create_tst_product
from crichtonweb.system.tests import create_tst_environment
from crichtonweb.issue.tests import create_tst_issue

def create_tst_release():
    myproduct = create_tst_product()

    myrelease = release.Release(product=myproduct, release_order=1, version="Test Version")
    myrelease.save()

    return myrelease

def create_tst_deployment_request():
    myrelease = create_tst_release()
    myenv = create_tst_environment()
    myissue = create_tst_issue()
    mydr = release.DeploymentRequest(release=myrelease, environment=myenv, ops_issue=myissue)
    mydr.save()
    return mydr
    
class ReleaseTestCase(crichtonTestCase):
    def test_create_release(self):
        myrelease = create_tst_release()
        self.run_std_tsts(myrelease)
        myrelease.delete()

class DeploymentRequestTestCase(crichtonTestCase):
    def test_create_deployment_request(self):
        mydr = create_tst_deployment_request()
        self.run_std_tsts(mydr, test_admin=False)
        mydr.delete()

# eof
