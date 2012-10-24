"""
XML serializer.

Modified from django.core.serializers.xml_serializer from Django 1.2.4.
Modified by Leo Simons for the BBC.
"""

__copyright__ = "Copyright (c) Django Software Foundation and individual contributors. Copyright (c) 2011 BBC."
__license__ = "Commercial"
__license_detail__ = """
Copyright (c) 2011 BBC.
All rights reserved.

Portions copyright (c) Django Software Foundation and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, 
       this list of conditions and the following disclaimer.
    
    2. Redistributions in binary form must reproduce the above copyright 
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
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

from django.conf import settings
from django.core.serializers import base
from django.core.exceptions import ValidationError
from django.db import models, DEFAULT_DB_ALIAS
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import smart_unicode
from xml.dom import pulldom
from xml.dom import Node
from xml import sax

from crichtonweb.hotjazz.utils import escape_xml_illegal_chars

class Serializer(base.Serializer):
    """
    Serializes a QuerySet to XML.
    """
    single_object = False
    objects_started = False
    list_elem_name = None
    ns = None
    
    def serialize(self, queryset, **options):
        self.single_object = options.get("single_object", False)
        return base.Serializer.serialize(self, queryset, **options)

    def indent(self, level):
        if self.options.get('indent', None) is not None:
            self.xml.ignorableWhitespace('\n' + ' ' * self.options.get('indent', None) * level)

    def start_serialization(self):
        """
        Start serialization -- open the XML document and the root element.
        """
        self.xml = SimplerXMLGenerator(self.stream, self.options.get("encoding", settings.DEFAULT_CHARSET))
        self.xml.startDocument()

    def end_serialization(self):
        """
        End serialization -- end the document.
        """
        if self.objects_started:
            self.indent(0)
            if not self.single_object:
                elem=""
                if self.ns:
                    elem += self.ns + ":"
                elem += self.list_elem_name
                self.xml.endElement(elem)
                self.indent(0)
        else:
            self.xml.startElement("empty", {})
            self.xml.endElement("empty")
        self.xml.endDocument()

    def start_object(self, obj):
        """
        Called as each object is handled.
        """
        if not hasattr(obj, "_meta"):
            raise base.SerializationError("Non-model object (%s) encountered during serialization" % type(obj))
        
        model_name = smart_unicode(obj._meta)
        elem_name = model_name.split(".")[-1]
        if not hasattr(obj._meta, 'ns'):
            setattr(obj._meta, 'ns', "_".join(model_name.split(".")[:-1]))
        if not self.ns:
            self.ns = obj._meta.ns
        if not hasattr(obj._meta, 'ns_uri'):
            setattr(obj._meta, 'ns_uri', "urn:x-ns:hotjazz:" + ".".join(model_name.split(".")[:-1]))

        xmlnstag="xmlns:" + obj._meta.ns
        attrs = {
            "xmlns:hotjazz" : "urn:x-ns:hotjazz",
            xmlnstag : obj._meta.ns_uri,
            "xmlns" : obj._meta.ns_uri
        }
        
        if not self.objects_started:
            self.objects_started = True
            
            if not self.single_object:
                self.list_elem_name = elem_name + "_list"
                attrs["hotjazz:type"] = "model_list"
                self.xml.startElement(obj._meta.ns + ":" + self.list_elem_name, attrs)
                self.indent(1)
        else:
            if self.single_object:
                raise base.SerializationError("Expecting one model object but got another one (%s) during serialization" % type(obj))
        
        obj_pk = obj._get_pk_val()
        attrs["hotjazz:type"] = "model"
        if obj_pk is not None:
            attrs["hotjazz:pk"] = smart_unicode(obj._get_pk_val())

        self.xml.startElement(obj._meta.ns + ":" + elem_name, attrs)
        
    
    def end_object(self, obj):
        """
        Called after handling all fields for an object.
        """
        if self.single_object:
            self.indent(0)
        else:
            self.indent(1)

        model_name = smart_unicode(obj._meta)
        elem_name = model_name.split(".")[-1]
        self.xml.endElement(obj._meta.ns + ":" + elem_name)

    def handle_field(self, obj, field):
        """
        Called to handle each field on an object (except for ForeignKeys and
        ManyToManyFields)
        """
        self.indent(2)
        
        self.xml.startElement(obj._meta.ns + ":" + field.name, {
            "hotjazz:type" : field.get_internal_type()
        })

        # Get a "string version" of the object's data.
        if getattr(obj, field.name) is not None:
            self.xml.characters(escape_xml_illegal_chars(field.value_to_string(obj)))
        else:
            pass
            #self.xml.addQuickElement("None")

        self.xml.endElement(obj._meta.ns + ":" + field.name)

    def handle_fk_field(self, obj, field):
        """
        Called to handle a ForeignKey (we need to treat them slightly
        differently from regular fields).
        """
        self._start_relational_field(obj, field, "ForeignKeyRelation")
        related = getattr(obj, field.name)
        if related is not None:
            elem_name = field.name + "_natural_ref"
            self.xml.startElement(obj._meta.ns + ":" + elem_name, {})

            if self.use_natural_keys and hasattr(related, 'natural_key'):
                # If related object has a natural key, use it
                related = related.natural_key()
                # Iterable natural keys are rolled out as subelements
                for key_value in related:
                    self.xml.startElement("hotjazz:natural_ref", {})
                    self.xml.characters(escape_xml_illegal_chars(smart_unicode(key_value)))
                    self.xml.endElement("hotjazz:natural_ref")
            else:
                if field.rel.field_name == related._meta.pk.name:
                    # Related to remote object via primary key
                    related = related._get_pk_val()
                else:
                    # Related to remote object via other field
                    related = getattr(related, field.rel.field_name)
                self.xml.startElement("hotjazz:pk_ref", {})
                self.xml.characters(escape_xml_illegal_chars(smart_unicode(related)))
                self.xml.endElement("hotjazz:pk_ref")

            self.xml.endElement(obj._meta.ns + ":" + elem_name)
        else:
            pass
            #self.xml.addQuickElement("None")
        self.xml.endElement(obj._meta.ns + ":" + field.name)

    def handle_m2m_field(self, obj, field):
        """
        Called to handle a ManyToManyField. Related objects are only
        serialized as references to the object's PK (i.e. the related *data*
        is not dumped, just the relation).
        """
        item_name = smart_unicode(field.rel.to._meta)
        item_elem_name = item_name.split(".")[-1]
        
        if field.rel.through._meta.auto_created:
            self._start_relational_field(obj, field, "ManyToManyRelation")
            if self.use_natural_keys and hasattr(field.rel.to, 'natural_key') and \
                    hasattr(field.rel.to._default_manager, 'get_by_natural_key'): # to match deserialize
                # If the objects in the m2m have a natural key, use it
                def handle_m2m(value):
                    natural = value.natural_key()
                    # Iterable natural keys are rolled out as subelements
                    self.xml.startElement(obj._meta.ns + ":" + item_elem_name, {})
                    for key_value in natural:
                        self.xml.startElement("hotjazz:natural_ref", {})
                        self.xml.characters(escape_xml_illegal_chars(smart_unicode(key_value)))
                        self.xml.endElement("hotjazz:natural_ref")
                    self.xml.endElement(obj._meta.ns + ":" + item_elem_name)
            else:
                def handle_m2m(value):
                    self.xml.addQuickElement(obj._meta.ns + ":" + item_elem_name, attrs={
                        'hotjazz:pk_ref' : smart_unicode(value._get_pk_val())
                    })
            at_least_one=False
            for relobj in getattr(obj, field.name).iterator():
                at_least_one=True
                self.indent(3)
                handle_m2m(relobj)

            if at_least_one:
                self.indent(2)
            self.xml.endElement(obj._meta.ns + ":" + field.name)

    def _start_relational_field(self, obj, field, reltype):
        """
        Helper to output the <field> element for relational fields
        """
        self.indent(2)
        self.xml.startElement(obj._meta.ns + ":" + field.name, {
            "hotjazz:type"  : reltype + "Field",
        })

class Deserializer(base.Deserializer):
    """
    Deserialize XML.
    
    TODO: use no hardcoded namespaces abbreviations
    """

    def __init__(self, stream_or_string, **options):
        super(Deserializer, self).__init__(stream_or_string, **options)
        parser = sax.make_parser()
        parser.setFeature(sax.handler.feature_namespaces,1)
        #parser.setFeature(sax.handler.feature_namespace_prefixes,1)
        self.event_stream = pulldom.parse(self.stream, parser)
        self.db = options.pop('using', DEFAULT_DB_ALIAS)

    def next(self):
        for event, node in self.event_stream:
            if event != "START_ELEMENT":
                continue
            
            if not node.hasAttribute("hotjazz:type"):
                continue
            
            nodeType = node.getAttribute("hotjazz:type")
            if nodeType == "model":
                self.event_stream.expandNode(node)
                return self._handle_object(node)
        raise StopIteration

    def _handle_object(self, node):
        """
        Convert a model node to a DeserializedObject.
        """
        # Look up the model using the model loading mechanism. If this fails,
        # bail.
        Model = self._get_model_from_node(node)

        # Start building a data dictionary from the object.
        # If the node is missing the pk set it to None
        if node.hasAttribute("hotjazz:pk"):
            pk = node.getAttribute("hotjazz:pk")
        else:
            pk = None

        data = {Model._meta.pk.attname : Model._meta.pk.to_python(pk)}

        # Also start building a dict of m2m data (this is saved as
        # {m2m_accessor_attribute : [list_of_related_objects]})
        m2m_data = {}

        # Deseralize each field.
        for child_node in node.childNodes:
            # ignore anything but elements
            if child_node.nodeType != Node.ELEMENT_NODE:
                continue
            
            # if the object has non-field contents, bail
            if not child_node.hasAttribute("hotjazz:type") \
                    or not child_node.getAttribute("hotjazz:type").endswith("Field"):
                raise base.DeserializationError("Unrecognized node (%s)" % smart_unicode(child_node))
            
            field_node = child_node
            field_name = field_node.tagName.split(":")[-1]
                
            # Get the field from the Model. This will raise a
            # FieldDoesNotExist if, well, the field doesn't exist, which will
            # be propagated correctly.
            field = Model._meta.get_field(field_name)

            # As is usually the case, relation fields get the special treatment.
            if field.rel and isinstance(field.rel, models.ManyToManyRel):
                m2m_data[field.name] = self._handle_m2m_field_node(field_node, field)
            elif field.rel and isinstance(field.rel, models.ManyToOneRel):
                data[field.attname] = self._handle_fk_field_node(field_node, field)
            else:
                value = None
                try:
                    value = field.to_python(getInnerText(field_node).strip())
                except ValidationError:
                    # assuming this is a NULL value for a non-char column
                    pass
                data[field.name] = value

        # Return a DeserializedObject so that the m2m data has a place to live.
        result = base.DeserializedObject(Model(**data), m2m_data)
        return result

    def _resolve_natural_key_m2m(self, node, field):
        keys = node.getElementsByTagName('hotjazz:natural_ref')
        field_value = [getInnerText(k).strip() for k in keys]
        obj_pk = field.rel.to._default_manager.db_manager(self.db).get_by_natural_key(*field_value).pk
        return obj_pk

    def _resolve_natural_key_fk(self, node, field):
        obj_pk = self._resolve_natural_key_m2m(node, field)
        # If this is a natural foreign key to an object that
        # has a FK/O2O as the foreign key, use the FK value
        if field.rel.to._meta.pk.rel:
            obj_pk = obj_pk.pk
        return obj_pk

    def _handle_fk_field_node(self, node, field):
        """
        Handle a field node for a ForeignKey
        """
        if hasattr(field.rel.to._default_manager, 'get_by_natural_key'):
            keys = node.getElementsByTagName('hotjazz:natural_ref')
            # If there are 'natural_ref' subelements, it must be a natural key
            if keys:
                obj_pk = self._resolve_natural_key_fk(node, field)
                return obj_pk
        # Otherwise, treat like a normal PK
        key = node.getElementsByTagName("hotjazz:pk_ref")
        if not key:
            return None
            # assuming for a moment this is actually a nullable field...
            # raise base.DeserializationError(
            #         "Expecting hotjazz:pk_ref to deserialize process field %s" % (
            #                 smart_unicode(field.name),))
        if key.length != 1:
            raise base.DeserializationError(
                    "Expecting one hotjazz:pk_ref to deserialize process field %s, got %d" % (
                            smart_unicode(field.name), key.length))
            
        field_value = getInnerText(key.item(0)).strip()
        obj_pk = field.rel.to._meta.get_field(field.rel.field_name).to_python(field_value)
        return obj_pk
    
    def _handle_m2m_field_node(self, node, field):
        """
        Handle a field node for a ManyToManyField.
        """
        if hasattr(field.rel.to._default_manager, 'get_by_natural_key'):
            def m2m_convert(n):
                keys = n.getElementsByTagName('hotjazz:natural_ref')
                # If there are 'natural' subelements, it must be a natural key
                if keys:
                    obj_pk = self._resolve_natural_key_m2m(node, field)
                else:
                    # Otherwise, treat like a normal PK value.
                    obj_pk = field.rel.to._meta.pk.to_python(n.getAttribute('hotjazz:pk_ref'))
                return obj_pk
        else:
            m2m_convert = lambda n: field.rel.to._meta.pk.to_python(n.getAttribute('hotjazz:pk_ref'))
        
        results = []
        for c in node.childNodes:
            # ignore anything but elements
            if c.nodeType != Node.ELEMENT_NODE:
                continue
            results.append(m2m_convert(c))
        return results

    def _get_model_from_node(self, node):
        """
        Helper to look up a model from a <type=model>.
        """

        name = ""
        #print "node.prefix", node.prefix
        #print "node.tagName", node.tagName
        #print "node.namespaceURI", node.namespaceURI
        if node.namespaceURI and node.namespaceURI.startswith("urn:x-ns:hotjazz:"):
            name = node.namespaceURI[len("urn:x-ns:hotjazz:"):] + ":" + \
                node.tagName.split(":")[-1]
        else:
            name = node.tagName
        #print "name", name

        model_identifier = name.replace("_", ".").replace(":", ".")
        #print "model_identifier", model_identifier

        try:
            Model = models.get_model(*model_identifier.split("."))
        except TypeError:
            raise
            #Model = None
        if Model is None:
            raise base.DeserializationError(
                "<%s> node has invalid model identifier: '%s'" % \
                    (node.nodeName, model_identifier))
        return Model


def getInnerText(node):
    """
    Get all the inner text of a DOM node (recursively).
    """
    # inspired by http://mail.python.org/pipermail/xml-sig/2005-March/011022.html
    inner_text = []
    for child in node.childNodes:
        if child.nodeType == child.TEXT_NODE or child.nodeType == child.CDATA_SECTION_NODE:
            inner_text.append(child.data)
        elif child.nodeType == child.ELEMENT_NODE:
            inner_text.extend(getInnerText(child))
        else:
           pass
    return u"".join(inner_text)

