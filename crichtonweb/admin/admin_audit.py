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
from django.contrib import admin
from django import template
from django.conf.urls.defaults import patterns, url
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.encoding import force_unicode
from django.contrib.admin.util import unquote
from django.utils.text import capfirst

from admin.softdelete import *

AUDIT_ACTIONS = {
    "I" : "Insert",
    "U" : "Update"
}

from crichtonweb.admin.options import ModelAdmin

class AuditedAdmin(ModelAdmin):
    list_select_related = True
    actions = [delete_selected, undelete_selected]

    def get_urls(self):
        urls = super(AuditedAdmin, self).get_urls()

        info = self.model._meta.app_label, self.model._meta.module_name
        my_urls = patterns('',
            url(r'^(.+)/audit/$',
            self.admin_site.admin_view(self.audit_view),
            name='%s_%s_audit' % info),
        )
        return my_urls + urls
    
    def change_view(self, request, object_id, extra_context=None):
        my_context = {
            "has_audit" : True
        }
        if extra_context and len(extra_context) >= 2:
            print "extra_context", extra_context
            my_context.update(extra_context or {})
        return super(AuditedAdmin, self).change_view(request, object_id,
                extra_context=my_context)

    def audit_view(self, request, object_id, extra_context=None):
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        audit_model = model.audit_log.model
        audit_opts = audit_model._meta
        obj = get_object_or_404(model, pk=unquote(object_id))
        audit_list = list(model.audit_log.filter(id=obj.id).order_by('action_date'))
        keys = []
        for f in audit_opts.fields:
            if f.name in ["id", "action_id", "action_date", "action_type", "action_user"]:
                continue
            keys.append(f.name)
        for audit_obj in audit_list:
            txt = ""
            for k in keys:
                v = unicode(getattr(audit_obj, k, ""))
                txt += k + "=" + v + ", "
            if len(txt) > 2:
                txt = txt[:-2]
            setattr(audit_obj, "txt", txt)
            setattr(audit_obj, "action", AUDIT_ACTIONS[audit_obj.action_type])
        context = {
            'title': 'Audit Log: %s' % force_unicode(obj),
            'audit_list': audit_list,
            'module_name': capfirst(force_unicode(opts.verbose_name_plural)),
            'object': obj,
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(self.object_history_template or [
            "admin/%s/%s/object_audit.html" % (app_label, opts.object_name.lower()),
            "admin/%s/object_audit.html" % app_label,
            "admin/object_audit.html"
        ], context, context_instance=context_instance)
