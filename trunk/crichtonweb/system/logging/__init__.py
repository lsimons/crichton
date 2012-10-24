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
"""Sets up default logger instance for both crichtonweb and crichtoncron.

Example usage:
from system.logging import web_log as logger
logger.error("oops")

Defines SafeRotatingFileHandler.
"""

import os
import sys
import fcntl
import stat
import errno
import time
import logging
import logging.handlers

class LockError(Exception):
    pass

def lock(f, timeout=0.02):
    locked = False
    slept = 0.0
    sleeptime = timeout/10
    while not locked and slept < timeout:
        try:
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            locked = True
        except IOError, e:
            if e.errno == errno.EACCES or e.errno == errno.EAGAIN:
                time.sleep(sleeptime)
                slept += sleeptime
    if not locked:
        raise LockError("Could not lock %s in %s seconds" % (f.name, timeout))

def unlock(f):
    fcntl.lockf(f, fcntl.LOCK_UN)

class SafeRotatingFileHandler(logging.Handler):
    """A custom, safe rotating file handler. This logger is like RotatingFileHandler, but
    * uses rw/rw/rw permissions for the files it creates
    * does not raise an exception if it cannot write to a file
    * should be multiprocess-safe through the use of a file lock
    """
    
    # inspired by http://stackoverflow.com/questions/1407474/
    # inspired by http://pypi.python.org/pypi/ConcurrentLogHandler
    # works only on unix

    def __init__(self, filename, lock_timeout=0.02, maxBytes=0, backupCount=0, level=logging.NOTSET):
        logging.Handler.__init__(self, level=logging.NOTSET)
        self.filename = os.path.abspath(filename)
        self.lock_filename = filename + ".lock"
        self.temp_filename = filename + ".rolltmp"
        self.lock_timeout = lock_timeout
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.stream = None
        self.lock_file = None
        self.open_lock_file()
        self.open_stream()
    
    def open_lock_file(self):
        try:
            self.lock_file = open(self.lock_filename, 'w')
            self.ensure_writeable(self.lock_filename)
        except (IOError, OSError):
            try:
                t, value, traceback = sys.exc_info()
                sys.stderr.write("ERROR: %s: %s (log lockfile open failed)\n" % (t.__name__, value))
            except (IOError, OSError):
                pass
    
    def close_lock_file(self):
        if self.lock_file is not None:
            try:
                try:
                    self.lock_file.close()
                    self.lock_file = None
                except (IOError, OSError):
                    try:
                        t, value, traceback = sys.exc_info()
                        sys.stderr.write("ERROR: %s: %s (log lockfile close failed)\n" % (t.__name__, value))
                    except (IOError, OsError):
                        pass
            finally:
                self.lock_file = None
    
    def open_stream(self):
        if self.stream is None:
            try:
                self.stream = open(self.filename, 'a')
                self.ensure_writeable(self.filename)
            except (IOError, OSError):
                try:
                    t, value, traceback = sys.exc_info()
                    sys.stderr.write("ERROR: %s: %s (logfile open failed)\n" % (t.__name__, value))
                except (IOError, OSError):
                    pass
    
    def close_stream(self):
        if self.stream is not None:
            try:
                try:
                    self.stream.close()
                except (IOError, OSError):
                    try:
                        t, value, traceback = sys.exc_info()
                        sys.stderr.write("ERROR: %s: %s (logfile close failed)\n" % (t.__name__, value))
                    except (IOError, OsError):
                        pass
            finally:
                self.stream = None
    
    def flush_stream(self):
        if self.stream is not None:
            try:
                self.stream.flush()
            except (IOError, OSError):
                pass
    
    def acquire(self):
        logging.Handler.acquire(self)
        lock(self.lock_file, timeout=self.lock_timeout)
    
    def release(self):
        try:
            self.flush_stream()
            unlock(self.lock_file)
        finally:
            logging.Handler.release(self)
    
    def close(self):
        self.close_lock_file()
        self.close_stream()
        logging.Handler.close(self)

    def emit(self, record):
        if self.should_rollover():
            self.do_rollover()
        
        msg = self.format(record) + "\n"
        msg = msg.encode("UTF-8")
        self.open_stream()

        if self.stream is not None:
            try:
                self.stream.write(msg)
            except (IOError, OsError):
                try:
                    sys.stderr.write("ERROR: should have logged: " + msg)
                except (IOError, OsError):
                    pass
        else:
            try:
                sys.stderr.write("ERROR: should have logged: " + msg)
            except (IOError, OsError):
                pass
    
    def handle(self, record):
        rv = self.filter(record)
        if rv:
            try:
                self.acquire()
                try:
                    self.emit(record)
                finally:
                    self.release()
            except LockError:
                try:
                    t, value, traceback = sys.exc_info()
                    sys.stderr.write("ERROR: %s: %s (acquiring log lockfile lock failed)\n" % (t.__name__, value))
                    msg = self.format(record)
                    sys.stderr.write("ERROR: should have logged: %s" % msg.encode("UTF-8"))
                except (IOError, OSError):
                    pass
        return rv

    def flush(self):
        pass # flush happens on every release()
    
    def should_rollover(self):
        if self._should_rollover():
            # maybe someone else rolled over for us already, check
            # we should be holding the lock right now
            # so close the log file, re-open it, and check the file
            # (which is now the right one)
            self.close_stream()
            self.open_stream()
            return self._should_rollover()
    
    def _should_rollover(self):
        if self.maxBytes > 0 and self.stream is not None:
            self.stream.seek(0, 2)
            if self.stream.tell() >= self.maxBytes:
                return True
        return False
    
    def do_rollover(self):
        if self.stream is None:
            return
        if self.backupCount <= 0:
            self.close_stream()
            return
        self.close_stream()
        
        if os.path.exists(self.temp_filename):
            sys.stderr.write("ERROR: %s exists. Pretty confused. Not rolling log file." % self.temp_filename)
            return
        
        try:
            os.rename(self.filename, self.temp_filename)
        except (IOError, OSError):
            t, value, traceback = sys.exc_info()
            sys.stderr.write("ERROR: %s: %s (cannot roll log files)\n" % (t.__name__, value))
            return
        
        for i in range(self.backupCount - 1, 0, -1):
            curr_file = "%s.%d" % (self.filename, i)
            if os.path.exists(curr_file):
                next_file = "%s.%d" % (self.filename, i + 1)
                try:
                    if os.path.exists(next_file):
                        os.remove(next_file)
                    os.rename(curr_file, next_file)
                except (IOError, OSError):
                    t, value, traceback = sys.exc_info()
                    sys.stderr.write("ERROR: %s: %s (cannot roll log files)\n" % (t.__name__, value))
                    try:
                        os.path.rename(tmpname, self.filename)
                    except (IOErorr, OSError):
                        t, value, traceback = sys.exc_info()
                        sys.stderr.write("ERROR: %s: %s (cannot move log file back into place)\n" % (t.__name__, value))
                    return
        next_file = "%s.1" % self.filename
        try:
            if os.path.exists(next_file):
                os.remove(next_file)
            os.rename(self.temp_filename, next_file)
        except (IOError, OSError):
            t, value, traceback = sys.exc_info()
            sys.stderr.write("ERROR: %s: %s (cannot roll log files)\n" % (t.__name__, value))
            try:
                os.path.rename(self.temp_filename, self.filename)
            except (IOErorr, OSError):
                t, value, traceback = sys.exc_info()
                sys.stderr.write("ERROR: %s: %s (cannot move log file back into place)\n" % (t.__name__, value))

    def ensure_writeable(self, fname):
        try:
            current_perms = os.stat(fname).st_mode
            new_perms = current_perms | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
            os.chmod(fname, new_perms)
        except (IOError, OSError):
            pass

# http://mail.python.org/pipermail/python-list/2007-October/513796.html
logging.handlers.SafeRotatingFileHandler = SafeRotatingFileHandler

web_log = logging.getLogger('crichtonweb')
cron_log = logging.getLogger('crichtoncron')
cli_log = logging.getLogger('crichtoncli')
