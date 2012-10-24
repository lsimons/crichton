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

from crichtoncli.commands import ApiCommand

from crichtonweb.requirement.actions import apply_request

import logging
logger = logging.getLogger(__name__)

class Command(ApiCommand):
    help = ("Takes a release request by issue, and updates the puppet config from it.")
    args = "<issue>"

    option_list = ApiCommand.option_list + (
        make_option("-y", action="store_true",
            default=False,
            help="Do not prompt for any comformation."),
    )

    # uses database!
    requires_model_validation = True
    
    def print_help(self, issue):
        super(ApiCommand, self).print_help(issue)
    
    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError("You must provide at least issue")
        
        confirm = not options.get("y", False)
        issue_name = args[0]
        
        def informer(issue, environment, release, packages):
            logger.info("")
            logger.info(("Processing deployment request for issue %s: %s" % (issue.name, issue.summary)).encode("UTF-8"))
            logger.info(("    targeting environment %s" % environment).encode("UTF-8"))
            logger.info(("    release %s of product %s" % (release.version, release.product.name)).encode("UTF-8"))

            for package in packages:
                logger.info(("      release element: %s" % package).encode("UTF-8"))
            print
        
        if confirm:
            def confirmer():
                try:
                    cmd = raw_input("Press enter to commit changes or CTRL+C to exit...")
                except KeyboardInterrupt:
                    logger.info("...exiting on user request.")
                    sys.exit(1)
                logger.info("committing...")
        else:
            def confirmer():
                pass
        
        apply_request(issue_name, confirmer=confirmer, informer=informer, logger=logger.info)

