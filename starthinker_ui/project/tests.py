# -*- coding: utf-8 -*-

###########################################################################
#
#  Copyright 2020 Google LLC
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
###########################################################################

from __future__ import unicode_literals

import os

from django.test import TestCase
from django.conf import settings

from starthinker_ui.account.tests import account_create
from starthinker_ui.project.models import Project


def project_create(share=''):

  with open(
      os.environ.get('STARTHINKER_SERVICE', 'MISSING RUN deploy.sh TO SET'),
      'r') as f:
    service = f.read()

  project = Project.objects.create(
      account=account_create(), service=service, share=share)

  return project


class ProjectTest(TestCase):

  def setUp(self):
    self.account = account_create()

    self.project_user = project_create()
    self.project_domain = project_create('domain')
    self.project_global = project_create('global')

  def test_ui_project(self):

    # not logged in ( blank )
    resp = self.client.get('/project/')
    self.assertEqual(resp.status_code, 200)

    self.client.force_login(
        self.account, backend=settings.AUTHENTICATION_BACKENDS[0])

    # logged in
    resp = self.client.get('/project/')
    self.assertEqual(resp.status_code, 200)

    self.assertContains(resp, self.project_user.identifier)
    self.assertContains(resp, self.project_domain.identifier)
    self.assertContains(resp, self.project_global.identifier)
    self.assertContains(resp, self.project_domain.share.upper())
    self.assertContains(resp, self.project_global.share.upper())

  def test_ui_project_edit(self):

    # not logged in ( blank )
    resp = self.client.get('/project/')
    self.assertEqual(resp.status_code, 200)

    self.client.force_login(self.account)

    # logged in
    resp = self.client.get('/project/edit/')
    self.assertEqual(resp.status_code, 200)

  def test_ui_recipe_edit(self):

    # not logged in ( redirect )
    resp = self.client.get('/recipe/edit/')
    self.assertEqual(resp.status_code, 302)

    self.client.force_login(
        self.account, backend=settings.AUTHENTICATION_BACKENDS[0])

    # logged in ( projects in form )
    resp = self.client.get('/recipe/edit/')
    self.assertEqual(resp.status_code, 200)
    self.assertContains(resp, self.project_user)
    self.assertContains(resp, self.project_domain)
    self.assertContains(resp, self.project_global)
