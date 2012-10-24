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
from optparse import make_option

from django.core.management.base import CommandError
from django.utils import simplejson

from crichtoncli.commands import ApiCommand
from crichtoncli.commands.common import print_table
from crichtoncli.apihelpers import *

from crichtonweb.release.models import DeploymentRequest
from crichtonweb.package.models import PackageLocation
from crichtonweb.system.models import Environment

import logging
logger = logging.getLogger(__name__)

def print_env_help():
    print
    print "Available environments:"
    for env in Environment.objects.all():
        print " ", env.name

def _get_pending_packages(env_name):
    try:
        env = Environment.objects.get_by_natural_key(env_name)
    except Environment.DoesNotExist:
        logger.error("Need a recognised environment: options are %s", ", ".join([str(x) for x in Environment.objects.all()]))
        return []


    if not env.repositories.count():
        logger.error("Environment '%s' needs at least one repository to be configured in order to use this command", env)
        return []
    
    depreqs = []
    for depreq in DeploymentRequest.objects.filter(environment=env):
        repos = []
        for repo in env.repositories.all():
            packages = []
            for elem in depreq.release.elements.all():
                # if the rpm corresponding to the package name/version does not exist on the target repo,
                # then list it
                try:
                    pl = PackageLocation.objects.get_by_natural_key(elem.package.name, elem.package.version, repo.name)
                except PackageLocation.DoesNotExist:
                    packages.append(elem.package.to_json())
            if packages:
                repos.append({"name": repo.name, "packages": packages})
        if not repos:
            continue

        # only show release info if there's some related pending info to show
        release = {
            "product": {"name": depreq.release.product.name},
            "version": depreq.release.version,
            "repositories": repos,
            }
        depreqs.append({ "ops_issue": depreq.ops_issue, "release": release })
    return depreqs

class Command(ApiCommand):
    help = ("Lists all packages for all outstanding deployment requests that need to be copied into the target repo.")
    args = "<env>"

    option_list = ApiCommand.option_list + (
        make_option("--json", action="store_true", dest="json",
            default=False, help="Produce raw json rather than "
                "formatted text. Default:False"),
    )

    # uses database!
    requires_model_validation = True
    
    def print_help(self, prog_name, subcommand):
        super(ApiCommand, self).print_help(prog_name, subcommand)
        print_env_help()
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("You must provide an env e.g. stage")
        
        env = args[0]
        
        # uses db to get current package locations.
        # for completely up-to-date information, could query repos directly.
        
        pendings = _get_pending_packages(env)

        if options["json"]:
            body = simplejson.dumps(pendings, indent=4)
            print body.encode("UTF-8")
            return
        
        if not pendings:
            print "No pending packages"
            return
        
        table = []
        table.append(["release", "deployment request", "repository", "packages"])
        for pending in pendings:
            release = pending["release"]
            for repo in release["repositories"]:
                table.append(["%s %s" % (release["product"]["name"], release["version"]),
                              pending["ops_issue"], repo["name"],
                              "%s %s" % (repo["packages"][0]["name"], repo["packages"][0]["version"])])
                for package in repo["packages"][1:]:
                    table.append(["", "", "", "%s %s" % (package["name"], package["version"])])

        print_table(table)
            
# eof
