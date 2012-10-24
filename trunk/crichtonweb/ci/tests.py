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
import logging

from crichtonweb.core.tests import crichtonTestCase
from crichtonweb.ci.models import BuildServer, BuildJob, BuildResult
from crichtonweb.package.tests import create_tst_package
from crichtonweb.prodmgmt.tests import create_tst_product

#
# Generators
#
def _gen_build_num():
    num = 0
    while True:
        yield num
        num += 1
gen_build_num = _gen_build_num()

def _gen_buildserver_num():
    num = 0
    while True:
        yield num
        num += 1
gen_buildserver_num = _gen_buildserver_num()

def _gen_buildjob_name():
    num = 0
    while True:
        yield "build_job_%s" % num
        num += 1
gen_buildjob_name = _gen_buildjob_name()

def _gen_buildserver():
    while True:
        num = gen_buildserver_num.next()
        logging.error("gen_test_buildserver: num=%s" % num)
        buildserver = BuildServer(name="buildserver_%s" % num, display_name="My BuildServer %s" % num)
        buildserver.save()
        yield buildserver
gen_buildserver = _gen_buildserver()        
    
def _gen_buildjob():
    while True:
        mybuildserver = gen_buildserver.next()
        myproduct = create_tst_product()
        name = gen_buildjob_name.next()
        mybuildjob = BuildJob(name=name, build_server=mybuildserver,
                              product = myproduct)
        mybuildjob.save()
        yield mybuildjob
gen_buildjob = _gen_buildjob()

def _gen_buildresult():
    while True:
        mybuildjob = gen_buildjob.next()
        mypackage = create_tst_package()
        build_number = gen_build_num.next()
        build_result = BuildResult(build_number=build_number, job=mybuildjob, produced_package=mypackage)
        build_result.save()
        yield build_result
gen_buildresult = _gen_buildresult()

#
# The Tests
#

class CiTestCase(crichtonTestCase):
    def test_buildserver(self):
        mybuildserver = gen_buildserver.next()
        self.run_std_tsts(mybuildserver)
        mybuildserver.delete()
        
    def test_buildjob(self):
        mybuildjob = gen_buildjob.next()
        self.run_std_tsts(mybuildjob)
        mybuildjob.delete()

    def test_buildresult(self):
        mybuildresult = gen_buildresult.next()
        self.run_std_tsts(mybuildresult)
        mybuildresult.delete()
        
# eof
