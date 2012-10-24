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
        "indexhudson",
        "--cert-file=" + cert_file,
        "--key-file=" + key_file,
        "--ca-file=" + ca_file,
        "--concurrency=4",
        "--detect-deploy",
    ]

    hudsons = {}

    # parse config first so we don't do anything until we read the entire config
    for section in [x for x in conf.sections() if x.startswith("indexhudson")]:
        servername = conf.get(section, "servername")
        serverbaseurl = conf.get(section, "serverbaseurl")
        hudsons[servername] = serverbaseurl

    # record problems rather than raise exceptions immediately, so other indexes may succeed
    problem_occurred = False
    problems = []

    for servername, serverbaseurl in hudsons.iteritems():
        hudsoncmd = cmd + [servername, serverbaseurl]
        logger.info("Running '%s'" % " ".join(hudsoncmd))
        status, stdout, stderr = callproc(hudsoncmd)
        if status != 0:
            problem_occurred = True
            problems.append("Problem running '%s', exit status %d" % (" ".join(hudsoncmd), status))
            if stderr != "":
                logger.error("STDERR from process '%s' follows:\n%s" % (" ".join(hudsoncmd), stderr))

    if problem_occurred:
        if len(problems) == 0:
            raise Exception(problems[0])
        else:
            raise Exception("\n".join(problems))
