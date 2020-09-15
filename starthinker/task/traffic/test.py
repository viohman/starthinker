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

from starthinker.util.google_api import API_DCM
from starthinker.util.dcm import get_profile_for_api
from starthinker.util.project import project, get_project


def _fail(message):
  print('-------------------------')
  print('*                       *')
  print('*                       *')
  print('* Bulkdozer Test Failed *')
  print('*                       *')
  print(message)
  print('*                       *')
  print('-------------------------')


def _passed():
  print('-------------------------')
  print('*                       *')
  print('*                       *')
  print('* Bulkdozer Test Passed *')
  print('*                       *')
  print('*                       *')
  print('-------------------------')


def bulkdozer_test():
  print('testing bulkdozer')

  if 'verify' in project.task['traffic']:
    is_admin, profile_id = get_profile_for_api(
        project.task['auth'], project.task['traffic']['account_id'])

    for entity in project.task['traffic']['verify']:
      service = getattr(
          API_DCM(project.task['auth'], internal=is_admin), entity['type'])
      cm_entity = service().get(profileId=profile_id, id=entity['id']).execute()

      values = entity['values']

      for key in values:
        if values[key] != cm_entity[key]:
          _fail('%s %s expected to be %s, was %s' %
                (entity['type'], key, values[key], cm_entity[key]))
          return

    _passed()
