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
import crichtonweb.package.models as package

def create_tst_version():
    x = randint(0,100)
    myversion = package.Version(name="version_%s" % x, major=1)
    myversion.save()
    return myversion
    
def create_tst_package():
    x = randint(0,100)
    myversion = create_tst_version()
    mypackage = package.Package(name="package_%x" % x, version=myversion)
    mypackage.save()
    return mypackage

def create_tst_packagename():
    x = randint(0,100)
    mypn = package.PackageName(name="packagename_%s" % x)
    mypn.save()
    return mypn

def create_tst_packagerepository():
    x = randint(0,100)
    me = package.PackageRepository(name="packagerepositoryname_%s" % x)
    me.save()
    return me

def create_tst_packagelocation():
    x = randint(0,100)
    me = package.PackageLocation(package=create_tst_package(), repository=create_tst_packagerepository())
    me.save()
    return me

class PackageTestCase(crichtonTestCase):
    def test_create_version(self):
        me = create_tst_version()
        self.run_std_tsts(me)
        self.assertRaises(Exception, me.delete)
        
    def test_create_package(self):
        me = create_tst_package()
        self.run_std_tsts(me)
        me.delete()
        
    def test_create_packagename(self):
        me = create_tst_packagename()
        self.run_std_tsts(me)
        self.assertRaises(Exception, me.delete)

    def test_create_packagerepository(self):
        me = create_tst_packagerepository()
        self.run_std_tsts(me)
        me.delete()

    def test_create_packagelocation(self):
        me = create_tst_packagelocation()
        self.run_std_tsts(me)
        me.delete()

class VersionParserTestCase(crichtonTestCase):
        
    def versiontester(self,
            name,
            major=None,
            minor=None,
            micro=None,
            revision=None,
            build=None,
            status='release'):
        version = package.Version.from_string(name)
        self.assertEqual(version.name, name)
        self.assertEqual(version.major, major)
        self.assertEqual(version.minor, minor)
        self.assertEqual(version.micro, micro)
        self.assertEqual(version.revision, revision)
        self.assertEqual(version.build, build)
        self.assertEqual(version.status, status)
    
    def test_basic_numbers(self):
        self.versiontester('0.0.1', major=0, minor=0, micro=1)
        self.versiontester('0.1.0', major=0, minor=1, micro=0)
        self.versiontester('1.0.0', major=1, minor=0, micro=0)
        self.versiontester('1.2.0', major=1, minor=2, micro=0)
        self.versiontester('1.2.3', major=1, minor=2, micro=3)
        self.versiontester('0.0.99', major=0, minor=0, micro=99)
        self.versiontester('9999999.0.0', major=9999999, minor=0, micro=0)
        self.versiontester('0.0.001', major=0, minor=0, micro=1)
        self.versiontester('3.0007', major=3, minor=7)
    
    def test_typical_forge_style_numbers(self):
        self.versiontester('0.0.1-32451.12', major=0, minor=0, micro=1,
                revision=32451, build=12)
        self.versiontester('0.1.0-43895.117', major=0, minor=1, micro=0,
                revision=43895, build=117)
        self.versiontester('1.0.0-65432.129', major=1, minor=0, micro=0,
                revision=65432, build=129)
    
    def test_snapshot(self):
        self.versiontester('0.0.1-32451.12-SNAPSHOT', major=0, minor=0, micro=1,
                revision=32451, build=12, status='snapshot')
        self.versiontester('0.1.0-SNAPSHOT', major=0, minor=1, micro=0,
                status='snapshot')
        self.versiontester('snapshot:1.0.0', major=1, minor=0, micro=0,
                status='snapshot')
    
    def test_php_examples(self):
        self.versiontester('trunk-dev',
                status='snapshot')
        self.versiontester('5.2-dev', major=5, minor=2,
                status='snapshot')
        self.versiontester('5.2.14', major=5, minor=2, micro=14)
        self.versiontester('4.2.1', major=4, minor=2, micro=1)
        self.versiontester('0.2a', major=0, minor=2,
                status='release') # decided that looking for 'a' or 'b' is too flakey
        self.versiontester('-1.7.14RC2', major=1, minor=7, micro=14,
                status='RC')

    def test_portability_examples(self):
        self.versiontester('4.3p2', major=4, minor=3) # portable openssh
        self.versiontester('3.9p9', major=3, minor=9) # portable openntpd
        self.versiontester('9.3.6-4.P1', major=9, minor=3, micro=6,
                revision=4) # bind-libs
    
    def test_various_things_found_in_the_wild(self):
        self.versiontester('0.9.8e', major=0, minor=9, micro=8) # openssl
        self.versiontester('095', major=95) # libvolume_id
        self.versiontester('20020927', major=20020927) # iputils
        self.versiontester('24.20060715', major=24, minor=20060715) # ncurses
        self.versiontester('37017186-45761324', major=37017186, minor=45761324) # gpg-pubkey
        self.versiontester('1.0.0b3', major=1, minor=0, micro=0,
                status='release') # udftools
        self.versiontester('5Server-31', major=5, minor=31) # redhat-release-notes
        self.versiontester('1.95.8-8.3.el5_4.2', major=1, minor=95, micro=8,
                revision=8, build=3) # expat
    
    def test_if_you_add_redhat_release_info_in_version(self):
        # what you should feed in as the version here is 0.4.20,
        #      33.el5_5.2 is the release version
        self.versiontester('0.4.20-33.el5_5.2', major=0, minor=4, micro=20,
                revision=33, build=5)
        # what you should feed in as the version here is 0.0.1_426857.8,
        #      1 is the release version
        self.versiontester('0.0.1_426857.8-1', major=0, minor=0, micro=1,
                revision=426857, build=8)

class RpmVersionParserTestCase(VersionParserTestCase):
    def versiontester(self,
            rpm_version,
            major=None,
            minor=None,
            micro=None,
            revision=None,
            build=None,
            status='release',
            rpm_release=None):
        version = package.Version.from_rpm(rpm_version, rpm_release)
        if rpm_release:
            self.assertEqual(version.name, rpm_version + '-' + rpm_release)
        else:
            self.assertEqual(version.name, rpm_version)
        self.assertEqual(version.major, major)
        self.assertEqual(version.minor, minor)
        self.assertEqual(version.micro, micro)
        self.assertEqual(version.revision, revision)
        self.assertEqual(version.build, build)
        self.assertEqual(version.status, status)
    
    def test_split_forge_numbers(self):
        self.versiontester('0.0.1', rpm_release='32451.12', major=0, minor=0, micro=1,
                revision=32451, build=12)
        self.versiontester('1.1.0', rpm_release='307194.108', major=1, minor=1, micro=0,
                revision=307194, build=108)
        self.versiontester('1.11.3', rpm_release='405640.271', major=1, minor=11, micro=3,
                revision=405640, build=271)
    
    def test_various_things_found_in_the_wild(self):
        self.versiontester('0.9.8e', rpm_release='12.el5_4.6', major=0, minor=9, micro=8,
                revision=12, build=4) # openssl, note el5 stripped
        self.versiontester('1.33.4', rpm_release='5.6.el5_bbc', major=1, minor=33, micro=4,
                revision=5, build=6) # bbc libselinux
        self.versiontester('1.21', rpm_release='1.el5.rf', major=1, minor=21, micro=None,
                revision=1) # perl-Expect
        self.versiontester('1.6.0.20', rpm_release='1jpp.1.el5', major=1, minor=6, micro=0,
                revision=20, build=1) # java-1.6.0-sun
        self.versiontester('1.0.9.1', rpm_release='1.15.el5', major=1, minor=0, micro=9,
                revision=1, build=1) # pacemaker
        self.versiontester('2.4.0.0', rpm_release='bbc', major=2, minor=4, micro=0,
                revision=0) # mod_whatkilledus
        self.versiontester('1.16', rpm_release='115735:115743', major=1, minor=16, micro=None,
                revision=115735, build=115743) # bbc-logfetch-server
        self.versiontester('1.1.0', rpm_release='b1', major=1, minor=1, micro=0,
                status='release') # kv-jmx
        self.versiontester('0.4.0.20091214', rpm_release='106287.41', major=0, minor=4, micro=0,
                revision=106287, build=41) # bbc-htmliplayer
        self.versiontester('F4.0.3.alpha', rpm_release='9a', major=4, minor=0, micro=3,
                revision=9, status='alpha') # tac_plus
        self.versiontester('0.4.0.20091208.1', rpm_release='104106.40', major=0, minor=4, micro=0,
                revision=104106, build=40) # bbc-static-htmliplayer

# eof
