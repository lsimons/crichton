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
import re
from itertools import chain
from django.forms.widgets import *
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.datastructures import MultiValueDict, MergeDict
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

class crichtonTextarea(Textarea):
    """Ensures all fields have specific line endings, to prevent changed_data
    telling us a field has changed when the only difference is e.g. extra 
    carriage returns.

    This is only needed when communicating with external systems where line 
    endings may get translated on the way.
    """
    _newlines_re = re.compile(r'(\r\n|\r|\n)')

    def __init__(self, attrs=None, newline="\n"):
        self.newline = newline
        super(crichtonTextarea, self).__init__(attrs)

    def value_from_datadict(self, data, files, name):
        value = super(crichtonTextarea, self).value_from_datadict(data, files, name)
        return self._newlines_re.sub(self.newline, value)

class ReadOnlySelectMultiple(SelectMultiple):
    """Widget designed to replace a SelectMultiple widget that you want to 
    make readonly."""

    # There are enough differences between this and the ReadOnlySelect widget to
    # warrant a separate class instead of trying to jam them together.
    # This inherits from SelectMultiple in order to pick up
    # value_from_datadict() and _has_changed()

    def __init__(self, delegate):
        super(ReadOnlySelectMultiple, self).__init__(delegate.attrs)
        self.delegate = delegate

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        for val in value:
            output.append(u'<input type="hidden" value="%s" %s />' % (val, flatatt(final_attrs)))

        selected_labels = []
        for option_value, option_label in chain(self.delegate.choices, choices):
            if isinstance(value, (list, tuple)) and option_value in value or option_value == value:
                selected_labels.append(option_label)
        selected_label = ', '.join(selected_labels)

        final_attrs = self.build_attrs(attrs, name="%s_readonlyselectlabel" % name)
        final_attrs["readonly"] = "readonly"
        final_attrs["id"] = final_attrs["name"]
        # MultipleSelect widgets often have a size attr, which messes up the 
        # text display, and no reason to keep it here
        if final_attrs.has_key('size'):
            del final_attrs['size']
        output.append(u'<input type="text" value="%s" %s />' % (selected_label, flatatt(final_attrs)))
        return mark_safe(u'\n'.join(output))

class ReadOnlySelect(Widget):
    """Widget designed to replace a Select widget that you want to make readonly."""
    def __init__(self, delegate):
        super(ReadOnlySelect, self).__init__(delegate.attrs)
        self.delegate = delegate

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<input type="hidden" value="%s" %s />' % (value, flatatt(final_attrs))]

        selected_label = None
        for option_value, option_label in chain(self.delegate.choices, choices):
            if isinstance(option_label, (list, tuple)):
                for option_value_2, option_label_2 in option_label:
                    if option_value_2 == value:
                        selected_label = option_label_2
                        break
            else:
                if option_value == value:
                    selected_label = option_label

        final_attrs = self.build_attrs(attrs, name="%s_readonlyselectlabel" % name)
        final_attrs["readonly"] = "readonly"
        final_attrs["id"] = final_attrs["name"]
        output.append(u'<input type="text" value="%s" %s />' % (selected_label, flatatt(final_attrs)))
        return mark_safe(u'\n'.join(output))

def force_readonly(form):
    for field in form.fields.values():
        if isinstance(field.widget, SelectMultiple):
            field.widget = ReadOnlySelectMultiple(field.widget)
        elif isinstance(field.widget, Select):
            field.widget = ReadOnlySelect(field.widget)
        if isinstance(field.widget, RelatedFieldWidgetWrapper):
            field.widget.widget = ReadOnlySelect(field.widget.widget)
            field.widget.widget.attrs['readonly'] = 'readonly'
        field.widget.attrs['readonly'] = 'readonly'
