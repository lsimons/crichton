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
# to run locally you need ttail. See tools/crichton/vendor/README.txt for instructions
from optparse import make_option
import multiprocessing
from subprocess import Popen, PIPE
import datetime
import time
import random
import sys

from django.core.management.base import CommandError
from django.db import close_connection

from crichtoncli.commands import ApiCommand
from crichtoncli.forker import run_all

from crichtonweb.system.models import Node, PackageInstallation
from crichtonweb.package.models import Package, PackageName, Version
from crichtonweb.system.models import crichtonCronJobStatus

import logging
logger = logging.getLogger(__name__)

class Command(ApiCommand):
    help = ("Tries to fetch rpm logs from all known nodes in an environment.")
    args = "<environment>"
    
    ttail_cmd = "ttail --cert=/etc/teleportd.pem --ca-cert=/etc/dev-services-chain.pem " +\
            "-t 3 -c +0 " +\
            "-h %(hostname)s:1235 " +\
            "/device-%(hostname)s-log/rpmlog"

    option_list = ApiCommand.option_list + (
        make_option("--keep-missing", action="store_true", dest="keep_missing",
            default=False, help="Do not take missing RPMs as a sign that they are uninstalled."),
        make_option("--concurrency", action="store", dest="numworkers",
            default=8,
            help="Number of nodes to query in parallel. "
                " Defaults to 8."),
        make_option("--ttail", action="store", dest="ttail",
            help="Specify custom ttail command to use.",
            default=ttail_cmd)
    )
    
    
    # uses database!
    requires_model_validation = True
    
    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError("You must provide environment")
        environment = args[0]

        ttail_cmd = options.get("ttail")
        keep_missing = options.get("keep_missing")
        numworkers = int(options.get("numworkers", '1'))
        
        def do_work(nodename, ttail_cmd):
            time.sleep(0.1 + random.random()/5)
            close_connection()
            
            node = Node.objects.get(name=nodename)
            nodename = node.name.split(".")[0]
            logger.info("indexing %s", nodename)
            cmd = ttail_cmd % {"hostname": nodename}
            logger.debug("Executing commmand '%s'", cmd)
            cmdlist = cmd.split(" ")
            p = Popen(cmdlist, stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = p.communicate()
            if p.returncode != 0:
                logger.error("  '%s' returned %d, ignoring", cmd, p.returncode)
                if stderr != "":
                    logger.error(stderr)
                return
            stdout = stdout.strip()
            if stdout == "":
                logger.error("'%s' returned empty result, ignoring", cmd)
                if stderr != "":
                    logger.error(stderr)
                return
            
            now = datetime.datetime.now()
            
            packages_seen = []
            for line in stdout.splitlines()[2:]:
                # format of line is unfortunately %{NAME}-%{VERSION}-%{RELEASE}.%{ARCH}.rpm
                
                # strip .%{ARCH}.rpm, depends on ARCH not containing .
                package_detail = ".".join(line.split(".")[:-2])
                
                # split by "-"
                package_info = package_detail.split("-")
                
                # pop off -%{RELEASE}, depends on RELEASE not containing -
                release = package_info.pop()
                
                # pop off -%{VERSION}, depends on VERSION not containing -
                version = package_info.pop()
                
                # what remains is the package name (that may have - in it)
                name = "-".join(package_info)
                
                version_obj, created = Version.objects.ensure_from_rpm(version, release)
                package_name, created = PackageName.objects.ensure(name)
                if created:
                    logger.info("  We had not seen package name %s before", name)
                package, created = Package.objects.ensure(name, version_obj)
                if created:
                    logger.info("  We had not seen package %s before", package_detail)
                packages_seen.append(package)
                package_installation, created = PackageInstallation.objects.ensure(package, node, seen_at=now)
                if created:
                    logger.info("  We had not seen package %s before on %s", package_detail, node.name)
                
            if not keep_missing:
                updated = PackageInstallation.objects.update_not_seen(node, packages_seen, not_seen_at=now)
                if updated > 0:
                    logger.info("  Did not see %d packages", updated)
            sys.exit(0)
        
        def make_process(nodename):
            return multiprocessing.Process(target=do_work, args=[nodename, ttail_cmd])
        workers = [make_process(nodename) for nodename in \
                Node.objects.filter(deleted=False, environment__name=environment).values_list('name', flat=True)]

        run_all(workers, numworkers)

        crichtonCronJobStatus.objects.update_success('index_rpm')
