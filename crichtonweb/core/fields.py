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
from django.utils.text import compress_string
from django.db.models.signals import post_init
import cStringIO, gzip

# adapted from http://djangosnippets.org/snippets/1495/

def uncompress_string(s):
    '''helper function to reverse django.utils.text.compress_string'''
    try:
        zbuf = cStringIO.StringIO(s)
        zfile = gzip.GzipFile(fileobj=zbuf)
        ret = zfile.read()
        zfile.close()
    except:
        ret = s
    return ret

class CompressedTextField(models.TextField):
    '''transparently compress data before hitting the db and uncompress after fetching'''
    """
    This code was taken from a Django snippet for Django 1.0.
    It appears to work but does not follow the Django 1.2 documented way of writing
    custom field classes, http://docs.djangoproject.com/en/1.2/howto/custom-model-fields/
    Might be worth rewriting at some time.
    """

    def get_db_prep_save(self, value, connection):
        if value is not None:
            if isinstance(value, unicode):
                value = value.encode('utf-8', 'replace')
            value = compress_string(value) 
        return models.TextField.get_db_prep_save(self, value, connection=connection)
 
    def _get_val_from_obj(self, obj):
        if obj:
            value = getattr(obj, self.attname)
            value = uncompress_string(value)
            try:
                if value is not None:
                    value = value.decode('utf-8', 'replace')
            except UnicodeDecodeError:
                pass
            except UnicodeEncodeError:
                pass
            return value
        else:
            return self.get_default() 
    
    def post_init(self, instance=None, **kwargs):
        value = self._get_val_from_obj(instance)
        if value:
            setattr(instance, self.attname, value)

    def contribute_to_class(self, cls, name):
        super(CompressedTextField, self).contribute_to_class(cls, name)
        post_init.connect(self.post_init, sender=cls)
    
    def get_internal_type(self):
        return "TextField"
                
    def db_type(self, connection):
        from django.conf import settings
        db_types = {'django.db.backends.mysql':'longblob','django.db.backends.sqlite3':'blob'}
        try:
            return db_types[ settings.DATABASES['default']['ENGINE'] ]
        except KeyError:
            raise Exception, '%s currently works only with: %s'%(self.__class__.__name__,','.join(db_types.keys()))
