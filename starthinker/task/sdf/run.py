###########################################################################
#
#  Copyright 2019 Google Inc.
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

from starthinker.util.project import project
from starthinker.util.sdf import sdf_download, sdf_to_bigquery
from starthinker.util.bigquery import query_to_table
import zipfile
import re


@project.from_parameters
def sdf():
  if project.verbose: print('SDF')

  # Download sdf files
  sdf_zip_file = sdf_download(
    project.task['auth'], 
    project.task['version'], 
    project.task['partner_id'], 
    project.task['file_types'], 
    project.task['filter_type'], 
    project.task['read']['filter_ids'])

  # Load data into BigQuery
  sdf_to_bigquery(sdf_zip_file, project.id, project.task['dataset'], project.task['time_partitioned_table'], project.task['create_single_day_table'], project.task.get('table_suffix', ''))
  
  if project.task['sdf_legacy'] and project.task['daily']:
    with zipfile.ZipFile(sdf_zip_file, 'r', zipfile.ZIP_DEFLATED) as d: 
        file_names = d.namelist()
        file_names = [name for name in file_names if not 'Skipped' in name]
        for file_name in file_names:
            table_name = file_name.split('.')[0].replace('-','_')
            query_to_table(project.task["bigquery_auth"], 
              project.id, 
              project.task['dataset'], 
              table_name,
              "SELECT PARSE_DATE('%%Y_%%m_%%d',_TABLE_SUFFIX) as SDF_Day, * FROM `%s.%s.%s_*`" % (project.id, project.task['dataset'], table_name), 
              disposition='WRITE_TRUNCATE',
              legacy=False)

if __name__ == "__main__":
  sdf()
