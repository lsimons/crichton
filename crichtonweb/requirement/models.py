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
from django.db import models
from django.core.exceptions import ValidationError

from crichtonweb.core.models import crichtonModel
from crichtonweb.package.models import Version

from audit_log.models.managers import AuditLog

from core.introspection_rules import add_rules
add_rules()

class PackageSpecification(crichtonModel):
    package = models.ForeignKey('package.PackageName')
    version_specification = models.ForeignKey('requirement.VersionSpecification', null=True, blank=True)
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "requirement"
        unique_together = ('package', 'version_specification')

    def __unicode__(self):
        if self.version_specification:
            return "%s @%s" % (self.package.name, unicode(self.version_specification))
        else:
            return self.package.name

    def get_api_url(self, suffix):
        return "/api/version_specification/one/%s.%s" % (self.id, suffix)

class VersionRangeManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

_LOOKING_FOR_MINIMUM_MODE = 1
_LOOKING_FOR_MINIMUM_VERSION_OR_COMMA = 2
_LOOKING_FOR_MAXIMUM_VERSION_OR_MODE = 3
_LOOKING_FOR_MAXIMUM_MODE = 4
_DONE = 5

class VersionRange(crichtonModel):
    can_delete = True
    objects = VersionRangeManager()
    name = models.CharField(max_length=103, primary_key=True,
            help_text="Version range string in canonical form.")
    minimum = models.ForeignKey('package.Version', null=True, blank=True, related_name='+',
            help_text="Either a minimum or maximum version is required")
    minimum_is_inclusive = models.BooleanField(default=True)
    maximum = models.ForeignKey('package.Version', null=True, blank=True, related_name='+')
    maximum_is_inclusive = models.BooleanField(default=False)

    class Meta:
        app_label = "requirement"
        
    @classmethod
    def from_versions(cls, minimum, maximum, minimum_is_inclusive=True,
            maximum_is_inclusive=False):
        """Turns a couple of Versions into a VersionRange."""
        
        if not minimum and not maximum:
            raise Exception("Must provide at least a minimum or a maximum Version")
        if minimum and minimum.name.find(",") != -1:
            raise Exception("Minimum version cannot contain character ','")
        if maximum and maximum.name.find(")") != -1:
            raise Exception("Maximum version cannot contain character ')'")
        if maximum and maximum.name.find("]") != -1:
            raise Exception("Maximum version cannot contain character ']'")
        
        result = VersionRange()
        result.minimum = minimum
        result.minimum_is_inclusive = minimum_is_inclusive
        result.maximum = maximum
        result.maximum_is_inclusive = maximum_is_inclusive
        name = ""
        if minimum_is_inclusive:
            name += "["
        else:
            name += "("
        if minimum:
            name += minimum.name
        name += ","
        if maximum:
            name += maximum.name
        if maximum_is_inclusive:
            name += "]"
        else:
            name += ")"
        result.name = name
        return result
    
    @classmethod
    def from_string(cls, name):
        """Parses a version range such as [1.0,2.0) and returns a VersionRange object.
        The returned Version objects are not connected to the database so before calling
        save() that needs to be resolved, i.e.
        
            range = VersionRange.from_string(...)
            if range.minimum:
                try:
                    range.minimum = Version.get(name=range.minimum.name)
                except Version.DoesNotExist:
                    range.minimum.save()
            if range.maximum:
                try:
                    range.maximum = Version.get(name=range.maximum.name)
                except Version.DoesNotExist:
                    range.maximum.save()

        """
        
        minimum = None
        minimum_is_inclusive = None
        minimum_str = ""
        maximum = None
        maximum_is_inclusive = None
        maximum_str = ""
        state = _LOOKING_FOR_MINIMUM_MODE
        
        # this takes the input string and turns it into
        #        [ or (                                 (minimum inclusive or exclusive)
        #        any number of characters except ,      (minimum version)
        #        ,
        #        any number of characters except ) or ] (maximum version)
        #        ) ]                                    (maximum inclusive or exclusive)
        
        for c in name:
            c = str(c)
            if state == _LOOKING_FOR_MINIMUM_MODE:
                if c == "[":
                    minimum_is_inclusive = True
                    state = _LOOKING_FOR_MINIMUM_VERSION_OR_COMMA
                elif c == "(":
                    minimum_is_inclusive = False
                    state = _LOOKING_FOR_MINIMUM_VERSION_OR_COMMA
                else:
                    raise Exception("Range must start with [ or (, not %s" % c)
            elif state == _LOOKING_FOR_MINIMUM_VERSION_OR_COMMA:
                if c == ",":
                    state = _LOOKING_FOR_MAXIMUM_VERSION_OR_MODE
                else:
                    minimum_str += c
            elif state == _LOOKING_FOR_MAXIMUM_VERSION_OR_MODE:
                if c == "]":
                    maximum_is_inclusive = True
                    state = _DONE
                elif c == ")":
                    maximum_is_inclusive = False
                    state = _DONE
                else:
                    maximum_str += c
            elif state == _DONE:
                raise Exception("Range must end after ] or ), but has additional character %s" % c)
        if state != _DONE:
            raise Exception("Range must contain a comma and end with a ] or )")
        
        assert minimum_is_inclusive != None and maximum_is_inclusive != None
        assert minimum_str != "" or maximum != ""
        
        if minimum_str != "":
            minimum = Version.from_string(minimum_str)
        if maximum_str != "":
            maximum = Version.from_string(maximum_str)
            
        result = VersionRange()
        result.name = name
        result.minimum = minimum
        result.minimum_is_inclusive = minimum_is_inclusive
        result.maximum = maximum
        result.maximum_is_inclusive = maximum_is_inclusive
        
        return result
    
    def clean(self):
        """Make sure there is at least a maximum or a minimum"""
        if not self.minimum and not self.maximum:
            raise ValidationError("VersionRange should nave at least a maximum version" + \
                " or a minimum version.")
    
    def __unicode__(self):
        return self.name
    
    def natural_key(self):
        return (self.name,)

    def get_api_url(self, suffix):
        return "/api/version_range/one/%s.%s" % (self.name, suffix)

class VersionSpecificationManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(Q(version__name=name) | Q(version_range__name=name))

class VersionSpecification(crichtonModel):
    can_delete = True
    objects = VersionSpecificationManager()
    version = models.ForeignKey('package.Version', null=True, blank=True, related_name='+',
        help_text="Select either a version or a version range.")
    version_range = models.ForeignKey('VersionRange', null=True, blank=True, related_name='+')
    
    class Meta:
        app_label = "requirement"
        unique_together = ("version", "version_range")

    def clean(self):
        """Makes sure this points at either a Version or a VersionRange."""
        if self.version and self.version_range:
            raise ValidationError("VersionSpecification should point to" +\
                    " either a Version or a VersionRange, not both")
        if not self.version and not self.version_range:
            raise ValidationError("VersionSpecification should point to" +\
                    " a Version or a VersionRange")
    
    def __unicode__(self):
        if self.version:
            return self.version.name
        elif self.version_range:
            return self.version_range.name
        else:
            return 'unset'
    
    def natural_key(self):
        return (self.__unicode__(),)
    natural_key.dependencies = ['package.version', 'requirement.versionrange']

    def get_api_url(self, suffix):
        return "/api/version_specification/one/%s.%s" % (self.id, suffix)
    
class Requirement(crichtonModel):
    # note OneToOneField doesn't want to work properly with audit_log
    application = models.ForeignKey('prodmgmt.Application', unique=True)
    default_specification = models.ForeignKey('PackageSpecification', null=True, blank=True,
            related_name="default_specifications")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)

    class Meta:
        app_label = "requirement"
    
    def __unicode__(self):
        return "%s requirement" % (self.application.name,)

    def get_api_url(self, suffix):
        return "/api/requirement/one/%s.%s" % (self.id, suffix)

class EnvironmentRequirement(crichtonModel):
    specification = models.ForeignKey('requirement.PackageSpecification', related_name="environment_requirements")
    environment = models.ForeignKey('system.Environment', related_name="requirements")
    requirement = models.ForeignKey('requirement.Requirement', related_name="environment_requirements")
    audit_log = AuditLog()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        app_label = "requirement"
        unique_together = ('specification', 'environment', 'requirement')

    def __unicode__(self):
        return "%s on %s" % (unicode(self.specification), self.environment.name)

    def get_api_url(self, suffix):
        return "/api/environment_requirement/one/%s.%s" % (self.id, suffix)
    
# eof
