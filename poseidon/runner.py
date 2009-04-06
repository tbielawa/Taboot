# Copyright 2009, Red Hat, Inc
# John Eckersberg <jeckersb@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
runner for poseidon that does all the heavy lifting.
"""
import threading
import poseidon.output

class CheckFailed(Exception):
    pass

class Runner(object):
    """
    The Runner, responsible for running a poseidon job.
    """

    import func.overlord.client as fc
    import threading

    def __init__(self, hostglobs, tasks, concurrency=1, output=poseidon.output.CLIOutput()):
        """
        Initialize the Runner.

        :Parameters:
           - `hostglobs`: a List of Func-compatible host-globs to operate on.
           - `tasks`: a List of tasks to execute.
           - `concurrency`: the number of hosts on which to operate on simultaneously.
           - `output`: an object that implements BaseOutput.
        """
        self._hostglobs = hostglobs
        self._tasks = tasks
        self._concurrency = concurrency
        self._output = output
        self._task_q = []
        self._hosts = self._expand_globs()
        self._event = self.threading.Event()

    def run(self, check=True, ignore_errors=False, dry_run=False):
        """
        Run the job.

        :Parameters:
           - `check`: whether to run self.check before.
           - `ignore_errors`: whether to ignore faults in tasks.
           - `dry_run`: if True, don't actually execute tasks, just print info
        """
        from poseidon.tasks import FuncTask
        if check:
            self.check()

        for host in self._hosts:
            if len(self._task_q) == self._concurrency:
                self._event.wait()
                self._event.clear()
                self._task_cleanup()
            t = TaskRunner(host, self._tasks, self._event, self._output)
            t.start()
            self._task_q.append(t)

    def _task_cleanup(self):
        new_task_q = []
        for task in self._task_q:
            if task.isAlive():
                new_task_q.append(task)
        self._task_q = new_task_q

    def check(self):
        """
        Run a sanity check on the job.

        For now just go with it.
        """
        return True

    def _expand_globs(self):
        """
        Returns the hosts that expand out from globs.
        """
        if not self._hostglobs:
            return []
        if isinstance(self._hostglobs, basestring):
            glob = self._hostglobs
        else:
            glob = ';'.join(self._hostglobs)
        c = self.fc.Client(glob)
        return c.list_minions()

class TaskRunner(threading.Thread):
    def __init__(self, host, tasks, event, output):
        import copy
        threading.Thread.__init__(self)
        self._host = host
        # we need our own copy of the tasks
        self._tasks = [copy.deepcopy(task) for task in tasks]
        self._event = event
        self._output = output

    def run(self):
        from poseidon.tasks import TaskResult
        for task in self._tasks:
            task.host = self._host
            try:
                result = task.run()
            except Exception, e:
                result = TaskResult(task, output=repr(e))

            self._output(result)
            if not result.success:
                break
        self._event.set()
