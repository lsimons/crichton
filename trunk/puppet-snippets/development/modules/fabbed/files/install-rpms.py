#!/usr/bin/env /usr/bin/python
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

# ensure-rpms.py
#
# Script for remotely managing rpm versions.
# Takes a list of rpms and tries to install those exact versions, rolling some of them
# back if needed. Can be called with a -d option to do a dry run.
#

import optparse
import re
import rpm
import subprocess
import sys

# Use the variable below to filter allowed RPMs
ALLOWED_RPM_REGEX = "^(bbc)"

# Constants
SUCCESS = 0
ERROR_BAD_RPMNAME = 1
ERROR_UNINSTALL_FAILED = 1


def split_rpm(rpm_name):
    """Splits rpm into name, version & release strings, returning all"""
    rpm_basename = ''
    rpm_ver = ''
    rpm_rel = ''

    # rpmname-$version-$release
    dash2 = rpm_name.rfind("-")
    dash1 = rpm_name.rfind("-", 0, dash2)
    if dash1 == -1 or dash2 == -1:
        print "ERROR: Badly formatted rpm name " + rpm_name + ", YOU SHALL NOT PARSE."
        sys.exit(ERROR_BAD_RPMNAME)
    rpm_basename = rpm_name[0:dash1]
    rpm_ver  = rpm_name[dash1+1:dash2]
    rpm_rel  = rpm_name[dash2+1:]

    return rpm_basename, rpm_ver, rpm_rel

def get_current_installed_rpm_EVR(rpm_basename):
    """Queries system to find current installed rpm details.
    
    Returns name, version & release.
    Returns blank strings if not installed.

    """
    return_ver = ''
    ts = rpm.TransactionSet()
    matcher = ts.dbMatch( 'name', rpm_basename )
    for header in matcher:
        if header['name'] == rpm_basename:
            return header['name'], header['version'], header['release']
    return "", "", ""

def ensure_rpm_list_present(orig_rpm_list, dry_run = False):
    """Takes a list of rpms and ensures that those exact versions are installed."""
    todo_nothing = []
    todo_install = []
    todo_update = []
    todo_revert = []

    for rpm_name in orig_rpm_list:
        rpm_basename, rpm_ver, rpm_rel = split_rpm(rpm_name)
        (current_basename, current_ver, current_rel) = get_current_installed_rpm_EVR(rpm_basename)
        if current_ver == "":
            todo_install.append(rpm_name)
        else:
            rpm_comparison = rpm.labelCompare((rpm_basename, rpm_ver, rpm_rel), (current_basename, current_ver, current_rel))
            if rpm_comparison == 0:
                # No change
                todo_nothing.append(rpm_name)
            elif rpm_comparison == 1:
                todo_update.append(rpm_name)
            else:
                todo_revert.append(rpm_name)

    if dry_run:
        print "DRY RUN"
    # Always print skips
    for rpm_name in todo_nothing: print "Skipping, already installed: " + rpm_name
    if dry_run:
        for rpm_name in todo_install: print "Installing new: " + rpm_name
        for rpm_name in todo_update:  print "Updating version: " + rpm_name
        for rpm_name in todo_revert:  print "Rolling back: " + rpm_name
    else:
        # Updating rpms for real
        # Sequence of events is as follows:
        # a) rpm -e any rpms that we are rolling back first
        # b) install any rolled back rpms
        # c) update any existing rpms
        # d) install new rpms
        if len(todo_revert) > 0:
            todo_revert_namesonly = []
            for rpm_name in todo_revert:
                rpm_basename, rpm_ver, rpm_rel = split_rpm(rpm_name)
                todo_revert_namesonly.append(rpm_basename)
            retcode, stdout, stderr = do_shell_cmd( ["/bin/rpm", "-e", "--nodeps", str.join(" ", todo_revert_namesonly)] )
            if retcode != 0:
                print "Aborting..."
                sys.exit(ERROR_UNINSTALL_FAILED)
            do_yum("install", todo_revert)
        if len(todo_install) > 0:
            do_yum("install", todo_install)
        if len(todo_update) > 0:
            do_yum("update", todo_update)

    return 0

def do_shell_cmd(args):
    """Runs the specified shell command with sudo privileges.

    Inputs: array of arguments as you'd pass to subprocess.Popen

    Returns return_code, stdout, stderr

    """
    print "Running: " + str.join(" ", args) + "..."
    exec_args = ["sudo"]
    exec_args.extend(args)
    proc = subprocess.Popen(exec_args, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    (stdout, stderr) = proc.communicate()
    retcode = proc.returncode
    if retcode != 0:
        print "ERROR: Non-zero return code. STDERR follows:"
        print stderr
    return retcode, stdout, stderr

def do_yum(command, rpm_list):
    """Run yum with specified command, returns non-zero on error"""
    shell_cmd_array = ["/usr/bin/yum", command, "-y"]
    shell_cmd_array.extend( rpm_list )
    retcode, stdout, stderr = do_shell_cmd( shell_cmd_array )
    if retcode == 0:
        # Grep for missing rpms
        missing_rpms = re.findall("No package [\w\.]+ available", stdout)
        if len(missing_rpms) > 0:
            for missing_rpm in missing_rpms:
                print "ERROR: No such rpm " + missing_rpm[11:-10]
            return 1
        else:
            print stdout
    return 0

def main():
    # Get options
    #
    parser = optparse.OptionParser("%prog [--dry] [--uninstall] space-separated-rpm-list")
    parser.add_option("-d", "--dry", action="store_true", dest="dry_run", default=False, help="Perform a dry run")
    parser.add_option("-u", "--uninstall", action="store_true", dest="uninstall", default=False, help="Uninstall the listed rpms")

    (opts, args) = parser.parse_args()

    if len(args) < 1:
        print "ERROR: no rpms specified"
        return 1

    # Format arg list into rpm list minus the .noarch.rpm, etc.
    # At the same time, make sure we only work with allowed rpms
    orig_rpm_list = []
    for arg in args:
        rpm_name = re.sub('\.(noarch|i386|i686|x86_64)\.rpm$', '', arg)
        if re.match( ALLOWED_RPM_REGEX, rpm_name ) == None:
            print "ERROR, rpm " + rpm_name + " not in allowed list for this script."
            return 1
        else:
            orig_rpm_list.append(rpm_name)

    return ensure_rpm_list_present(orig_rpm_list, opts.dry_run)

if __name__ == "__main__":
    sys.exit(main())

