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

# Build script run from hudson to build crichtonweb and
# push it to the right repo
# Usage:
#   ./ci.sh [-publish] [basedir] [target_env]

### setup / cleanup
set -e

PUBLISH=0
if [[ "x$1" = "x-publish" ]]; then
    PUBLISH=1
    shift
fi
BASEDIR=${1:-$PWD}
TARGET_ENV=${2:-$TARGET_ENV}

# make sure we have absolute path to a valid BASEDIR directory
[[ -d "$BASEDIR" ]] || (echo "BASEDIR should be directory but was $BASEDIR" 1>&2; exit 1)
BASEDIR=$(cd "$BASEDIR"; pwd)

. "$BASEDIR/../../buildutils/build-functions.rc"

### get rid of output of previous builds
clean_previous_builds "$BASEDIR"

### todo: run tests here

### do build
python setup.py bdist_rpm

### put RPMS in a neat dir structure
collect_rpms "$BASEDIR"
structure_rpms "$BASEDIR"

### push out to yum repos
if [[ "x$PUBLISH" == "x1" ]]; then
    publish_rpms "$BASEDIR" "$TARGET_ENV"
else
    echo "Not publishing RPMs. Add -publish to publish."
    echo
fi
