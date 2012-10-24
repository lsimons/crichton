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
        
        # Adding model 'DeploymentSystemAuditLogEntry'
        db.create_table('deployment_deploymentsystemauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(max_length=128, db_index=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('deployment_system_type', self.gf('django.db.models.fields.CharField')(default='puppet', max_length=12)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('takes_specific_version', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('takes_specific_pool', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_deploymentsystem_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('deployment', ['DeploymentSystemAuditLogEntry'])

        # Adding model 'DeploymentSystem'
        db.create_table('deployment_deploymentsystem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=128, db_index=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('deployment_system_type', self.gf('django.db.models.fields.CharField')(default='puppet', max_length=12)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('takes_specific_version', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('takes_specific_pool', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('deployment', ['DeploymentSystem'])

        # Adding model 'DeploymentPreferenceAuditLogEntry'
        db.create_table('deployment_deploymentpreferenceauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_deployment_preferences', to=orm['system.Environment'])),
            ('deployment_system', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_environment_usages', to=orm['deployment.DeploymentSystem'])),
            ('preference_number', self.gf('django.db.models.fields.SmallIntegerField')(default=999)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_deploymentpreference_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('deployment', ['DeploymentPreferenceAuditLogEntry'])

        # Adding model 'DeploymentPreference'
        db.create_table('deployment_deploymentpreference', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('environment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='deployment_preferences', to=orm['system.Environment'])),
            ('deployment_system', self.gf('django.db.models.fields.related.ForeignKey')(related_name='environment_usages', to=orm['deployment.DeploymentSystem'])),
            ('preference_number', self.gf('django.db.models.fields.SmallIntegerField')(default=999)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('deployment', ['DeploymentPreference'])

        # Adding unique constraint on 'DeploymentPreference', fields ['environment', 'preference_number']
        db.create_unique('deployment_deploymentpreference', ['environment_id', 'preference_number'])

        # Adding model 'RecipeAuditLogEntry'
        db.create_table('deployment_recipeauditlogentry', (
            ('id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('deployment_system', self.gf('django.db.models.fields.related.ForeignKey')(related_name='_auditlog_recipes', to=orm['deployment.DeploymentSystem'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('action_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('action_user', self.gf('audit_log.models.fields.LastUserField')(related_name='_recipe_audit_log_entry')),
            ('action_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('deployment', ['RecipeAuditLogEntry'])

        # Adding model 'Recipe'
        db.create_table('deployment_recipe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('deployment_system', self.gf('django.db.models.fields.related.ForeignKey')(related_name='recipes', to=orm['deployment.DeploymentSystem'])),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('deployment', ['Recipe'])

        # Adding unique constraint on 'Recipe', fields ['name', 'deployment_system']
        db.create_unique('deployment_recipe', ['name', 'deployment_system_id'])

        # Adding M2M table for field packages on 'Recipe'
        db.create_table('deployment_recipe_packages', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('recipe', models.ForeignKey(orm['deployment.recipe'], null=False)),
            ('packagename', models.ForeignKey(orm['package.packagename'], null=False))
        ))
        db.create_unique('deployment_recipe_packages', ['recipe_id', 'packagename_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Recipe', fields ['name', 'deployment_system']
        db.delete_unique('deployment_recipe', ['name', 'deployment_system_id'])

        # Removing unique constraint on 'DeploymentPreference', fields ['environment', 'preference_number']
        db.delete_unique('deployment_deploymentpreference', ['environment_id', 'preference_number'])

        # Deleting model 'DeploymentSystemAuditLogEntry'
        db.delete_table('deployment_deploymentsystemauditlogentry')

        # Deleting model 'DeploymentSystem'
        db.delete_table('deployment_deploymentsystem')

        # Deleting model 'DeploymentPreferenceAuditLogEntry'
        db.delete_table('deployment_deploymentpreferenceauditlogentry')

        # Deleting model 'DeploymentPreference'
        db.delete_table('deployment_deploymentpreference')

        # Deleting model 'RecipeAuditLogEntry'
        db.delete_table('deployment_recipeauditlogentry')

        # Deleting model 'Recipe'
        db.delete_table('deployment_recipe')

        # Removing M2M table for field packages on 'Recipe'
        db.delete_table('deployment_recipe_packages')


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
        'deployment.deploymentpreference': {
            'Meta': {'ordering': "('environment', 'preference_number')", 'unique_together': "(('environment', 'preference_number'),)", 'object_name': 'DeploymentPreference'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deployment_system': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'environment_usages'", 'to': "orm['deployment.DeploymentSystem']"}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'deployment_preferences'", 'to': "orm['system.Environment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preference_number': ('django.db.models.fields.SmallIntegerField', [], {'default': '999'})
        },
        'deployment.deploymentpreferenceauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'DeploymentPreferenceAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_deploymentpreference_audit_log_entry'"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deployment_system': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_environment_usages'", 'to': "orm['deployment.DeploymentSystem']"}),
            'environment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_deployment_preferences'", 'to': "orm['system.Environment']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'preference_number': ('django.db.models.fields.SmallIntegerField', [], {'default': '999'})
        },
        'deployment.deploymentsystem': {
            'Meta': {'ordering': "('name',)", 'object_name': 'DeploymentSystem'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deployment_system_type': ('django.db.models.fields.CharField', [], {'default': "'puppet'", 'max_length': '12'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'takes_specific_pool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'takes_specific_version': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        'deployment.deploymentsystemauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'DeploymentSystemAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_deploymentsystem_audit_log_entry'"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deployment_system_type': ('django.db.models.fields.CharField', [], {'default': "'puppet'", 'max_length': '12'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'max_length': '128', 'db_index': 'True'}),
            'takes_specific_pool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'takes_specific_version': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        'deployment.recipe': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('name', 'deployment_system'),)", 'object_name': 'Recipe'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deployment_system': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'recipes'", 'to': "orm['deployment.DeploymentSystem']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'packages': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'recipes'", 'blank': 'True', 'to': "orm['package.PackageName']"})
        },
        'deployment.recipeauditlogentry': {
            'Meta': {'ordering': "('-action_date',)", 'object_name': 'RecipeAuditLogEntry'},
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'action_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'action_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'action_user': ('audit_log.models.fields.LastUserField', [], {'related_name': "'_recipe_audit_log_entry'"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'deployment_system': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_auditlog_recipes'", 'to': "orm['deployment.DeploymentSystem']"}),
            'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'package.packagename': {
            'Meta': {'ordering': "('name',)", 'object_name': 'PackageName'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'system.environment': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Environment'},
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        }
    }

    complete_apps = ['deployment']
