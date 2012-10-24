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
from crichtonweb.issue.models import *

# Just using random numbers to create unique names for the moment.
# Should build a generator instead

def create_tst_tracker():
    x = randint(0,100)
    mytracker = IssueTracker(name="tracker_%s" % x, display_name="My Tracker %s" % x)
    mytracker.save()
    
    return mytracker

def create_tst_issue_tracker_project():
    mytracker = create_tst_tracker()

    x = randint(0,100)
    myitp = IssueTrackerProject(name="project_%s" %x,
                                display_name="My Project %s" % x,
                                issue_tracker=mytracker)
    myitp.save()
    return myitp
    
def create_tst_issue():
    myitp = create_tst_issue_tracker_project()

    x = randint(0,100)
    myissue = Issue(name="issue_%s", project=myitp)
    myissue.save()
    return myissue
    
class IssueTestCase(crichtonTestCase):
    def test_create_tracker(self):
        me = create_tst_tracker()
        self.run_std_tsts(me)
        me.delete()
        
    def test_create_issue_tracker_project(self):
        me = create_tst_issue_tracker_project()
        self.run_std_tsts(me)
        me.delete()
        
    def test_create_issue(self):
        me = create_tst_issue()
        self.run_std_tsts(me)
        me.delete()
        
# eof
