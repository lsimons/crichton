Hotjazz is yet another half-baked mini-framework that you plug into
Django to produce RESTful (well sort-of RESTful, it doesn't really do
hyperlinking of any kind) web services semi-automatically based on
your django-orm Model definitions.

Hotjazz especially shines when
* you're prepared to jump in and fiddle with things yourself if they
  don't quite do what you need them to, yet
* you need to expose a lot of django objects over http in a sort-of
  reasonable way
* you don't care very much about doing "proper" REST but you need or
  want to go a bit beyond Django's built in support for 
    application/x-www-form-urlencoded
* you want to write very little code
* you don't need much documentation or handholding

If none of the above is true, don't use it. Even if those things are
true you may want to used django-piston instead.

Usage example:

        # in settings.py
        SERIALIZATION_MODULES = {
            "xml" : "hotjazz.xml_serializer",
            "json" : "hotjazz.json_serializer",
        }

        # in urls.py
        urlpatterns = patterns('',
            # your other stuff here...
        )
    
        from django.contrib.auth.models import User
        from hotjazz.conf import service_config, service
    
        services = service_config('api',
            service(
                pattern=r'^user/one/{username}\.{format}$',
                name="api-username-one",
                exposes=User,
                exclude_fields=('password',),
                get_for__username="username"
            ),
            service(
                pattern=r'^user/list/all\.{format}$',
                name="api-username-all",
                exposes=User.objects.all,
                exclude_fields=('password',)
            ),
            username=r'(?P<username>.{1,255})',
        )
    
        urlpatterns = services.get_documentation_url_patterns()
        urlpatterns += services.get_index_url_patterns()
        
        # services go last because doc regexes need to get preference
        urlpatterns += services.get_url_patterns()
        
        # on the command line
        ./manage.py runserver
        
        # on another command line
        curl http://localhost:8000/api/user/list/all.xml
        curl http://localhost:8000/api/user/one/katie.xml > katie.xml
        cat katie.xml | sed 's/Cruise-Holmes/Holmes/g' > katie-divorce.xml
        curl -X POST -T katie-divorce.xml \
                http://localhost:8000/api/user/one/katie.xml

Hotjazz is inspired by but very different from django-piston. It uses some
bits of code from django-piston.

Hotjazz includes custom JSON and XML serializers that plug into the django
serialization framework. They're derivatives of code from the django core
project.

Hotjazz was written in about a day and a half by Leo Simons for the BBC as
part of another project. If you're reading this the BBC probably gracefully
open sourced it. Thanks, BBC!
