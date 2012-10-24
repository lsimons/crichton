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
from lettuce import *
from lxml import html
from lettuce.django import django_url
from lettuce import world
from selenium import webdriver
#from selenium import selenium
import threading

#from crichtonweb.prodmgmt.models import Person
from django.contrib.auth.models import User

from pdb import set_trace

# 3 ways of writing page manipulations, all different syntax:
# a) Django client, use lxml to parse html
# b) Selenium WebDriver client, use their syntax
# c) Use original selenium? Remote?
#
# In this file, I'm using Selenium WebDriver

#
# Because the Selenium WebDriver folk are adamant that they are developing a "Browser Automation" tool, not
# "Web Application Testing" tool, they refuse to support header modification, so without a proxy server,
# we cannot use the usual header modification trick for authentication testing.
# Unfortunately, at time of writing, setting proxy settings didn't work so we can't use that either.
# So we shall log in using the old-fashioned username/password method :-)

#
# Setup/Teardown of Test Database
# Based on comment in https://github.com/gabrielfalcao/lettuce/issues/73
#
from django.core.management import call_command
from lettuce import before, world, after
from django.test.simple import DjangoTestSuiteRunner
from django.conf import settings
#@before.all
#def setup_test_database():
@before.harvest
def setup_test_database(vars):
    set_trace()
    world.test_runner = DjangoTestSuiteRunner(interactive=False)
    world.test_runner.setup_test_environment()
    world.test_db = world.test_runner.setup_databases()
    call_command('migrate', **{"settings": settings.SETTINGS_MODULE})

@after.harvest
#@after.all
def teardown_test_database(results):
    world.test_runner.teardown_databases(world.test_db)
    world.test_runner.teardown_test_environment()

#@before.each_feature
#def before_each_feature(feature):
#    call_command('flush', **{"settings": settings.SETTINGS_MODULE, "interactive": False})

#
# Other Setup/Teardown
#
@before.harvest
def set_browser(vars):

    if True:
        # This should set the proxy settings, however at time of writing (July 2011), only 2 out of the 4
        # settings actually change.
        # http://code.google.com/p/selenium/issues/detail?id=2061
        PROXY_PORT = 9638
        profile = webdriver.FirefoxProfile()
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", "127.0.0.1")
        profile.set_preference("network.proxy.http_port", PROXY_PORT)
        profile.set_preference("network.proxy.no_proxies_on", " ")
        profile.update_preferences()

        world.driver = webdriver.Firefox(firefox_profile=profile)
    else:
        #world.driver = webdriver.Firefox()
        world.driver = webdriver.Chrome()
        # Both these crash when attempting to post the login form.
        # I'm getting the impression it would be worth waiting a few months to let this new selenium code
        # settle down
    
@before.harvest
def create_admin_user(vars):
    first_name = "Admin"
    last_name = "Smith"
    username = "%s %s" % (first_name, last_name)
    email = "%s@testcompany.com" % first_name.lower()

    # crichton model
#    person = Person(username=username, first_name=first_name, last_name=last_name, email=email)
#    person.save()

    # equivalent Django model
    #user = create_superuser(username, email, password)
    user = User(username=username, first_name=first_name, last_name=last_name, email=email)
    password = User.objects.make_random_password()
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

    world.admin_user = user
    world.admin_user_pw = password

#@before.harvest
#def create_staff_user(vars):
#    assert False, 'This step must be implemented'
#    
#@before.harvest
#def create_ordinary_user(vars):
#    assert False, 'This step must be implemented'
    
@after.harvest
def close_browser(results):
    world.driver.close()

#
# Common Steps
#
@step(u'I am not logged in')
def i_am_not_logged_in(step):
    # noop
    pass

@step(u'I am logged in')
def i_am_logged_in(step):
    pass
    return
    # noop
    url = django_url("/admin/")
    world.driver.get(url)
    set_trace()
    frm_login = world.driver.find_element_by_id("login-form")
    fld_username = world.driver.find_element_by_id("id_username")
    fld_password = world.driver.find_element_by_id("id_password")
    fld_submit = world.driver.find_element_by_xpath("//input[@type='submit']")
    fld_username.send_keys(world.admin_user.username)
    fld_password.send_keys(world.admin_user_pw)
    #frm_login.submit()
    fld_submit.click()
    
@step('I go to "(.*)"')
def i_go_to(step, url):
    url = django_url(url)
    world.driver.get(url)
    world.dom = html.fromstring(world.driver.page_source)

@step(u'I press "(.*)"')
def press_button(step, button_name):
    assert False, 'This step must be implemented'

@step(u'I should have gone to "(.*)"')
def i_should_have_gone_to_group1(step, group1):
    print world.driver.current_url()
    assert False, 'This step must be implemented'

@step(u'Then I should see the button "(.*)"')
def then_i_should_see_the_button_group1(step, group1):
    assert False, 'This step must be implemented'

@step(u'And I am logged in')
def and_i_am_logged_in(step):
    assert False, 'This step must be implemented'

# eof
