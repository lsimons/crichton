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
# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'IssueType'
        db.create_table('jirarpc_issuetype', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45, primary_key=True)),
            ('jira_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('jirarpc', ['IssueType'])

        # Adding model 'CustomField'
        db.create_table('jirarpc_customfield', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45, primary_key=True)),
            ('jira_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('jirarpc', ['CustomField'])


    def backwards(self, orm):
        
        # Deleting model 'IssueType'
        db.delete_table('jirarpc_issuetype')

        # Deleting model 'CustomField'
        db.delete_table('jirarpc_customfield')


    models = {
        'jirarpc.customfield': {
            'Meta': {'ordering': "('name',)", 'object_name': 'CustomField'},
            'jira_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45', 'primary_key': 'True'})
        },
        'jirarpc.issuetype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'IssueType'},
            'jira_id': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45', 'primary_key': 'True'})
        }
    }

    complete_apps = ['jirarpc']
