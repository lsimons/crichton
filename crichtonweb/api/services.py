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
from django.conf.urls.defaults import patterns
from django.core.serializers import register_serializer

from issue.models import *
from jirarpc.models import *
from package.models import *
from prodmgmt.models import *
from ci.models import *
from release.models import *
from system.models import *
from deployment.models import *
from requirement.models import *

from hotjazz.conf import service_config, service
from hotjazz.conf import ServiceConfigError

services = service_config('',
    format=r'(?P<format>[a-z_]{1,12})',
    name=r'(?P<name>[^/]{1,255})',
    id=r'(?P<id>[0-9]{1,11})',
    number=r'(?P<id>[0-9]{1,11})',
)

# todo various additional / convenience APIs

services.add(
    service(
        pattern=r'^internet_address/one/{address}\.{format}$',
        name="api-internet_address-one",
        exposes=InternetAddress,
        get_for__address="address"
    ),
    service(
        pattern=r'^internet_address/list/all\.{format}$',
        name="api-internet_address-list",
        exposes=InternetAddress.objects.all
    ),
    address=r'(?P<address>[^/]{1,45})',
)

services.add(
    service(
        pattern=r'^person/audit/{username}\.{format}$',
        name="api-person-audit",
        exposes=Person.audit_log.all,
        get_for__username="username"
    ),
    service(
        pattern=r'^person/one/{username}\.{format}$',
        name="api-person-one",
        exposes=Person,
        get_for__username="username"
    ),
    service(
        pattern=r'^person/list/all\.{format}$',
        name="api-person-list",
        exposes=Person.objects.all
    ),
    username=r'(?P<username>[^/]{1,30})',
)

def camel_to_url(model_name):
    if not model_name or len(model_name) == 0:
        raise ServiceConfigError("Cannot get model name")
    
    result = model_name[0].lower()
    i = 1
    while i < len(model_name):
        c = model_name[i]
        i += 1
        if c.isupper():
            result += "_" + c.lower()
        else:
            result += c
    return result

def url_to_camel(url_name):
    if not url_name or len(url_name)== 0:
        raise ServiceConfigError("Cannot get url name")
    
    result = url_name[0].upper()
    i = 1
    next_upper = False
    while i < len(url_name):
        c = url_name[i]
        i += 1
        if c == "_":
            if next_upper:
                raise ServiceConfigError("Double underscore in %s" % url_name)
            next_upper = True
        elif next_upper:
            result += c.upper()
            next_upper = False
        else:
            result += c.lower()
    return result

def add_crud_for_named_models(*args, **kwargs):
    global services
    
    audited = kwargs.get("audited", True)
    
    for model in args:
        object_name = model._meta.object_name
        url_name = camel_to_url(object_name)

        if audited:
            pattern = "^%(url_name)s/audit/{name}\\.{format}$" % locals()
            name = "api-%(url_name)s-audit" % locals()
            services.add(service(
                    pattern=pattern,
                    name=name,
                    exposes=model.audit_log.all,
                    get_for__name="name"
                ))
        
        pattern = "^%(url_name)s/one/{name}\\.{format}$" % locals()
        name = "api-%(url_name)s-one" % locals()
        
        list_pattern = "^%(url_name)s/list/all\\.{format}$" % locals()
        list_name = "api-%(url_name)s-list" % locals()
        services.add(
            service(
                pattern=pattern,
                name=name,
                exposes=model,
                get_for__name="name"
            ),
            service(
                pattern=list_pattern,
                name=list_name,
                exposes=model.objects.all
            ),
        )

def add_crud_for_simple_id_models(*args, **kwargs):
    global services
    
    audited = kwargs.get("audited", False)
    
    for model in args:
        object_name = model._meta.object_name
        url_name = camel_to_url(object_name)
        
        if audited:
            pattern = "^%(url_name)s/audit/{id}\\.{format}$" % locals()
            name = "api-%(url_name)s-audit" % locals()
            services.add(service(
                    pattern=pattern,
                    name=name,
                    exposes=model.audit_log.all,
                    get_for__id="id"
                ))
        
        pattern = "^%(url_name)s/one/{id}\\.{format}$" % locals()
        name = "api-%(url_name)s-one" % locals()
        
        list_pattern = "^%(url_name)s/list/all\\.{format}$" % locals()
        list_name = "api-%(url_name)s-list" % locals()
        services.add(
            service(
                pattern=pattern,
                name=name,
                exposes=model,
                get_for__id="id"
            ),
            service(
                pattern=list_pattern,
                name=list_name,
                exposes=model.objects.all
            ),
        )
        

add_crud_for_named_models(BuildServer,DeploymentSystem,IssueTracker)
add_crud_for_named_models(Product,Application,Environment,Node,Pool)
add_crud_for_named_models(CustomField,IssueType)

services.add(
    service(
        pattern=r'^issue_tracker_project/audit/{name}@{issue_tracker_name}\.{format}$',
        name="api-issue_tracker_project-audit",
        exposes=IssueTrackerProject.audit_log.all,
        get_for__name="name",
        get_for__issue_tracker_name="issue_tracker__name"
    ),
    service(
        pattern=r'^issue_tracker_project/one/{name}@{issue_tracker_name}\.{format}$',
        name="api-issue_tracker_project-one",
        exposes=IssueTrackerProject,
        get_for__name="name",
        get_for__issue_tracker_name="issue_tracker__name"
    ),
    # we're just going to have one list view here since hopefully issue tracker
    # project name clashes are rare!
    service(
        pattern=r'^issue_tracker_project/list/all\.{format}$',
        name="api-issue_tracker_project-list",
        exposes=IssueTrackerProject.objects.all
    ),
    issue_tracker_name=r'(?P<issue_tracker_name>[^/]{1,255})',
)

services.add(
    service(
        pattern=r'^issue/audit/{project_name}:{name}@{issue_tracker_name}\.{format}$',
        name="api-issue-audit",
        exposes=Issue.audit_log.all,
        get_for__name="name",
        get_for__project_name="project__name",
        get_for__issue_tracker_name="project__issue_tracker__name"
    ),
    service(
        # for jira this might be issue/one/PIPELINE:PIPELINE-213@forge-jira.xml, which is a
        # bit ugly, but a small price to pay for consistency...
        pattern=r'^issue/one/{project_name}:{name}@{issue_tracker_name}\.{format}$',
        name="api-issue-one",
        exposes=Issue,
        get_for__name="name",
        get_for__project_name="project__name",
        get_for__issue_tracker_name="project__issue_tracker__name"
    ),
    # we're just going to have one list view here since hopefully issue name clashes are rare!
    service(
        pattern=r'^issue/list/all\.{format}$',
        name="api-issue-list",
        exposes=Issue.objects.all
    ),
    project_name=r'(?P<project_name>[^/]{1,255})',
)

#services.add(
#    service(
#        pattern=r'^issue_type/one/{name}\.{format}$',
#        name="api-issue_type-one",
#        exposes=IssueType,
#        get_for__name="issue_type__name",
#    ),
#    service(
#        pattern=r'^issue_type/list/all\.{format}$',
#        name="api-issue_type-all",
#        exposes=IssueType.objects.all,
#    ),
#    service(
#        pattern=r'^custom_field/{name}\.{format}$',
#        name="api-custom_field-one",
#        exposes=CustomField,
#        get_for__name="custom_field__name",
#    ),
#    service(
#        pattern=r'^custom_field/list/all\.{format}$',
#        name="api-custom_field-all",
#        exposes=CustomField.objects.all,
#    ),
#)

services.add(
    service(
        pattern=r'^deployment_preference/audit/{environment_name}_{number}\.{format}$',
        name="api-deployment_preference-audit",
        exposes=DeploymentPreference.audit_log.all,
        get_for__environment_name="environment__name",
        get_for__number="preference_number"
    ),
    service(
        pattern=r'^deployment_preference/one/{environment_name}_{number}\.{format}$',
        name="api-deployment_preference-one",
        exposes=DeploymentPreference,
        get_for__environment_name="environment__name",
        get_for__number="preference_number"
    ),
    service(
        pattern=r'^deployment_preference/list/for/{environment_name}\.{format}$',
        name="api-deployment_preference-list-for-environment",
        exposes=DeploymentPreference.objects.all,
        get_for__environment_name="environment__name"
    ),
    service(
        pattern=r'^deployment_preference/list/all\.{format}$',
        name="api-deployment_preference-list",
        exposes=DeploymentPreference.objects.all
    ),
    environment_name=r'(?P<environment_name>[^/]{1,255})',
    number=r'(?P<number>[0-9]{1,11})',
)

services.add(
    service(
        pattern=r'^pool_membership/audit/{pool_name}_{node_name}\.{format}$',
        name="api-pool_membership-audit",
        exposes=PoolMembership.audit_log.all,
        get_for__pool_name="pool__name",
        get_for__node_name="node__name"
    ),
    service(
        pattern=r'^pool_membership/one/{pool_name}_{node_name}\.{format}$',
        name="api-pool_membership-one",
        exposes=PoolMembership,
        get_for__pool_name="pool__name",
        get_for__node_name="node__name"
    ),
    service(
        pattern=r'^pool_membership/list/for/{pool_name}\.{format}$',
        name="api-pool_membership-list-for-pool",
        exposes=PoolMembership.objects.all,
        get_for__pool_name="pool__name"
    ),
    service(
        pattern=r'^pool_membership/list/all\.{format}$',
        name="api-pool_membership-list",
        exposes=PoolMembership.objects.all
    ),
    pool_name=r'(?P<pool_name>[^/]{1,255})',
    node_name=r'(?P<node_name>[^/]{1,255})',
)

services.add(
    service(
        pattern=r'^node_address/audit/{name}@{address}\.{format}$',
        name="api-node_address-audit",
        exposes=NodeAddress.audit_log.all,
        get_for__name="node__name",
        get_for__address="address__address"
    ),
    service(
        pattern=r'^node_address/one/{name}@{address}\.{format}$',
        name="api-node_address-one",
        exposes=NodeAddress,
        get_for__name="node__name",
        get_for__address="address__address"
    ),
    service(
        pattern=r'^node_address/list/for/{name}\.{format}$',
        name="api-node_address-list-for-node",
        exposes=NodeAddress.objects.all,
        get_for__name="node__name"
    ),
    service(
        pattern=r'^node_address/list/all\.{format}$',
        name="api-node_address-list",
        exposes=NodeAddress.objects.all
    ),
)

add_crud_for_named_models(Role)

services.add(
    service(
        pattern=r'^role_membership/audit/{role_name}:{application_name}\.{format}$',
        name="api-role_membership-audit",
        exposes=RoleMembership.audit_log.all,
        get_for__role_name="role__name",
        get_for__application_name="application__name"
    ),
    service(
        pattern=r'^role_membership/one/{role_name}:{application_name}\.{format}$',
        name="api-role_membership-one",
        exposes=RoleMembership,
        get_for__role_name="role__name",
        get_for__application_name="application__name"
    ),
    service(
        pattern=r'^role_membership/list/for/{role_name}\.{format}$',
        name="api-role_membership-list-for-node",
        exposes=RoleMembership.objects.all,
        get_for__role_name="role__name"
    ),
    service(
        pattern=r'^role_membership/list/all\.{format}$',
        name="api-role_membership-list",
        exposes=RoleMembership.objects.all
    ),
    role_name=r'(?P<role_name>[^/]{1,255})',
    application_name=r'(?P<application_name>[^/]{1,255})',
)

add_crud_for_named_models(Version, VersionRange, audited=False)
add_crud_for_simple_id_models(VersionSpecification)

add_crud_for_named_models(PackageName, audited=False)

services.add(
    service(
        pattern=r'^package/audit/{name}@{version}\.{format}$',
        name="api-package-audit",
        exposes=Package.audit_log.all,
        get_for__name="name",
        get_for__version="version"
    ),
    service(
        pattern=r'^package/one/{name}@{version}\.{format}$',
        name="api-package-one",
        exposes=Package,
        get_for__name="name",
        get_for__version="version"
    ),
    service(
        pattern=r'^package/list/for/{name}\.{format}$',
        name="api-package-list",
        exposes=Package.objects.all,
        get_for__name="name"
    ),
    service(
        pattern=r'^package/list/all\.{format}$',
        name="api-package-list-all",
        exposes=Package.objects.all
    ),
    version=r'(?P<version>[^/]{1,50})',
)

add_crud_for_named_models(PackageRepository)

services.add(
    service(
        pattern=r'^package_location/audit/{name}@{version}:{repo_name}\.{format}$',
        name="api-package_location-audit",
        exposes=PackageLocation.audit_log.all,
        get_for__name="package__name",
        get_for__version="package__version",
        get_for__repo_name="repository__name"
    ),
    service(
        pattern=r'^package_location/one/{name}@{version}:{repo_name}\.{format}$',
        name="api-package_location-one",
        exposes=PackageLocation,
        get_for__name="package__name",
        get_for__version="package__version",
        get_for__repo_name="repository__name"
    ),
    service(
        pattern=r'^package_location/list/for/{name}@{version}\.{format}$',
        name="api-package_location-list",
        exposes=PackageLocation.objects.all,
        get_for__name="package__name",
        get_for__version="package__version"
    ),
    service(
        pattern=r'^package_location/list/all\.{format}$',
        name="api-package_location-list-all",
        exposes=PackageLocation.objects.all
    ),
    repo_name=r'(?P<repo_name>[^/]{1,255})',
)

add_crud_for_simple_id_models(PackageInstallation)

services.add(
    service(
        pattern=r'^build_job/audit/{name}@{build_server_name}\.{format}$',
        name="api-build_job-audit",
        exposes=BuildJob.audit_log.all,
        get_for__name="name",
        get_for__build_server_name="build_server__name"
    ),
    service(
        pattern=r'^build_job/one/{name}@{build_server_name}\.{format}$',
        name="api-build_job-one",
        exposes=BuildJob,
        get_for__name="name",
        get_for__build_server_name="build_server__name"
    ),
    service(
        pattern=r'^build_job/list/for/{name}\.{format}$',
        name="api-build_job-list",
        exposes=BuildJob.objects.all,
        get_for__name="name",
    ),
    service(
        pattern=r'^build_job/list/all\.{format}$',
        name="api-build_job-list-all",
        exposes=BuildJob.objects.all
    ),
    build_server_name=r'(?P<build_server_name>[^/]{1,255})',
)

services.add(
    service(
        pattern=r'^build_result/one/{job_name}:{build_number}@{build_server_name}\.{format}$',
        name="api-build_result-one",
        exposes=BuildResult,
        get_for__build_server_name="job__build_server__name",
        get_for__job_name="job__name",
        get_for__build_number="build_number"
    ),
    service(
        pattern=r'^build_result/list/for/{job_name}@{build_server_name}\.{format}$',
        name="api-build_result-list",
        exposes=BuildResult.objects.all,
        # log is excluded because it could mean _lots_ of data otherwise
        exclude_fields=('log',),
        get_for__build_server_name="job__build_server__name",
        get_for__job_name="job__name"
    ),
    service(
        pattern=r'^build_result/list/all\.{format}$',
        name="api-build_result-list-all",
        exposes=BuildResult.objects.all,
        # log is excluded because it could mean _lots_ of data otherwise
        exclude_fields=('log',)
    ),
    build_number=r'(?P<build_number>[0-9]{1,11})',
    job_name=r'(?P<job_name>[^/]{1,255})',
)

services.add(
    service(
        pattern=r'^recipe/audit/{name}@{deployment_system_name}\.{format}$',
        name="api-recipe-audit",
        exposes=Recipe.audit_log.all,
        get_for__name="name",
        get_for__deployment_system_name="deployment_system__name"
    ),
    service(
        pattern=r'^recipe/one/{name}@{deployment_system_name}\.{format}$',
        name="api-recipe-one",
        exposes=Recipe,
        get_for__name="name",
        get_for__deployment_system_name="deployment_system__name"
    ),
    service(
        pattern=r'^recipe/list/for/{name}\.{format}$',
        name="api-recipe-list",
        exposes=Recipe.objects.all,
        get_for__name="name",
    ),
    service(
        pattern=r'^recipe/list/all\.{format}$',
        name="api-recipe-list-all",
        exposes=Recipe.objects.all
    ),
    deployment_system_name=r'(?P<deployment_system_name>[^/]{1,255})',
)

services.add(
    service(
        pattern=r'^recipe_package/audit/{name}@{package_name}\.{format}$',
        name="api-recipe_package-audit",
        exposes=RecipePackage.audit_log.all,
        get_for__name="recipe__name",
        get_for__package_name="package__name"
    ),
    service(
        pattern=r'^recipe_package/one/{name}@{package_name}\.{format}$',
        name="api-recipe_package-one",
        exposes=RecipePackage,
        get_for__name="recipe__name",
        get_for__package_name="package__name"
    ),
    service(
        pattern=r'^recipe_package/list/for/{name}\.{format}$',
        name="api-recipe_package-list",
        exposes=RecipePackage.objects.all,
        get_for__name="recipe__name",
    ),
    service(
        pattern=r'^recipe_package/list/all\.{format}$',
        name="api-recipe_package-list-all",
        exposes=RecipePackage.objects.all
    ),
    package_name=r'(?P<package_name>[^/]{1,255})',
)

add_crud_for_simple_id_models(ProductDeployment, ApplicationDeployment, NodeDeployment)

add_crud_for_simple_id_models(PackageSpecification)
add_crud_for_simple_id_models(EnvironmentRequirement, Requirement, audited=True)

services.add(
    service(
        pattern=r'^release/audit/{product_name}@{release_version}\.{format}$',
        name="api-release-audit",
        exposes=Release.audit_log.all,
        get_for__product_name="product__name",
        get_for__release_version="version"
    ),
    service(
        pattern=r'^release/one/{product_name}@{release_version}\.{format}$',
        name="api-release-one",
        exposes=Release,
        get_for__product_name="product__name",
        get_for__release_version="version"
    ),
    service(
        pattern=r'^release/list/for/{product_name}\.{format}$',
        name="api-release-list",
        exposes=Release.objects.all,
        get_for__product_name="product__name",
    ),
    service(
        pattern=r'^release/list/all\.{format}$',
        name="api-release-list-all",
        exposes=Release.objects.all
    ),
    product_name=r'(?P<product_name>[^/]{1,128})',
    release_version=r'(?P<release_version>[^/]{1,128})',
)

services.add(
    service(
        pattern=r'^release_element/audit/{package_name}@{version}:{product_name}@{release_version}\.{format}$',
        name="api-release_element-audit",
        exposes=ReleaseElement.audit_log.all,
        get_for__package_name="package__name",
        get_for__version="package__version__name",
        get_for__product_name="release__product__name",
        get_for__release_version="release__version"
    ),
    service(
        pattern=r'^release_element/one/{package_name}@{version}:{product_name}@{release_version}\.{format}$',
        name="api-release_element-one",
        exposes=ReleaseElement,
        get_for__package_name="package__name",
        get_for__version="package__version__name",
        get_for__product_name="release__product__name",
        get_for__release_version="release__version"
    ),
    service(
        pattern=r'^release_element/list/for/{product_name}@{release_version}\.{format}$',
        name="api-release_element-list",
        exposes=ReleaseElement.objects.all,
        get_for__product_name="release__product__name",
        get_for__release_version="release__version"
    ),
    service(
        pattern=r'^release_element/list/all\.{format}$',
        name="api-release_element-list-all",
        exposes=ReleaseElement.objects.all
    ),
    package_name=r'(?P<package_name>[^/]{1,255})',
)

services.add(
    service(
        pattern=r'^deployment_request/audit/{product_name}@{release_version}:{environment_name}\.{format}$',
        name="api-deployment_request-audit",
        exposes=DeploymentRequest.audit_log.all,
        get_for__product_name="release__product__name",
        get_for__release_version="release__version",
        get_for__environment_name="environment__name",
    ),
    service(
        pattern=r'^deployment_request/one/{product_name}@{release_version}:{environment_name}\.{format}$',
        name="api-deployment_request-one",
        exposes=DeploymentRequest,
        get_for__product_name="release__product__name",
        get_for__release_version="release__version",
        get_for__environment_name="environment__name",
    ),
    service(
        pattern=r'^deployment_request/list/all\.{format}$',
        name="api-deployment_request-all",
        exposes=DeploymentRequest.objects.all,
    ),
)

services.add(
    service(
        pattern=r'^crichton_cron_job_status/one/{name}\.{format}$',
        name="api-crichton_cron_job_status-one",
        exposes=crichtonCronJobStatus,
        get_for__name="name",
    ),
    service( 
        pattern=r'^crichton_cron_job_status/list/all\.{format}$',
        name="api-crichton_cron_job_status-all",
        exposes=crichtonCronJobStatus.objects.all, 
    ),
)

urlpatterns = services.get_documentation_url_patterns()
urlpatterns += services.get_index_url_patterns()
urlpatterns += patterns('',
    (r'^deployment_request/one/for/fab/(?P<product_name>[^/]{1,255})@(?P<release_version>[^/]{1,255}):(?P<environment_name>[^/]{1,255})\.json$',
        'api.fabsupport.deployment_request'),
)
urlpatterns += services.get_url_patterns()
