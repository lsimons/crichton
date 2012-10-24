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
from django.core.management.base import CommandError
from django.db import transaction

from crichtonweb.issue.models import Issue
from crichtonweb.release.models import DeploymentRequest, Release, ReleaseElement
from crichtonweb.package.models import Package, PackageName, Version
from crichtonweb.requirement.models import Requirement, EnvironmentRequirement
from crichtonweb.requirement.models import VersionSpecification, PackageSpecification

from crichtonweb.core.utils import rollback

class ConsistencyError(Exception):
    pass

@rollback
def validate_requirements(pools, roles, environments):
    errors = []
    for pool in pools:
        if pool.role.deleted:
            errors.append("Pool %s has role %s but that role has been deleted" % (pool.name, pool.role.name))
    for role in roles:
        for env in environments:
            for app_member in role.applications.filter(deleted=False):
                app = app_member.application
                if app.deleted:
                    errors.append("Role %s has application %s "
                            "which has been deleted" % (role, app))
                    continue
                for req in Requirement.objects.filter(deleted=False, application=app):
                    for env_req in req.environment_requirements.filter(deleted=False, environment=env):
                        pspec = env_req.specification
                        if pspec.deleted:
                            errors.append("Application %s has requirement %s which for environment %s "
                                    "has specification %s which has been deleted" % (
                                    app, req, env, pspec))
                        package_name = pspec.package.name
                        vspec = pspec.version_specification
                        if vspec:
                            # vspec is primitive
                            # if vspec.deleted:
                            #     raise CommandError("Application %s has requirement %s which for environment %s "
                            #             "resolves to specification %s which has package specification %s "
                            #             "which has version specification %s which has been deleted" % (
                            #             app, req, env, spec, pspec, vspec))
                            if vspec.version_range:
                                errors.append("Application %s has requirement %s which for environment %s "
                                        "resolves to a package specification for package %s and version "
                                        "range %s, but version ranges are not supported by puppet" % (
                                        app, req, env, package_name, vs.version_range))
    if len(errors) > 0:
        raise ConsistencyError("\n".join(errors))

#@transaction.commit_manually
def update_requirements(elements, environment, confirmer=None, logger=None):
    # this is some interesting logic: for each release element, we want to find if any
    # requirements already exist for its application. If so, we want to _replace_ the
    # specification on the relevant environment requirement, because specifications could
    # be in use in multiple times, and we don't want to update all of those places, just
    # the ones for this application/environment.
    
    if confirmer and not callable(confirmer):
        raise Exception("Keyword argument confirmer should be a callable")
    if logger and not callable(logger):
        raise Exception("Keyword argument logger should be a callable")
    
    if not logger:
        def logger(msg):
            if msg != "":
                print unicode(msg).encode("UTF-8")
            else:
                print
    
    making_changes = False
    try:
        logger("Changes:")
        logger("")
        for e in elements:
            # TODO PackageSpecification should use Package and not PackageName
            app = e.application
            version = e.package.version
            pkg_name_obj, created = PackageName.objects.get_or_create(name=e.package.name)
            if created:
                making_changes = True
            
            req, created = Requirement.objects.get_or_create(application=app)
            if created:
                making_changes = True
            if req.deleted:
                making_changes = True
                req.deleted = False
                req.save()
            
            vspec, created = VersionSpecification.objects.get_or_create(version=version)
            if created:
                making_changes = True
            # is primitive... if vspec.deleted:
            #     vspec.deleted = False
            #     vspec.save()
            
            pspec, created = PackageSpecification.objects.get_or_create(package=pkg_name_obj,
                    version_specification=vspec)
            if created:
                making_changes = True
            if pspec.deleted:
                making_changes = True
                pspec.deleted = False
                pspec.save()
            
            try:
                env_req = req.environment_requirements.get(environment=environment,
                        specification__package=pkg_name_obj)
                if pspec == env_req.specification:
                    if env_req.deleted:
                        making_changes = True
                        logger("  Requirement %s = %s was specified for environment %s but deleted, undeleting" % (
                                pkg_name_obj, vspec, environment))
                    else:
                        logger("  Requirement %s = %s already specified for environment %s, no change" % (
                                pkg_name_obj, vspec, environment))
                        continue
                else:
                    making_changes = True
                    old_vspec = env_req.specification.version_specification
                    logger("  Updating %s = %s requirement on environment %s (was %s)" % (
                            pkg_name_obj, vspec, environment, old_vspec))
                    # todo compare old and new, issue warning or abort if downgrade
                    env_req.specification = pspec
                if env_req.deleted:
                    env_req.deleted = False
                env_req.save()
            except EnvironmentRequirement.DoesNotExist:
                making_changes = True
                env_req = EnvironmentRequirement.objects.create(
                        requirement=req, environment=environment, specification = pspec)
                logger("  Adding %s = %s requirement on environment %s" % (
                        pkg_name_obj, vspec, environment))
        logger("")
        if making_changes and confirmer:
            confirmer()
    except:
        logger("")
        logger("Rolling back")
        try:
            transaction.rollback()
        except:
            pass
        raise
    else:
        if not making_changes:
            logger("No changes to make!")
            transaction.rollback()
        else:
            transaction.commit()
            logger("Changes committed. You probably want to run ./crichton.py puppetinit now.")

@transaction.commit_manually
def apply_request(issue_name, confirmer=None, informer=None, logger=None):
    try:
        try:
            issue = Issue.objects.get(name=issue_name, deleted=False)
        except Issue.DoesNotExist:
            raise CommandError("No such issue %s" % issue_name)
        
        try:
            deployment_request = DeploymentRequest.objects.get(ops_issue=issue, deleted=False)
        except DeploymentRequest.DoesNotExist:
            raise CommandError("No deployment request for issue %s" % issue_name)
        
        release = deployment_request.release
        if release.deleted:
            raise CommandError("release for issue %s has been deleted" % issue_name)
        
        environment = deployment_request.environment
        if environment.deleted:
            raise CommandError("environment for deployment request for issue %s has been deleted" % issue_name)
        transaction.rollback()
        
        packages = []
        elements = list(release.elements.filter(deleted=False))
        for e in elements:
            if not e.application:
                raise CommandError(
                        "release specifies package %s but does not specify the application" % e.package.name)
            if e.application.deleted:
                raise CommandError(
                        "application %s is to be released, but it has been deleted" % e.application.name)
            package = e.package
            
            # check that we don't see same-package different-version
            for other_package in packages:
                if package.name != other_package.name:
                    continue
                if package.version != other_package.version:
                    raise CommandError("Seem to be requiring two different versions of package %s:"
                            "version %s and version %s" % (package.version, other_package.version))
            if not package in packages:
                packages.append(package)
        transaction.rollback()
        
        if informer and callable(informer):
            informer(issue, environment, release, packages)
        
        update_requirements(elements, environment, confirmer=confirmer, logger=logger)
    except:
        try:
            transaction.rollback()
        except:
            pass
        raise
