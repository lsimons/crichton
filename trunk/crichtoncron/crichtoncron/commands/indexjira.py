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
    cert_file = conf.get("crichtoncron", "cert_file")
    key_file = conf.get("crichtoncron", "key_file")
    ca_file = conf.get("crichtoncron", "ca_file")
    crichtonclicommand = conf.get("crichtoncron", "crichtonclicommand")
    cmd = [
        crichtonclicommand,
        "indexjiraproject",
        "--cert-file=" + cert_file,
        "--key-file=" + key_file,
        "--ca-file=" + ca_file,
    ]
    
    projects = []
    
    # parse config first so we don't do anything until we read the entire config
    for section in [x for x in conf.sections() if x.startswith("indexjiraproject")]:
        jiraname = conf.get(section, "jiraname")
        jirabaseurl = conf.get(section, "jirabaseurl")
        projectname = conf.get(section, "projectname")
        projects.append((jiraname, jirabaseurl, projectname))
    
    # record problems rather than raise exceptions immediately, so other indexes may succeed
    problem_occurred = False
    problems = []
    
    for jiraname, jirabaseurl, projectname in projects:
        jiracmd = cmd + [jiraname, jirabaseurl, projectname]
        logger.info("Running '%s'" % " ".join(jiracmd))
        status, stdout, stderr = callproc(jiracmd)
        logger.info(stdout)
        if status != 0:
            problem_occurred = True
            problems.append("Problem running '%s', exit status %d" % (" ".join(jiracmd), status))
            if stderr != "":
                logger.error("STDERR from process '%s' follows:\n%s" % (" ".join(jiracmd), stderr))
    
    if problem_occurred:
        if len(problems) == 0:
            raise Exception(problems[0])
        else:
            raise Exception("\n".join(problems))
