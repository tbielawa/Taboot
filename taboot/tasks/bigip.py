# -*- coding: utf-8 -*-
# Taboot - Client utility for performing deployments with Func.
# Copyright © 2012, Red Hat, Inc.
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
import commands
from taboot import log
from taboot.log import *
import threading

"""
Enable and disable nodes in an F5 BigIP LB
"""

# The bigip script is subject to a race condition which has an effect
# of changing the 'active' partition unexpectedly. Therefore we limit
# access to it to a single thread at a time.
BIGIP_MUTEX = threading.Lock()


class BigIPBaseTask(BaseTask):
    """
    Common functions shared between the subclasses.
    """

    def run_bigip_cmd(self, cmd):
        """
        `cmd` - should be a list of arguments to the bigip command

        ex: ['show', self._host] OR ['state', '-d', self._host]
        """
        BIGIP_MUTEX.acquire()
        (status, output) = commands.getstatusoutput(" ".join(cmd))
        BIGIP_MUTEX.release()
        return (status, output)

    def show_host(self):
        cmd = ['show', self._host]
        (status, output) = self.run_bigip_cmd(cmd)
        return output


class OutOfRotation(BigIPBaseTask):
    """
    Disable a node in the F5
    """
    def run(self, *args):
        cmd = ['state', '-d', self._host]
        (status, output) = self.run_bigip_cmd(cmd)

        success = True
        if not status == 0:
            # Output is the error message if success did not happen
            success = False
        else:
            # Output is 'bigip show...' if successful
            output = self.show_host()

        return TaskResult(self, success=success, output=output)


class InRotation(BigIPBaseTask):
    """
    Enable a node in the F5
    """
    def run(self, *args):
        cmd = ['state', '-e', self._host]
        (status, output) = self.run_bigip_cmd(cmd)

        success = True
        if not status == 0:
            # Output is the error message if success did not happen
            success = False
        else:
            # Output is 'bigip show...' if successful
            output = self.show_host()

        return TaskResult(self, success=success, output=output)


class ConfigSync(BigIPBaseTask):
    """
    Perform a config sync on specified environments.
    """

    def __init__(self, envs=[], **kwargs):
        self.envs = envs
        super(ConfigSync, self).__init__(**kwargs)

    def run(self, *args):
        cmd = ['sync', '-e', ' '.join(self.envs)]
        (status, output) = self.run_bigip_cmd(cmd)

        success = True
        if not status == 0:
            # Output is the error message if success did not happen
            success = False
        else:
            output = "Successfully synced %s environments!" % \
                (' && '.join(self.envs))

        return TaskResult(self, success=success, output=output)
