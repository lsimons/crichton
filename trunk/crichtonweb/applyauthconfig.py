#!/usr/bin/env python
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

# Script that applies settings.AUTH_CONFIG to the database

import sys
from os import path
from os.path import dirname, abspath

thisdir = dirname(abspath(__file__))

crichtonwebdir = "/usr/local/crichtonweb"
if path.exists(crichtonwebdir):
    sys.path.insert(0, abspath(path.join(crichtonwebdir, "..")))
    sys.path.insert(0, crichtonwebdir)

crichtonwebdir = abspath(thisdir)
if path.exists(crichtonwebdir):
    sys.path.insert(0, abspath(path.join(crichtonwebdir, "..")))
    sys.path.insert(0, crichtonwebdir)

# django initialization
#   http://www.b-list.org/weblog/2007/sep/22/standalone-django-scripts/
from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.contrib.auth.models import User, Group, Permission
from django.db import transaction
from django.db.models import get_models
from crichtonweb.core.utils import commit_or_rollback, rollback

@commit_or_rollback
def ensure_group(name):
    group, created = Group.objects.get_or_create(name=name)
    return group

@rollback
def ensure_groups(groups):
    for group in groups:
        print "ensure_group", group
        ensure_group(group)

@commit_or_rollback
def ensure_group_member(user, group):
    if isinstance(user, str) or isinstance(user, unicode):
        user = User.objects.get(username=user)
        transaction.rollback()
    if isinstance(group, str) or isinstance(group, unicode):
        group = ensure_group(group)
    
    if user.groups.filter(name=group.name).exists():
        return
    user.groups.add(group)
    user.save()
    transaction.commit()

@commit_or_rollback
def ensure_superuser(username, email, **kwargs):
    password = 'password'
    try:
        email_name, domain_part = email.strip().split('@', 1)
    except ValueError:
        pass
    else:
        email = '@'.join([email_name, domain_part.lower()])
    
    try:
        user = User.objects.get(username=username)
        user.email = email
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.set_password(password)
    except User.DoesNotExist:
        user = User.objects.create_superuser(username, email, password)
    
    for k, v in kwargs.iteritems():
        if k in ["username", "email"]:
            continue
        if not hasattr(user, k):
            raise Exception("User does not have property %s" % k)
        setattr(user, k, v)
    user.save()
    ensure_group_member(user, "Administrators")

@rollback
def ensure_superusers(superusers):
    for superuser in superusers:
        username = superuser["username"]
        email = superuser["email"]
        del superuser["username"], superuser["email"]
        print "ensure_superuser", username, email
        ensure_superuser(username, email, **superuser)

@rollback
def make_everyone_a_user():
    user_group = ensure_group("Users")
    for user in User.objects.all():
        ensure_group_member(user, user_group)

@commit_or_rollback
def ensure_group_permission(group, permission):
    if isinstance(group, str) or isinstance(group, unicode):
        group = ensure_group(group)
    if group.permissions.filter(id=permission.id).exists():
        return
    group.permissions.add(permission)
    group.save()

@rollback
def grant_permission(group, action, model):
    print "grant_permission", group, action, model
    codename = "%s_%s" % (action, model.split(".", 1)[1].lower())
    permission = Permission.objects.get(codename=codename)
    ensure_group_permission(group, permission)

@rollback
def grant_group_permissions(permissions):
    for instruction in list(permissions):
        group = instruction["group"]
        grants = instruction["grants"]
        inherit_from = instruction.get("inherit_from", [])
        for other_group in inherit_from:
            if other_group == group:
                continue
            for instruction in permissions:
                if instruction["group"] == other_group:
                    grants.extend(instruction["grants"])
        for grant in grants:
            actions = grant["actions"]
            models = grant["models"]
            for model in models:
                for action in actions:
                    grant_permission(group, action, model)

@rollback
def apply_config(auth_config):
    groups = auth_config.get("groups", [])
    ensure_groups(groups)

    superusers = auth_config.get("superusers", [])
    ensure_superusers(superusers)

    group_permissions = auth_config.get("group_permissions", [])
    grant_group_permissions(group_permissions)

    make_everyone_a_user()

if __name__ == "__main__":
    auth_config = settings.AUTH_CONFIG
    apply_config(auth_config)
