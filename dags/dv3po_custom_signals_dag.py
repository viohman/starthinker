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
"""--------------------------------------------------------------

Before running this Airflow module...

  Install StarThinker in cloud composer from open source:

    pip install git+https://github.com/google/starthinker

  Or push local code to the cloud composer plugins directory:

    source install/deploy.sh
    4) Composer Menu
    l) Install All

--------------------------------------------------------------

[DV-3PO] Custom Signals

[DV-3PO] Custom Signals allows automated changes to be made to DV360 campaigns
based on external signals from weather and social media trends. In the future it
will also support news, disaster alerts, stocks, sports, custom APIs, etc.

Open the template sheet: <a target='_blank'
href='https://docs.google.com/spreadsheets/d/1xl2bknsn9ptCKwg1sZqTBpmRFDdcG3ATdp2f4C2CQ2U/edit#gid=1579485492'>[DV-3PO]
Custom Signals Configs</a>.
Make a copy of the sheet through the menu File -> Make a copy, for clarity we
suggest you rename the copy to a meaningful name describing the usage of this
copy.
In the Station IDs field below enter a comma separated list of NOAA weather
station IDs. Most major airports are stations and their ID typically is K
followed by the 3 letter airport code, e.g. KORD for Chicago O'Hare
International Airport, KSFO for San Francisco international airport, etc. You
can get a full list of stations <a target='_blank'
href='https://www1.ncdc.noaa.gov/pub/data/noaa/isd-history.txt'>here</a>, the
station ID to use is the 'CALL' column of this list.
In the Sheet URL field below, enter the URL of the copy of the config sheet
you've created.
Go to the sheet and configure the rules you'd like to be applied in the Rules
tab.
In the Advertiser ID column, enter the advertiser ID of the line items you'd
like to automatically update.
In the Line Item ID colunn, enter the line item ID of the line item you'd like
to automatically update.
The 'Active' column of the Rules tab allows you to control if the line item
should be active or paused. If this field is TRUE the line item will be set to
active, if this field is FALSE the line item will be set to inactive. You can
use a formula to take weather data into consideration to update this field, e.g.
=IF(Weather!C2>30, TRUE, FALSE) will cause the line item to be activated if the
temperature of the first station in the Weather tab is above 30 degrees. Leave
this field empty if you don't want it to be modified by the tool.
The 'Fixed Bid' column of the Rules tab allows you to control the fixed bid
amount of the line item. The value set to this field will be applied to the
specified line item. You can use a formula to take weather data into
consideration to update this field, e.g. =IF(Weather!G2>3, 0.7, 0.4) will cause
bid to be set to $0.7 if the wind speed of the first line in the Weather tab is
greater than 3 mph, or $0.4 otherwise. Leave this field empty if you don't want
it to be modified by the tool.

"""

from starthinker_airflow.factory import DAG_Factory

# Add the following credentials to your Airflow configuration.
USER_CONN_ID = 'starthinker_user'  # The connection to use for user authentication.
GCP_CONN_ID = 'starthinker_service'  # The connection to use for service authentication.

INPUTS = {
    'auth_read': 'user',  # Credentials used for reading data.
    'station_ids': '',  # NOAA Weather Station ID
    'sheet_url': '',  # Feed Sheet URL
}

TASKS = [{
    'weather_gov': {
        'auth': 'user',
        'stations': {
            'field': {
                'description': 'NOAA Weather Station ID',
                'name': 'station_ids',
                'default': '',
                'kind': 'string_list',
                'order': 1
            }
        },
        'out': {
            'sheets': {
                'tab': 'Weather',
                'delete': True,
                'sheet': {
                    'field': {
                        'description': 'Feed Sheet URL',
                        'name': 'sheet_url',
                        'default': '',
                        'kind': 'string',
                        'order': 2
                    }
                },
                'range': 'A2:K'
            }
        }
    }
}, {
    'lineitem_beta': {
        'auth': {
            'field': {
                'description': 'Credentials used for reading data.',
                'name': 'auth_read',
                'default': 'user',
                'kind': 'authentication',
                'order': 1
            }
        },
        'patch': {},
        'read': {
            'sheet': {
                'tab': 'Rules',
                'sheet': {
                    'field': {
                        'description': 'Feed Sheet URL',
                        'name': 'sheet_url',
                        'default': '',
                        'kind': 'string',
                        'order': 2
                    }
                },
                'range': 'A1:D'
            }
        }
    }
}]

DAG_FACTORY = DAG_Factory('dv3po_custom_signals', {'tasks': TASKS}, INPUTS)
DAG_FACTORY.apply_credentails(USER_CONN_ID, GCP_CONN_ID)
DAG = DAG_FACTORY.execute()

if __name__ == '__main__':
  DAG_FACTORY.print_commandline()
