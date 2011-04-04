# Copyright 2011, Red Hat, Inc
#
# This software may be freely redistributed under the terms of the GNU
# general public license version 3.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

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
                          self._seconds)
