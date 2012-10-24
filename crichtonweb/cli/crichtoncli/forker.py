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
from django.db import close_connection
from crichtonweb.core.utils import gc_collect

def run_all(workers, numworkers=1):
    """Given a workers iterable, of subprocess.Process instances, start() them all, numworkers
    at a time, and wait for all of them to finish.
    
    This provides an alternative to the common approach of using multiprocessing.Queue. This
    approach has the disadvantage that it spawns many more child processes, but the upside is
    that this helps control memory growth / fragmentation."""
    close_connection() # close before fork()
    gc_collect() # clean up before fork()

    active_workers = {}
    i = 0
    workers_it = iter(workers)
    while len(active_workers) < numworkers:
        try:
            worker = workers_it.next()
        except StopIteration:
            break
        worker.start()
        active_workers[i] = worker
        i += 1
        
        # reap through processes and clean up ones that are done
        for key in active_workers.keys():
            old_worker = active_workers[key]
            if old_worker.exitcode is not None:
                active_workers.pop(key)

        # don't want to spawn any more processes, so wait for one to finish
        if len(active_workers) == numworkers:
            key, old_worker = active_workers.popitem()
            old_worker.join(60)

    # wait for all workers to finish their last task
    while len(active_workers) > 0:
        key, old_worker = active_workers.popitem()
        old_worker.join()
