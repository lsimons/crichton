"""
JSON serializer that spits out ExtJS compatible data.
"""

from django.utils import simplejson
from django.utils.encoding import smart_unicode
from crichtonweb.hotjazz.json_serializer import Serializer as BaseSerializer
from crichtonweb.hotjazz.json_serializer import Deserializer as BaseDeserializer
from crichtonweb.hotjazz.json_serializer import DjangoJSONEncoder

class Serializer(BaseSerializer):
    def dump(self, objects, stream, cls=DjangoJSONEncoder, **options):
        ext_dict = {'success': True, 'data': objects, 'message': ''}
        simplejson.dump(ext_dict, stream, cls=cls, **options)
    
    def end_object(self, obj):
        # override PythonSerializer#end_object to not add the fields:[] indirection
        #obj_data = {
        #    "model"  : smart_unicode(obj._meta),
        #    "pk"     : smart_unicode(obj._get_pk_val(), strings_only=True),
        #}
        obj_data = {}
        obj_data.update(self._current)
        self.objects.append(obj_data)
        self._current = None

def Deserializer(stream_or_string, **options):
    raise "TODO"
    #for obj in BaseDeserializer(stream_or_string, **options):
    #    yield obj
