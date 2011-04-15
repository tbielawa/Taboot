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

from taboot.tasks import BaseTask, TaskResult


class WaitCLI(BaseTask):
    """
    Display a prompt message to the CLI and wait for user to press
    enter before returning from task.
    """

    def __init__(self, message="Press enter to continue\n", **kwargs):
        """
        :Parameters:
          - `message`: The message to prompt on the CLI
        """
        super(WaitCLI, self).__init__()
        self._message = message

    def run(self, runner):
        raw_input(self._message)
        return TaskResult(self, success=True)
