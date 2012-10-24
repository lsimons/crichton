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
import sys
from optparse import make_option

from django.core.management.base import CommandError
from django.core.exceptions import ValidationError

from crichtoncli.apihelpers import *
from crichtoncli.commands import ApiCommand

from crichtonweb.requirement.puppet import update_puppet_svn

import logging
logger = logging.getLogger(__name__)

class Command(ApiCommand):
    help = ("Updates a puppet config with roles, pools, nodes.")

    option_list = ApiCommand.option_list + (
        # todo replace with what simon is doing for this stuff
        make_option("--repo", action="store",
            default="https://repo.domain.comtools/crichton/trunk/puppet-editor/example1",
            help="Provide the SVN repository URL where the puppet config is stored."
                " Defaults to https://repo.domain.comtools/crichton/trunk/puppet-editor/example1."),
        make_option("-y", action="store_true",
            default=False,
            help="Do not prompt for any comformation."),
    )

    # uses database!
    requires_model_validation = True
    
    def print_help(self, issue):
        super(ApiCommand, self).print_help(issue)
    
    def handle(self, *args, **options):
        svnurl = options.get("repo")
        confirm = not options.get("y", False)
        
        if confirm:
            def confirmer():
                try:
                    cmd = raw_input("Press enter to commit changes or CTRL+C to exit...")
                except KeyboardInterrupt:
                    logger.info("...exiting on user request.")
                    print
                    sys.exit(1)
                logger.info("committing...")
        else:
            def confirmer():
                pass
        
        logger.info("")
        logger.info("Modifying puppet config in svn at")
        logger.info("  %s", svnurl)
        
        update_puppet_svn(svnurl, confirmer=confirmer, logger=logger.info)

