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
        
        # Adding model 'BuildJobAuditLogEntry'
        db.create_table('ci_buildjobauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('build_server', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_jobs', to=orm['ci.BuildServer'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='_auditlog_build_jobs', null=True, to=orm['prodmgmt.Product'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_buildjob_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('ci', ['BuildJobAuditLogEntry'])

        # Adding model 'BuildJob'
        db.create_table('ci_buildjob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('build_server', self.gf('django.db.models.fields.related.ForeignKey')(related_name='jobs', to=orm['ci.BuildServer'])),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='build_jobs', null=True, to=orm['prodmgmt.Product'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ci', ['BuildJob'])

        # Adding unique constraint on 'BuildJob', fields ['name', 'build_server']
        db.create_unique('ci_buildjob', ['name', 'build_server_id'])

        # Adding model 'BuildResultAuditLogEntry'
        db.create_table('ci_buildresultauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('build_number', self.gf('django.db.models.fields.IntegerField')()),
            ('succeeded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('finished_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('log', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_results', to=orm['ci.BuildJob'])),
            ('produced_package', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='_auditlog_builds', null=True, to=orm['package.Package'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_buildresult_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('ci', ['BuildResultAuditLogEntry'])

        # Adding model 'BuildResult'
        db.create_table('ci_buildresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('build_number', self.gf('django.db.models.fields.IntegerField')()),
            ('succeeded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('finished_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('log', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('job', self.gf('django.db.models.fields.related.ForeignKey')(related_name='results', to=orm['ci.BuildJob'])),
            ('produced_package', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='builds', null=True, to=orm['package.Package'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ci', ['BuildResult'])

        # Adding unique constraint on 'BuildResult', fields ['job', 'build_number']
        db.create_unique('ci_buildresult', ['job_id', 'build_number'])

        # Adding model 'BuildServerAuditLogEntry'
        db.create_table('ci_buildserverauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=128, db_index=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('build_server_type', self.gf('django.db.models.fields.CharField')(default='hudson', max_length=12)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('build_job_pattern', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_buildserver_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('ci', ['BuildServerAuditLogEntry'])

        # Adding model 'BuildServer'
        db.create_table('ci_buildserver', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=128, db_index=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('build_server_type', self.gf('django.db.models.fields.CharField')(default='hudson', max_length=12)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('build_job_pattern', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('ci', ['BuildServer'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'BuildResult', fields ['job', 'build_number']
        db.delete_unique('ci_buildresult', ['job_id', 'build_number'])

        # Removing unique constraint on 'BuildJob', fields ['name', 'build_server']
        db.delete_unique('ci_buildjob', ['name', 'build_server_id'])

        # Deleting model 'BuildJobAuditLogEntry'
        db.delete_table('ci_buildjobauditlogentry')

        # Deleting model 'BuildJob'
        db.delete_table('ci_buildjob')

        # Deleting model 'BuildResultAuditLogEntry'
        db.delete_table('ci_buildresultauditlogentry')

        # Deleting model 'BuildResult'
        db.delete_table('ci_buildresult')

        # Deleting model 'BuildServerAuditLogEntry'
        db.delete_table('ci_buildserverauditlogentry')

        # Deleting model 'BuildServer'
        db.delete_table('ci_buildserver')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'ci.buildjob': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('name', 'build_server'),)", 'object_name': 'BuildJob'},
            'build_server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'jobs'", 'to': "orm['ci.BuildServer']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'build_jobs'", 'null': 'True', 'to': "orm['prodmgmt.Product']"})
        },
        'ci.buildjobauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'BuildJobAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_buildjob_audit_log_entry'"}),
            'build_server': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_jobs'", 'to': "orm['ci.BuildServer']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_build_jobs'", 'null': 'True', 'to': "orm['prodmgmt.Product']"})
        },
        'ci.buildresult': {
            'Meta': {'unique_together': "(('job', 'build_number'),)", 'object_name': 'BuildResult'},
            'build_number': ('django.db.models.fields.IntegerField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'finished_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'results'", 'to': "orm['ci.BuildJob']"}),
            'log': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'produced_package': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'builds'", 'null': 'True', 'to': "orm['package.Package']"}),
            'succeeded': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'ci.buildresultauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'BuildResultAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_buildresult_audit_log_entry'"}),
            'build_number': ('django.db.models.fields.IntegerField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'finished_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'job': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_results'", 'to': "orm['ci.BuildJob']"}),
            'log': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'produced_package': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_builds'", 'null': 'True', 'to': "orm['package.Package']"}),
            'succeeded': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'ci.buildserver': {
            'Meta': {'ordering': "('name',)", 'object_name': 'BuildServer'},
            'build_job_pattern': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'build_server_type': ('django.db.models.fields.CharField', [], {'default': "'hudson'", 'max_length': '12'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        'ci.buildserverauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'BuildServerAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_buildserver_audit_log_entry'"}),
            'build_job_pattern': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'build_server_type': ('django.db.models.fields.CharField', [], {'default': "'hudson'", 'max_length': '12'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'issue.issue': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('name', 'project'),)", 'object_name': 'Issue'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'db_index': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issues'", 'to': "orm['issue.IssueTrackerProject']"})
        },
        'issue.issuetracker': {
            'Meta': {'ordering': "('name',)", 'object_name': 'IssueTracker'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_url_pattern': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'tracker_type': ('django.db.models.fields.CharField', [], {'default': "'jira'", 'max_length': '12'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        'issue.issuetrackerproject': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('name', 'issue_tracker'),)", 'object_name': 'IssueTrackerProject'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue_tracker': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'projects'", 'to': "orm['issue.IssueTracker']"}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'db_index': 'True'})
        },
        'package.package': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('name', 'version'),)", 'object_name': 'Package'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['package.Version']"})
        },
        'package.version': {
            'Meta': {'ordering': "('major', 'minor', 'micro', 'revision')", 'object_name': 'Version'},
            'build': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'major': ('django.db.models.fields.IntegerField', [], {}),
            'micro': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'minor': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rpm_release': ('django.db.models.fields.CharField', [], {'max_length': '48', 'null': 'True', 'blank': 'True'}),
            'rpm_version': ('django.db.models.fields.CharField', [], {'max_length': '48', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'release'", 'max_length': '16'})
        },
        'prodmgmt.person': {
            'Meta': {'ordering': "('username',)", 'object_name': 'Person'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'distinguished_name': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'prodmgmt.product': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Product'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_products'", 'to': "orm['prodmgmt.Person']"}),
            'pipeline_issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['issue.Issue']"})
        }
    }

    complete_apps = ['ci']
