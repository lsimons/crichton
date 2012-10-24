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
from random import randint
from crichtonweb.core.tests import crichtonTestCase
import crichtonweb.prodmgmt.models as prodmgmt
from crichtonweb.issue.tests import create_tst_issue

def create_tst_person():
    x = randint(0,100)
    myperson = prodmgmt.Person(username="person %s" % x)
    myperson.save()
    return myperson

def create_tst_product():
    x = randint(0,100)
        
    myperson = create_tst_person()
    myissue = create_tst_issue()
    
    myproduct = prodmgmt.Product(name="product_%s" % x, display_name="My Product %s" % x,
                                 owner=myperson, pipeline_issue=myissue)
    myproduct.save()

    return myproduct
    
def create_tst_application():
    myproduct = create_tst_product()
        
    myapplication = prodmgmt.Application(name="application", display_name="My Application", product=myproduct)
    myapplication.save()

    return myapplication

class ProdMgmtTestCase(crichtonTestCase):
    def test_create_application(self):
        myapplication = create_tst_application()
        self.run_std_tsts(myapplication)
        myapplication.delete()
        
    def test_create_person(self):
        myperson = create_tst_person()
        self.run_std_tsts(myperson)
        myperson.delete()

    def test_create_product(self):
        myproduct = create_tst_product()
        self.run_std_tsts(myproduct)
        myproduct.delete()

# eof
