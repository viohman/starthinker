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

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from starthinker_ui.recipe.scripts import Script
from website.views import solutions, solution, help


class Command(BaseCommand):
  help = 'Generate HTML For GitHub'

  def add_arguments(self, parser):
    parser.add_argument(
        '--analytics',
        action='store',
        dest='analytics',
        required=True,
        type=str,
        help='Google analytics tag.',
    )

  def handle(self, *args, **kwargs):

    settings.GOOGLE_ANALYTICS = kwargs['analytics']

    directory = '%s/docs' % settings.UI_ROOT
    print('Writing:', directory)
    with open('%s/index.html' % directory, 'w') as index_file:
      index_file.write(solutions(request=None))

    directory = '%s/docs/help' % settings.UI_ROOT
    print('Writing:', directory)
    with open('%s/index.html' % directory, 'w') as index_file:
      index_file.write(help(request=None))

    directory = '%s/docs/solution' % settings.UI_ROOT
    print('Writing:', directory)
    with open('%s/index.html' % directory, 'w') as index_file:
      index_file.write(solutions(request=None))

    for s in Script.get_scripts():
      if s.get_open_source():
        directory = '%s/docs/solution/%s' % (settings.UI_ROOT, s.get_tag())
        print('Writing:', directory)
        if not os.path.exists(directory):
          os.makedirs(directory)
        with open('%s/index.html' % directory, 'w') as solution_file:
          solution_file.write(solution(request=None, tag=s.get_tag()))
