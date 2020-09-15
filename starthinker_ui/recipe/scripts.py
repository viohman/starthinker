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

import os
import re
import json
import pprint
from copy import deepcopy
from datetime import datetime, date

from django.conf import settings

from starthinker.config import UI_ROOT
from starthinker.script.parse import json_set_fields, text_set_fields
from starthinker.util.project import get_project

# cache scripts in memory
SCRIPTS = {}


def load_scripts():
  if not SCRIPTS:
    for root, dirs, files in os.walk(UI_ROOT + '/scripts/'):
      for filename in files:
        if filename.endswith('.json'):
          try:
            script = get_project(root + filename)
            if not 'script' in script:
              continue
            script['path'] = root + filename
            SCRIPTS[filename.replace('script_', '', 1).replace('.json', '',
                                                               1)] = script
            print('OK', filename)
          except Exception as e:
            print('ERROR:', filename, str(e))


# Try to load from the lookup script ( appengine can't read files so need to generate script )
try:
  from starthinker_ui.recipe.scripts_lookup import SCRIPTS
  print('Loading From: starthinker.starthinker_ui.recipe.scripts_lookup')
  print(
      'To load from scripts directly delete: starthinker/starthinker_ui/recipe/scripts_lookup.py'
  )
# If it fails, load the scripts directly from the json files
except ImportError as e:
  print('Loading From: script_.*\.json')
  load_scripts()


class Script:

  @staticmethod
  def get_scripts(account_email=None, ui=False):
    for tag in sorted(iter(SCRIPTS.keys())):
      if account_email in SCRIPTS[tag]['script'].get('private',
                                                     (account_email,)):
        if not ui or ('from' in SCRIPTS[tag]['script'] and
                      'to' in SCRIPTS[tag]['script']):
          yield Script(tag)

  def __init__(self, tag):
    self.tag = tag
    self.script = SCRIPTS.get(tag, {})

  def exists(self):
    return self.script != {}

  def get_tag(self):
    return self.tag

  def get_link(self):
    return '%s/solution/%s/' % (
        settings.CONST_URL,
        self.tag,
    )

  def get_link_client(self):
    if self.script.get('script', {}).get('license',
                                         '') == 'Apache License, Version 2.0':
      return 'https://google.github.io/starthinker/solution/%s/' % self.tag
    else:
      return ''

  def get_link_ui(self):
    return '/recipe/%s/?script=%s' % ('manual' if self.is_manual() else 'edit',
                                      self.get_tag())

  def get_link_colab(self):
    return 'https://colab.research.google.com/github/google/starthinker/blob/master/colabs/%s.ipynb' % self.get_tag(
    )

  def get_link_airflow(self):
    return 'https://github.com/google/starthinker/blob/master/dags/%s_dag.py' % self.get_tag(
    )

  def get_released(self):
    try:
      return datetime.strptime(
          self.script.get('script', {}).get('released', ''), '%Y-%m-%d').date()
    except:
      return None

  def get_released_ago(self):
    agos = []
    days = (date.today() - self.get_released()).days

    if days <= 7:
      agos.append('7 days')
    if days <= 30:
      agos.append('30 days')
    if days <= 90:
      agos.append('90 days')
    if days > 90:
      agos.append('older')

    return agos

  def get_name(self):
    return self.script.get('script', {}).get('title', '')

  def get_icon(self):
    return self.script.get('script', {}).get('icon', '')

  def get_description(self, variables={}):
    return text_set_fields(
        self.script.get('script', {}).get('description', ''), variables)

  def get_instructions(self, variables={}):
    return [
        text_set_fields(instruction, variables)
        for instruction in self.script.get('script', {}).get(
            'instructions', [])
    ]

  def get_authors(self):
    return set(deepcopy(self.script.get('script', {}).get('authors', [])))

  def get_image(self):
    return self.script.get('script', {}).get('image', None)

  def get_sample(self):
    return self.script.get('script', {}).get('sample', None)

  def get_test(self):
    return self.script.get('script', {}).get('test', None)

  def get_documentation(self):
    return self.script.get('script', {}).get('documentation', None)

  def get_open_source(self):
    if self.script.get('script', {}).get('license',
                                         '') == 'Apache License, Version 2.0':
      return 'https://github.com/google/starthinker/blob/master' + self.script[
          'path'].replace(UI_ROOT, '', 1)
    else:
      return ''

  def get_from(self):
    return self.script.get('script', {}).get('from', [])

  def get_to(self):
    return self.script.get('script', {}).get('to', [])

  def get_pitches(self):
    return self.script.get('script', {}).get('pitches', [])

  def get_impacts(self):
    return self.script.get('script', {}).get('impacts', {})

  def get_tasks(self):
    return deepcopy(self.script.get('tasks', []))

  def get_tasks_linked(self):
    tasks = self.get_tasks()
    data = json.dumps(tasks, indent=4)
    for task in set([next(iter(task.keys())) for task in tasks]):
      data = re.sub(
          r'\n {8}"%s": {' % task,
          '\n        "<a href="https://github.com/google/starthinker/tree/master/starthinker/task/%s/run.py" target="_blank">%s</a>": {'
          % (task, task), data)
    return data

  def is_manual(self):
    return self.script.get('setup', {}).get('day', None) == []

  @staticmethod
  def get_json(uuid, project_id, credentials_user, credentials_service,
               timezone, days, hours, values):
    tasks = []
    hours = set(hours)
    for v in values:
      ts = Script(v['tag']).get_tasks()
      json_set_fields(ts, v['values'])
      tasks.extend(ts)

    data = {
        #"script":{
        #  "tag":self.get_tag(),
        #  "authors":self.get_authors()
        #},
        'setup': {
            'uuid': uuid,
            'id': project_id,
            'timezone': timezone,
            'day': days,
            'hour': sorted(hours),
            'auth': {
                'user': credentials_user,
                'service': credentials_service,
            }
        },
        'tasks': tasks,
    }

    return data


if __name__ == '__main__':
  """ Create a scripts_lookup.py file to load from instead of json scripts, used by appengine.

  The scripts_lookup.py file acts as a buffer storing all the configurations for
  all the scripts.
  It is necessary because some servers like Google App Engine cannot build the
  lookup using the file system.
  For development you can delete: scripts_lookup.py, the script templats will be
  loaded directly from files.

  """

  filename = '%s/starthinker_ui/recipe/scripts_lookup.py' % UI_ROOT
  print('WRITING:', filename)
  content = ('# DO NOT EDIT, GENERATED BY: python '
             'starthinker_ui/recipe/scripts.py\n\nSCRIPTS = %s') % pprint.pformat(
      SCRIPTS, indent=1)
  with open(filename, 'w') as file:
    file.write(content)
