"""
Functions and classes for creating a hotjazz configuration.

Use service_config() to create a new ServiceConfig, and then
populate that config with service definitions created using service().
"""

# Copyright (c) 2011 BBC. All rights reserved.
import re

from django.db.models import Model
from django.db.models.query import QuerySet
from django.conf.urls.defaults import patterns, url
from django.core.exceptions import ImproperlyConfigured

from crichtonweb.hotjazz.views import make_service_view, make_service_documentation_view, make_service_index_view

def service_config(prefix, *args, **kwargs):
    return ServiceConfig(prefix, *args, **kwargs)

def service(*args, **kwargs):
    return ServiceDefinition(*args, **kwargs)

class ServiceConfigError(ImproperlyConfigured):
    pass

class ServiceDefinition(object):
    def __init__(self, pattern=None, name=None, exposes=None, read_only=False, **kwargs):
        self.pattern = pattern
        self.name = name
        self.exposes = exposes
        self.read_only = read_only
        # TODO validate kwargs
        self.kwargs = kwargs
        self.variable_expressions = {}
    
    def _get_pattern(self):
        return self._pattern
    def _set_pattern(self, pattern):
        self.pattern_re = re.compile(pattern)
        self._pattern = pattern
    pattern = property(_get_pattern, _set_pattern)
    
    def _get_name(self):
        return self._name
    def _set_name(self, name):
        if not re.match(r'[a-z][a-z-0-9]*(?:-[a-z0-9]+)*', name):
            raise ServiceConfigError("Bad service name " + name)
        self._name = name
    name = property(_get_name, _set_name)
    
    def _get_exposes(self):
        return self._exposes
    def _set_exposes(self, exposes):
        if not hasattr(exposes, "objects") and not callable(exposes):
            raise ServiceConfigError("Can only expose django Models or QuerySets, not " + str(exposes))
        self._exposes = exposes
    exposes = property(_get_exposes, _set_exposes)
    
    def _get_read_only(self):
        return self._read_only
    def _set_read_only(self, read_only):
        self._read_only = bool(read_only)
    read_only = property(_get_read_only, _set_read_only)
    
    def _get_django_url_pattern(self, postfix = None):
        url_pattern = self.pattern
        if postfix != None:
            if self.pattern.endswith("$"):
                url_pattern = url_pattern[:-1] + postfix + "$"
            else:
                url_pattern = url_pattern + postfix + "$"
        for name, regex in self.variable_expressions.iteritems():
            to_replace = "{%s}" % (name,)
            url_pattern = url_pattern.replace(to_replace, regex)
        re.compile(url_pattern)
        return url_pattern

    def _get_django_url(self):
        """How Django should expose the service."""
        url_pattern = self._get_django_url_pattern()
        view = make_service_view(self.exposes, self.read_only, **self.kwargs)
        return url(url_pattern, view, name=self.name, kwargs=self.kwargs)
    django_url = property(_get_django_url)
    
    def _get_django_documentation_url(self):
        """How Django should expose the documentation for an invocation of the service."""
        url_pattern = self._get_django_url_pattern(postfix="/doc.html")
        view = make_service_documentation_view(self)
        name = self.name + "-doc"
        return url(url_pattern, view, name=name)
    django_documentation_url = property(_get_django_documentation_url)
    
    def _get_pattern_str(self):
        """How documentation should describe the URL for the service."""
        p = self.pattern
        if p.startswith("^"):
            p = p[1:]
        if p.endswith("$"):
            p = p[:-1]
        p = p.replace(r"\.", ".")
        return p
    pattern_str = property(_get_pattern_str)

    def _get_pattern_str_url(self):
        """How documentation should link to the documentation for the service."""
        p = self.pattern
        if p.startswith("^"):
            p = p[1:]
        if p.endswith("$"):
            p = p[:-1]
        p = p.replace(r"\.", ".")
        p += "/doc.html"
        return p
    pattern_str_url = property(_get_pattern_str_url)
    
    def _get_django_pattern_str_url(self):
        """How Django should expose the documentation at its canonical URL."""
        r = self.pattern
        r = r.replace("{", "\\{")
        r = r.replace("}", "\\}")
        if r.endswith("$"):
            r = r[:-1]
        r += r"/doc\.html$"
        view = make_service_documentation_view(self)
        name = self.name + "-doc-canonical"
        return url(r, view, name=name)
    django_pattern_str_url = property(_get_django_pattern_str_url)

class ServiceConfig(object):
    def __init__(self, prefix, *args, **variable_expressions):
        self.prefix = prefix
        self.service_definitions = []
        self.variable_expressions = {}
        self.add_variable(**variable_expressions)
        self.add_service(*args)
        self.enable_documentation = True
        
    def add_service(self, *args, **kwargs):
        for a in args:
            if not isinstance(a, ServiceDefinition):
                raise ServiceConfigError("ServiceConfig only accepts ServiceDefinitions")
            a.variable_expressions = self.variable_expressions
        self.service_definitions.extend(args)
        self.add_variable(**kwargs)
    add_services = add_service
    add = add_service
    
    def add_variable(self, **args):
        for pattern in args.values():
            re.compile(pattern)
        self.variable_expressions.update(args)
    add_variables = add_variable

    def get_url_patterns(self):
        return patterns(self.prefix, *list([x.django_url for x in self.service_definitions]))
    
    def get_documentation_url_patterns(self):
        data=list([x.django_documentation_url for x in self.service_definitions])
        data.extend([x.django_pattern_str_url for x in self.service_definitions])
        return patterns(self.prefix, *data)
    
    def get_index_url_patterns(self):
        url_pattern = r'^/?$'
        view = make_service_index_view(self)
        return patterns(self.prefix, url(r'^/?$', view))
