# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from taboot.tasks import FuncTask, TaskResult


class Run(FuncTask):
    """
    Run arbitrary commands via Func.  The arguments passed to __init__
    are used to execute func.overlord.Client.command.run(args).

    :Parameters:
     - `command`: Command to run on the remote host
    """

    def __init__(self, command, **kwargs):
        super(Run, self).__init__(command, **kwargs)
        self._command = 'command.run'

    def _process_result(self, result):
        t = TaskResult(self)
        if result[0] == 0:
            t.success = True
        else:
            t.success = False
        t.output = result[1]
        return t
