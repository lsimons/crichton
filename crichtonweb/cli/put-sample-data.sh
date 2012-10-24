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

./db-init.sh

./crichton.py put person matthew.wood sample-data/person_matthew.wood.xml
./crichton.py put issue PIPELINE:PIPELINE-72@forge-jira sample-data/issue_PIPELINE__PIPELINE-72__forge-jira.xml
./crichton.py put product barlesque sample-data/product_barlesque.xml
./crichton.py put application barlesque-static sample-data/application_barlesque-static.xml
./crichton.py put application barlesque-pal sample-data/application_barlesque-pal.xml

./crichton.py put build_job barlesque_lib@hudson-ci-pal-int sample-data/build_job_barlesque_lib__hudson-ci-pal-int.xml
./crichton.py put build_job barlesque@hudson-ci-pal-test sample-data/build_job_barlesque__hudson-ci-pal-test.xml
./crichton.py put build_job barlesque-regression-tests@hudson-ci-pal-int sample-data/build_job_barlesque-regression-tests__hudson-ci-pal-int.xml
./crichton.py put build_job barlesque-regression-tests@hudson-ci-pal-test sample-data/build_job_barlesque-regression-tests__hudson-ci-pal-test.xml
./crichton.py put build_job barlesque-sanity-checks@hudson-ci-pal-test sample-data/build_job_barlesque-sanity-checks__hudson-ci-pal-test.xml

./crichton.py put build_result barlesque-regression-tests:24@hudson-ci-pal-int sample-data/build_result_barlesque-regression-tests__24__hudson-ci-pal-int.xml
./crichton.py put build_result barlesque-regression-tests:28@hudson-ci-pal-int sample-data/build_result_barlesque-regression-tests__28__hudson-ci-pal-int.xml

./crichton.py put build_result barlesque-regression-tests:86@hudson-ci-pal-test sample-data/build_result_barlesque-regression-tests__86__hudson-ci-pal-test.xml
./crichton.py put build_result barlesque-regression-tests:87@hudson-ci-pal-test sample-data/build_result_barlesque-regression-tests__87__hudson-ci-pal-test.xml
./crichton.py put build_result barlesque-regression-tests:88@hudson-ci-pal-test sample-data/build_result_barlesque-regression-tests__88__hudson-ci-pal-test.xml
./crichton.py put build_result barlesque-regression-tests:89@hudson-ci-pal-test sample-data/build_result_barlesque-regression-tests__89__hudson-ci-pal-test.xml
./crichton.py put build_result barlesque-regression-tests:90@hudson-ci-pal-test sample-data/build_result_barlesque-regression-tests__90__hudson-ci-pal-test.xml

./crichton.py put build_result barlesque-sanity-checks:72@hudson-ci-pal-test sample-data/build_result_barlesque-sanity-checks__72__hudson-ci-pal-test.xml

./crichton.py put build_result barlesque:137@hudson-ci-pal-test sample-data/build_result_barlesque__137__hudson-ci-pal-test.xml

./crichton.py put build_result barlesque_lib:1355@hudson-ci-pal-int sample-data/build_result_barlesque_lib__1355__hudson-ci-pal-int.xml
./crichton.py put build_result barlesque_lib:1356@hudson-ci-pal-int sample-data/build_result_barlesque_lib__1356__hudson-ci-pal-int.xml
./crichton.py put build_result barlesque_lib:1357@hudson-ci-pal-int sample-data/build_result_barlesque_lib__1357__hudson-ci-pal-int.xml
./crichton.py put build_result barlesque_lib:1358@hudson-ci-pal-int sample-data/build_result_barlesque_lib__1358__hudson-ci-pal-int.xml
./crichton.py put build_result barlesque_lib:1359@hudson-ci-pal-int sample-data/build_result_barlesque_lib__1359__hudson-ci-pal-int.xml

./crichton.py put version 1.7.0-397935.133 sample-data/version_1.7.0-397935.133.xml
./crichton.py put version 1.7.1-404015.134 sample-data/version_1.7.1-404015.134.xml
./crichton.py put version 1.8.2-425849.137 sample-data/version_1.8.2-425849.137.xml

./crichton.py put package bbc-pal-barlesque@1.7.0-397935.133 sample-data/package_bbc-pal-barlesque__1.7.0-397935.133.xml
./crichton.py put package bbc-pal-barlesque@1.7.1-404015.134 sample-data/package_bbc-pal-barlesque__1.7.1-404015.134.xml
./crichton.py put package bbc-pal-barlesque@1.8.2-425849.137 sample-data/package_bbc-pal-barlesque__1.8.2-425849.137.xml

./crichton.py put package bbc-static-barlesque@1.7.0-397935.133 sample-data/package_bbc-static-barlesque__1.7.0-397935.133.xml
./crichton.py put package bbc-static-barlesque-1.7.0@1.7.0-397935.133 sample-data/package_bbc-static-barlesque-1.7.0__1.7.0-397935.133.xml
./crichton.py put package bbc-static-barlesque@1.7.1-404015.134 sample-data/package_bbc-static-barlesque__1.7.1-404015.134.xml
./crichton.py put package bbc-static-barlesque-1.7.1@1.7.1-404015.134 sample-data/package_bbc-static-barlesque-1.7.1__1.7.1-404015.134.xml
./crichton.py put package bbc-static-barlesque@1.8.2-425849.137 sample-data/package_bbc-static-barlesque__1.8.2-425849.137.xml
./crichton.py put package bbc-static-barlesque-1.8.2@1.8.2-425849.137 sample-data/package_bbc-static-barlesque-1.8.2__1.8.2-425849.137.xml

./crichton.py put package_name bbc-pal-barlesque sample-data/package_name_bbc-pal-barlesque.xml

./crichton.py put package_name bbc-static-barlesque sample-data/package_name_bbc-static-barlesque.xml
./crichton.py put package_name bbc-static-barlesque-1.7.0 sample-data/package_name_bbc-static-barlesque-1.7.0.xml
./crichton.py put package_name bbc-static-barlesque-1.7.1 sample-data/package_name_bbc-static-barlesque-1.7.1.xml
./crichton.py put package_name bbc-static-barlesque-1.8.2 sample-data/package_name_bbc-static-barlesque-1.8.2.xml

./crichton.py put release barlesque@1.7.0 sample-data/release_barlesque__1.7.0.xml
./crichton.py put release_element bbc-pal-barlesque@1.7.0-397935.133:barlesque@1.7.0 sample-data/release_element_bbc-pal-barlesque__barlesque__1.7.0.xml
./crichton.py put release_element bbc-static-barlesque@1.7.0-397935.133:barlesque@1.7.0 sample-data/release_element_bbc-static-barlesque__barlesque__1.7.0.xml
./crichton.py put release_element bbc-static-barlesque-1.7.0@1.7.0-397935.133:barlesque@1.7.0 sample-data/release_element_bbc-static-barlesque-1.7.0__barlesque__1.7.0.xml

./crichton.py put release barlesque@1.8.2 sample-data/release_barlesque__1.8.2.xml
./crichton.py put release_element bbc-pal-barlesque@1.8.2-425849.137:barlesque@1.8.2 sample-data/release_element_bbc-pal-barlesque__barlesque__1.8.2.xml
./crichton.py put release_element bbc-static-barlesque@1.8.2-425849.137:barlesque@1.8.2 sample-data/release_element_bbc-static-barlesque__barlesque__1.8.2.xml
./crichton.py put release_element bbc-static-barlesque-1.8.2@1.8.2-425849.137:barlesque@1.8.2 sample-data/release_element_bbc-static-barlesque-1.8.2__barlesque__1.8.2.xml

# first, make the request
./crichton.py put deployment_request barlesque@1.7.0:stage sample-data/deployment_request_barlesque__1.7.0__stage.xml
# then, file the jira
./crichton.py put issue OPS:OPS-35085@forge-jira sample-data/issue_OPS__OPS-35085__forge-jira.xml
# then, update the request with the jira number
./crichton.py put deployment_request barlesque@1.7.0:stage sample-data/deployment_request_barlesque__1.7.0__stage.with-jira.xml

./crichton.py put deployment_request barlesque@1.8.2:stage sample-data/deployment_request_barlesque__1.8.2__stage.xml
./crichton.py put issue OPS:OPS-36814@forge-jira sample-data/issue_OPS__OPS-36814__forge-jira.xml
./crichton.py put deployment_request barlesque@1.8.2:stage sample-data/deployment_request_barlesque__1.8.2__stage.with-jira.xml
