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

from urllib import request
from urllib.error import HTTPError

from starthinker.util.data import get_rows
from starthinker.util.data import put_rows
from starthinker.util.project import project


URL_SCHEMA = [
  { 'name': 'URL', 'type': 'STRING', 'mode': 'REQUIRED' },
  { 'name': 'Status', 'type': 'INTEGER', 'mode': 'NULLABLE' },
  { 'name': 'Read', 'type': 'BYTES', 'mode': 'NULLABLE' }
]

def url_fetch():

  for url in get_rows(project.task['auth'], project.task['urls'], unnest=True):

    if project.verbose:
      print('URL', url)

    record = {
      'url':url
    }

    url_request = request.Request(url, data=project.task.get('data'))
    try:
      url_response = request.urlopen(url_request)

      if project.task.get('status', False):
        record['status'] = url_response.status

      if project.task.get('read', False):
        record['read'] = url_response.read()

    except HTTPError as error:

      if project.task.get('status', False):
        record['status'] = error.status

    yield record


@project.from_parameters
def url():

  # Eventually add format detection or parameters to put_rows
  if 'bigquery' in project.task['to']:
    project.task['to']['bigquery']['format'] = 'JSON'

  put_rows(
    project.task['auth'],
    project.task['to'],
    url_fetch(),
    URL_SCHEMA
  )

if __name__ == '__main__':
  url()
