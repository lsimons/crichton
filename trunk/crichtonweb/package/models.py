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
import re

from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError

from audit_log.models.managers import AuditLog

from crichtonweb.core.models import crichtonModel

from core.utils import commit_or_rollback
from core.introspection_rules import add_rules
add_rules()

class PackageManager(models.Manager):
    def get_by_natural_key(self, name, version_name):
        return self.get(name=name, version__name=version_name)
    
    @commit_or_rollback
    def ensure(self, name, version):
        result, created = self.get_or_create(name=name, version=version)
        result.undelete()
        return result, created

class Package(crichtonModel):
    objects = PackageManager()
    # this is _not_ linked to PackageName on purpose -- it is
    #   weird, but possible to know about a Package but not separately
    #   know about the PackageName
    name = models.CharField(max_length=255,
            help_text="The name of this package.")
    version = models.ForeignKey('Version')
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "package"
        unique_together = ("name", "version")
        ordering = ('name',)

    def __unicode__(self):
        return (self.name or 'unnamed') + '-' + \
                (self.version and self.version.name or 'unversioned')
    
    def natural_key(self):
        return (self.name, self.version.name)
    natural_key.dependencies = ['package.version']
    
    def get_api_url(self, suffix):
        return "/api/package/one/%s@%s.%s" % (self.name, self.version, suffix)

    def to_json(self):
        # see also hotjazz/json_serializer.py
        # not using that here because we want different output than just the object
        json = { "name": self.name,
                 "version": str(self.version),
                 "rpm_version": self.version.rpm_version,
                 "rpm_release": self.version.rpm_release
                 }
        return json
    
class PackageNameManager(models.Manager):
    @commit_or_rollback
    def ensure(self, name):
        return self.get_or_create(name=name)

class PackageName(crichtonModel):
    objects = PackageNameManager()
    name = models.CharField(max_length=255, primary_key=True,
            help_text="The name of this package.")
    
    class Meta:
        app_label = "package"
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
    def get_api_url(self, suffix):
        return "/api/package_name/one/%s.%s" % (self.name, suffix)
    
class VersionManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
    @commit_or_rollback
    def ensure_from_rpm(self, version, release):
        version_obj = Version.from_rpm(version, release)
        if version_obj.major == None:
            version_obj.major = 0
            version_obj.status = 'snapshot'
        try:
            version_obj.save()
        except IntegrityError, e:
            transaction.rollback()
            version_obj = Version.objects.get(name=version_obj.name)
            return version_obj, False
        return version_obj, True

_LOOKING_FOR_MAJOR=1
_IN_MAJOR=2
_LOOKING_FOR_MINOR=3
_IN_MINOR=4
_LOOKING_FOR_MICRO=5
_IN_MICRO=6
_LOOKING_FOR_REVISION=7
_IN_REVISION=8
_LOOKING_FOR_BUILD=9
_IN_BUILD=10
_DONE=11

_numbers=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
_number_status_re=re.compile(r'(rc|alpha|beta|a|b)[0-9]+', re.I)
_number_portability_re=re.compile(r'([0-9\._-]p)[0-9]+', re.I)

# minimum svn revision is 100 digits here. Bit hacky, but true for our data set
# maximum number of builds is 99999 here. Bit hacky, but true for our data set.
_std_format_rpm_release_re=re.compile(r'^([0-9][0-9][0-9]+)\.([0-9]{1,5})$')
_rpm_os_version_re=re.compile(r'el5|el6')

def _find_release_status(version_name):
    lname = version_name.lower()
    lname = lname.replace("bbc", "")
    status = 'release'
    found_status = False
    for (shorthand, description) in Version.RELEASE_STATUSES:
        if lname.find(shorthand.lower()) != -1:
            status = shorthand
            found_status = True
            break
    if not found_status:
        for alias_set in Version.RELEASE_STATUS_ALIASES:
            shorthand = alias_set[0]
            for alias in alias_set:
                if lname.find(alias) != -1:
                    status = shorthand
                    found_status = True
                    break
    return status

class Version(crichtonModel):
    objects = VersionManager()
    RELEASE_STATUSES = (
        ('alpha', 'Alpha'),
        ('beta', 'Beta'),
        ('RC', 'Release Candidate'),
        ('release', 'Release'),
        ('snapshot', 'Snapshot'),
    )
    RELEASE_STATUS_ALIASES = (
        ('snapshot', 'dev'),
        ('RC', 'rc'),
    )
    name = models.CharField(max_length=50, primary_key=True,
            help_text="Version string in canonical form.")
    major = models.IntegerField()
    minor = models.IntegerField(null=True,blank=True)
    micro = models.IntegerField(null=True,blank=True)
    build = models.IntegerField(null=True,blank=True)
    revision = models.IntegerField(null=True,blank=True)
    status = models.CharField(max_length=16, choices=RELEASE_STATUSES, default='release')
    rpm_version = models.CharField(max_length=48,null=True,blank=True)
    rpm_release = models.CharField(max_length=48,null=True,blank=True)
    
    class Meta:
        app_label = "package"
        ordering = ('major', 'minor', 'micro', 'revision')

    @classmethod
    def from_string(cls, name):
        """Parses a version string and returns a Version object.
        
        Note that if you have an rpm_version and an rpm_release seperately, it is better to
        use Version.from_rpm() instead.
        """
        #
        # Note that this implementation was chosen after careful study of things like
        #
        #   http://concisionandconcinnity.blogspot.com/2008/12/rpm-style-version-comparison-in-python.html
        #   http://ant.apache.org/ivy/history/latest-milestone/settings/latest-strategies.html
        #   http://php.net/manual/en/function.version-compare.php
        #   http://apr.apache.org/versioning.html
        #   http://fedoraproject.org/wiki/Tools/RPM/VersionComparison
        #   https://bugzilla.redhat.com/show_bug.cgi?id=178798
        #   http://www.openssh.org/portable.html
        #
        # and associated source code.
        v = Version()
        v.name = name
        
        state = _LOOKING_FOR_MAJOR
        number_accum=""
        
        name = _number_status_re.sub(r'\1', name) # turn i.e. 1.0-alpha3 into 1.0-alpha
        name = _number_portability_re.sub(r'\1', name) # turn i.e. 4.3p2-41 into 4.3p-41
        
        for c in name:
            if state == _LOOKING_FOR_MAJOR:
                if c in _numbers:
                    number_accum += c
                    state = _IN_MAJOR
            elif state == _IN_MAJOR:
                if c in _numbers:
                    number_accum += c
                else:
                    v.major = int(number_accum)
                    number_accum = ""
                    state = _LOOKING_FOR_MINOR
            elif state == _LOOKING_FOR_MINOR:
                if c in _numbers:
                    number_accum += c
                    state = _IN_MINOR
            elif state == _IN_MINOR:
                if c in _numbers:
                    number_accum += c
                else:
                    v.minor = int(number_accum)
                    number_accum = ""
                    state = _LOOKING_FOR_MICRO
            elif state == _LOOKING_FOR_MICRO:
                if c in _numbers:
                    number_accum += c
                    state = _IN_MICRO
            elif state == _IN_MICRO:
                if c in _numbers:
                    number_accum += c
                else:
                    v.micro = int(number_accum)
                    number_accum = ""
                    state = _LOOKING_FOR_REVISION
            elif state == _LOOKING_FOR_REVISION:
                if c in _numbers:
                    number_accum += c
                    state = _IN_REVISION
            elif state == _IN_REVISION:
                if c in _numbers:
                    number_accum += c
                else:
                    v.revision = int(number_accum)
                    number_accum = ""
                    state = _LOOKING_FOR_BUILD
            elif state == _LOOKING_FOR_BUILD:
                if c in _numbers:
                    number_accum += c
                    state = _IN_BUILD
            elif state == _IN_BUILD:
                if c in _numbers:
                    number_accum += c
                else:
                    v.build = int(number_accum)
                    number_accum = ""
                    state = _DONE
                    break
        if number_accum != "":
            if state == _IN_MAJOR:
                v.major = int(number_accum)
            elif state == _IN_MINOR:
                v.minor = int(number_accum)
            elif state == _IN_MICRO:
                v.micro = int(number_accum)
            elif state == _IN_REVISION:
                v.revision = int(number_accum)
            elif state == _IN_BUILD:
                v.build = int(number_accum)
            # unused state = _DONE
        
        v.status = _find_release_status(v.name)
        return v
    
    @classmethod
    def from_rpm(cls, rpm_version, rpm_release):
        """Parses version and release strings and returns a Version object."""
        #
        # RPM and Yum tend to split major.minor.micro-revision.build into
        # version=major.minor.micro, release=revision.build
        #
        # when that happens, we know we should not look for major.minor.micro
        # inside version, and we should prefer revision.build from the release
        # if that looks like it matches our expected pattern.
        #
        v = Version()
        v.rpm_version = rpm_version
        v.rpm_release = rpm_release
        v.name = rpm_version
        if rpm_release != None:
            v.name += '-' + rpm_release
            rpm_release = _rpm_os_version_re.sub('', rpm_release) # turn i.e. 1.0-1.el5 into 1.0-1.
            rpm_release = _number_status_re.sub(r'\1', rpm_release) # turn i.e. 1.0-alpha3 into 1.0-alpha
            rpm_release = _number_portability_re.sub(r'\1', rpm_release) # turn i.e. 4.3p2-41 into 4.3p-41
            
        normal_v = Version.from_string(rpm_version)
        v.major = normal_v.major
        v.minor = normal_v.minor
        v.micro = normal_v.micro
        std_release = None
        if rpm_release:
            std_release = _std_format_rpm_release_re.match(rpm_release)
        if std_release:
            # we like the format of rpm_release. Use always.
            v.revision = int(std_release.group(1))
            v.build = int(std_release.group(2))
        else:
            # we don't like rpm_release as much. Prefer data found in version,
            # but allow release to contain revision/build in other formats
            state = _LOOKING_FOR_REVISION
            if normal_v.revision != None:
                v.revision = normal_v.revision
                state = _LOOKING_FOR_BUILD
            if normal_v.build != None:
                v.build = normal_v.build
                state = _DONE
            if not state == _DONE and rpm_release != None:
                number_accum=""
                for c in rpm_release:
                    if state == _LOOKING_FOR_REVISION:
                        if c in _numbers:
                            number_accum += c
                            state = _IN_REVISION
                    elif state == _IN_REVISION:
                        if c in _numbers:
                            number_accum += c
                        else:
                            v.revision = int(number_accum)
                            number_accum = ""
                            state = _LOOKING_FOR_BUILD
                    elif state == _LOOKING_FOR_BUILD:
                        if c in _numbers:
                            number_accum += c
                            state = _IN_BUILD
                    elif state == _IN_BUILD:
                        if c in _numbers:
                            number_accum += c
                        else:
                            v.build = int(number_accum)
                            number_accum = ""
                            state = _DONE
                            break
                if number_accum != "":
                    if state == _IN_REVISION:
                        v.revision = int(number_accum)
                    elif state == _IN_BUILD:
                        v.build = int(number_accum)
                    # unused state = _DONE
        
        # release status is allowed in release field,
        # so we want to reparse rather than take normal_v.status
        v.status = _find_release_status(v.name)
        return v
    
    @classmethod
    def from_numbers(cls, major, minor=None, micro=None, build=None,
            revision=None, status=None):
        """Turns a set of version numbers into a Version object."""
        
        if minor == None and micro != None:
            raise ValidationError("Can't have micro without minor")
        if micro == None and revision != None:
            raise ValidationError("Can't have revision without micro")
        if revision == None and build != None:
            raise ValidationError("Can't have revision without build")
        
        name = str(major)
        if minor != None:
            name += "." + str(minor)
        if micro != None:
            name += "." + str(micro)
        if revision != None:
            name += "-" + str(revision)
        if build != None:
            name += "." + build
        
        v = Version()
        v.name = name
        v.major = major
        v.minor = minor
        v.micro = micro
        v.revision = revision
        v.build = build
        v.status = status
        
        return v
    
    def clean(self):
        """Makes sure major/minor/micro/build/revision/status match with the name."""
        pass # "TODO raise django ValidationError for problems"
    
    def __unicode__(self):
        return self.name
    
    def natural_key(self):
        return (self.name,)
    
    def get_api_url(self, suffix):
        return "/api/version/one/%s.%s" % (self.name, suffix)

class PackageRepositoryManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)
    
    @commit_or_rollback
    def ensure_yum(self, reponame, repobaseurl):
        result, created = self.get_or_create(name=reponame,
            defaults={
                    "url": repobaseurl,
            })
        if result.url != repobaseurl:
            result.url = repobaseurl
            result.save()
        result.undelete()
        return result, created

class PackageRepository(crichtonModel):
    objects = PackageRepositoryManager()
    PACKAGE_REPOSITORY_TYPES = (
        ('yum', 'Yum'),
    )
    name = models.SlugField(max_length=128, unique=True)
    # no display_name, why do we have those anyway? ...
    package_repository_type = models.CharField(max_length=12, choices=PACKAGE_REPOSITORY_TYPES,
            default='yum')
    url = models.URLField(max_length=255, blank=True, verify_exists=False)
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "package"
        ordering = ('name',)
        verbose_name_plural = "package repositories"

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    def get_api_url(self, suffix):
        return "/api/package_repository/one/%s.%s" % (self.name, suffix)

class PackageLocationManager(models.Manager):
    def get_by_natural_key(self, package_name, package_version, repository_name):
        return self.get(package__name=package_name, package__version=package_version,
                repository__name=repository_name)
    
    @commit_or_rollback
    def ensure(self, repo, package):
        result, created = self.get_or_create(repository=repo, package=package)
        result.undelete()
        return result, created

class PackageLocation(crichtonModel):
    objects = PackageLocationManager()
    package = models.ForeignKey('Package', related_name="locations")
    repository = models.ForeignKey('PackageRepository', related_name="packages")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "package"
        unique_together = ('package', 'repository')

    def __unicode__(self):
        return "%s:%s" % (unicode(self.package), unicode(self.repository))
    
    def natural_key(self):
        return (self.package.name, self.package.version, self.repository.name)

    def get_api_url(self, suffix):
        return "/api/package_location/one/%s@%s:%s.%s" % (self.package.name, self.package.version,
                self.repository.name, suffix)

# eof
