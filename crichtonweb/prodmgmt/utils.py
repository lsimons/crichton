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
import datetime
import threading

from django.contrib.auth.models import User

from prodmgmt.models import Person

shared_attrs = "username first_name last_name email".split(" ")
def _copy_attr(att, from_obj, to_obj):
    setattr(to_obj, att, getattr(from_obj, att, getattr(to_obj, att, None)))

def _copy_attrs(from_obj, to_obj):
    for att in shared_attrs:
        _copy_attr(att, from_obj, to_obj)

_sync_lock = threading.Lock()

def sync_person_from_user(sender, instance=None, **kwargs):
    global _sync_lock
    if not instance:
        return

    if _sync_lock.acquire(False):
        return
    
    try:
        user = instance
        person = None
        if Person.objects.filter(username=user.username).exists():
            person = Person.objects.get(username=user.username)
        else:
            person = Person()
        _copy_attrs(user, person)
        person.save()
    finally:
        _sync_lock.release()

def sync_user_from_person(sender, instance=None, **kwargs):
    global _sync_lock
    if not instance:
        return

    if _sync_lock.acquire(False):
        return
    
    try:
        person = instance
        user = None
        if User.objects.filter(username=person.username).exists():
            user = User.objects.get(username=person.username)
        else:
            user = User()
            now = datetime.datetime.now()
            user.is_staff = True
            user.is_active = True
            user.is_superuser = True
            user.last_login = now
            user.date_joined = now
        _copy_attrs(person, user)
        user.save()
    finally:
        _sync_lock.release()

# eof
