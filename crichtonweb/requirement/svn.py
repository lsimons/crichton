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
import os
from subprocess import call

from django.core.management.base import CommandError

def checkout(basedir, svnurl, targetname, logger=None):
    cmd = ["svn", "co", "-q", svnurl, targetname]
    if logger: logger("+ " + " ".join(cmd))
    retcode = call(cmd, cwd=basedir)
    if retcode:
        raise CommandError("Cannot check out %s" % repo)

def diff(workingcopydir, logger=None):
    cmd = ["svn", "diff"]
    if logger: logger("+ " + " ".join(cmd))
    retcode = call(cmd, cwd=workingcopydir)
    
    if retcode:
        raise CommandError("Failure running svn diff on %s" % (workingcopydir,))

def commit(workingcopydir, message, logger=None):
    commit_dir = os.path.dirname(workingcopydir)
    commit_log = os.path.join(commit_dir, "commit-log")
    f = open(commit_log, 'w')
    f.write(message)
    f.close()
    
    cmd = ["svn", "commit", "-F", commit_log]
    if logger: logger("+ " + " ".join(cmd))
    retcode = call(cmd, cwd=workingcopydir)
    if retcode:
        raise CommandError("Error occurred committing change")
    
def ensure_svn_dir(dirname, logger=None):
    cwd = os.path.dirname(dirname)
    basename = os.path.basename(dirname)
    if not os.path.exists(dirname):
        cmd = ["svn", "mkdir", "-q", basename]
        if logger: logger("+ " + " ".join(cmd))
        retcode = call(cmd, cwd=cwd)
        if retcode:
            raise CommandError("Cannot svn mkdir %s" % dirname)
    # else:
    #     retcode = call(["svn", "add", "-N", basename], cwd=cwd)
    #     if retcode:
    #         raise CommandError("Cannot svn add %s" % dirname)

def ensure_svn_file(fname, logger=None):
    if not os.path.exists(fname):
        f = open(fname, 'w')
        f.write('\n')
        f.close()
        cwd = os.path.dirname(fname)
        basename = os.path.basename(fname)
        cmd = ["svn", "add", "-q", basename]
        if logger: logger("+ " + " ".join(cmd))
        retcode = call(cmd, cwd=cwd)
        if retcode:
            raise CommandError("Cannot svn add %s" % fname)

