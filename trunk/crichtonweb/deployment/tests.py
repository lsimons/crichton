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
import logging

from django.core.exceptions import PermissionDenied

from crichtonweb.core.tests import crichtonTestCase
from crichtonweb.deployment.models import *
from crichtonweb.package.tests import create_tst_packagename
from crichtonweb.system.tests import create_tst_environment, create_tst_pool, create_tst_node
from crichtonweb.prodmgmt.tests import create_tst_product

#
# Generators
#
def _gen_applicationdeployment():
    while True:
        env = create_tst_environment()
        pool = create_tst_pool()
        recipe = gen_recipe.next()
        pd = gen_productdeployment.next()
        ad = ApplicationDeployment(environment=env, pool=pool, recipe=recipe, product_deployment=pd)
        ad.save()
        yield ad
gen_applicationdeployment = _gen_applicationdeployment()

def _gen_deploymentsystem():
    num = 0
    while True:
        ds = DeploymentSystem(name="ds_%s" % num, display_name="Deployment System %s" % num)
        ds.save()
        yield ds
        num += 1
gen_deploymentsystem = _gen_deploymentsystem()

def _gen_deploymentpreference():
    num = 0
    while True:
        env = create_tst_environment()
        ds = gen_deploymentsystem.next()
        dp = DeploymentPreference(environment = env, deployment_system=ds, preference_number=num)
        dp.save()
        yield dp
        num += 1
gen_deploymentpreference = _gen_deploymentpreference()

def _gen_nodedeployment():
    while True:
        ad = gen_applicationdeployment.next()
        node = create_tst_node()
        nd = NodeDeployment(application_deployment=ad, node=node)
        nd.save()
        yield nd
gen_nodedeployment = _gen_nodedeployment()

def _gen_productdeployment():
    while True:
        product = create_tst_product()
        env = create_tst_environment()
        pd = ProductDeployment(product=product, environment=env)
        pd.save()
        yield pd
gen_productdeployment = _gen_productdeployment()

def _gen_recipe():
    num = 0
    while True:
        ds = gen_deploymentsystem.next()
        recipe = Recipe(name="recipe %s" % num, deployment_system=ds)
        recipe.save()
        yield recipe
        num += 1
gen_recipe = _gen_recipe()

def _gen_recipepackage():
    num = 0
    while True:
        r = gen_recipe.next()
        p = create_tst_packagename()
        me = RecipePackage(recipe=r, package=p)
        me.save()
        yield me
        num += 1
gen_recipepackage = _gen_recipepackage()

#
# Test Cases
#
class ApplicationDeploymentTestCase(crichtonTestCase):

    def test_applicationdeployment(self):
        ad = gen_applicationdeployment.next()
        self.run_std_tsts(ad)
        self.assertRaises(PermissionDenied, ad.delete)
        
    def test_deploymentsystem(self):
        ds = gen_deploymentsystem.next()
        self.run_std_tsts(ds)
        ds.delete()
        
    def test_deploymentpreference(self):
        dp = gen_deploymentpreference.next()
        self.run_std_tsts(dp)
        dp.delete()
        
    def test_nodedeployment(self):
        me = gen_nodedeployment.next()
        self.run_std_tsts(me)
        self.assertRaises(PermissionDenied, me.delete)
        
    def test_productdeployment(self):
        me = gen_productdeployment.next()
        self.run_std_tsts(me)
        self.assertRaises(PermissionDenied, me.delete)
        
    def test_recipe(self):
        me = gen_recipe.next()
        self.run_std_tsts(me)
        me.delete()

    def test_recipepackage(self):
        me = gen_recipepackage.next()
        self.run_std_tsts(me)
        me.delete()

# eof
