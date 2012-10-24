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
        
        # Adding model 'ReleaseAuditLogEntry'
        db.create_table('release_releaseauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_releases', to=orm['prodmgmt.Product'])),
            ('release_number', self.gf('django.db.models.fields.IntegerField')()),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_release_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('release', ['ReleaseAuditLogEntry'])

        # Adding model 'Release'
        db.create_table('release_release', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(related_name='releases', to=orm['prodmgmt.Product'])),
            ('release_number', self.gf('django.db.models.fields.IntegerField')()),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('release', ['Release'])

        # Adding unique constraint on 'Release', fields ['product', 'release_number']
        db.create_unique('release_release', ['product_id', 'release_number'])

        # Adding unique constraint on 'Release', fields ['product', 'version']
        db.create_unique('release_release', ['product_id', 'version'])

        # Adding model 'ReleaseElementAuditLogEntry'
        db.create_table('release_releaseelementauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_elements', to=orm['release.Release'])),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['package.PackageName'])),
            ('package_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['package.Version'])),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prodmgmt.Application'], null=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_releaseelement_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('release', ['ReleaseElementAuditLogEntry'])

        # Adding model 'ReleaseElement'
        db.create_table('release_releaseelement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='elements', to=orm['release.Release'])),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['package.PackageName'])),
            ('package_version', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['package.Version'])),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prodmgmt.Application'], null=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('release', ['ReleaseElement'])

        # Adding unique constraint on 'ReleaseElement', fields ['release', 'package']
        db.create_unique('release_releaseelement', ['release_id', 'package_id'])

        # Adding model 'DeploymentRequestAuditLogEntry'
        db.create_table('release_deploymentrequestauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_deployment_requests', to=orm['release.Release'])),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_deployment_requests', to=orm['system.Environment'])),
            ('ops_issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='_auditlog_+', null=True, to=orm['issue.Issue'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_deploymentrequest_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('release', ['DeploymentRequestAuditLogEntry'])

        # Adding model 'DeploymentRequest'
        db.create_table('release_deploymentrequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('release', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deployment_requests', to=orm['release.Release'])),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deployment_requests', to=orm['system.Environment'])),
            ('ops_issue', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['issue.Issue'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('release', ['DeploymentRequest'])

        # Adding unique constraint on 'DeploymentRequest', fields ['release', 'environment']
        db.create_unique('release_deploymentrequest', ['release_id', 'environment_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'DeploymentRequest', fields ['release', 'environment']
        db.delete_unique('release_deploymentrequest', ['release_id', 'environment_id'])

        # Removing unique constraint on 'ReleaseElement', fields ['release', 'package']
        db.delete_unique('release_releaseelement', ['release_id', 'package_id'])

        # Removing unique constraint on 'Release', fields ['product', 'version']
        db.delete_unique('release_release', ['product_id', 'version'])

        # Removing unique constraint on 'Release', fields ['product', 'release_number']
        db.delete_unique('release_release', ['product_id', 'release_number'])

        # Deleting model 'ReleaseAuditLogEntry'
        db.delete_table('release_releaseauditlogentry')

        # Deleting model 'Release'
        db.delete_table('release_release')

        # Deleting model 'ReleaseElementAuditLogEntry'
        db.delete_table('release_releaseelementauditlogentry')

        # Deleting model 'ReleaseElement'
        db.delete_table('release_releaseelement')

        # Deleting model 'DeploymentRequestAuditLogEntry'
        db.delete_table('release_deploymentrequestauditlogentry')

        # Deleting model 'DeploymentRequest'
        db.delete_table('release_deploymentrequest')


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
        'package.packagename': {
            'Meta': {'ordering': "('name',)", 'object_name': 'PackageName'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
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
        'prodmgmt.application': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Application'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'applications'", 'to': "orm['prodmgmt.Product']"})
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
        },
        'release.deploymentrequest': {
            'Meta': {'unique_together': "(('release', 'environment'),)", 'object_name': 'DeploymentRequest'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployment_requests'", 'to': "orm['system.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ops_issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['issue.Issue']"}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployment_requests'", 'to': "orm['release.Release']"})
        },
        'release.deploymentrequestauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'DeploymentRequestAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_deploymentrequest_audit_log_entry'"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_deployment_requests'", 'to': "orm['system.Environment']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'ops_issue': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_+'", 'null': 'True', 'to': "orm['issue.Issue']"}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_deployment_requests'", 'to': "orm['release.Release']"})
        },
        'release.release': {
            'Meta': {'ordering': "('product', 'release_number')", 'unique_together': "(('product', 'release_number'), ('product', 'version'))", 'object_name': 'Release'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'releases'", 'to': "orm['prodmgmt.Product']"}),
            'release_number': ('django.db.models.fields.IntegerField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'release.releaseauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'ReleaseAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_release_audit_log_entry'"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_releases'", 'to': "orm['prodmgmt.Product']"}),
            'release_number': ('django.db.models.fields.IntegerField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'release.releaseelement': {
            'Meta': {'unique_together': "(('release', 'package'),)", 'object_name': 'ReleaseElement'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['prodmgmt.Application']", 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['package.PackageName']"}),
            'package_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['package.Version']"}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'elements'", 'to': "orm['release.Release']"})
        },
        'release.releaseelementauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'ReleaseElementAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_releaseelement_audit_log_entry'"}),
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['prodmgmt.Application']", 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['package.PackageName']"}),
            'package_version': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['package.Version']"}),
            'release': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_elements'", 'to': "orm['release.Release']"})
        },
        'system.environment': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Environment'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        }
    }

    complete_apps = ['release']
