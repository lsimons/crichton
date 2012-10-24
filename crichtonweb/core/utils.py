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
import gc

from django.db import transaction

def gc_collect():
    """Try to collect generation 2, falling back to normal gc collect
    if this python instance doesn't support that."""
    try:
        gc.collect(2)
    except TypeError:
        gc.collect()

def commit_or_rollback(func):
    """Decorator that tries to commit at the end of a function, or rollback
    if there was an exception."""
    @transaction.commit_manually
    def f(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except:
            try:
                transaction.rollback()
            except:
                pass
            raise
        else:
            transaction.commit()
        return result
    return f

def rollback(func):
    """Decorator that rolls back at the end of a function."""
    @transaction.commit_manually
    def f(*args, **kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except:
            try:
                transaction.rollback()
            except:
                pass
            raise
        else:
            transaction.rollback()
        return result
    return f
