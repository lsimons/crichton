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
  # ./crichton.py indexyumrepo bbc-live https://yum.dev.domain.com/live \
  #     --cert-file=/Users/$USER/.bbc/dev.domain.com.pem \
  #     --key-file=/Users/$USER/.bbc/dev.domain.com.key \
  #     --ca-file=/Users/$USER/.bbc/ca.pem
from os import makedirs, rename, geteuid, getenv, lstat, uname
from os.path import exists
from stat import *
from shlex import split
from glob import glob
from subprocess import call, Popen, PIPE
from optparse import make_option
from pwd import getpwuid

from django.core.management.base import CommandError
from django.db import transaction

from MySQLdb import IntegrityError

from crichtoncli.commands import ApiCommand
from crichtonweb.core.utils import commit_or_rollback
from crichtonweb.package.models import Package, PackageName, Version
from crichtonweb.package.models import PackageRepository, PackageLocation
from crichtonweb.system.models import crichtonCronJobStatus

import logging
logger = logging.getLogger(__name__)

yum_conf_template="""
[main]

# put cache in our own little universse
cachedir=/data/crichton/yum/cache/%(reponame)s

# persistdir is for newer versions of yum
persistdir=/data/crichton/yum/cache/%(reponame)s

reposdir=/data/crichton/yum/repos.d
logfile=/data/crichton/yum/log/%(reponame)s.log
plugins=0
pluginspath=/data/crichton/yum/plugins
pluginsconfpath=/data/crichton/yum/pluginconf.d

# never prompt for anything
assumeyes=1

# if yum is dead/busy, try again later
retries=1
timeout=5

# but support caching
http_caching=all

# refresh metadata every time we are run
metadata_expire=0

# all I really need is primary.xml.gz
mdpolicy=group:primary

# define our one repo
[%(reponame)s]
name=Repo
baseurl=%(repobaseurl)s
enabled=1
gpgcheck=0
sslclientcert=%(cert_file)s
sslclientkey=%(key_file)s
sslcacert=%(ca_file)s
sslverify=1
"""

@commit_or_rollback
def delete(model_obj):
    model_obj.delete()

class Command(ApiCommand):
    help = ("Crawl a yum repo and add info on all"
            "packages it contains to the crichton db."
            " Can only run locally.")
    args = "<reponame> <repobaseurl>"

    option_list = ApiCommand.option_list + (
        make_option("--keep-missing", action="store_true", dest="keep_missing",
            default=False,
            help="When a package is no longer listed in a repo "
                "that location is normally soft-deleted. Disable that behavior."
                " Defaults to false."),
    )
    
    # uses database!
    requires_model_validation = True
    
    def print_help(self, reponame, repobaseurl):
        super(ApiCommand, self).print_help(reponame, repobaseurl)
    
    def get_cache_dir(self, reponame):
        """When yum is not run as root, in some versions it will ignore the
            cachedir setting in the conf file and use a per-user cache
            directory. Try to match its behavior, and find what likely has
            become the cache directory for the current run. Yuck."""
        
        configured_dir = "/data/crichton/yum/cache/" + reponame
        
        # if root, respect config (yay...)
        uid = geteuid()
        if uid == 0:
            return configured_dir
        
        # yes, this horrible way is really how yum looks for $USER...
        usertup = getpwuid(uid)
        username = usertup[0]
        
        # not root, so there may be a per-user private dir
        tmpdir = getenv('TMPDIR')
        if tmpdir is None:
            tmpdir = '/var/tmp'

        # check for /var/tmp/yum-username-* - 
        prefix = 'yum-%s-' % (username,)
        dirpath = '%s/%s*' % (tmpdir, prefix)
        cachedir = None
        cachedirs = sorted(glob(dirpath))
        for thisdir in cachedirs:
            stats = lstat(thisdir)
            if S_ISDIR(stats[0]) and S_IMODE(stats[0]) == 448 and stats[4] == uid:
                cachedir = thisdir
                break
        
        if not cachedir:
            return configured_dir
        else:
            # this test is for another spoted cache directory exception :(
            if not glob('%s/%s/primary.xml.gz.sqlite' % (cachedir, reponame)):
                # yes, really, like this
                basedir = uname()[4]
                from yum.config import _getsysver
                releasever = _getsysver('/', 'redhat-release') # may return '$releasever'...
                suffix = '/%s/%s' % (basedir, releasever)
                cachedir += suffix

        return cachedir
    
    def ensure_package(self, name, arch, version, epoch, release, location_href):
        # todo consider teaching crichton about architectures, epochs
        version_obj, created = Version.objects.ensure_from_rpm(version, release)
        PackageName.objects.ensure(name)
        return Package.objects.ensure(name, version_obj)
    
    @transaction.commit_manually
    def soft_delete_missing(self, repo, packages_seen):
        logger.info("Pruning package locations that appear to no longer exist")
        try:
            locations_to_delete = []
            for package_location in PackageLocation.objects.filter(repository=repo, deleted=False):
                if (package_location.package.name, package_location.package.version.name) in packages_seen:
                    continue
                locations_to_delete.append(package_location)
            transaction.rollback()
        
            for package_location in locations_to_delete:
                delete(package_location)
                logger.info("Soft-deleted package location %s", unicode(package_location))
            del locations_to_delete
        finally:
            transaction.rollback()
    
    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError(
                    "You must provide at least reponame and repobasurl")
        
        reponame = args[0]
        repobaseurl = args[1]
        keep_missing = options.get("keep_missing", False)
        ctx = locals()
        ctx.update(options)
        conf_file_data = yum_conf_template % ctx
        
        for d in ["/data/crichton/yum",
                "/data/crichton/yum/cache",
                "/data/crichton/yum/lib",
                "/data/crichton/yum/logs",
                "/data/crichton/yum/repos.d",
                "/data/crichton/yum/plugins",
                "/data/crichton/yum/pluginconf.d"]:
            if not exists(d):
                makedirs(d)
        
        fname="/data/crichton/yum/%s.conf" % (reponame,)
        f = open(fname + ".new", "w")
        f.write(conf_file_data)
        f.close()
        rename(fname + ".new", fname)

        cmd = "yum -c %s makecache" % (fname,)
        cmdarr = split(cmd)
        status = call(cmdarr)
        if status != 0:
            raise CommandError("%s returned %d" % (cmd, status))
        
        repo, created = PackageRepository.objects.ensure_yum(reponame, repobaseurl)
        if created:
            logger.info("Created new package repository %s", unicode(repo))
        
        cache_dir = self.get_cache_dir(reponame)
        
        # CREATE TABLE packages (  pkgKey INTEGER PRIMARY KEY,  pkgId TEXT,
        #                         name TEXT,  arch TEXT,  version TEXT,  epoch TEXT,
        #                         release TEXT,  summary TEXT,  description TEXT,
        #                         url TEXT,  time_file INTEGER,  time_build INTEGER,
        #                         rpm_license TEXT,  rpm_vendor TEXT,  rpm_group TEXT,
        #                         rpm_buildhost TEXT,  rpm_sourcerpm TEXT,
        #                         rpm_header_start INTEGER,  rpm_header_end INTEGER,
        #                         rpm_packager TEXT,  size_package INTEGER,  size_installed INTEGER,
        #                         size_archive INTEGER,  location_href TEXT,  location_base TEXT,
        #                         checksum_type TEXT);
        cmd = "sqlite3 -list -separator '|' " +\
            cache_dir + "/" + reponame + "/primary.xml.gz.sqlite " +\
            "'SELECT name, arch, version, epoch, release, location_href FROM packages ORDER BY pkgKey ASC'"
        # columns selected here must match ensure_package() above and # columns check, below
        cmdarr = split(cmd)
        logger.debug("Running command '%s'", cmd)
        p = Popen(cmdarr, stdout=PIPE)
        # so this gobbles up some memory but it avoids blocking forevah.
        # Non-blocking IO and python is just a little too hard.
        (stdout, stderr) = p.communicate()
        if stdout != "":
            logger.debug(stdout)
        if p.returncode != 0:
            logger.error("%s returned %d" % (cmd, p.returncode))
            if stderr != "":
                logger.error(stderr)
            raise CommandError("%s returned %d" % (cmd, p.returncode))
        
        packages_seen = []
        logger.info("Ensuring packages and locations exist in the database")
        for line in stdout.split("\n"):
            # print "processing", line
            args = line.split("|")
            if len(args) != 6:
                continue
            package, created = self.ensure_package(*args)
            if created:
                logger.info("Created new package %s", unicode(package))
            package_location, created = PackageLocation.objects.ensure(repo, package)
            if created:
                logger.info("  Created new package location %s", unicode(package_location))

            packages_seen.append((package.name, package.version.name))
        del stdout
        
        if not keep_missing:
            self.soft_delete_missing(repo, packages_seen)
        del packages_seen
        
        crichtonCronJobStatus.objects.update_success('index_yum_repo')
