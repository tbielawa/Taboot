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

class CheckFailed(Exception):
    pass

class Runner(object):
    """
    The Runner, responsible for running a poseidon job.
    """

    import func.overlord.client as fc
    import threading

    def __init__(self, hostglobs, tasks, concurrency=1):
        """
        Initialize the Runner.

        :Parameters:
           - `hostglobs`: a List of Func-compatible host-globs to operate on.
           - `tasks`: a List of tasks to execute.
           - `concurrency`: the number of hosts on which to operate on simultaneously.
        """
        self.hostglobs = hostglobs
        self.tasks = tasks
        self.concurrency = concurrency
        self.task_q = []
        self.hosts = self._expand_globs()
        self.event = self.threading.Event()

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

        for host in self.hosts:
            if len(self.task_q) == self.concurrency:
                self.event.wait()
                self.event.clear()
                self._task_cleanup()
            t = TaskRunner(host, self.tasks[:], self.event)
            t.start()
            self.task_q.append(t)

    def _task_cleanup(self):
        new_task_q = []
        for task in self.task_q:
            if task.isAlive():
                new_task_q.append(task)
        self.task_q = new_task_q

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
        if not self.hostglobs:
            return []
        if isinstance(self.hostglobs, basestring):
            glob = self.hostglobs
        else:
            glob = ';'.join(self.hostglobs)
        c = self.fc.Client(glob)
        return c.list_minions()

#     def _host_groups(self):
#         """
#         Returns a List of Lists which subdivides the hosts into chunks
#         based on concurrency.

#         Example:

#         If self.hosts = ['host1', 'host2', 'host3', 'host4'] and
#         concurrency = 2, then return

#         [['host1', 'host2'], ['host3', 'host4']]
#         """
#         if self.concurrency >= len(self.hosts):
#             return [self.hosts]

#         groups = []
#         this_group = []
#         for host in self.hosts:
#             this_group.append(host)
#             if len(this_group) == self.concurrency:
#                 groups.append(this_group)
#                 this_group = []
#         if this_group:
#             groups.append(this_group)
#         return groups


class TaskRunner(threading.Thread):
    def __init__(self, host, tasks, event):
        threading.Thread.__init__(self)
        self._host = host
        self._tasks = tasks
        self._event = event

    def run(self):
        from poseidon.tasks import FuncTask
        for task in self._tasks:
            if isinstance(task, FuncTask):
                task.set_host(self._host)
            task.run()
        self._event.set()
