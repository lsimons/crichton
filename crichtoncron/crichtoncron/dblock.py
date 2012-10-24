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
from threading import Lock
import MySQLdb
from MySQLdb.constants import CLIENT

from crichtoncron import crichtonweb_settings

_dbconf = crichtonweb_settings.DATABASES['default']
_do_db_lock = True
if _dbconf['ENGINE'] != 'django.db.backends.mysql':
    _do_db_lock = False

def get_connection():
    # the below inspired by django.db.backends.mysql.base
    kwargs = {
        'charset': 'utf8',
        'use_unicode': True,
    }
    if _dbconf['USER']:
        kwargs['user'] = _dbconf['USER']
    if _dbconf['NAME']:
        kwargs['db'] = _dbconf['NAME']
    if _dbconf['PASSWORD']:
        kwargs['passwd'] = _dbconf['PASSWORD']
    if _dbconf['HOST'].startswith('/'):
        kwargs['unix_socket'] = _dbconf['HOST']
    elif _dbconf['HOST']:
        kwargs['host'] = _dbconf['HOST']
    if _dbconf['PORT']:
        kwargs['port'] = int(_dbconf['PORT'])
    kwargs['client_flag'] = CLIENT.FOUND_ROWS
    return MySQLdb.connect(**kwargs)

def initdb():
    connection = get_connection()
    try:
        cursor = connection.cursor()

        table_exists = False
        try:
            cursor.execute("SHOW CREATE TABLE crichtoncron;")
            table_exists = True
        except:
            connection.rollback()

        if not table_exists:
            try:
                cursor.execute("CREATE TABLE crichtoncron (cronid varchar(128) not null primary key) ENGINE=InnoDB;")
                connection.commit()
            except MySQLdb.OperationalError:
                connection.rollback()
                # we are assuming it was there already so swallowing
    finally:
        try:
            connection.close()
        except:
            pass

_lock = None
_lock_name = None
_threadlock = Lock()

def lock(command):
    global _lock, _lock_name, _threadlock
    _threadlock.acquire()
    try:
        connection = get_connection()
        if _lock:
            if _lock_name and command != _lock_name:
                raise Exception("Locked %s, cannot also lock %s" % (_lock_name, command))
            else:
                _lock.execute("SELECT TRUE;")
                return
        if _lock_name and _lock_name != command:
            raise Exception("Locked %s, cannot also lock %s" % (_lock_name, command))
        
        cursor = connection.cursor()
        cursor.execute("INSERT IGNORE INTO crichtoncron (cronid) VALUES (%s)", [command])
        cursor.execute("SELECT * FROM crichtoncron WHERE cronid = %s FOR UPDATE", [command])
        _lock = connection
    finally:
        _threadlock.release()

def unlock(command):
    global _lock, _lock_name, _threadlock
    _threadlock.acquire()
    try:
        if not _lock:
            return
        if _lock_name and _lock_name != command:
            raise Exception("Locked %s but trying to release %s" % (_lock_name, command))
        
        _lock.rollback()
        _lock.close()
        _lock = None
        _lock_name = None
    finally:
        _threadlock.release()
