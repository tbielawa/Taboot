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


"""
Enable and disable nodes in an F5 BigIP LB
"""


class BigIPBaseTask(BaseTask):
    """
    This also does nothing. But it helps to collect common tasks
    together under a base task when generating inheritance graphs.
    """

    def show_host(self):
        cmd = ['bigip', 'show', self._host]
        (status, output) = commands.getstatusoutput(" ".join(cmd))
        return output


class OutOfRotation(BigIPBaseTask):
    """
    Disable a node in the F5
    """
    def run(self, *args):
        cmd = ['bigip', 'state', '-d', self._host]
        (status, output) = commands.getstatusoutput(" ".join(cmd))

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
        cmd = ['bigip', 'state', '-e', self._host]
        (status, output) = commands.getstatusoutput(" ".join(cmd))

        success = True
        if not status == 0:
            # Output is the error message if success did not happen
            success = False
        else:
            # Output is 'bigip show...' if successful
            output = self.show_host()

        return TaskResult(self, success=success, output=output)
