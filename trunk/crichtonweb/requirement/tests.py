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
from crichtonweb.package.models import Version
from crichtonweb.requirement.models import *
from crichtonweb.package.tests import create_tst_version
from crichtonweb.package.tests import create_tst_packagename
from crichtonweb.prodmgmt.tests import create_tst_application
from crichtonweb.system.tests import create_tst_environment

def create_tst_versionspecification():
    version = create_tst_version()
    vr = create_tst_versionrange()
    me = VersionSpecification(version=version, version_range=vr)
    me.save()
    return me

def create_tst_packagespecification():
    pn = create_tst_packagename()
    vs = create_tst_versionspecification()
    ps = PackageSpecification(package=pn, version_specification=vs)
    ps.save()
    return ps

def create_tst_versionrange():
    x = randint(0,100)
    a = create_tst_version()
    b = create_tst_version()
    minimum = min(a, b)
    maximum = max(a, b)
    me = VersionRange(name="name_%s" % x, minimum=minimum, maximum=maximum)
    me.save()
    return me

def create_tst_requirement():
    app = create_tst_application()
    ps = create_tst_packagespecification()
    me = Requirement(application=app, default_specification=ps)
    me.save()
    return me

def create_tst_environmentrequirement():
    ps = create_tst_packagespecification()
    env = create_tst_environment()
    req = create_tst_requirement()
    me = EnvironmentRequirement(specification=ps, environment=env, requirement=req)
    me.save()
    return me

class RequirementTestCase(crichtonTestCase):
    def test_create_packagespecification(self):
        me = create_tst_packagespecification()
        self.run_std_tsts(me)
        me.delete()
        
    def test_create_versionrange(self):
        me = create_tst_versionrange()
        self.assertTrue(isinstance(me, crichtonModel))
        self.run_std_tsts(me)
        me.delete()
        
    def test_create_versionspecification(self):
        me = create_tst_versionspecification()
        self.assertTrue(issubclass(VersionSpecification, crichtonModel))
        self.run_std_tsts(me)
        me.delete()
        
    def test_create_requirement(self):
        me = create_tst_requirement()
        self.run_std_tsts(me)
        me.delete()
        
    def test_create_environmentrequirement(self):
        me = create_tst_environmentrequirement()
        self.run_std_tsts(me)
        me.delete()

class VersionRangeParserTestCase(crichtonTestCase):

    def versionrangetester(self,
            name,
            minimum=None,
            minimum_is_inclusive=None,
            maximum=None,
            maximum_is_inclusive=None):
        vr = VersionRange.from_string(name)
        self.assertEqual(vr.name, name)
        self.assertEqual(vr.minimum, minimum)
        self.assertEqual(vr.minimum_is_inclusive, minimum_is_inclusive)
        self.assertEqual(vr.maximum, maximum)
        self.assertEqual(vr.maximum_is_inclusive, maximum_is_inclusive)
    
    def test_basic_ranges(self):
        self.versionrangetester("[1,2]",
            Version.from_string("1"),
            True,
            Version.from_string("2"),
            True)
        self.versionrangetester("(1,2]",
            Version.from_string("1"),
            False,
            Version.from_string("2"),
            True)
        self.versionrangetester("[1,2)",
            Version.from_string("1"),
            True,
            Version.from_string("2"),
            False)
        self.versionrangetester("(1,2)",
            Version.from_string("1"),
            False,
            Version.from_string("2"),
            False)
        self.versionrangetester("[1.0.1-abc,2.0.3-def_123456_dwaaaaaa]",
            Version.from_string("1.0.1-abc"),
            True,
            Version.from_string("2.0.3-def_123456_dwaaaaaa"),
            True)
    
    def test_very_weird_but_parseable_stuff(self):
        self.versionrangetester("[[[1,[[2]",
            Version.from_string("[[1"),
            True,
            Version.from_string("[[2"),
            True)
        self.versionrangetester("[1,,,,2]",
            Version.from_string("1"),
            True,
            Version.from_string(",,,2"),
            True)
        self.versionrangetester("[1,2,,,]",
            Version.from_string("1"),
            True,
            Version.from_string("2,,,"),
            True)

    def test_exceptions_for_unparsable_stuff(self):
        try:
            self.versionrangetester("[]")
            fail("Expected exception")
        except:
            pass
        try:
            self.versionrangetester("[,]")
            fail("Expected exception")
        except:
            pass
        try:
            self.versionrangetester("[1,2")
            fail("Expected exception")
        except:
            pass
        try:
            self.versionrangetester("1,2]")
            fail("Expected exception")
        except:
            pass
        try:
            self.versionrangetester("[12]")
            fail("Expected exception")
        except:
            pass

# eof
