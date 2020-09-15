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

# SEE: https://github.com/geduldig/TwitterAPI
# SEE: https://developer.twitter.com/en/docs/basics/rate-limits

from time import sleep
from TwitterAPI import TwitterAPI

from starthinker.util.project import project
from starthinker.util.data import get_rows, put_rows

# FOR WOEID SEE
# http://cagricelebi.com/blog/dear-twitter-please-stop-using-woeid/
# https://archive.org/details/geoplanet_data_7.10.0.zip
# https://github.com/Ray-SunR/woeid
# https://stackoverflow.com/questions/12434591/get-woeid-from-city-name

TWITTER_API = None


def get_twitter_api():
  global TWITTER_API
  if TWITTER_API is None:
    TWITTER_API = TwitterAPI(
        project.task['key'], project.task['secret'], auth_type='oAuth2')
  return TWITTER_API


TWITTER_TRENDS_PLACE_SCHEMA = [
    {
        'name': 'Woeid',
        'type': 'INTEGER'
    },
    {
        'name': 'Name',
        'type': 'STRING'
    },
    {
        'name': 'Url',
        'type': 'STRING'
    },
    {
        'name': 'Promoted_Content',
        'type': 'STRING',
        'mode': 'NULLABLE'
    },
    {
        'name': 'Query',
        'type': 'STRING',
    },
    {
        'name': 'Tweet_Volume',
        'type': 'INTEGER'
    },
]


def twitter_trends_places():
  if project.verbose:
    print('TWITTER TRENDS PLACE')
  print('PL',
        list(get_rows(project.task['auth'], project.task['trends']['places'])))

  for place in get_rows(project.task['auth'], project.task['trends']['places']):
    if project.verbose:
      print('PLACE', place)
    results = get_twitter_api().request('trends/place', {'id': int(place)})
    for r in results:
      if project.verbose:
        print('RESULT', r['name'])
      yield [
          place, r['name'], r['url'], r['promoted_content'], r['query'],
          r['tweet_volume']
      ]
    print('.', end='')
    sleep(15 * 60 / 75)  # rate limit ( improve to retry )


TWITTER_TRENDS_CLOSEST_SCHEMA = [
    {
        'name': 'Latitude',
        'type': 'FLOAT'
    },
    {
        'name': 'Longitude',
        'type': 'FLOAT'
    },
    {
        'name': 'Country',
        'type': 'STRING'
    },
    {
        'name': 'Country_Code',
        'type': 'STRING'
    },
    {
        'name': 'Name',
        'type': 'STRING',
        'mode': 'NULLABLE'
    },
    {
        'name': 'Parent_Id',
        'type': 'INTEGER',
    },
    {
        'name': 'Place_Type_Code',
        'type': 'INTEGER'
    },
    {
        'name': 'Place_Type_Name',
        'type': 'STRING'
    },
    {
        'name': 'URL',
        'type': 'STRING'
    },
    {
        'name': 'Woeid',
        'type': 'INTEGER'
    },
]


def twitter_trends_closest():
  if project.verbose:
    print('TWITTER TRENDS CLOSEST')
  for row in get_rows(project.task['auth'], project.task['trends']['closest']):
    lat, lon = row[0], row[1]
    results = api.request('trends/closest', {'lat': lat, 'long': lon})
    for r in results:
      yield [
          lat, lon, r['country'], r['countryCode'], r['name'], r['parentid'],
          r['placeType']['code'], r['placeType']['name'], r['url'], r['woeid']
      ]


TWITTER_TRENDS_AVAILABLE_SCHEMA = TWITTER_TRENDS_CLOSEST_SCHEMA


def twitter_trends_available():
  if project.verbose:
    print('TWITTER TRENDS AVAILABLE')
  results = api.request('trends/available', {})
  for r in results:
    yield [
        r['country'], r['countryCode'], r['name'], r['parentid'],
        r['placeType']['code'], r['placeType']['name'], r['url'], r['woeid']
    ]


@project.from_parameters
def twitter():
  if project.verbose:
    print('TWITTER')

  rows = None

  if 'trends' in project.task:
    if 'places' in project.task['trends']:
      rows = twitter_trends_places()
      project.task['out']['bigquery']['schema'] = TWITTER_TRENDS_PLACE_SCHEMA
      project.task['out']['bigquery']['skip_rows'] = 0
    elif 'closest' in project.task['trends']:
      rows = twitter_trends_closest()
      project.task['out']['bigquery']['schema'] = TWITTER_TRENDS_CLOSEST_SCHEMA
      project.task['out']['bigquery']['skip_rows'] = 0
    else:
      rows = twitter_trends_available()
      project.task['out']['bigquery'][
          'schema'] = TWITTER_TRENDS_AVAILABLE_SCHEMA
      project.task['out']['bigquery']['skip_rows'] = 0

  if rows:
    put_rows(project.task['auth'], project.task['out'], rows)


if __name__ == '__main__':
  twitter()
