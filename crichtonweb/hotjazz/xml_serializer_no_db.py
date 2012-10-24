
from crichtonweb.hotjazz.xml_serializer import Deserializer as Parent
from crichtonweb.hotjazz.xml_serializer import Serializer, getInnerText


class Deserializer(Parent):
    """Modified deserializer that does not use a database connection.
       Note this somewhat breaks the models that result!!"""
    
    def _resolve_natural_key_m2m(self, node, field):
        keys = node.getElementsByTagName('hotjazz:natural_ref')
        field_value = [getInnerText(k).strip() for k in keys]
        # TODO use model's built-in way to serialize natural key where available
        obj_pk = "-".join(field_value)
        return obj_pk

    def _resolve_natural_key_fk(self, node, field):
        return self._resolve_natural_key_m2m(node, field)