#!/usr/bin/env bash
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

set -e
set -x

CURRDIR="$( cd "$( dirname "$0" )" && pwd )"
PATH="$PATH:/usr/local/bin:$CURRDIR"
cd $CURRDIR

crichton.py put environment int init-data/environment_int.xml
crichton.py put environment test init-data/environment_test.xml
crichton.py put environment stage init-data/environment_stage.xml
crichton.py put environment live init-data/environment_live.xml
crichton.py put environment stable init-data/environment_stable.xml
crichton.py put environment sandbox init-data/environment_sandbox.xml

crichton.py put role database init-data/role_database.xml
crichton.py put role application init-data/role_application.xml
crichton.py put role activemq init-data/role_activemq.xml
crichton.py put role pal init-data/role_pal.xml
crichton.py put role static init-data/role_static.xml

crichton.py put deployment_system hudson-ci-app-int init-data/deployment_system_hudson-ci-app-int.xml
crichton.py put deployment_system hudson-ci-app-test init-data/deployment_system_hudson-ci-app-test.xml
crichton.py put deployment_system hudson-ci-db-int init-data/deployment_system_hudson-ci-db-int.xml
crichton.py put deployment_system hudson-ci-db-test init-data/deployment_system_hudson-ci-db-test.xml
crichton.py put deployment_system hudson-ci-pal-int init-data/deployment_system_hudson-ci-pal-int.xml
crichton.py put deployment_system hudson-ci-pal-test init-data/deployment_system_hudson-ci-pal-test.xml
crichton.py put deployment_system production-puppet init-data/deployment_system_production-puppet.xml
crichton.py put deployment_system production-fabric init-data/deployment_system_production-fabric.xml

crichton.py put deployment_preference int_1 init-data/deployment_preference_int_1.xml
crichton.py put deployment_preference int_2 init-data/deployment_preference_int_2.xml
crichton.py put deployment_preference int_3 init-data/deployment_preference_int_3.xml
crichton.py put deployment_preference int_4 init-data/deployment_preference_int_4.xml
crichton.py put deployment_preference test_1 init-data/deployment_preference_test_1.xml
crichton.py put deployment_preference test_2 init-data/deployment_preference_test_2.xml
crichton.py put deployment_preference test_3 init-data/deployment_preference_test_3.xml
crichton.py put deployment_preference test_4 init-data/deployment_preference_test_4.xml
crichton.py put deployment_preference stage_1 init-data/deployment_preference_stage_1.xml
crichton.py put deployment_preference stage_2 init-data/deployment_preference_stage_2.xml
crichton.py put deployment_preference live_1 init-data/deployment_preference_live_1.xml
crichton.py put deployment_preference live_2 init-data/deployment_preference_live_2.xml
crichton.py put deployment_preference stable_1 init-data/deployment_preference_stable_1.xml
crichton.py put deployment_preference stable_2 init-data/deployment_preference_stable_2.xml

crichton.py put build_server hudson-ci-app-int init-data/build_server_hudson-ci-app-int.xml
crichton.py put build_server hudson-ci-app-test init-data/build_server_hudson-ci-app-test.xml
crichton.py put build_server hudson-ci-db-int init-data/build_server_hudson-ci-db-int.xml
crichton.py put build_server hudson-ci-db-test init-data/build_server_hudson-ci-db-test.xml
crichton.py put build_server hudson-ci-pal-int init-data/build_server_hudson-ci-pal-int.xml
crichton.py put build_server hudson-ci-pal-test init-data/build_server_hudson-ci-pal-test.xml

crichton.py put issue_tracker forge-jira init-data/issue_tracker_forge-jira.xml
crichton.py put issue_tracker_project PIPELINE@forge-jira init-data/issue_tracker_project_PIPELINE__forge-jira.xml
crichton.py put issue_tracker_project OPS@forge-jira init-data/issue_tracker_project_OPS__forge-jira.xml

crichton.py put issue_type change init-data/issue_type_change.xml

crichton.py put custom_field test_instructions_sanity_checks init-data/custom_field_test_instructions_sanity_checks.xml
crichton.py put custom_field change_description init-data/custom_field_change_description.xml
crichton.py put custom_field contact_number init-data/custom_field_contact_number.xml
crichton.py put custom_field change_type init-data/custom_field_change_type.xml
crichton.py put custom_field rollback_instructions init-data/custom_field_rollback_instructions.xml
crichton.py put custom_field environment init-data/custom_field_environment.xml
crichton.py put custom_field change_end_date_and_time init-data/custom_field_change_end_date_and_time.xml
crichton.py put custom_field change_start_date_and_time init-data/custom_field_change_start_date_and_time.xml
crichton.py put custom_field platform init-data/custom_field_platform.xml
crichton.py put custom_field production_group init-data/custom_field_production_group.xml
crichton.py put custom_field service_picker init-data/custom_field_service_picker.xml
crichton.py put custom_field other_service init-data/custom_field_other_service.xml
crichton.py put custom_field release_content init-data/custom_field_release_content.xml
crichton.py put custom_field reference_number init-data/custom_field_reference_number.xml
crichton.py put custom_field group_assignee init-data/custom_field_group_assignee.xml
crichton.py put custom_field release_instructions init-data/custom_field_release_instructions.xml
crichton.py put custom_field change_reason init-data/custom_field_change_reason.xml
crichton.py put custom_field infosec_approval init-data/custom_field_infosec_approval.xml

crichton.py put crichton_cron_job_status index_hudson init-data/crichton_cron_job_status_index_hudson.xml
crichton.py put crichton_cron_job_status index_zenoss init-data/crichton_cron_job_status_index_zenoss.xml
crichton.py put crichton_cron_job_status index_rpm init-data/crichton_cron_job_status_index_rpm.xml
crichton.py put crichton_cron_job_status index_jira_project init-data/crichton_cron_job_status_index_jira_project.xml
crichton.py put crichton_cron_job_status index_yum_repo init-data/crichton_cron_job_status_index_yum_repo.xml
