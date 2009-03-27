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

class CheckFailed(Exception):
    pass

class Runner(object):
    """
    The Runner, responsible for running a poseidon job.
    """

    import func.overlord.client as fc

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
        self.hosts = self._expand_globs()
        self.host_groups = self._host_groups()

    def run(self, check=True, ignore_errors=False, dry_run=False):
        """
        Run the job.

        :Parameters:
           - `check`: whether to run self.check before.
           - `ignore_errors`: whether to ignore faults in tasks.
           - `dry_run`: if True, don't actually execute tasks, just print info
        """
        if check:
            self.check()

        for group in self.host_groups:
            for task in self.tasks:
                d = Dispatcher(group, task, dry_run)
                success = d.run()

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
        #DEBUG
        return ['host1', 'host2', 'host3', 'host4', 'host5', 'host6']
        if not self.hostglobs:
            return []
        if isinstance(self.hostglobs, basestring):
            glob = self.hostglobs
        else:
            glob = ';'.join(self.hostglobs)
        c = self.fc.Client(glob)
        return c.list_minions()

    def _host_groups(self):
        """
        Returns a List of Lists which subdivides the hosts into chunks
        based on concurrency.

        Example:

        If self.hosts = ['host1', 'host2', 'host3', 'host4'] and
        concurrency = 2, then return

        [['host1', 'host2'], ['host3', 'host4']]
        """
        if self.concurrency >= len(self.hosts):
            return [self.hosts]

        groups = []
        this_group = []
        for host in self.hosts:
            this_group.append(host)
            if len(this_group) == self.concurrency:
                groups.append(this_group)
                this_group = []
        if this_group:
            groups.append(this_group)
        return groups

class Dispatcher(object):
    """
    Run a task.
    """

    def __init__(self, hosts, task, dry_run):
        self.hosts = hosts
        self.task = task
        self.dry_run = dry_run

    def run(self):
        """
        Run the task.  If dry_run, just print what you're doing.
        """
        if self.dry_run:
            print "Executing task '%s' on hosts %s" % (self.task, self.hosts)
            return
