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

# South introspection rules for django-audit-log
#       from http://south.aeracode.org/ticket/693
# can probably removed when south goes 1.0 (using 0.7)
# invoked from models.py
from south.modelsinspector import add_introspection_rules
from django.contrib.auth.models import User

__rules_added = False
def add_rules():
    global __rules_added
    if __rules_added:
        return
    __rules_added = True
    
    try:
        # Try and import the field so we can see if audit_log is available
        from audit_log.models import fields

        # Make sure the `to` and `null` parameters will be ignored
        rules = [(
            (fields.LastUserField,),
            [],
            {
                'to': ['rel.to', {'default': User}],
                'null': ['null', {'default': True}],
            },
        )]

        # Add the rules for the `LastUserField`
        add_introspection_rules(
            rules,
            ['^audit_log\.models\.fields\.LastUserField'],
        )
        
        # Add the rules for the `CompressedTextField`
        add_introspection_rules([], ["^core\.fields\.CompressedTextField"])
    except ImportError:
        pass
