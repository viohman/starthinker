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
"""Processes standard read / write JSON block for dynamic loading of data.

The goal is to create standard re-usable input output blocks.  These functions
are extensible, and should include additional sources and destinations over
time.
Key benfits include:

  - Allows single point API revision for common read / write tasks.
  - Reduce risk with test case coverage for this module inherited by recipes
  using it.
  - Using standard blocks is a big time savings.

"""

import pysftp
import traceback

from starthinker.util.project import project
from starthinker.util.storage import parse_path, makedirs_safe, object_put, bucket_create
from starthinker.util.bigquery import query_to_rows, table_to_rows, rows_to_table, json_to_table, incremental_rows_to_table, query_parameters
from starthinker.util.sheets import sheets_read, sheets_write, sheets_clear
from starthinker.util.csv import rows_to_csv


def get_rows(auth, source):
  """Processes standard read JSON block for dynamic loading of data.

  Allows us to quickly pull a column or columns of data from and use it as an
  input
  into a script. For example pull a list of ids from bigquery and act on each
  one.

  - When pulling a single column specify single_cell = True. Returns list AKA
  values.
  - When pulling a multiple columns specify single_cell = False. Returns list of
  lists AKA rows.
  - Values are always given as a list ( single_cell will trigger necessary
  wrapping ).
  - Values, bigquery, sheet are optional, if multiple given result is one
  continous iterator.
  - Extensible, add a handler to define a new source ( be kind update the
  documentation json ).

  Include the following JSON in a recipe, then in the run.py handler when
  encountering that block pass it to this function and use the returned results.

    from utils.data import get_rows

    var_json = {
      "in":{
        "single_cell":[ boolean ],
        "values": [ integer list ],
        "bigquery":{
          "dataset": [ string ],
          "query": [ string ],
          "legacy":[ boolean ]
        },
        "bigquery":{
          "dataset": [ string ],
          "table": [ string ],
        },
        "sheet":{
          "sheet":[ string - full URL, suggest using share link ],
          "tab":[ string ],
          "range":[ string - A1:A notation ]
        }
      }
    }

    values = get_rows('user', var_json)

  Or you can use it directly with project singleton.

    from util.project import project
    from utils.data import get_rows

    @project.from_parameters
    def something():
      values = get_rows(project.task['auth'], project.task['in'])

    if __name__ == "__main__":
      something()

  Args:
    auth: (string) The type of authentication to use, user or service.
    source: (json) A json block resembling var_json described above.

  Returns:
    If single_cell is False: Returns a list of row values [[v1], [v2], ... ]
    If single_cell is True: Returns a list of values [v1, v2, ...]
"""

  # if handler points to list, concatenate all the values from various sources into one list
  if isinstance(source, list):
    for s in source:
      for r in get_rows(auth, s):
        yield r

  # if handler is an endpoint, fetch data
  else:
    if 'values' in source:
      if isinstance(source['values'], list):
        for value in source['values']:
          yield value
      else:
        yield source['values']

    if 'sheet' in source:
      rows = sheets_read(
          project.task['auth'],
          source['sheet']['sheet'],
          source['sheet']['tab'],
          source['sheet']['range'],
      )

      for row in rows:
        yield row[0] if source.get('single_cell', False) else row

    if 'bigquery' in source:

      rows = []

      if 'table' in source['bigquery']:
        rows = table_to_rows(
            source['bigquery'].get('auth', auth),
            project.id,
            source['bigquery']['dataset'],
            source['bigquery']['table'],
            as_object=source['bigquery'].get('as_object', False))

      else:
        rows = query_to_rows(
            source['bigquery'].get('auth', auth),
            project.id,
            source['bigquery']['dataset'],
            query_parameters(source['bigquery']['query'],
                             source['bigquery'].get('parameters', {})),
            legacy=source['bigquery'].get('legacy', False),
            as_object=source['bigquery'].get('as_object', False))

      for row in rows:
        yield row[0] if source.get('single_cell', False) else row


def put_rows(auth, destination, rows, variant=''):
  """Processes standard write JSON block for dynamic export of data.

  Allows us to quickly write the results of a script to a destination.  For
  example
  write the results of a DCM report into BigQuery.

  - Will write to multiple destinations if specified.
  - Extensible, add a handler to define a new destination ( be kind update the
  documentation json ).

  Include the following JSON in a recipe, then in the run.py handler when
  encountering that block pass it to this function and use the returned results.

    from utils.data import put_rows

    var_json = {
      "out":{
        "bigquery":{
          "dataset": [ string ],
          "table": [ string ]
          "schema": [ json - standard bigquery schema json ],
          "skip_rows": [ integer - for removing header ]
          "disposition": [ string - same as BigQuery documentation ]
        },
        "sheets":{
          "sheet":[ string - full URL, suggest using share link ],
          "tab":[ string ],
          "range":[ string - A1:A notation ]
          "delete": [ boolean - if sheet range should be cleared before writing
          ]
        },
        "storage":{
          "bucket": [ string ],
          "path": [ string ]
        },
        "file":[ string - full path to place to write file ]
      }
    }

    values = put_rows('user', var_json)

  Or you can use it directly with project singleton.

    from util.project import project
    from utils.data import put_rows

    @project.from_parameters
    def something():
      values = get_rows(project.task['auth'], project.task['out'])

    if __name__ == "__main__":
      something()

  Args:
    auth: (string) The type of authentication to use, user or service.
    destination: (json) A json block resembling var_json described above. rows (
      list ) The data being written as a list object. variant (string) Appended
      to destination to differentieate multiple objects

  Returns:
    If single_cell is False: Returns a list of row values [[v1], [v2], ... ]
    If single_cell is True: Returns a list of values [v1, v2, ...]
"""

  if 'bigquery' in destination:

    if destination['bigquery'].get('format', 'CSV') == 'JSON':
      json_to_table(
          destination['bigquery'].get('auth', auth),
          destination['bigquery'].get('project_id', project.id),
          destination['bigquery']['dataset'],
          destination['bigquery']['table'] + variant,
          rows,
          destination['bigquery'].get('schema', []),
          destination['bigquery'].get('disposition', 'WRITE_TRUNCATE'),
      )

    elif destination['bigquery'].get('is_incremental_load', False) == True:
      incremental_rows_to_table(
          destination['bigquery'].get('auth', auth),
          destination['bigquery'].get('project_id', project.id),
          destination['bigquery']['dataset'],
          destination['bigquery']['table'] + variant,
          rows,
          destination['bigquery'].get('schema', []),
          destination['bigquery'].get(
              'skip_rows',
              1),  #0 if 'schema' in destination['bigquery'] else 1),
          destination['bigquery'].get('disposition', 'WRITE_APPEND'),
          billing_project_id=project.id)

    else:
      rows_to_table(
          destination['bigquery'].get('auth', auth),
          destination['bigquery'].get('project_id', project.id),
          destination['bigquery']['dataset'],
          destination['bigquery']['table'] + variant,
          rows,
          destination['bigquery'].get('schema', []),
          destination['bigquery'].get(
              'skip_rows',
              1),  #0 if 'schema' in destination['bigquery'] else 1),
          destination['bigquery'].get('disposition', 'WRITE_TRUNCATE'),
      )

  if 'sheets' in destination:
    if destination['sheets'].get('delete', False):
      sheets_clear(
          auth,
          destination['sheets']['sheet'],
          destination['sheets']['tab'] + variant,
          destination['sheets']['range'],
      )

    sheets_write(auth, destination['sheets']['sheet'],
                 destination['sheets']['tab'] + variant,
                 destination['sheets']['range'], rows)

  if 'file' in destination:
    path_out, file_ext = destination['file'].rsplit('.', 1)
    file_out = path_out + variant + '.' + file_ext
    if project.verbose:
      print('SAVING', file_out)
    makedirs_safe(parse_path(file_out))
    with open(file_out, 'w') as save_file:
      save_file.write(rows_to_csv(rows).read())

  if 'storage' in destination and destination['storage'].get(
      'bucket') and destination['storage'].get('path'):
    # create the bucket
    bucket_create(auth, project.id, destination['storage']['bucket'])

    # put the file
    file_out = destination['storage']['bucket'] + ':' + destination['storage'][
        'path'] + variant
    if project.verbose:
      print('SAVING', file_out)
    object_put(auth, file_out, rows_to_csv(rows))

  if 'sftp' in destination:
    try:
      cnopts = pysftp.CnOpts()
      cnopts.hostkeys = None

      path_out, file_out = destination['sftp']['file'].rsplit('.', 1)
      file_out = path_out + variant + file_out

      sftp = pysftp.Connection(
          host=destination['sftp']['host'],
          username=destination['sftp']['username'],
          password=destination['sftp']['password'],
          port=destination['sftp']['port'],
          cnopts=cnopts)

      if '/' in file_out:
        dir_out, file_out = file_out.rsplit('/', 1)
        sftp.cwd(dir_out)

      sftp.putfo(rows_to_csv(rows), file_out)

    except e:
      print(str(e))
      traceback.print_exc()
