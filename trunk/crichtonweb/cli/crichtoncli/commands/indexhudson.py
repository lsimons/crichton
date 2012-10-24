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
# example of running locally:
#   ./crichton.py indexhudson localdevhudson http://jenkins.sandbox:8080/ --detect-deploy
#
#   ./crichton.py indexhudson hudson-ci-app-int https://ci-app.int.domain.local/hudson/ --detect-deploy \
#       --cert-file=/Users/$USER/.bbc/dev.domain.com.pem \
#       --key-file=/Users/$USER/.bbc/dev.domain.com.key \
#       --ca-file=/Users/$USER/.bbc/ca.pem \
#       --concurrency=4
import sys
import datetime
import time
import random
from optparse import make_option
import multiprocessing
from httplib import IncompleteRead
from urllib import quote

import httplib2

from django.core.management.base import CommandError
from django.utils import simplejson
from django.utils.encoding import iri_to_uri
from django.db import transaction, close_connection

from MySQLdb import IntegrityError, OperationalError

from crichtoncli.commands import ApiCommand
from crichtoncli.apihelpers import *
from crichtoncli.forker import run_all
from crichtonweb.core.httpshelpers import *
from crichtonweb.ci.models import *
from crichtonweb.core.utils import gc_collect, commit_or_rollback, rollback
from crichtonweb.deployment.models import *
from crichtonweb.system.models import crichtonCronJobStatus

import logging
logger = logging.getLogger(__name__)

# should be smaller than mysql max_packet_size, this is 16MB which is more common than you might think.
# bigger values get tailed to fit
max_log_size = 16777216

def fetch_job_list(http_client, hudsonbaseurl):
    job_list_url = "%sapi/json?tree=jobs[name]" % (hudsonbaseurl,)
    resp, content = http_client.request(iri_to_uri(job_list_url), "GET")
    expect_ok(resp, content)
    expect_json(resp, content)
    
    json = simplejson.loads(content)
    job_list = json.get("jobs", [])
    del resp, content, json
    gc_collect()
    return job_list

def fetch_result_list(http_client, build_server_url, build_job_name):
    build_result_list_url = \
            "%sjob/%s/api/json?tree=builds[number,result,building,timestamp,duration]" % \
            (build_server_url,quote(build_job_name))
    resp, content = http_client.request(iri_to_uri(build_result_list_url), "GET")
    try:
        expect_ok(resp, content)
    except HttpError:
        logger.error("Got %d fetching build results for job %s, skipping", resp.status, unicode(build_job_name))
        return []
    expect_json(resp, content)
    json = simplejson.loads(content)
    build_result_list_fat = json.get("builds", [])
    logger.info("Processing build results for %s", build_job_name)
    build_result_list = []
    for build_result in build_result_list_fat:
        build_result_list.append({
            "number": build_result.get("number"),
            "result": build_result.get("result"),
            "building": build_result.get("building"),
            "timestamp": build_result.get("timestamp"),
            "duration": build_result.get("duration"),
        })
    del resp, content, json, build_result_list_fat
    gc_collect()
    return build_result_list

@rollback
def ensure_build_results(http_client, build_server_name, build_job_name, force_reindex=False):
    build_server = BuildServer.objects.get(name=build_server_name)
    transaction.rollback()

    build_result_list = fetch_result_list(http_client, build_server.url, build_job_name)
    
    for build_result in build_result_list:
        ensure_build_result(http_client, build_server, build_job_name, build_result, force_reindex=force_reindex)
        gc_collect()

@rollback
def ensure_build_result(http_client, build_server, build_job_name, build_result, force_reindex=False):
    build_number = build_result.get("number", None)
    if build_number == None: # some hudsons will start build numbering with #0
        logger.error("Got build result for job %s without build number, ignoring", build_job_name)
        return
    
    building = build_result.get("building", True)
    if building:
        # we'll process this later, once its complete
        logger.info("Skipping over %s #%d it is still building", build_job_name, build_number)
        return
    
    build_job = BuildJob.objects.get(build_server=build_server, name=build_job_name)
    transaction.rollback()
    log = None
    build_result_obj = None
    try:
        if not force_reindex:
            # we check for existance here so we may avoid a GET on /consoleText for the log
            exists = False
            try:
                exists = BuildResult.objects.filter(job=build_job, build_number=build_number).exists()
            finally:
                try:
                    transaction.rollback()
                except:
                    pass
            if exists:
                return
    
        success = build_result.get("result", "FAILURE") != "FAILURE"
        timestamp = datetime.datetime.fromtimestamp((build_result.get("timestamp", 0) + build_result.get("duration", 0))/1000)
    
        log_url = "%sjob/%s/%d/consoleText" % (build_server.url, quote(build_job.name), build_number)
        try:
            resp, content = http_client.request(iri_to_uri(log_url), "GET")
            if ok(resp):
                log = content
            else:
                log = "No log, got status %d trying to fetch it" % (resp.status,)
            if log and len(log) > max_log_size:
                log = log[:-max_log_size]
            del resp
            del content
        except IncompleteRead:
            # File "/Library/Python/2.6/site-packages/httplib2/__init__.py", line 1129, in request
            #   (response, content) = self._request(conn, authority, uri, request_uri, method, body, headers, redirections, cachekey)
            # File "/Library/Python/2.6/site-packages/httplib2/__init__.py", line 901, in _request
            #   (response, content) = self._conn_request(conn, request_uri, method, body, headers)
            # File "/Library/Python/2.6/site-packages/httplib2/__init__.py", line 884, in _conn_request
            #   content = response.read()
            # File "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/httplib.py", line 517, in read
            #   return self._read_chunked(amt)
            # File "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/httplib.py", line 567, in _read_chunked
            #   value += self._safe_read(chunk_left)
            # File "/System/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/httplib.py", line 619, in _safe_read
            #   raise IncompleteRead(s)
            log = "Log too big, could not fetch"
        
        build_result_obj, created = BuildResult.objects.ensure(build_job, build_number, success, timestamp, log)
        if created:
            logger.info("  Created new build result %s", unicode(build_result_obj))
        else:
            logger.info("  Updated build result %s", unicode(build_result_obj))
    finally:
        del build_result_obj
        del build_job
        del log


@rollback
def fetch_build_results(build_server_url, cert_file, key_file, ca_file, numworkers, build_server_name, force_reindex=False):
    def do_work(build_server_name, build_job_name, force_reindex=False):
        time.sleep(0.1 + random.random()/5)
        close_connection()
        http_client = makeHttps(build_server_url, cert_file, key_file, ca_file)
        try:
            ensure_build_results(http_client, build_server_name, build_job_name, force_reindex=force_reindex)
        except OperationalError:
            logger.error(
                "MySQL operational error trying to write build results for %s, trying again",
                unicode(build_job))
            close_connection()
            try:
                ensure_build_results(http_client, build_server_name, build_job_name)
            except OperationalError:
                logger.error(
                    "Still a MySQL operational error, skipping %s@%s",
                    build_job_name, build_server_name)
                close_connection()
        close_connection()
        sys.exit(0)
    
    logger.info("Getting build results")
    
    def make_process(build_job):
        return multiprocessing.Process(target=do_work, args=[build_server_name, build_job.name],
                kwargs={"force_reindex": force_reindex})
    workers = [make_process(build_job) for build_job in BuildJob.objects.filter(build_server__name=build_server_name, deleted=False)]
    
    run_all(workers, numworkers)

@commit_or_rollback
def delete(model_obj):
    model_obj.delete()

@rollback
def get_recipes_to_delete(deployment_system, all_recipes):
    result = []
    for recipe in Recipe.objects.filter(deployment_system=deployment_system):
        if recipe.deleted:
            continue
        if recipe.name in all_recipes:
            continue
        result.append(recipe)
    return result

def soft_delete_missing_recipes(deployment_system, all_recipes):
    logger.info("Pruning recipes that appear to no longer exist")
    recipes_to_delete = get_recipes_to_delete(deployment_system, all_recipes)
    for recipe in recipes_to_delete:
        delete(recipe)
        logger.info("Soft-deleted recipe %s", recipe.name)

@rollback
def get_jobs_to_delete(build_server, all_jobs):
    result = []
    for job in BuildJob.objects.filter(build_server=build_server):
        if job.deleted:
            continue
        if job.name in all_jobs:
            continue
        result.append(job)
    return result

def soft_delete_missing_jobs(build_server, all_jobs):
    logger.info("Pruning build jobs that appear to no longer exist")
    jobs_to_delete = get_jobs_to_delete(build_server, all_jobs)
    for job in jobs_to_delete:
        delete(job)
        logger.info("Soft-deleted build job %s", job.name)

class Command(ApiCommand):
    help = ("Crawl a hudson server and add interesting things"
            " it contains to the crichton db."
            " Can only run locally.")
    args = "<hudsonname> <hudsonbaseurl>"

    option_list = ApiCommand.option_list + (
        make_option("--detect-deploy", action="store_true", dest="detect_deploy",
            default=False,
            help="Try to determine if hudson jobs deploy packages to servers "
                "and if they do consider those jobs deployment recipes not buid jobs."
                " Defaults to false."),
        make_option("--keep-missing", action="store_true", dest="keep_missing",
            default=False,
            help="When a job is no longer listed in hudson it is "
                "normally soft-deleted. Disable that behavior."
                " Defaults to false."),
        make_option("--skip-results", action="store_true", dest="skip_results",
            default=False,
            help="Normally we try and fetch all new build results "
                "for all jobs. Disable that behavior."
                " Defaults to false."),
        make_option("--concurrency", action="store", dest="numworkers",
            default=4,
            help="Number of build results to process in parallel. "
                " Defaults to 4."),
        make_option("--force-reindex", action="store_true", dest="force_reindex",
            default=False,
            help="Force a reindex of all data, rather than skipping over build "
                " results that we've indexed before. Should not be needed normally;"
                " use after i.e. a bugfix. Default is false."),
    )
    
    # uses database!
    requires_model_validation = True
    
    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError(
                    "You must provide at least hudsonname and hudsonbasurl")
        
        hudsonname = args[0]
        hudsonbaseurl = args[1]
        if not hudsonbaseurl.endswith("/"):
            hudsonbaseurl += "/"
        detect_deploy = options.get("detect_deploy", False)
        skip_results = options.get("skip_results", False)
        
        cert_file = options.get("cert_file", None)
        key_file = options.get("key_file", None)
        ca_file = options.get("ca_file", None)
        numworkers = int(options.get("numworkers", '1'))
        keep_missing = options.get("keep_missing", False)
        force_reindex = options.get("force_reindex", False)

        hudson_client = makeHttps(hudsonbaseurl, **options)
        
        logger.info("Getting list of jobs for %s", hudsonname)
        job_list = fetch_job_list(hudson_client, hudsonbaseurl)
        if len(job_list) == 0:
            logger.error("Got 0-length list of jobs, looks like this hudson instance is empty")
        
        build_server, created = BuildServer.objects.ensure_hudson(hudsonname, hudsonbaseurl)
        if created:
            logger.info("Created new build server %s", unicode(build_server))
        
        deployment_system = None
        if detect_deploy:
            deployment_system, created = DeploymentSystem.objects.ensure_hudson(hudsonname, hudsonbaseurl)
            if created:
                logger.info("Created new deployment system %s", unicode(deployment_system))
        
        all_jobs = []
        all_recipes = []
        
        for job in job_list:
            job_name = job.get("name")
            if not job_name:
                logger.error("Got job without name, ignoring")
                continue
            if job_name.strip() == "":
                logger.error("Got job with a whitespace name: '%s', ignoring", job_name)
                continue
        
            # todo is searching job name for "deploy" reasonable way to detect deploy jobs??
            # can we do something better??
            if detect_deploy and job_name.find("deploy") != -1:
                result, created = Recipe.objects.ensure(deployment_system, job_name)
                if created:
                    logger.info("Created new recipe %s", unicode(result))
                # todo can we feed hudson build results in as deployment logs here????
                # todo how to find packages that are deployed through job
                all_recipes.append(job_name)
            else:
                result, created = BuildJob.objects.ensure(build_server, job_name)
                if created:
                    logger.info("Created new build job %s", unicode(result))
                all_jobs.append(job_name)
        
        logger.info("Saved build job list from %s", unicode(build_server))
        
        if not keep_missing:
            if detect_deploy:
                soft_delete_missing_recipes(deployment_system, all_recipes)
            soft_delete_missing_jobs(build_server, all_jobs)
        
        # django normally closes connections after every request (yes really)
        # by calling close_connection. MySQL + MySQLdb doesn't always cope well
        # with keeping connections open very long and doing a lot to them. So,
        # we close connections periodically after doing a bunch of stuff, that
        # way avoiding 2006 "MySQL has gone away" errors.
        #
        # see
        #   http://stackoverflow.com/questions/1303654/threaded-django-task-doesnt-automatically-handle-transactions-or-db-connections
        #   http://code.djangoproject.com/ticket/9964
        close_connection()
        
        del job_list
        del all_jobs
        del all_recipes
        del build_server
        del deployment_system
        gc_collect()
        
        if not skip_results:
            fetch_build_results(hudsonbaseurl, cert_file, key_file, ca_file, numworkers, hudsonname, force_reindex=force_reindex)
        
        crichtonCronJobStatus.objects.update_success('index_hudson')
