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
import os
from subprocess import call
from tempfile import mkdtemp
from shutil import rmtree

from crichtonweb.requirement.models import Requirement, EnvironmentRequirement
from crichtonweb.requirement.models import PackageSpecification, VersionSpecification
from crichtonweb.system.models import Pool, PoolMembership, Node, Role, Environment
from crichtonweb.requirement.actions import validate_requirements
from crichtonweb.requirement.svn import *
from crichtonweb.core.utils import rollback

@rollback
def write_pool_pp(fname, pool):
    f = open(fname, 'w')
    f.write("class ")
    f.write(pool.puppet_name)
    f.write(" {\n")
    for app_member in pool.role.applications.filter(deleted=False).order_by('application__name'):
        app = app_member.application
        f.write("    include ")
        f.write(pool.puppet_application_name(app))
        f.write("\n")
    f.write("}\n")
    f.close()

@rollback
def write_systems_pp(fname, pools):
    f = open(fname, 'w')
    for pool in pools:
        f.write('node ')
        node_names = []
        for membership in pool.members.filter(deleted=False).order_by('node__name'):
            node = membership.node
            if node.deleted:
                continue
            node_names.append(node.name.split(".")[0]) # todo should we use short/unqualified name?
        f.write(", ".join(node_names))
        f.write(" { include ")
        f.write(pool.puppet_name)
        f.write(" }\n")
    f.close()

@rollback
def write_role_pp(fname, role):
    f = open(fname, 'w')
    f.write("class ")
    f.write(role.puppet_name)
    f.write(" {\n}\n")
    f.close()

@rollback
def write_role_env_pp(fname, role, environment):
    f = open(fname, 'w')
    f.write("class ")
    f.write(role.puppet_environment_name(environment))
    f.write(" inherits ")
    f.write(role.puppet_name)
    f.write(" {\n}\n")
    f.close()

@rollback
def _get_specs(env, app):
    specs = []
    for req in Requirement.objects.filter(deleted=False, application=app):
        req_qs = list(req.environment_requirements.filter(deleted=False, environment=env))
        if req_qs:
            for env_req in req_qs:
                spec = env_req.specification
                specs.append(spec)
        else:
            spec = req.default_specification
            if spec and not spec.deleted:
                specs.append(spec)
    return specs

def _find_edit_manifest_cmd():
    edit_manifest = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "edit_manifest_package.rb"))
    if not os.path.exists(edit_manifest):
        edit_manifest = "/usr/local/crichtonweb/edit_manifest_package.rb"
        if not os.path.exists(edit_manifest):
            edit_manifest = "/usr/local/bin/edit_manifest_package.rb"
            if not os.path.exists(edit_manifest):
                edit_manifest = "edit_manifest_package.rb"
    return edit_manifest

def write_app_pp(fname, role, env, app, logger=None):
    specs = _get_specs(env, app)

    edit_manifest = _find_edit_manifest_cmd()
    classname = role.puppet_application_name(app, env)
    parent = role.puppet_environment_name(env)

    cmd = [edit_manifest, classname, fname]
    if parent:
        cmd.append("--parent=%s" % parent)
    
    for pspec in specs:
        package_name = pspec.package.name
        vspec = pspec.version_specification
        if vspec:
            version_name = vspec.version.name
        else:
            version_name = "latest"
        cmd.append("%s=%s" % (package_name, version_name))
    
    if logger: logger("+ " + " ".join(cmd))
    retcode = call(cmd)
    if retcode:
        raise CommandError("Error occurred writing puppet manifest %s" % fname)

@rollback
def update_puppet_working_copy(repodir, pools, roles, environments, logger=None):
    pooldir = os.path.join(repodir, "pools")
    ensure_svn_dir(pooldir, logger=logger)
    
    for pool in pools:
        pool_pp = os.path.join(pooldir, pool.puppet_file_name)
        if logger: logger("writing pool file %s" % os.path.basename(pool_pp))
        ensure_svn_file(pool_pp, logger=logger)
        write_pool_pp(pool_pp, pool)
    
    systemdir = os.path.join(repodir, "systems")
    ensure_svn_dir(systemdir, logger=logger)
    
    systems_pp = os.path.join(systemdir, "systems.pp")
    if logger: logger("writing systems file %s" % os.path.basename(systems_pp))
    ensure_svn_file(systems_pp, logger=logger)
    write_systems_pp(systems_pp, pools)
    
    rolebasedir = os.path.join(repodir, "roles")
    ensure_svn_dir(rolebasedir, logger=logger)
    for role in roles:
        roledir = os.path.join(rolebasedir, role.name)
        ensure_svn_dir(roledir, logger=logger)
        
        role_pp = os.path.join(roledir, role.puppet_file_name)
        if not os.path.exists(role_pp):
            if logger: logger("writing role file %s" % os.path.basename(role_pp))
            ensure_svn_file(role_pp, logger=logger)
            write_role_pp(role_pp, role)
        
        for env in environments:
            envdir = os.path.join(roledir, env.name)
            ensure_svn_dir(envdir, logger=logger)
            
            role_env_pp = os.path.join(envdir, role.puppet_environment_file_name(env))
            if not os.path.exists(role_env_pp):
                if logger: logger("writing role_env file %s" % os.path.basename(role_env_pp))
                ensure_svn_file(role_env_pp, logger=logger)
                write_role_env_pp(role_env_pp, role, env)
            
            for app_member in role.applications.filter(deleted=False):
                app = app_member.application
                app_pp = os.path.join(envdir, role.puppet_application_file_name(app, env))
                ensure_svn_file(app_pp, logger=logger)
                if logger: logger("writing role_env_app file %s" % os.path.basename(app_pp))
                write_app_pp(app_pp, role, env, app, logger=logger)

@rollback
def update_puppet_svn(svnurl, confirmer=None, logger=None):
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
    
    pools = list(Pool.objects.filter(deleted=False).order_by('name'))
    roles = list(Role.objects.filter(deleted=False).order_by('name'))
    environments = list(Environment.objects.filter(deleted=False).order_by('name'))
    
    validate_requirements(pools, roles, environments)
    
    logger("")
    
    basedir = mkdtemp("crichton_puppetinit")
    try:
        targetname = "repo"
        repodir = os.path.join(basedir, "repo")
        
        checkout(basedir, svnurl, targetname, logger=logger)
        
        update_puppet_working_copy(repodir, pools, roles, environments, logger=logger)
        
        logger("Changes:")
        logger("")
        diff(repodir, logger=logger)
        
        logger("")
        if confirmer:
            confirmer()
        
        commit(repodir, "Applying changes from crichton.", logger=logger)
    except:
        logger("")
        logger("Left unfinished changes in working directory %s" % basedir)
        raise
    else:
        logger("")
        logger("Changes committed to SVN. You probably want to run puppet now.")
        rmtree(basedir)
