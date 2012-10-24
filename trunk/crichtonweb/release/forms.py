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
import copy
import logging

from django import forms
from django.contrib import messages
from django.forms import ModelForm, ModelChoiceField
from django.forms.models import ModelFormMetaclass
from django.db import models
from django.db.models import Q
from django.forms.widgets import *
from django.core.exceptions import ValidationError
from django.forms.util import flatatt

from ajax_select.fields import AutoCompleteSelectField

from crichtonweb.core.widgets import force_readonly
from crichtonweb.issue.models import Issue, IssueTracker, IssueTrackerProject
from crichtonweb.package.models import PackageName, Version, Package
from crichtonweb.prodmgmt.models import Product, Application
from crichtonweb.release.models import DeploymentRequest, Release, ReleaseElement
from crichtonweb.system.models import Environment

from crichtonweb.prodmgmt.forms import ProductField

class DeploymentRequestForm(ModelForm):
    release = AutoCompleteSelectField('release', label='Release')
    ops_issue = AutoCompleteSelectField('ops_issue', label='OPS ticket')

    class Meta:
        model = DeploymentRequest

class ReleaseUtils:
    @staticmethod
    def autogenerate_release_order(product):
        product_releases = Release.objects.filter(product=product)
        if not product_releases:
            relnum = 1
        else:
            curmax = product_releases.order_by('-release_order').values_list('release_order', flat=True)[0]
            relnum = curmax + 1
        return relnum

class ReleaseForm(ModelForm):
    product = ProductField('product', label='Product')
    
    release_order = forms.IntegerField(required=False, help_text="Determines the ordering for this release related to others. Leave blank to get the next number automatically assigned.", label="Release Order")
    rpm_helptext="""
Paste a list of RPMs to be added, one per line. For example,<br>
&nbsp;&nbsp;&nbsp;crichtoncron-1.0.3_531642.15-1<br>
&nbsp;&nbsp;&nbsp;crichtoncli-1.0.3_532167.24-1<br>
&nbsp;&nbsp;&nbsp;crichtonweb-1.0.3_532616.42-1<br>
For this to work, the package must already exist in the database.
<p><b>NOTE: you can only use this on a Change Release form, not on an Add Release.</b></p>
"""    
    rpms = forms.CharField(required=False, widget=forms.Textarea, label="RPMs", help_text=rpm_helptext)
    is_auto_deployable = forms.BooleanField(required=False)
                                            
    class Meta:
        model = Release
    
    def __init__(self, *args, **kwargs):
        super(ReleaseForm, self).__init__(*args, **kwargs)

        instance = getattr(self, 'instance', None)
        if instance:
            self.initial['rpms'] = ""
        if instance and instance.id and instance.deployment_requests.exists():
            force_readonly(self)
        if instance:
            self.initial['is_auto_deployable'] = instance.is_auto_deployable()

    def save(self, commit=False):

        # if we're creating this and we don't have a release_order set, assign the next one
        if self.instance.pk is None and self.instance.release_order is None:
            self.instance.release_order = ReleaseUtils.autogenerate_release_order(self.instance.product)

        if self.instance.pk is None and commit == False:
            # Can't do the rpm bit, we need the instance to exist
            return super(ReleaseForm, self).save(commit=commit)

        # if rpms provided, save them as release elements
        rpms = self.cleaned_data['rpms']
        if rpms:
            for rpm in rpms.split('\n'):
                bits = rpm.strip().split("-")
                package = None
                for i in range(1, len(bits)):
                    name = "-".join(bits[:i])
                    version = "-".join(bits[i:])
                    try:
                        package = Package.objects.get(name=name, version=version)
                        break
                    except Package.DoesNotExist:
                        pass
                
                if package is None:
                    logging.debug("No package found for rpm %s" % rpm)
                    continue

                # We have a valid package. Add it as a ReleaseElement if not already there.
                try:
                    re = ReleaseElement.objects.get(release=self.instance, package=package)
                except ReleaseElement.DoesNotExist:
                    re = ReleaseElement(release=self.instance, package=package)
                    re.save()
                    logging.debug("Saved ReleaseElement from package %s" % re)
            
        return super(ReleaseForm, self).save(commit=commit)
            
class ReleaseElementForm(ModelForm):
    release = AutoCompleteSelectField('release')
    package = AutoCompleteSelectField('package', label="Package")
    application = AutoCompleteSelectField('application', label="Application", required=False)
    
    class Meta:
        model = ReleaseElement

    def __init__(self, *args, **kwargs):
        super(ReleaseElementForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.id and instance.release.deployment_requests.exists():
            force_readonly(self)

class CloneReleaseForm(forms.Form):
    copy_release_from = AutoCompleteSelectField('release', help_text="Start typing the release you want to clone and the field will auto-complete.")
    version = forms.CharField(max_length=128, help_text="How you identify this release. Each release for a product must have a distinct version.")
    release_order = forms.IntegerField(required=False, help_text="Determines the ordering for this release related to others. Leave blank to get the next number automatically assigned.", label="Release Order")
    redirecturl = forms.CharField(widget=forms.HiddenInput)

    def clean(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.has_key('copy_release_from') and cleaned_data.has_key('version') and \
           Release.objects.filter(product=cleaned_data['copy_release_from'], version=cleaned_data['version']).count() > 0:
            raise forms.ValidationError("Sorry, but a release with that version already exists. Please choose a different version.")
        return cleaned_data

    def save(self, request):
        """Clone all existing data for this release, then return new object."""
        master_release = self.cleaned_data['copy_release_from']
        if self.cleaned_data.has_key('release_order') and self.cleaned_data['release_order']:
            release_order = self.cleaned_data['release_order']
        else:
            release_order = ReleaseUtils.autogenerate_release_order(master_release.product)

        cloned_release = Release(
            product = master_release.product,
            release_order = release_order,
            version = self.cleaned_data['version']
        )
        cloned_release.save()

        for elem in ReleaseElement.objects.filter(release=master_release, deleted=False):
            new_elem = copy.copy(elem)
            new_elem.pk = None
            new_elem.release = cloned_release
            new_elem.save()

        messages.success(request, "The release has been successfully cloned. Please make any changes to the new release below.")
        return cloned_release
# eof
