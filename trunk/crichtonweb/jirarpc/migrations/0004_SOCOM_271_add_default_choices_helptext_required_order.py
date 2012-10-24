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
        
        # Adding field 'CustomFieldAuditLogEntry.default'
        db.add_column('jirarpc_customfieldauditlogentry', 'default', self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True), keep_default=False)

        # Adding field 'CustomFieldAuditLogEntry.choices'
        db.add_column('jirarpc_customfieldauditlogentry', 'choices', self.gf('django.db.models.fields.CharField')(default='', max_length=1024, blank=True), keep_default=False)

        # Adding field 'CustomFieldAuditLogEntry.helptext'
        db.add_column('jirarpc_customfieldauditlogentry', 'helptext', self.gf('django.db.models.fields.CharField')(default='', max_length=1024, blank=True), keep_default=False)

        # Adding field 'CustomFieldAuditLogEntry.required'
        db.add_column('jirarpc_customfieldauditlogentry', 'required', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)

        # Adding field 'CustomFieldAuditLogEntry.order'
        db.add_column('jirarpc_customfieldauditlogentry', 'order', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding field 'CustomField.default'
        db.add_column('jirarpc_customfield', 'default', self.gf('django.db.models.fields.CharField')(default='', max_length=40, blank=True), keep_default=False)

        # Adding field 'CustomField.choices'
        db.add_column('jirarpc_customfield', 'choices', self.gf('django.db.models.fields.CharField')(default='', max_length=1024, blank=True), keep_default=False)

        # Adding field 'CustomField.helptext'
        db.add_column('jirarpc_customfield', 'helptext', self.gf('django.db.models.fields.CharField')(default='', max_length=1024, blank=True), keep_default=False)

        # Adding field 'CustomField.required'
        db.add_column('jirarpc_customfield', 'required', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)

        # Adding field 'CustomField.order'
        db.add_column('jirarpc_customfield', 'order', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'CustomFieldAuditLogEntry.default'
        db.delete_column('jirarpc_customfieldauditlogentry', 'default')

        # Deleting field 'CustomFieldAuditLogEntry.choices'
        db.delete_column('jirarpc_customfieldauditlogentry', 'choices')

        # Deleting field 'CustomFieldAuditLogEntry.helptext'
        db.delete_column('jirarpc_customfieldauditlogentry', 'helptext')

        # Deleting field 'CustomFieldAuditLogEntry.required'
        db.delete_column('jirarpc_customfieldauditlogentry', 'required')

        # Deleting field 'CustomFieldAuditLogEntry.order'
        db.delete_column('jirarpc_customfieldauditlogentry', 'order')

        # Deleting field 'CustomField.default'
        db.delete_column('jirarpc_customfield', 'default')

        # Deleting field 'CustomField.choices'
        db.delete_column('jirarpc_customfield', 'choices')

        # Deleting field 'CustomField.helptext'
        db.delete_column('jirarpc_customfield', 'helptext')

        # Deleting field 'CustomField.required'
        db.delete_column('jirarpc_customfield', 'required')

        # Deleting field 'CustomField.order'
        db.delete_column('jirarpc_customfield', 'order')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'jirarpc.customfield': {
            'Meta': {'ordering': "('name',)", 'object_name': 'CustomField'},
            'choices': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'default': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'helptext': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'jira_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45', 'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'char'", 'max_length': '4'})
        },
        'jirarpc.customfieldauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'CustomFieldAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_customfield_audit_log_entry'"}),
            'choices': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'default': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'blank': 'True'}),
            'helptext': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'jira_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45', 'db_index': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'char'", 'max_length': '4'})
        },
        'jirarpc.issuetype': {
            'Meta': {'ordering': "('name',)", 'object_name': 'IssueType'},
            'jira_id': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45', 'primary_key': 'True'})
        },
        'jirarpc.issuetypeauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'IssueTypeAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_issuetype_audit_log_entry'"}),
            'jira_id': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45', 'db_index': 'True'})
        }
    }

    complete_apps = ['jirarpc']
