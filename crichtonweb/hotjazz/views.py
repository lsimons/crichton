"""
Generic views that can expose Models, QueryObjects and Callables,
as well as their documentation.
"""
# Copyright (c) 2011 BBC. All rights reserved.

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core import serializers
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from crichtonweb.hotjazz.utils import coerce_put_post, intercept_api_exceptions
from crichtonweb.hotjazz.utils import RuntimeServiceConfigError, HttpError, MultipleResults, get_one
from crichtonweb.hotjazz import _CONTENT_TYPES

def make_service_view(to_expose, read_only=False, **config_kwargs):
    filter_config = {}
    thing_to_expose=[to_expose] # extra wrap so callable_service_view has something to change
    
    # this looks for kwargs like
    #   get_for__username="person__user__username"
    # and saves them as a dictionary like
    #   "person__user__username" : "username"
    for k,v in config_kwargs.iteritems():
        if not k.startswith("get_for__"):
            continue
        look_for_var = k[len("get_for__"):]
        look_for_clause = v
        filter_config[look_for_clause] = look_for_var

    def make_query_filter(request, **query_kwargs):
        # this looks for variables in kwargs based on
        # the needed variables identified in filter_config, resulting
        # in something effectively like
        #   to_expose.objects.get("person__user__username"=kwargs["username"])
        query_filter={}
        for look_for_clause,look_for_var in filter_config.iteritems():
            look_for_val=query_kwargs[look_for_var]
            query_filter[look_for_clause]=look_for_val
        return query_filter
    
    @csrf_exempt
    @intercept_api_exceptions
    def single_object_service_view(request, **single_kwargs):
        """Generic RESTful web service view that should handle any Model."""
        cls=thing_to_expose[0]
        field_names = getattr(cls, '_hotjazz_field_names')
        query_filter=make_query_filter(request,**single_kwargs)
        format = single_kwargs.get("format", "json")

        content_type = _CONTENT_TYPES.get(format, "application/json")

        method = request.method.upper()
        if method == "GET":
            try:
                obj = cls.objects.get(**query_filter)
            except ObjectDoesNotExist:
                raise HttpError("Object not found", status=404)
            body = serializers.serialize(format, (obj,), single_object=True,
                    fields=field_names, indent=4, use_natural_keys=True)
            return HttpResponse(body, content_type=content_type, status=200)
        elif read_only:
            raise HttpError("Only GET is allowed here, not %s\n" % request.method, status=405)
        elif method in ("POST", "PUT"):
            if method == "PUT":
                coerce_put_post(request)
            
            deserialized = serializers.deserialize(format, request.raw_post_data)
            obj = None
            try:
                obj = get_one(deserialized)
            except MultipleResults:
                raise HttpError("Deserialized multiple objects, but can take only one", status=400)
            except StopIteration:
                raise HttpError("Deserialized no objects", status=400)
            if obj.object._meta.app_label != cls._meta.app_label or \
                obj.object._meta.object_name != cls._meta.object_name:
                raise HttpError("Deserialized object is of type %s.%s, expected %s.%s\n" % (
                        obj.object._meta.app_label, obj.object._meta.object_name,
                        cls._meta.app_label, cls._meta.object_name), status=400)
            
            orig_obj = None
            code = 200
            try:
                orig_obj = cls.objects.get(**query_filter)
            except ObjectDoesNotExist:
                pass
            if not orig_obj:
                obj.save()
                code = 201
            elif not hasattr(obj.object, "pk") or obj.object.pk == None:
                obj.object.pk = orig_obj.pk
                obj.save()
            else:
                if not obj.object.pk == orig_obj.pk:
                    raise HttpError("You specified primary key %s, but should be %s\n" % (obj.object.pk, orig_obj.pk), status=400)
                obj.save()
            return HttpResponse("Saved.\n", content_type='text/plain', status=code)
        else:
            raise HttpError("Only GET/PUT/POST is allowed here, not %s" % request.method, status=405)

    @csrf_exempt
    @intercept_api_exceptions
    def object_list_service_view(request, **list_kwargs):
        """Generic RESTful web service view that should handle any QuerySet."""
        query_filter=make_query_filter(request,**list_kwargs)
        
        qs=thing_to_expose[0]
        field_names = getattr(qs, '_hotjazz_field_names')
        if len(query_filter) > 0:
            qs = qs.filter(**query_filter)
        method = request.method.upper()
        if method != "GET":
            raise HttpError("Only GET is allowed here, not %s\n" % request.method, status=405)

        format = list_kwargs.get("format", "json")
        content_type = _CONTENT_TYPES.get(format, "application/json")
        body = serializers.serialize(format, qs, single_object=False,
                fields=field_names, indent=4, use_natural_keys=True)
        return HttpResponse(body, content_type=content_type, status=200)
    
    def get_object_or_qs_view(thing_to_make_view_for):
        """Internal helper than can make either a Model view or a QuerySet view."""
        # this is an internal function so it can be called from callable_service_view()
        view = None
        model_options = None
        if hasattr(thing_to_make_view_for, "objects") and \
                hasattr(thing_to_make_view_for.objects, "get"):
            model_options = thing_to_make_view_for._meta
            view = single_object_service_view
        if isinstance(thing_to_make_view_for, QuerySet):
            model_options = thing_to_make_view_for.model._meta
            view = object_list_service_view
        
        if model_options:
            field_names = list([field.name for field in model_options.fields])
            m2m_field_names = list([field.name for field in model_options.many_to_many])
            field_names.extend(m2m_field_names)
            for exclude in config_kwargs.get("exclude_fields", []):
                if exclude in field_names:
                    field_names.remove(exclude)
            setattr(thing_to_make_view_for, '_hotjazz_field_names', field_names)
        
        return view
    
    @csrf_exempt
    @intercept_api_exceptions
    def callable_service_view(request, **runtime_kwargs):
        """Generic RESTful web service view that can invoke a callable
                that should return a Model or QuerySet."""
        thing_to_expose[0] = to_expose()
        view = get_object_or_qs_view(thing_to_expose[0])
        if not view:
            raise RuntimeServiceConfigError(
                    "Can only expose django Models or QuerySets, not " + str(to_expose))
        else:
            return view(request, **runtime_kwargs)
    
    view = get_object_or_qs_view(to_expose)
    if not view:
        if callable(to_expose):
            return callable_service_view
        else:
            raise RuntimeServiceConfigError(
                    "Can only expose django Models or QuerySets, not " + str(to_expose))
    else:
        return view

# todo auto-generate documentation

def make_service_documentation_view(service):
    def service_documentation_view(request, **kwargs):
        to_expose=service.exposes
        if callable(to_expose):
            to_expose = to_expose()
        
        model = to_expose
        returns_list = isinstance(to_expose, QuerySet)
        if returns_list:
            model = to_expose.model
        meta = model._meta
        object_name = meta.object_name
        pattern_str = service.pattern_str
        read_only = service.read_only or returns_list
        methods = read_only and "GET" or "GET, PUT, POST"
        
        variables = locals()
        variables.update(meta.__dict__)
        
        body = """
        <html>
        <head><title>API docs for %(pattern_str)s</title></head>
        <body>
        <a href="javascript:history.go(-1)">&lt;&lt; back</a>
        <h1>API docs for %(pattern_str)s</h1>
        <pre>
Returns a list:          %(returns_list)s
Http methods:            %(methods)s

Exposes objects of type: %(object_name)s
    
  Supported fields:""" % variables
        
        for field in meta.fields:
            data = dict(field.__dict__)
            data["cls"] = field.__class__.__name__
            data["unique"] = field.unique
            data["default"] = str(data["default"])
            if "NOT_PROVIDED" in data["default"]:
                data["default"] = "None"
            choices = [choice for (choice,value) in field.choices]
            data["restricts_choices"] = len(choices) > 0
            if data["restricts_choices"]:
                data["choices"] = "Choices:    " + ", ".join(choices) + "\n"
            else:
                data["choices"] = ""
            
            if field.rel:
                data["points_to"] = "\n        points to:              " + \
                        field.rel.to._meta.object_name + " (" +\
                        str(field.__class__.__name__).replace("Rel", "") + ")"
            else:
                data["points_to"] = ""
            body += """
    %(name)s : %(cls)s
            %(help_text)s%(points_to)s
        maximum length:         %(max_length)s
        auto-created:           %(auto_created)s
        can be null:            %(null)s
        can be blank:           %(blank)s
        is unique:              %(unique)s
        default value:          %(default)s
        restricts choices:      %(restricts_choices)s
            %(choices)s""" % data
        body += """
        </pre>
        </body>
        </html>
        """
        
        return HttpResponse(body, content_type='text/html', status=200)
    
    return service_documentation_view

def make_service_index_view(service_config):
    def service_index_view(request, **kwargs):
        
        body = """
        <html>
        <head><title>List of available services</title></head>
        <body>
        <h1>List of available services:</h1>
        <ul>
        """
        for service in service_config.service_definitions:
            pattern_str = service.pattern_str
            service_doc_url = service.pattern_str_url
            body += """
            <li><a href="%(service_doc_url)s">%(pattern_str)s</a></li>
            """ % locals()
        body += """
        </ul>
        </body>
        </html>
        """
        return HttpResponse(body, content_type='text/html', status=200)
    
    return service_index_view
