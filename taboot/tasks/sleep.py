# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2011, Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from taboot.tasks import BaseTask, TaskResult


class SleepBase(BaseTask):
    """
    Base class for task-queue pausing classes.
    """

    def __init__(self, **kwargs):
        super(SleepBase, self).__init__(**kwargs)


class Seconds(SleepBase):
    """
    Halt task processing on a node for a certain number of seconds.

    :Parameters:
      - `seconds`: Number of seconds to halt execution for.
    """

    def __init__(self, seconds=60, **kwargs):
        super(Seconds, self).__init__(**kwargs)
        self._seconds = seconds

    def run(self, runner):
        import time
        time.sleep(self._seconds)
        return TaskResult(self, success=True,
                          output="Paused for %s seconds" %
                          self._seconds)


class Minutes(SleepBase):
    """
    Halt task processing on a node for a certain number of minutes.

    :Parameters:
      - `minutes`: Number of minutes to halt execution for.
    """

    def __init__(self, minutes=1, **kwargs):
        super(Minutes, self).__init__(**kwargs)
        self._seconds = minutes * 60

    def run(self, runner):
        import time
        time.sleep(self._seconds)
        return TaskResult(self, success=True,
                          output="Paused for %s minutes" %
                          minutes)
