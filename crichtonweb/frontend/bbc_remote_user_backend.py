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

from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import Group

from pdb import set_trace
import re
import sys

class BBCRemoteUserBackend(RemoteUserBackend):
    """ Subclasses the standard backend to extract the user name from the certificate header
      it is enabled by adding it into the settings file as 
      AUTHENTICATION_BACKENDS = (
          'BBCRemoteUserBackend',
      )
      
      The HTTP_REMOTE_USER should be overridden as in bbc_remote_user_backend.py
      its just too easy to spoof.  A good implementation would clean all the SSL
      headers before populating them with the current request so they can't be 
      spoofed.
      
      >>> from django.test.client import Client
      >>> c = Client()
      >>> response = c.post("/login/", {}, HTTP_REMOTE_USER='Test User')
      >>> response.status_code
      200
  	"""
    def __init__(self):
        self.email = ''
        self.first_name = ''
        self.last_name = ''
    
    def clean_username(self, username):
        """ Extract the user name, email, first & last names from HTTP_SSLCertSubject
        """
               
        result = re.search(r'Email=(.*?),', username)
        if result:
           self.email = result.group(1)

        result = re.search(r'CN=(.*?),', username)
        if result:
           cn = result.group(1)
           username = re.sub(' ','.', cn)
           # Extract first and last names
           spaceindex = cn.find(' ')
           if spaceindex > 0:
              self.first_name = cn[0:spaceindex]
              self.last_name = cn[spaceindex+1:]
           else:
              self.first_name = cn
        else:
           return 

        return username
    
    def configure_user(self, user):
        """ If a new user is created this method will be called
            we can set the other attributes here, such as email
            address etc.
        """
        user.email = self.email
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.is_staff = True              && This is anomalous it means all users are Staff
        user.set_password('password')
        user.save()
        if not user.groups.filter(name="Users").exists():
            user_group, created = Group.objects.get_or_create(name="Users")
            user.groups.add(user_group)
            user.save()
        return user
        
if __name__ == "__main__":
    """
    To run this test,
    $ cd crichtonweb
    $ DJANGO_SETTINGS_MODULE=settings python frontend/bbc_remote_user_backend.py
    """
    
    import doctest
    doctest.testmod()

# eof    

  
