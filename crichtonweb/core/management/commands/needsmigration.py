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
import sys
from optparse import make_option

from django.core.management.base import BaseCommand

from south import migration
from south.models import MigrationHistory

class Command(BaseCommand):
    help = "Checks to see if there are any pending migrations for all apps."
    
    def handle(*args, **kwargs):
        needs_migration = False
        
        apps = list(migration.all_migrations())
        applied_migrations = [(x.app_name, x.migration) for x in list(MigrationHistory.objects.all())]
        
        for app in apps:
            for mi in app:
                app_label = mi.app_label()
                migration_name = mi.name()
                if (app_label, migration_name) not in applied_migrations:
                    needs_migration = True
                    print "Migration needed for %s: %s" % (app_label, migration_name)
        
        if needs_migration:
            print "Migration needed."
            sys.exit(1)
        else:
            print "No migration needed."
            sys.exit(0)
