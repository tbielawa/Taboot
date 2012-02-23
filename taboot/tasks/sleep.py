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

import types
from taboot.tasks import poller
import taboot.util
import sys
from taboot.log import *
from taboot.tasks import BaseTask, TaskResult
from termios import tcflush, TCIFLUSH


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
        self._minutes = minutes
        self._seconds = minutes * 60

    def run(self, runner):
        import time
        time.sleep(self._seconds)
        return TaskResult(self, success=True,
                          output="Paused for %s minutes" %
                          self._minutes)


class WaitOnInput(SleepBase):
    """
    Halt task processing on a node until the user presses enter.

    :Parameters:
      - `message`: The message to prompt on the CLI.
    """

    def __init__(self, message="Press enter to continue\n", **kwargs):
        super(WaitOnInput, self).__init__(**kwargs)
        self._message = message
        self.concurrentFriendly = False

    def run(self, runner):
        import time
        start = time.time()
        tcflush(sys.stdin, TCIFLUSH)
        raw_input(self._message)
        return TaskResult(self, success=True,
                          output="Paused for %s seconds" %
                          (time.time() - start))


class FindInFile(poller.PollTask):
    """
    Halt task processing until a specific string is found in a file or files.

    :Parameters:
      - `search_path`: A single path or a list of paths to search
      - `search_string`: String to match in `File`
      - `sleep_interval`: How many seconds to wait between each subsequent search. Default: 15
      - `max_attempts`: How many times the file will be checked before returning as an error. Default: 4
      - `ignore_case`: Set the case sensitivity of the search for `SearchString` in `File`. Default: True
      - `egrep`: Set to use Extended Regular Expressions. Default: False
    """

    def __init__(self, search_path, search_string,
                 sleep_interval=int(15), max_attempts=int(4),
                 ignore_case=True, egrep=False,
                 **kwargs):
        # This will become a datastructure representing a command.Run
        # task that calls out to grep on the target host.
        self._search_paths = []
        self._grep_options = []
        self._search_string = search_string
        task = {'command.Run': None}

        # Accept a single string, or a list of paths
        self._add_search_path(search_path)

        if ignore_case:
            self._add_grep_option('i')

        if egrep:
            self._add_grep_option('E')

        task_command = self._task_command()
        task['command.Run'] = task_command
        
        self._sleep_interval = sleep_interval
        self._max_attempts = max_attempts
        print kwargs
        #kwargs['sleep_interval'] = sleep_interval
        #kwargs['max_attempts
        log_debug("About to call the super to FindInFile")
        super(FindInFile, self).__init__(task,
                                         sleep_interval=sleep_interval,
                                         max_attempts=max_attempts,
                                         **kwargs)
        
    def _add_grep_option(self, option):
        """Adds another item to the grep options"""
        self._grep_options.append(option)
        log_debug("Added %s to the grep options", option)

    def _grep_options_group(self):
        """Build the string to use for the options to grep"""
        return "".join(['-'] + self._grep_options)

    def _add_search_path(self, path):
        if path.__class__ == types.ListType:
            self._search_paths.extend(path)
        elif path.__class__ == types.StringType:
            self._search_paths.append(path)
        else:
            log_debug("Can't add %s to the search paths.", path)
            log_debug("(cont) Not a string or list of strings")
            raise Exception("Can't add to search paths")

        log_debug("Added %s to search paths", path)

    def _task_command(self):
        """Build the task for poller.PollTask"""
        opts = self._grep_options_group()
        paths = self._search_paths
        sstr = self._search_string
        return " ".join(taboot.util.flatten(["grep", opts, sstr, paths]))
