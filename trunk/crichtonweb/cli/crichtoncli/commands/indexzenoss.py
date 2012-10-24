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
# example that you can run on mac:
# ./crichton.py indexzenoss https://monitor.forge.domain.local/ Devices/BBC/ApplicationHost/Platform/Delivery \
#     --cert-file=/Users/$USER/.bbc/dev.domain.com.pem \
#     --key-file=/Users/$USER/.bbc/dev.domain.com.key \
#     --ca-file=/Users/$USER/.bbc/ca.pem

import re
from optparse import make_option

from django.core.management.base import CommandError
from django.db import transaction
from django.utils.encoding import iri_to_uri

from crichtoncli.apihelpers import *
from crichtoncli.commands import ApiCommand
from crichtonweb.core.httpshelpers import *
from crichtonweb.system.models import Environment, Pool, Node, PoolMembership, Role, crichtonCronJobStatus

import logging
logger = logging.getLogger(__name__)

class Command(ApiCommand):
    help = ("Crawl a zenoss device collection and add all"
            "devices it contains to the crichton db as nodes."
            " Can only run locally.")
    args = "<zenossbaseurl> <zenossselector>"

    # option_list = ApiCommand.option_list + (
    # )
    
    # uses database!
    requires_model_validation = True
    
    def print_help(self, zenossbaseurl, zenossselector):
        super(ApiCommand, self).print_help(zenossbaseurl, zenossselector)
    
    def _ensure_role_for_pool(self, pool_name):
        role_name = pool_name.split("_")[0]
        role, created = Role.objects.get_or_create(name=role_name)
        role.undelete()
        return role
    
    def _format_pool_name(self, name):
        return re.sub(r'[^a-zA-Z0-9_]', '_', name).lower()
    
    @transaction.commit_manually
    def ensure_pool(self, environment, name):
        # the pool creation we do here seems a bit hacky / our-zenoss-setup-specific
        # so it is not worthy of migration into the PoolManager class imho
        
        pool = None
        created = False
        try:
            name = self._format_pool_name(name)
            role = self._ensure_role_for_pool(name)
            
            pool, created = Pool.objects.get_or_create(environment=environment, name=name, defaults={
                "role": role,
            })
            if pool.role != role:
                pool.role = role
                pool.save()
            pool.undelete()
        except Exception, e:
            logger.error("ensure_pool failed with %s, roolling this transaction back" % str(e))
            transaction.rollback()
            raise
        else:
            transaction.commit()
        return pool, created
    
    # @transaction.commit_manually
    # def ensure_ip_address(self, node, ip_address):
    #     try:
    #         ip_address, created = IpAddress.objects.get_or_create(address=ip_address)
    #         if not node.ip_addresses.filter(address=ip_address):
    #             node.ip_addresses.add(ip_address)
    #             node.save()
    #     except:
    #         transaction.rollback()
    #         raise
    #     else:
    #         transaction.commit()

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError(
                    "You must provide at least zenossbaseurl and zenossselector")
        
        zenossbaseurl = args[0]
        if not zenossbaseurl.endswith("/"):
            zenossbaseurl += "/"
        zenossselector = args[1]
        zenoss_client = makeHttps(zenossbaseurl, **options)
        
        # issue_tracker = self.ensure_issue_tracker(jiraname, jirabaseurl)
        # project = self.ensure_project(issue_tracker, projectname)
        
        logger.info("Getting list of nodes for %s", zenossselector)
        device_list_url = "%szport/dmd/%s/getSubDevices" % (zenossbaseurl, zenossselector)
        resp, content = zenoss_client.request(iri_to_uri(device_list_url), "GET")
        expect_ok(resp, content)
        # expect_xml(resp, content)
        
        # ['BBCApplicationHostDevice at /zport/dmd/Devices/BBC/ApplicationHost/Platform/Delivery/Database/MySQL-Only/devices/db030.back.live.cwwtf.local>', 
        #  ....
        # 'BBCApplicationHostDevice at /zport/dmd/Devices/BBC/ApplicationHost/Platform/Delivery/InterPlatformMQ/Integration/devices/ipmq001.back.int.cwwtf.local']
        
        # get rid of [' and of ']
        content = content[2:][:-1]
        
        # split on , then remove whitespace, then get rid of the start quote ' and end quote ',
        devlist = [x.strip()[1:][:-1] for x in content.split(",")]
        
        # split on " at " and throw away the first part
        devlist = [x.split(" at ")[1].strip() for x in devlist]
        
        # get rid of /zport/dmd/
        devlist = [x.replace("/zport/dmd/","", 1) for x in devlist]
        
        # get rid of Devices/BBC/ApplicationHost/Platform/Delivery/
        devlist = [x.replace(zenossselector + "/","", 1) for x in devlist]
        
        # so now we have "InterPlatformMQ/Integration/devices/ipmq001.back.int.cwwtf.local"
        # split on "/devices/"
        devlist = [x.split("/devices/") for x in devlist]

        devlist = [(p.replace("/", "_"), n) for (p, n) in devlist]
        # so now we have ("InterPlatformMQ_Integration", "ipmq001.back.int.cwwtf.local")
        
        def get_env(n): # ipmq001.back.int.cwwtf.local
            env = n[n.find(".")+1:] # back.int.cwwtf.local
            env = env.replace("back.", "") # int.cwwtf.local
            env = env.replace(".local", "") # int.cwwtf
            env = env.split(".")[0] # int
            return env

        pools = {}
        environments = {}
        c = 0

        for p, n in devlist:
            e = get_env(n)

            # an exmaple
            # n -> db118.back.stage.telhc.local
            # p -> Database_Postgres
            # e -> stage

            if not e in environments:
                environment, created = Environment.objects.ensure(e)
                if created:
                    logger.info("Created environment %s", unicode(environment))
                environments[e] = environment
            else:
                environment = environments[e]

            pool_success = True # lets be positive :)
            if not p in pools:
                logger.info("Ensuring pool %s", unicode(p))
                try:
                    pool, created = self.ensure_pool(environment, p)
                    pools[p] = pool
                except:
                    pass
                    pool_success = False
            else:
                pool = pools[p]
            
            c += 1
            node, created = Node.objects.ensure(environment, n)
            if pool_success:
                pool_membership, created = PoolMembership.objects.ensure(pool, node)

        logger.info("Saw %d nodes", c)
        crichtonCronJobStatus.objects.update_success('index_zenoss')
