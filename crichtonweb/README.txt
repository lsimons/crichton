TL;DR version
-------------
It's all pretty much standard Django and python stuff. There's some
convenience scripts.

Study before you change
-----------------------
This application is built using the Django webapp framework for
Python. You should learn the basics of Django if you hope to
understand crichton:

    http://docs.djangoproject.com/en/1.2/intro/tutorial01/

Django doesn't provide built-in support for evolving database schemas,
so we use a Django extension for that called South:

    http://south.aeracode.org/

It is a good idea to study south for a bit if you will be changes or
adding Models; at least read through its tutorial. South can be a bit
flakey if you do complex stuff to the model. Avoid complex stuff :)

For the service APIs we have our own mini-framework, which is
unfortunate but there's no particularly good REST support in Django
yet and the other mini-frameworks out there aren't great either. You
can read about it a bit in

    hotjazz/README.txt

You'll have to learn a bit about python metaprogramming if you plan
to hack on that stuff:

    http://blog.ianbicking.org/python-metaprogramming-and-macros.html


Set up for development
----------------------
    mkdir -p /data/app-logs/crichton
    cd crichtonweb
    ./createdb.sh [-p[mysqlrootpassword]]
    python manage.py syncdb
        [yes] create admin user
        (add a superuser for yourself)

    ./manage.py migrate
    ./manage.py runserver

In another terminal

    (cd cli && ./put-sample-data.sh)


how to add entities
-------------------
1) define a django model in ${yourapp}/models.py, for example:

    class MyNewObject(models.Model):
        name = models.CharField(max_length=30,unique=True)
        foo = models.CharField(max_length=200,null=True,blank=True)
        audit_log = AuditLog()
        
        class Meta:
            app_label = "${yourapp}"
            ordering = ('name',)

2) make new database migration and apply to database

    ./manage.py schemamigration ${yourapp} --auto add_my_new_object
    ./manage.py migrate ${yourapp}

3) to define a REST API for the model,
   edit api/services.py, for example:

    service(
        pattern=r'^my_new_object/one/{name}\.{format}$',
        name="api-my_new_object-one",
        exposes=MyNewObject,
        exclude_fields=('secret','stuff'),
        get_for__name="name"
    )

4) to add the model to the django-admin interface,
   edit ${yourapp}/admin.py, for example:
   
       + class MyNewObjectAdmin(AuditedAdmin):
       +     list_display = ('name', 'foo')
       +     list_display_links = ('name',)
       +     list_filter = ('deleted',)
       +     fields = ('name', 'foo', 'deleted')
       +     search_fields = ('name', 'foo')
       + 
       
        for model in [IssueTracker,
                IssueTrackerProject,
       -        Issue]:
       +        Issue,
       +        MyNewObject]:

   if you are adding admin.py for the first time, you also need to
   add it to urls.py:

       + import crichtonweb.${yourapp}.admin

5) to add the model to the cli tool,
    you don't need to do anything currently. It's fully automagic.

6) to add the model to the user/operations permissions, edit settings.py AUTH_CONFIG:

        AUTH_CONFIG = {
            ...
            "group_permissions": [
                {
                    "group": "Users",
                    "grants": [
                        {
                            actions: ["add", "change", "delete"], 
                            models: [
                                "frontend.FollowedProduct",
                                ...
                                "${yourapp}.MyNewObject"
                                ...
    
    (if you don't do something like this, the model will not show up in the admin
    interface except for administrators.)

7) hand-test the admin app.
    
    Add some sample data in the UI by hand.

        ./manage.py runserver
        open http://localhost:8000/admin/${yourapp}/mynewobject/add/
            (add some sample data)
    
    Test it's all working.

8) add the sample data as XML to test the CLI

        cd cli;
        ./crichton.py list my_new_object
        ./crichton.py list my_new_object --xml
        ./crichton.py get my_new_object <key-for-your-data> --xml
        ./crichton.py get my_new_object <key-for-your-data> --xml > sample-data/my_new_object_<key-for-your-data>.xml
        ./crichton.py put my_new_object <key-for-your-data> --xml sample-data/my_new_object_<key-for-your-data>.xml
        vi sample-data/my_new_object_<key-for-your-data>.xml
            (remove the hotjazz:pk, format, remove the core:deleted element)
        ./crichton.py put my_new_object <key-for-your-data> --xml sample-data/my_new_object_<key-for-your-data>.xml
    
    add that last command to put-sample-data.sh. Run
    
        ./put-sample-data.sh
    
9) should be done. Test and commit.


Fiddling with fixture data
--------------------------
    core/management/commands/dumpdata.py is modified from
        http://www.djangosnippets.org/snippets/1457/

to be able to dump our model. If all is well, you can use

    ./manage.py dumpdata > file.json

to dump your current database, and

    ./manage.py loadddata ./file.json

to load that data back in. If all is not well, good luck. Something
that might help you then would perhaps be something like

    mysqldump -uroot --complete-insert --no-create-db --no-create-info \
            --skip-triggers crichton > data.sql
    ./dropdb.sh 
    ./createdb.sh 
    ./manage.py syncdb
    ./manage.py migrate
    echo "show tables" | mysql -uroot crichton | grep -v "Tables_in" > tables.txt
    for i in `cat tables.txt`; do echo "SET foreign_key_checks = 0; truncate table $i; SET foreign_key_checks = 1; " | mysql -uroot crichton; done
    mysql -uroot crichton < data.sql 

Note that we're moving away from using fixtures like this since we
can now populate the database using our own API pretty easily.
