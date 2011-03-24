# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from poseidon.tasks import BaseTask, TaskResult


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
