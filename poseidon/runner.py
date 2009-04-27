# Copyright 2009, Red Hat, Inc
# John Eckersberg <jeckersb@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

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

    def __init__(self, hostglobs, tasks, concurrency=1, output=poseidon.output.CLIOutput(), expand_globs=True):
        """
        Initialize the Runner.

        :Parameters:
           - `hostglobs`: a List of Func-compatible host-globs to operate on.
           - `tasks`: a List of tasks to execute.
           - `concurrency`: the number of hosts on which to operate on simultaneously.
           - `output`: an object that implements BaseOutput.
           - `expand_globs`: whether to expand the globs or just leave them as is.
        """
        self._hostglobs = hostglobs
        self._tasks = tasks
        self._concurrency = concurrency
        self._output = output
        self._task_q = []
        if expand_globs:
            self._hosts = self._expand_globs()
        else:
            self._hosts = hostglobs
        self._semaphore = self.threading.Semaphore(self._concurrency)
        self._fail_event = self.threading.Event()

    def run(self, ignore_errors=False, dry_run=False):
        """
        Run the job.
        """
        for host in self._hosts:
            t = TaskRunner(host, self._tasks, self._semaphore, self._output, self._fail_event)
            t.start()
            self._task_q.append(t)

        for task in self._task_q:
            task.join()

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
    from poseidon.tasks import TaskResult
    def __init__(self, host, tasks, semaphore, output, fail_event):
        import copy
        threading.Thread.__init__(self)
        self._host = host
        # we need our own copy of the tasks
        self._tasks = [copy.deepcopy(task) for task in tasks]
        self._semaphore = semaphore
        self._output = output
        self._fail_event = fail_event

    def run(self):
        self._semaphore.acquire()

        if self._fail_event.isSet():
            # some other host has bombed
            self._semaphore.release()
            return

        try:
            host_success = True
            for task in self._tasks:
                result = self.run_task(task)
                self._output_result(result)
                if not result.success:
                    host_success = False
                    break
        except:
            self._bail_failure()
            raise

        if not host_success:
            self._bail_failure()
        else:
            self._semaphore.release()
            return host_success

    def _bail_failure():
        self._fail_event.set()
        self._semaphore.release()

    def run_task(self, task):
        task.host = self._host
        try:
            result = task.run(self)
        except Exception, e:
            result = self.TaskResult(task, output=repr(e))
        return result

    def _output_result(self, result):
        if isinstance(self._output, list):
            for output in self._output:
                output(result)
        else:
            self._output(result)
