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
from crichtoncron import conf, callproc
from crichtonweb.system.logging import cron_log as logger

def run():
    crichtonclicommand = conf.get("crichtoncron", "crichtonclicommand")
    cmd = [
        crichtonclicommand,
        "indexrpm"
    ]
    
    environments = []
    
    # parse config first so we don't do anything until we read the entire config
    for section in [x for x in conf.sections() if x.startswith("indexrpm")]:
        environment = conf.get(section, "environment")
        environments.append(environment)
    
    # record problems rather than raise exceptions immediately, so other indexes may succeed
    problem_occurred = False
    problems = []
    
    for environment in environments:
        indexrpmcmd = cmd + [environment]
        logger.info("Running '%s'" % " ".join(indexrpmcmd))
        status, stdout, stderr = callproc(indexrpmcmd)
        logger.info(stdout)
        if status != 0:
            problem_occurred = True
            problems.append("Problem running '%s', exit status %d" % (" ".join(indexrpmcmd), status))
            if stderr != "":
                logger.error("STDERR from process '%s' follows:\n%s" % (" ".join(indexrpmcmd), stderr))
    
    if problem_occurred:
        if len(problems) == 0:
            raise Exception(problems[0])
        else:
            raise Exception("\n".join(problems))
