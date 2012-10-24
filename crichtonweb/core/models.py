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
from django.db import models
from django.core.exceptions import PermissionDenied
from django.contrib.admin.util import quote

class crichtonModel(models.Model):
    # A crichtonModel will only be allowed to soft-delete if it has a field called "deleted".
    # It is also possible for some models to refuse even a soft delete e.g. ApplicationDeployment
    # No crichtonModel will be allowed to do a real delete, except for the ones expressing user preferences
    # in the frontend, e.g. frontend.FollowedProduct.

    can_delete = False
    has_api = True
    
    class Meta:
        abstract = True
    
    def _get_admin_base(self):
        return "/admin"
    
    def get_absolute_url(self):
        return "%s/%s/%s/%s/" % (self._get_admin_base(), self._meta.app_label,
                                 self._meta.module_name.lower(),
                                 quote(self._get_pk_val()))
    
    def get_view_url(self):
        return "/view/%s/%s/%s/" % (self._meta.app_label,
                                      self._meta.module_name.lower(),
                                      quote(self._get_pk_val()))
    
    def get_link(self, a_extras=""):
        return '<a href="%s" %s>%s</a>' % (self.get_absolute_url(), a_extras, self)

    def _do_soft_delete(cls):
        field_list = [f.name for f in cls._meta.fields]
        #deleted_field = [f for f in cls._meta.fields if f.name=="deleted"][0]
        if "deleted" in field_list:# and isinstance(deleted_field, models.BooleanField):
            return True

        elif "audit_log" in field_list and isinstance(cls._meta.fields["audit_log"], AuditLog):
            # deletion would break foreign keys in auditlogentry
            return True
        
        else:
            return False
    _do_soft_delete = classmethod(_do_soft_delete)
        
    def delete(self, *args, **kwargs):
        if self._do_soft_delete():
            if not self.deleted:
                self.deleted = True
                self.save()

        elif self.can_delete:
            models.Model.delete(self, *args, **kwargs)

        else:
            raise PermissionDenied("Not allowed to delete object '%s'" % self._meta.module_name)

    def undelete(self):
        if self._do_soft_delete() and self.deleted:
            self.deleted = False
            self.save()
        
# eof
