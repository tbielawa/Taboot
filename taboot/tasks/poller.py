# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2009, Red Hat, Inc.
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

from taboot.tasks import BaseTask
from taboot.tasks import TaskResult
import time


class PollTask(BaseTask):
    """
    PollTask.  A task that will poll a particular task until the task
    succeeds or until max_attempts is reached.

    :Parameters:
        - `task` The task to poll.
        - `sleep_interval` The number of seconds to wait before trying
                           the task again.
        - `max_attempts` The maximum number of attempts that the task
                         should be run.
        - `fail_task` The task to run when max_attempts has been exhausted.
                      If no fail_task is provided, then a simple TaskResult
                      indicating failure is returned.
    """

    def __init__(self, task, sleep_interval=5, max_attempts=6,
                 fail_task=None, **kwargs):
        super(PollTask, self).__init__(**kwargs)
        from log import *
        import pdb; pdb.set_trace()
        log_debug("Poller setting self._task with %s", str(task))
        self._task = task
        self._sleep_interval = sleep_interval
        self._max_attempts = max_attempts
        self._fail_task = fail_task

    def run(self, runner):
        for x in range(self._max_attempts):
            result = runner.run_task(self._task)
            if result.success:
                return result
            time.sleep(self._sleep_interval)

        # exhausted max_attempts
        if self._fail_task != None:
            return runner.run_task(self._fail_task)
        else:
            # return a "failed" TaskResult, stop executing further tasks
            return TaskResult(self, success=False,
                    output="Max attempts of %s reached running %s" %
                              (self._max_attempts, repr(self._task)))
