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


class Runner(object):
    """
    The Runner, responsible for running a poseidon job.
    """

    import threading
    import poseidon.output

    def __init__(self, hostglobs, tasks, concurrency=1,
                 output=[poseidon.output.CLIOutput], expand_globs=True):
        """
        :Parameters:
           - `hostglobs`: a List of Func-compatible host globs to operate on.
           - `tasks`: a List of tasks to execute.  Each item in this list must
             follow the following format:
               - A single `type` object, which will be instantiated with no
                 arguments
               - A 2-tuple of the form (`type`, `arg`) where `arg` is the only
                 argument used to instantiate `type`
               - A 2-tuple of the form (`type`, `tuple`) where `tuple` is used
                 to construct `type` via positional argument expansion
           - `concurrency`: the number of hosts on which to operate on
             simultaneously.
           - `output`: a list following the same format as `tasks`, containing
             types (and possibly arguments) used for output
           - `expand_globs`: whether to expand the globs or just leave them as
             is.
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

    def run(self):
        """
        Run the job.
        """
        for host in self._hosts:
            t = TaskRunner(host, self._tasks, self._semaphore, self._output,
                           self._fail_event)
            t.start()
            self._task_q.append(t)

        for task in self._task_q:
            task.join()

    def _expand_globs(self):
        """
        Returns the hosts that expand out from globs.
        """

        import func.overlord.client as fc

        if not self._hostglobs:
            return []
        if isinstance(self._hostglobs, basestring):
            glob = self._hostglobs
        else:
            glob = ';'.join(self._hostglobs)
        c = fc.Client(glob)
        return c.list_minions()


class TaskRunner(threading.Thread):
    """
    TaskRunner is responsible for executing a set of tasks for a
    single host in it's own thread.
    """

    from poseidon.tasks import TaskResult as _TaskResult

    def __init__(self, host, tasks, semaphore, output, fail_event):
        """
        :Parameters:
          - `host`: The host to operate on.
          - `tasks`: A list of tasks to perform (see class::`Runner`)
          - `semaphore`: The :class:`Runner` semaphore to acquire before
            executing
          - `output`: A list of outputters to use. (see class::`Runner`)
          - `fail_event`: The :class:`Runner` failure event to check before
            executing.  If this event is set when the TaskRunner acquires the
            semaphore, then the TaskRunner is effectively a no-op.
        """

        threading.Thread.__init__(self)
        self._host = host
        self._tasks = tasks
        self._semaphore = semaphore
        self._output = output
        self._fail_event = fail_event
        self._state = {}

    def __getitem__(self, key):
        return self._state[key]

    def __setitem__(self, key, value):
        self._state[key] = value

    def run(self):
        """
        Run the task(s) for the given host.  If the fail_event passed
        from the invoking :class:`Runner` is set, do nothing.
        """

        self._semaphore.acquire()

        if self._fail_event.isSet():
            # some other host has bombed
            self._semaphore.release()
            return

        try:
            host_success = True
            for task in self._tasks:
                result = self.run_task(task)
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

    def _bail_failure(self):
        """
        Die nicely :)
        """

        self._fail_event.set()
        self._semaphore.release()

    def run_task(self, task):
        """
        Run a single task.  Sets task.host and then invokes the run
        method for the task.

        :Parameters:
          - `task`: The task to run
        """

        task = self.__instantiator(task, host=self._host)

        outputters = []
        for o in self._output:
            instance = self.__instantiator(o, host=self._host, task=task)
            outputters.append(instance)

        try:
            result = task.run(self)
        except Exception, e:
            result = self._TaskResult(task, output=repr(e))

        for o in outputters:
            o.write(result)

        return result

    def __instantiator(self, type_blob, **kwargs):
        """
        Instantiate a type, which must be in one of the following formats:
          - A single `type` object
          - A 2-tuple of the form (`type`, `arg`) where `arg` is the only
            argument used to instantiate `type`
          - A 2-tuple of the form (`type`, `tuple`) where `tuple` is used
            to construct `type` via positional argument expansion
        In all cases, **kwargs is also passed in at instantiation. Most common
        case for this is setting host.

        Returns the instantiated object.
        """

        the_type, args = (None, None)
        if isinstance(type_blob, tuple):
            the_type = type_blob[0]
        elif isinstance(type_blob, type):
            return type_blob(**kwargs)

        try:
            args = type_blob[1]
        except:
            args = ()

        if not isinstance(args, tuple):
            args = (args, )

        return the_type(*args, **kwargs)
