"""
Various helpers.

Modified from piston.utils from piston 0.2.2.
Modified by Leo Simons for the BBC.
"""

__copyright__ = "Copyright (c) Jesper Noer and contributors. Copyright (c) 2011 BBC."
__license__ = "Commercial"
__license_detail__ = """
Copyright (c) 2011 BBC.
All rights reserved.

Copyright (c) Jesper Noer and contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, 
       this list of conditions and the following disclaimer.
    
    2. Redistributions in binary form must reproduce the above copyright 
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of piston nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import re
import sys
import traceback
import StringIO

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.

from crichtonweb.hotjazz import _CONTENT_TYPES
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.utils.decorators import available_attrs
from django.http import HttpResponse
from django.utils.html import escape

try:
    from django.utils.html import escapejs # django 1.2.5+
except ImportError:
    # backport from django 1.2.5
    from django.utils.functional import allow_lazy
    from django.utils.safestring import mark_safe
    from django.utils.encoding import force_unicode

    _base_js_escapes = (
        ('\\', r'\u005C'),
        ('\'', r'\u0027'),
        ('"', r'\u0022'),
        ('>', r'\u003E'),
        ('<', r'\u003C'),
        ('&', r'\u0026'),
        ('=', r'\u003D'),
        ('-', r'\u002D'),
        (';', r'\u003B'),
        (u'\u2028', r'\u2028'),
        (u'\u2029', r'\u2029')
    )

    # Escape every ASCII character with a value less than 32.
    _js_escapes = (_base_js_escapes +
                   tuple([('%c' % z, '\\u%04X' % z) for z in range(32)]))

    def escapejs(value):
        """Hex encodes characters for use in JavaScript strings."""
        for bad, good in _js_escapes:
            value = mark_safe(force_unicode(value).replace(bad, good))
        return value
    escapejs = allow_lazy(escapejs, unicode)

def coerce_put_post(request): # from piston
    """
    Django doesn't particularly understand REST.
    In case we send data over PUT, Django won't
    actually look at the data and load it. We need
    to twist its arm here.
    
    The try/except abominiation here is due to a bug
    in mod_python. This should fix it.
    """
    if request.method == "PUT":
        try:
            request.method = "POST"
            request._load_post_and_files()
            request.method = "PUT"
        except AttributeError:
            request.META['REQUEST_METHOD'] = 'POST'
            request._load_post_and_files()
            request.META['REQUEST_METHOD'] = 'PUT'
            
        request.PUT = request.POST

# xml 1.0 valid characters:
#    Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
# so to invert that, not in Char ::
#       x0 - x8 | xB | xC | xE - x1F 
#       (most control characters, though TAB, CR, LF allowed)
#       | #xD800 - #xDFFF
#       (unicode surrogate characters)
#       | #xFFFE | #xFFFF |
#       (unicode end-of-plane non-characters)
#       >= 110000
#       that would be beyond unicode!!!
_illegal_xml_chars_RE = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')

def escape_xml_illegal_chars(val, replacement='?'):
    """Filter out characters that are illegal in XML.
    
    Looks for any character in val that is not allowed in XML
    and replaces it with replacement ('?' by default).
    
    >>> escape_xml_illegal_chars("foo \x0c bar")
    u'foo ? bar'
    >>> escape_xml_illegal_chars("foo \x0c\x0c bar")
    u'foo ?? bar'
    >>> escape_xml_illegal_chars("foo \x1b bar")
    u'foo ? bar'
    >>> escape_xml_illegal_chars(u"foo \uFFFF bar")
    u'foo ? bar'
    >>> escape_xml_illegal_chars(u"foo \uFFFE bar")
    u'foo ? bar'
    >>> escape_xml_illegal_chars(u"foo bar")
    u'foo bar'
    >>> escape_xml_illegal_chars(u"foo bar", "")
    u'foo bar'
    >>> escape_xml_illegal_chars(u"foo \uFFFE bar", "BLAH")
    u'foo BLAH bar'
    >>> escape_xml_illegal_chars(u"foo \uFFFE bar", " ")
    u'foo   bar'
    >>> escape_xml_illegal_chars(u"foo \uFFFE bar", "\x0c")
    u'foo \\x0c bar'
    >>> escape_xml_illegal_chars(u"foo \uFFFE bar", replacement=" ")
    u'foo   bar'
    """
    if not isinstance(val, unicode):
        val = unicode(val)
    result = _illegal_xml_chars_RE.sub(replacement, val)
    if not isinstance(result, unicode):
        result = unicode(result)
    return result

def _error_response(request, exc_info, *args, **kwargs):
    exc_type = exc_info[0]
    exc_value = exc_info[1]
    exc_traceback = exc_info[2]
    buf = StringIO.StringIO()
    traceback.print_tb(exc_traceback, None, buf)
    traceback_str = buf.getvalue()
    
    format = kwargs.get("format", "json")
    content_type = _CONTENT_TYPES.get(format, "application/json")
    
    status = kwargs.get("status", 500)
    if hasattr(exc_value, "request") and hasattr(exc_value.request, "status"):
        status = exc_value.request.status or status
    elif hasattr(exc_value, "status"):
        status = exc_value.status or status
    
    if format == "xml":
        escapefunc = escape
    else:
        escapefunc = escapejs
    
    ctx = {
        "status": escapefunc(str(status)),
        "exc_value": escapefunc(str(exc_value)),
        "exc_type": escapefunc(str(exc_type)),
        "traceback_str": escapefunc(traceback_str),
    }
    
    # note the use of simple % instead of a serialization library is a choice here:
    #   we don't want to risk having serialization errors get in the way of spitting
    #   out our error message
    body = None
    if format == "xml":
        body = """<?xml version="1.0" encoding="utf-8"?>
<hotjazz:error
        xmlns="urn:x-ns:hotjazz"
        xmlns:hotjazz="urn:x-ns:hotjazz"
        hotjazz:type="exception">
    <hotjazz:status hotjazz:type="IntegerField">%(status)s</hotjazz:status>
    <hotjazz:detail hotjazz:type="CharField">%(exc_value)s</hotjazz:detail>
    <hotjazz:error_type hotjazz:type="CharField">%(exc_type)s</hotjazz:error_type>
    <hotjazz:traceback hotjazz:type="CharField">
%(traceback_str)s
    </hotjazz:traceback>
</hotjazz:error>
""" % ctx
    else: # assume json
        body = """
{
    "status": "%(status)s",
    "detail": "%(exc_value)s",
    "error_type": "%(exc_type)s",
    "traceback": "%(traceback_str)s",
}
""" % ctx
    
    return HttpResponse(body, content_type=content_type, status=int(status))

def intercept_api_exceptions(func):
    def inner_func(request, *args, **kwargs):
        response = None
        try:
            response = func(request, *args, **kwargs)
        except:
            exc_info = sys.exc_info()
            #try:
            response = _error_response(request, exc_info, *args, **kwargs)
            #except:
            #    raise exc_info[0], exc_info[1], exc_info[2]
        return response
    return wraps(func, assigned=available_attrs(func))(inner_func)

class RuntimeServiceConfigError(ImproperlyConfigured):
    pass

class HttpError(Exception):
    def __init__(self, desc, status):
        Exception.__init__(self, desc)
        self.status = status

def MultipleResults(Exception):
    pass

def get_one(iterable): # todo move me
    it = iterable.__iter__()
    obj = it.next()
    try:
        it.next()
        raise MultipleResults
    except StopIteration:
        pass
    return obj
