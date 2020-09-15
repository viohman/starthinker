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

'''
--------------------------------------------------------------

Before running this Airflow module...

  Install StarThinker in cloud composer from open source: 

    pip install git+https://github.com/google/starthinker

  Or push local code to the cloud composer plugins directory:

    source install/deploy.sh
    4) Composer Menu	   
    l) Install All

--------------------------------------------------------------

CM Report Replicate

Replicate a report across multiple networks and advertisers.

Provide the name or ID of an existing report.
Run the recipe once to generate the input sheet called CM Replicate For UNDEFINED.
Enter network and advertiser ids to replicate the report.
Data will be written to BigQuery &gt; UNDEFINED &gt; UNDEFINED &gt; [REPORT NAME]_All

'''

from starthinker_airflow.factory import DAG_Factory
 
# Add the following credentials to your Airflow configuration.
USER_CONN_ID = "starthinker_user" # The connection to use for user authentication.
GCP_CONN_ID = "starthinker_service" # The connection to use for service authentication.

INPUTS = {
  'auth_read': 'user',  # Credentials used for reading data.
  'recipe_name': '',  # Sheet to read ids from.
  'auth_write': 'service',  # Credentials used for writing data.
  'account': '',  # CM network id.
  'recipe_slug': '',
  'report_id': '',  # CM template report id, for template
  'report_name': '',  # CM template report name, empty if using id instead.
  'delete': False,  # Use only to reset the reports if setup changes.
  'Aggregate': False,  # Append report data to existing table, requires Date column.
}

TASKS = [
  {
    'drive': {
      'auth': 'user',
      'copy': {
        'source': 'https://docs.google.com/spreadsheets/d/1Su3t2YUWV_GG9RD63Wa3GNANmQZswTHstFY6aDPm6qE/',
        'destination': {
          'field': {
            'name': 'recipe_name',
            'prefix': 'CM Replicate For ',
            'kind': 'string',
            'order': 1,
            'description': 'Name of document to deploy to.',
            'default': ''
          }
        }
      }
    }
  },
  {
    'dataset': {
      'auth': {
        'field': {
          'name': 'auth_write',
          'kind': 'authentication',
          'order': 1,
          'default': 'service',
          'description': 'Credentials used for writing data.'
        }
      },
      'dataset': {
        'field': {
          'name': 'recipe_slug',
          'kind': 'string',
          'order': 2,
          'default': '',
          'description': 'Name of Google BigQuery dataset to create.'
        }
      }
    }
  },
  {
    'dcm_replicate': {
      'auth': {
        'field': {
          'name': 'auth_read',
          'kind': 'authentication',
          'order': 0,
          'default': 'user',
          'description': 'Credentials used for reading data.'
        }
      },
      'report': {
        'account': {
          'field': {
            'name': 'account',
            'kind': 'integer',
            'order': 3,
            'default': '',
            'description': 'CM network id.'
          }
        },
        'id': {
          'field': {
            'name': 'report_id',
            'kind': 'integer',
            'order': 4,
            'default': '',
            'description': 'CM template report id, for template'
          }
        },
        'name': {
          'field': {
            'name': 'report_name',
            'kind': 'string',
            'order': 5,
            'default': '',
            'description': 'CM template report name, empty if using id instead.'
          }
        },
        'delete': {
          'field': {
            'name': 'delete',
            'kind': 'boolean',
            'order': 6,
            'default': False,
            'description': 'Use only to reset the reports if setup changes.'
          }
        }
      },
      'in': {
        'sheet': {
          'field': {
            'name': 'recipe_name',
            'prefix': 'CM Replicate For ',
            'kind': 'string',
            'order': 1,
            'default': '',
            'description': 'Sheet to read ids from.'
          }
        },
        'tab': 'Accounts'
      },
      'out': {
        'bigquery': {
          'dataset': {
            'field': {
              'name': 'recipe_slug',
              'kind': 'string',
              'order': 4,
              'default': ''
            }
          },
          'is_incremental_load': {
            'field': {
              'name': 'Aggregate',
              'kind': 'boolean',
              'order': 7,
              'default': False,
              'description': 'Append report data to existing table, requires Date column.'
            }
          }
        }
      }
    }
  }
]

DAG_FACTORY = DAG_Factory('dcm_replicate_to_bigquery', { 'tasks':TASKS }, INPUTS)
DAG_FACTORY.apply_credentails(USER_CONN_ID, GCP_CONN_ID)
DAG = DAG_FACTORY.execute()

if __name__ == "__main__":
  DAG_FACTORY.print_commandline()
