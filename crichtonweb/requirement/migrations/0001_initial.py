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
        
        # Adding model 'PackageSpecificationAuditLogEntry'
        db.create_table('requirement_packagespecificationauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['package.PackageName'])),
            ('version_specification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requirement.VersionSpecification'], null=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_packagespecification_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('requirement', ['PackageSpecificationAuditLogEntry'])

        # Adding model 'PackageSpecification'
        db.create_table('requirement_packagespecification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['package.PackageName'])),
            ('version_specification', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['requirement.VersionSpecification'], null=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('requirement', ['PackageSpecification'])

        # Adding unique constraint on 'PackageSpecification', fields ['package', 'version_specification']
        db.create_unique('requirement_packagespecification', ['package_id', 'version_specification_id'])

        # Adding model 'VersionRange'
        db.create_table('requirement_versionrange', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=103, primary_key=True)),
            ('minimum', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['package.Version'])),
            ('minimum_is_inclusive', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('maximum', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['package.Version'])),
            ('maximum_is_inclusive', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('requirement', ['VersionRange'])

        # Adding model 'VersionSpecification'
        db.create_table('requirement_versionspecification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['package.Version'])),
            ('version_range', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['requirement.VersionRange'])),
        ))
        db.send_create_signal('requirement', ['VersionSpecification'])

        # Adding unique constraint on 'VersionSpecification', fields ['version', 'version_range']
        db.create_unique('requirement_versionspecification', ['version_id', 'version_range_id'])

        # Adding model 'RequirementAuditLogEntry'
        db.create_table('requirement_requirementauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prodmgmt.Application'])),
            ('default_specification', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='_auditlog_default_specifications', null=True, to=orm['requirement.PackageSpecification'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_requirement_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('requirement', ['RequirementAuditLogEntry'])

        # Adding model 'Requirement'
        db.create_table('requirement_requirement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['prodmgmt.Application'], unique=True)),
            ('default_specification', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='default_specifications', null=True, to=orm['requirement.PackageSpecification'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('requirement', ['Requirement'])

        # Adding model 'EnvironmentRequirementAuditLogEntry'
        db.create_table('requirement_environmentrequirementauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('specification', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_environment_requirements', to=orm['requirement.PackageSpecification'])),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_requirements', to=orm['system.Environment'])),
            ('requirement', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_environment_specifications', to=orm['requirement.Requirement'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_environmentrequirement_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('requirement', ['EnvironmentRequirementAuditLogEntry'])

        # Adding model 'EnvironmentRequirement'
        db.create_table('requirement_environmentrequirement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('specification', self.gf('django.db.models.fields.related.ForeignKey')(related_name='environment_requirements', to=orm['requirement.PackageSpecification'])),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requirements', to=orm['system.Environment'])),
            ('requirement', self.gf('django.db.models.fields.related.ForeignKey')(related_name='environment_specifications', to=orm['requirement.Requirement'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('requirement', ['EnvironmentRequirement'])

        # Adding unique constraint on 'EnvironmentRequirement', fields ['specification', 'environment', 'requirement']
        db.create_unique('requirement_environmentrequirement', ['specification_id', 'environment_id', 'requirement_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'EnvironmentRequirement', fields ['specification', 'environment', 'requirement']
        db.delete_unique('requirement_environmentrequirement', ['specification_id', 'environment_id', 'requirement_id'])

        # Removing unique constraint on 'VersionSpecification', fields ['version', 'version_range']
        db.delete_unique('requirement_versionspecification', ['version_id', 'version_range_id'])

        # Removing unique constraint on 'PackageSpecification', fields ['package', 'version_specification']
        db.delete_unique('requirement_packagespecification', ['package_id', 'version_specification_id'])

        # Deleting model 'PackageSpecificationAuditLogEntry'
        db.delete_table('requirement_packagespecificationauditlogentry')

        # Deleting model 'PackageSpecification'
        db.delete_table('requirement_packagespecification')

        # Deleting model 'VersionRange'
        db.delete_table('requirement_versionrange')

        # Deleting model 'VersionSpecification'
        db.delete_table('requirement_versionspecification')

        # Deleting model 'RequirementAuditLogEntry'
        db.delete_table('requirement_requirementauditlogentry')

        # Deleting model 'Requirement'
        db.delete_table('requirement_requirement')

        # Deleting model 'EnvironmentRequirementAuditLogEntry'
        db.delete_table('requirement_environmentrequirementauditlogentry')

        # Deleting model 'EnvironmentRequirement'
        db.delete_table('requirement_environmentrequirement')


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
        'requirement.environmentrequirement': {
            'Meta': {'unique_together': "(('specification', 'environment', 'requirement'),)", 'object_name': 'EnvironmentRequirement'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requirements'", 'to': "orm['system.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'requirement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environment_specifications'", 'to': "orm['requirement.Requirement']"}),
            'specification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environment_requirements'", 'to': "orm['requirement.PackageSpecification']"})
        },
        'requirement.environmentrequirementauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'EnvironmentRequirementAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_environmentrequirement_audit_log_entry'"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_requirements'", 'to': "orm['system.Environment']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'requirement': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_environment_specifications'", 'to': "orm['requirement.Requirement']"}),
            'specification': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_environment_requirements'", 'to': "orm['requirement.PackageSpecification']"})
        },
        'requirement.packagespecification': {
            'Meta': {'unique_together': "(('package', 'version_specification'),)", 'object_name': 'PackageSpecification'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['package.PackageName']"}),
            'version_specification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requirement.VersionSpecification']", 'null': 'True', 'blank': 'True'})
        },
        'requirement.packagespecificationauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'PackageSpecificationAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_packagespecification_audit_log_entry'"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['package.PackageName']"}),
            'version_specification': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['requirement.VersionSpecification']", 'null': 'True', 'blank': 'True'})
        },
        'requirement.requirement': {
            'Meta': {'object_name': 'Requirement'},
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['prodmgmt.Application']", 'unique': 'True'}),
            'default_specification': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'default_specifications'", 'null': 'True', 'to': "orm['requirement.PackageSpecification']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'requirement.requirementauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'RequirementAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_requirement_audit_log_entry'"}),
            'application': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['prodmgmt.Application']"}),
            'default_specification': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'_auditlog_default_specifications'", 'null': 'True', 'to': "orm['requirement.PackageSpecification']"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'})
        },
        'requirement.versionrange': {
            'Meta': {'object_name': 'VersionRange'},
            'maximum': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['package.Version']"}),
            'maximum_is_inclusive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'minimum': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['package.Version']"}),
            'minimum_is_inclusive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '103', 'primary_key': 'True'})
        },
        'requirement.versionspecification': {
            'Meta': {'unique_together': "(('version', 'version_range'),)", 'object_name': 'VersionSpecification'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['package.Version']"}),
            'version_range': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['requirement.VersionRange']"})
        },
        'system.environment': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Environment'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        }
    }

    complete_apps = ['requirement']
